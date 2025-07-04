"""
High-level mesh generation functions for easy usage.
"""

import os
import re
from .geometry import GeometryGenerator
from .gmsh_interface import GmshInterface
from .utils import validate_positive_float, validate_positive_list, validate_matching_lengths


def _extract_mesh_statistics(msh_file):
    """
    Extract basic statistics from a Gmsh .msh file.
    
    Args:
        msh_file (str): Path to the .msh file
        
    Returns:
        dict: Dictionary with mesh statistics including vertex and element counts
    """
    stats = {
        'physical_groups': {},
        'num_vertices': 0,
        'num_elements': 0
    }
    
    try:
        with open(msh_file, 'r') as f:
            content = f.read()
        
        # Extract physical groups
        phys_section = re.search(r'\$PhysicalNames\s*\n(.*?)\$EndPhysicalNames', content, re.DOTALL)
        if phys_section:
            lines = phys_section.group(1).strip().split('\n')
            if lines and lines[0].isdigit():
                num_groups = int(lines[0])
                for i in range(1, min(num_groups + 1, len(lines))):
                    parts = lines[i].split()
                    if len(parts) >= 3:
                        group_name = parts[2].strip('"')
                        stats['physical_groups'][group_name] = {
                            'dimension': int(parts[0]),
                            'tag': int(parts[1])
                        }
        
        # Extract vertex count from Nodes section
        nodes_section = re.search(r'\$Nodes\s*\n(.*?)\n', content)
        if nodes_section:
            node_header = nodes_section.group(1).strip().split()
            if len(node_header) >= 4:
                stats['num_vertices'] = int(node_header[3])  # Total number of nodes
        
        # Extract element count from Elements section  
        elements_section = re.search(r'\$Elements\s*\n(.*?)\n', content)
        if elements_section:
            elem_header = elements_section.group(1).strip().split()
            if len(elem_header) >= 4:
                stats['num_elements'] = int(elem_header[3])  # Total number of elements
                        
    except Exception:
        # If parsing fails, return empty stats
        pass
        
    return stats


def create_mesh(ml, radius, layers, subdivisions=None, layer_names=None, 
                output_name="mesh", gui_mode=False, verbose=False, 
                geo_only=False, progress_callback=None):
    """
    Create a cylindrical multilayer mesh with a single function call.
    
    This is a high-level convenience function that handles the complete workflow:
    geometry generation → .geo file creation → Gmsh execution → .msh file output.
    
    Args:
        ml (float): Characteristic mesh length (nm)
        radius (float): Cylinder radius (nm)
        layers (list[float]): Layer thicknesses in nm
        subdivisions (list[int], optional): Vertical subdivisions per layer. 
                                          Defaults to [1] for each layer.
        layer_names (list[str], optional): Names for layers (used in Physical Volumes)
        output_name (str): Base name for output files (without extension).
                          Default: "mesh"
        gui_mode (bool): Open Gmsh GUI instead of batch processing. Default: False
        verbose (bool): Show Gmsh output messages. Default: False
        geo_only (bool): Only create .geo file, skip Gmsh execution. Default: False
        progress_callback (callable, optional): Function to call with progress updates.
                                               Called with (step, total_steps, message)
    
    Returns:
        dict: Result dictionary with keys:
            - 'success' (bool): Whether the operation succeeded
            - 'geo_file' (str): Path to generated .geo file
            - 'msh_file' (str): Path to generated .msh file (None if geo_only=True)
            - 'error' (str): Error message if success=False
            - 'geo_size' (int): Size of .geo file in characters
            - 'msh_size' (int): Size of .msh file in bytes (None if geo_only=True)
    
    Examples:
        >>> # Simple mesh
        >>> result = create_mesh(ml=2.0, radius=10.0, layers=[3.0, 2.0])
        
        >>> # Detailed mesh with layer names
        >>> result = create_mesh(
        ...     ml=1.5, radius=8.0, layers=[2.0, 1.0, 3.0],
        ...     subdivisions=[2, 1, 2], 
        ...     layer_names=['Bottom', 'Spacer', 'Top'],
        ...     output_name='my_device'
        ... )
        
        >>> # Only create geometry file
        >>> result = create_mesh(ml=2.0, radius=5.0, layers=[1.0], geo_only=True)
        
    Note:
        This function does not raise exceptions. All errors are returned in the 
        result dictionary with success=False and a descriptive error message.
    """
    
    # Input validation
    try:
        # Type validation
        if not isinstance(layers, (list, tuple)):
            raise ValueError("layers must be a list or tuple of numbers")
        if subdivisions is not None and not isinstance(subdivisions, (list, tuple)):
            raise ValueError("subdivisions must be a list or tuple of integers")
        if layer_names is not None and not isinstance(layer_names, (list, tuple)):
            raise ValueError("layer_names must be a list or tuple of strings")
            
        validate_positive_float(ml, "mesh length")
        validate_positive_float(radius, "radius")
        validate_positive_list(layers, "layer thicknesses")
        
        # Set default subdivisions if not provided
        if subdivisions is None:
            subdivisions = [1] * len(layers)
        else:
            validate_matching_lengths(subdivisions, layers, "subdivisions", "layers")
        
        # Validate layer names if provided
        if layer_names is not None:
            validate_matching_lengths(layer_names, layers, "layer names", "layers")
                
    except Exception as e:
        return {
            'success': False,
            'geo_file': None,
            'msh_file': None,
            'error': str(e),
            'geo_size': None,
            'msh_size': None,
            'parameters': {
                'ml': None,
                'radius': None,
                'layers': None,
                'subdivisions': None,
                'layer_names': None,
                'total_height': None,
                'num_layers': None
            },
            'mesh_info': {}
        }
    
    # File paths
    geo_file = f"{output_name}.geo"
    msh_file = f"{output_name}.msh" if not geo_only else None
    
    try:
        total_steps = 3 if geo_only else 5
        
        if progress_callback:
            progress_callback(1, total_steps, "Creating geometry generator...")
            
        # Step 1: Create geometry generator
        geometry_gen = GeometryGenerator(
            ml=ml,
            radius=radius,
            layer_thicknesses=layers,
            subdivisions=subdivisions,
            layer_names=layer_names
        )
        
        if progress_callback:
            progress_callback(2, total_steps, "Generating geometry script...")
        
        # Step 2: Generate geometry script
        geo_content = geometry_gen.generate_geo_script()
        geo_size = len(geo_content)
        
        if progress_callback:
            progress_callback(3, total_steps, f"Writing geometry file: {geo_file}")
        
        # Step 3: Write .geo file
        gmsh_interface = GmshInterface()
        gmsh_interface.write_geometry_file(geo_content, geo_file)
        
        if geo_only:
            return {
                'success': True,
                'geo_file': geo_file,
                'msh_file': None,
                'error': None,
                'geo_size': geo_size,
                'msh_size': None,
                'parameters': {
                    'ml': ml,
                    'radius': radius,
                    'layers': layers,
                    'subdivisions': subdivisions,
                    'layer_names': layer_names,
                    'total_height': sum(layers),
                    'num_layers': len(layers)
                },
                'mesh_info': {}
            }
        
        # Step 4: Run Gmsh to create .msh file
        gmsh_interface.run_mesh_generation(
            geo_path=geo_file,
            mesh_path=msh_file,
            gui_mode=gui_mode,
            verbose=verbose
        )
        
        # Step 5: Check results and gather mesh statistics
        msh_size = None
        mesh_info = {}
        
        if os.path.exists(msh_file):
            msh_size = os.path.getsize(msh_file)
            
            # Extract basic mesh statistics from the .msh file
            try:
                mesh_info = _extract_mesh_statistics(msh_file)
            except Exception:
                # If we can't extract stats, just continue
                pass
                
        elif not gui_mode:  # GUI mode doesn't guarantee mesh creation
            return {
                'success': False,
                'geo_file': geo_file,
                'msh_file': None,
                'error': f"Mesh file {msh_file} was not created",
                'geo_size': geo_size,
                'msh_size': None,
                'parameters': {
                    'ml': ml,
                    'radius': radius,
                    'layers': layers,
                    'subdivisions': subdivisions,
                    'layer_names': layer_names,
                    'total_height': sum(layers),
                    'num_layers': len(layers)
                },
                'mesh_info': {}
            }
        
        return {
            'success': True,
            'geo_file': geo_file,
            'msh_file': msh_file,
            'error': None,
            'geo_size': geo_size,
            'msh_size': msh_size,
            'parameters': {
                'ml': ml,
                'radius': radius,
                'layers': layers,
                'subdivisions': subdivisions,
                'layer_names': layer_names,
                'total_height': sum(layers),
                'num_layers': len(layers)
            },
            'mesh_info': mesh_info
        }
        
    except Exception as e:
        return {
            'success': False,
            'geo_file': geo_file if os.path.exists(geo_file) else None,
            'msh_file': None,
            'error': str(e),
            'geo_size': None,
            'msh_size': None,
            'parameters': {
                'ml': ml if 'ml' in locals() else None,
                'radius': radius if 'radius' in locals() else None,
                'layers': layers if 'layers' in locals() else None,
                'subdivisions': subdivisions if 'subdivisions' in locals() else None,
                'layer_names': layer_names if 'layer_names' in locals() else None,
                'total_height': sum(layers) if 'layers' in locals() and layers else None,
                'num_layers': len(layers) if 'layers' in locals() and layers else None
            },
            'mesh_info': {}
        }


def create_mesh_from_config(config_file, output_name="mesh", gui_mode=False, 
                           verbose=False, geo_only=False):
    """
    Create a mesh from a configuration file.
    
    Args:
        config_file (str): Path to JSON configuration file
        output_name (str): Base name for output files. Default: "mesh"
        gui_mode (bool): Open Gmsh GUI. Default: False
        verbose (bool): Show Gmsh output. Default: False
        geo_only (bool): Only create .geo file. Default: False
    
    Returns:
        dict: Same as create_mesh() function
        
    Example:
        >>> result = create_mesh_from_config('my_device.json', output_name='device')
    """
    
    try:
        from .config import ConfigManager
        
        # Load configuration
        config_manager = ConfigManager()
        config = config_manager.load_config(config_file)
        
        # Extract parameters
        ml = config.get('ml')
        radius = config.get('radius')
        layers = config.get('layers')
        subdivisions = config.get('subdivisions')
        layer_names = config.get('layer_names')
        
        # Validate required parameters
        if ml is None:
            raise ValueError("Config file missing required parameter: 'ml'")
        if radius is None:
            raise ValueError("Config file missing required parameter: 'radius'")
        if layers is None:
            raise ValueError("Config file missing required parameter: 'layers'")
            
        # Call main create_mesh function
        return create_mesh(
            ml=ml,
            radius=radius,
            layers=layers,
            subdivisions=subdivisions,
            layer_names=layer_names,
            output_name=output_name,
            gui_mode=gui_mode,
            verbose=verbose,
            geo_only=geo_only
        )
        
    except Exception as e:
        return {
            'success': False,
            'geo_file': None,
            'msh_file': None,
            'error': f"Error loading config: {e}",
            'geo_size': None,
            'msh_size': None,
            'parameters': {
                'ml': None,
                'radius': None,
                'layers': None,
                'subdivisions': None,
                'layer_names': None,
                'total_height': None,
                'num_layers': None
            },
            'mesh_info': {}
        }


def print_mesh_summary(result):
    """
    Print a formatted summary of mesh generation results.
    
    Args:
        result (dict): Result dictionary from create_mesh() or create_mesh_from_config()
        
    Example:
        >>> result = create_mesh(ml=2.0, radius=10.0, layers=[3.0, 2.0])
        >>> print_mesh_summary(result)
    """
    print()
    print("="*60)
    print("MESH GENERATION SUMMARY")
    print("="*60)
    
    if result['success']:
        print("✅ Mesh generation successful!")
        print(f"📁 Geometry file: {result['geo_file']}")
        print(f"📁 Mesh file: {result['msh_file']}")
        
        # Convert sizes to MB
        geo_size_mb = result['geo_size'] / (1024 * 1024)  # characters to MB (approximate)
        msh_size_mb = result['msh_size'] / (1024 * 1024)  # bytes to MB
        
        print(f"📏 Geometry file size: {geo_size_mb:.3f} MB")
        print(f"📏 Mesh file size: {msh_size_mb:.3f} MB")
        
        params = result['parameters']
        print(f"\n🔧 PARAMETERS:")
        print(f"   • Mesh length: {params['ml']}")
        print(f"   • Radius: {params['radius']}")
        print(f"   • Total height: {params['total_height']}")
        print(f"   • Number of layers: {params['num_layers']}")
        print(f"   • Layer thicknesses: {params['layers']}")
        if params['layer_names']:
            print(f"   • Layer names: {params['layer_names']}")
        print(f"   • Subdivisions: {params['subdivisions']}")
        
        mesh_info = result['mesh_info']
        print(f"\n🌐 MESH STATISTICS:")
        print(f"   • Vertices (nodes): {mesh_info.get('num_vertices', 'N/A')}")
        print(f"   • Elements: {mesh_info.get('num_elements', 'N/A')}")
        
        if mesh_info['physical_groups']:
            print(f"   • Physical groups: {len(mesh_info['physical_groups'])}")
            
            # Separate surfaces and volumes
            surfaces = {name: info for name, info in mesh_info['physical_groups'].items() if info['dimension'] == 2}
            volumes = {name: info for name, info in mesh_info['physical_groups'].items() if info['dimension'] == 3}
            
            if surfaces:
                print(f"       Surfaces ({len(surfaces)}):")
                for name, info in surfaces.items():
                    print(f"       - {name} (tag {info['tag']})")
            
            if volumes:
                print(f"       Volumes ({len(volumes)}):")
                for name, info in volumes.items():
                    print(f"       - {name} (tag {info['tag']})")
        
    else:
        print("❌ Mesh generation failed!")
        print(f"💥 Error: {result['error']}")
        if result['geo_file']:
            print(f"📁 Geometry file: {result['geo_file']} (may have been created)")
    
    print("="*60)
