"""
Display utilities for formatted output and summaries.
"""

import os
from .utils import ColorFormatter
from .mesh_generator import _extract_mesh_statistics


class DisplayManager:
    """Handles formatted display of mesh parameters and summaries."""
    
    def __init__(self):
        self.C = ColorFormatter
    
    def print_summary(self, args):
        """Print a formatted summary of the mesh parameters."""
        # Header
        layer_count = len(args.layers)
        mesh_type = "Single Cylinder" if layer_count == 1 else f"{layer_count}-Layer Stack"
        print(f"\n{self.C.BOLD}{self.C.CYAN}★ {mesh_type} Parameters Summary {self.C.RESET}")

        # Core parameters
        print(f"  {self.C.GREEN}Radius:{self.C.RESET}       {args.radius:.2f} nm")
        print(f"  {self.C.GREEN}Mesh length:{self.C.RESET} {args.ml:.2f} nm")

        # Layer details
        print(f"\n  {self.C.YELLOW}Layer configuration:{self.C.RESET}")
        total_height = 0
        
        for i, (thickness, subdivisions) in enumerate(zip(args.layers, args.subdivisions), 1):
            layer_name = ""
            if hasattr(args, 'layer_names') and args.layer_names and i <= len(args.layer_names):
                layer_name = f" ({args.layer_names[i-1]})"
            print(f"    {self.C.MAGENTA}Layer {i}:{self.C.RESET} {thickness:.2f} nm ({subdivisions} subdivision{'s' if subdivisions != 1 else ''}){layer_name}")
            total_height += thickness
        
        print(f"    {self.C.YELLOW}Total height:{self.C.RESET} {total_height:.2f} nm")
        if layer_count > 1:
            print(f"    {self.C.YELLOW}Number of layers:{self.C.RESET} {layer_count}")
        
        # File info
        print(f"\n  {self.C.GREEN}Output files:{self.C.RESET}")
        print(f"    {self.C.GREEN}Geometry:{self.C.RESET} {args.geo}")
        if not args.no_run and not args.gui:
            print(f"    {self.C.GREEN}Mesh:{self.C.RESET}     {args.mesh}")
            
            # Add mesh statistics if mesh file exists
            if os.path.exists(args.mesh):
                try:
                    mesh_stats = _extract_mesh_statistics(args.mesh)
                    self._print_mesh_statistics(mesh_stats)
                except Exception:
                    # If mesh statistics extraction fails, silently skip
                    pass
        
        print()
    
    def _print_mesh_statistics(self, mesh_stats):
        """Print mesh statistics including vertices, elements, and physical groups."""
        print(f"\n  {self.C.CYAN}Mesh Statistics:{self.C.RESET}")
        print(f"    {self.C.MAGENTA}Vertices (nodes):{self.C.RESET} {mesh_stats.get('num_vertices', 'N/A')}")
        print(f"    {self.C.MAGENTA}Elements:{self.C.RESET} {mesh_stats.get('num_elements', 'N/A')}")
        
        if mesh_stats.get('physical_groups'):
            print(f"    {self.C.MAGENTA}Physical groups:{self.C.RESET} {len(mesh_stats['physical_groups'])}")
            
            # Separate surfaces and volumes
            surfaces = {name: info for name, info in mesh_stats['physical_groups'].items() if info['dimension'] == 2}
            volumes = {name: info for name, info in mesh_stats['physical_groups'].items() if info['dimension'] == 3}
            
            if surfaces:
                print(f"        {self.C.YELLOW}Surfaces ({len(surfaces)}):{self.C.RESET}")
                for name, info in surfaces.items():
                    print(f"        - {name} (tag {info['tag']})")
            
            if volumes:
                print(f"        {self.C.YELLOW}Volumes ({len(volumes)}):{self.C.RESET}")
                for name, info in volumes.items():
                    print(f"        - {name} (tag {info['tag']})")
    
    def print_no_run_info(self, args):
        """Print information when skipping Gmsh execution."""
        layer_count = len(args.layers)
        mesh_type = "single cylinder" if layer_count == 1 else f"{layer_count}-layer stack"
        print(f"Skipping Gmsh run (per --no-run). {mesh_type.capitalize()} geometry file ready.")
        self.print_summary(args)
