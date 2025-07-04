"""
Fluent/Builder API for intuitive mesh creation.
"""

from .mesh_generator import create_mesh
from .config import ConfigManager


class MeshBuilder:
    """
    Fluent interface for building cylindrical meshes.
    
    Example:
        mesh = (MeshBuilder()
                .cylinder(radius=10.0)
                .mesh_size(2.0)
                .add_layer("Base", thickness=2.0, subdivisions=2)
                .add_layer("Interface", thickness=1.0)
                .add_layer("Top", thickness=3.0, subdivisions=2)
                .build())
    """
    
    def __init__(self):
        self._radius = None
        self._ml = None
        self._layers = []
        self._subdivisions = []
        self._layer_names = []
        self._output_name = "mesh"
        self._gui_mode = False
        self._verbose = False
        self._geo_only = False
    
    def cylinder(self, radius):
        """Set cylinder radius."""
        self._radius = radius
        return self
    
    def mesh_size(self, ml):
        """Set characteristic mesh length."""
        self._ml = ml
        return self
    
    def add_layer(self, name_or_thickness, thickness=None, subdivisions=1):
        """
        Add a layer to the cylinder.
        
        Args:
            name_or_thickness: Layer name (str) or thickness (float)
            thickness: Layer thickness if first arg is name
            subdivisions: Number of vertical subdivisions
        """
        if isinstance(name_or_thickness, str):
            # Named layer: add_layer("Base", thickness=2.0)
            name = name_or_thickness
            if thickness is None:
                raise ValueError("thickness required when providing layer name")
            thick = thickness
        else:
            # Unnamed layer: add_layer(2.0)
            thick = name_or_thickness
            name = None
        
        self._layers.append(thick)
        self._subdivisions.append(subdivisions)
        if name:
            # Pad layer names list if needed
            while len(self._layer_names) < len(self._layers) - 1:
                self._layer_names.append(None)
            self._layer_names.append(name)
        
        return self
    
    def output(self, name):
        """Set output filename base."""
        self._output_name = name
        return self
    
    def gui(self, enabled=True):
        """Enable/disable GUI mode."""
        self._gui_mode = enabled
        return self
    
    def verbose(self, enabled=True):
        """Enable/disable verbose output."""
        self._verbose = enabled
        return self
    
    def geometry_only(self, enabled=True):
        """Only generate geometry file, skip meshing."""
        self._geo_only = enabled
        return self
    
    def build(self):
        """Build the mesh with current settings."""
        if self._radius is None:
            raise ValueError("Cylinder radius not set. Use .cylinder(radius)")
        if self._ml is None:
            raise ValueError("Mesh size not set. Use .mesh_size(ml)")
        if not self._layers:
            raise ValueError("No layers defined. Use .add_layer()")
        
        # Clean up layer names (remove None entries from end)
        layer_names = self._layer_names if any(self._layer_names) else None
        
        return create_mesh(
            ml=self._ml,
            radius=self._radius,
            layers=self._layers,
            subdivisions=self._subdivisions,
            layer_names=layer_names,
            output_name=self._output_name,
            gui_mode=self._gui_mode,
            verbose=self._verbose,
            geo_only=self._geo_only
        )


class ConfigBuilder:
    """Builder for creating configuration files."""
    
    def __init__(self):
        self._config = {}
    
    def from_builder(self, mesh_builder):
        """Create config from a MeshBuilder."""
        self._config = {
            "ml": mesh_builder._ml,
            "radius": mesh_builder._radius,
            "layers": mesh_builder._layers,
            "subdivisions": mesh_builder._subdivisions,
        }
        if any(mesh_builder._layer_names):
            self._config["layer_names"] = mesh_builder._layer_names
        return self
    
    def save(self, filename):
        """Save configuration to JSON file."""
        config_manager = ConfigManager()
        config_manager.save_config_dict(self._config, filename)
        return self
