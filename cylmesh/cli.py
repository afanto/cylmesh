"""
Command-line interface parser and validation.
"""

import argparse
from .utils import ValidationError, validate_positive_float, validate_positive_list


class CLIParser:
    """Handles command-line argument parsing and validation."""
    
    def __init__(self, version, author, date):
        self.version = version
        self.author = author
        self.date = date
    
    def create_parser(self):
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description=f"Generate a cylindrical multilayer finite-element mesh with Gmsh. (v{self.version})",
            epilog=f"Created by {self.author}, {self.date}. For more examples and documentation, visit: https://github.com/afanto/cylmesh"
        )

        parser.add_argument("--version", action="version", 
                          version=f"cylmesh v{self.version} by {self.author} ({self.date})")

        # Geometry parameters
        geo_group = parser.add_argument_group("geometry parameters")
        geo_group.add_argument("--ml", type=float,
                              help="Characteristic mesh length (nm) [REQUIRED unless using --config]")
        geo_group.add_argument("--radius", type=float,
                              help="Cylinder radius (nm) [REQUIRED unless using --config]")
        geo_group.add_argument("--layers", type=float, nargs='+', 
                              help="Layer thicknesses in nm (space-separated) [REQUIRED unless using --config]")
        geo_group.add_argument("--subdivisions", type=int, nargs='*', 
                              help="Vertical subdivisions per layer (optional, defaults to 1 for each)")
        geo_group.add_argument("--layer-names", type=str, nargs='*',
                              help="Optional names for layers (e.g., --layer-names FM1 Spacer FM2)")
        geo_group.add_argument("--config", type=str,
                              help="Load parameters from JSON config file")

        # File parameters
        file_group = parser.add_argument_group("file parameters")
        file_group.add_argument("--geo", default="mesh.geo", 
                               help="Output .geo filename")
        file_group.add_argument("--mesh", default="mesh.msh", 
                               help="Output .msh filename")

        # Execution parameters
        exec_group = parser.add_argument_group("execution parameters")
        exec_group.add_argument("--no-run", action="store_true",
                               help="Only write the .geo file; skip the Gmsh step")
        exec_group.add_argument("--gui", action="store_true",
                               help="Open Gmsh GUI instead of generating mesh automatically")
        exec_group.add_argument("--verbose", "-v", action="store_true",
                               help="Enable verbose output from Gmsh")
        exec_group.add_argument("--save-config", type=str,
                               help="Save current parameters to JSON config file")

        return parser
    
    def parse_and_validate(self):
        """Parse command line arguments and perform validation."""
        parser = self.create_parser()
        args = parser.parse_args()
        
        # Check if no meaningful arguments provided - show help
        if not args.layers and not args.config and not args.save_config:
            parser.print_help()
            import sys
            sys.exit(0)
        
        # Validate required parameters
        if not args.config:
            # If not using config, ml, radius, and layers are all required
            if not args.layers:
                parser.error("--layers is required unless using --config")
            if args.ml is None:
                parser.error("--ml is required unless using --config")
            if args.radius is None:
                parser.error("--radius is required unless using --config")
        
        try:
            # Set default layers if not provided (fallback for config loading)
            if not args.layers:
                args.layers = []  # Will be set from config
            
            # Validate subdivisions (only if layers are provided)
            if args.layers and args.subdivisions and len(args.subdivisions) != len(args.layers):
                raise ValidationError(f"Number of subdivisions ({len(args.subdivisions)}) must match number of layers ({len(args.layers)})")
            
            if args.layers and not args.subdivisions:
                args.subdivisions = [1] * len(args.layers)
            
            # Validate positive values
            if args.layers:
                validate_positive_list(args.layers, "layer thicknesses")
            if args.radius is not None:
                validate_positive_float(args.radius, "radius")
            if args.ml is not None:
                validate_positive_float(args.ml, "mesh length")
            
        except ValidationError as e:
            parser.error(str(e))
        
        return args, parser
