"""
Main application orchestrator for the mesh generator.
"""

import sys
from .geometry import GeometryGenerator
from .gmsh_interface import GmshInterface
from .config import ConfigManager
from .cli import CLIParser
from .display import DisplayManager


class MeshGeneratorApp:
    """Main application class that orchestrates the mesh generation process."""
    
    def __init__(self, version, author, date):
        self.version = version
        self.author = author
        self.date = date
        
        self.cli_parser = CLIParser(version, author, date)
        self.config_manager = ConfigManager()
        self.gmsh_interface = GmshInterface()
        self.display_manager = DisplayManager()
    
    def run(self):
        """Main execution method."""
        # Parse command line arguments
        args, parser = self.cli_parser.parse_and_validate()
        
        # Load config file if specified
        if args.config:
            config = self.config_manager.load_config(args.config)
            self.config_manager.apply_config_to_args(args, parser, config)
            
            # Ensure subdivisions are set after config loading
            if not args.subdivisions and args.layers:
                args.subdivisions = [1] * len(args.layers)
        
        # Final validation - ensure we have all required parameters after config loading
        if not args.layers:
            print("Error: No layers specified. Use --layers or provide a --config file with layers.")
            parser.print_help()
            sys.exit(1)
        
        if args.ml is None:
            print("Error: No mesh length specified. Use --ml or provide a --config file with ml.")
            parser.print_help()
            sys.exit(1)
        
        if args.radius is None:
            print("Error: No radius specified. Use --radius or provide a --config file with radius.")
            parser.print_help()
            sys.exit(1)
        
        # Final validation of positive values
        try:
            from .utils import validate_positive_float, validate_positive_list
            validate_positive_list(args.layers, "layer thicknesses")
            validate_positive_float(args.radius, "radius")
            validate_positive_float(args.ml, "mesh length")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        
        # Save config if requested
        if args.save_config:
            self.config_manager.save_config(args, args.save_config)
            return  # Don't proceed after saving config
        
        # Check Gmsh availability unless we're in no-run mode
        if not args.no_run:
            gmsh_version = self.gmsh_interface.check_availability()
            if not gmsh_version:
                self.gmsh_interface.display_installation_help()
                sys.exit("Cannot continue without Gmsh")
            else:
                print(f"→ Using {gmsh_version}")
        
        # Generate geometry file
        self._generate_geometry_file(args)

        # Handle no-run mode
        if args.no_run:
            self.display_manager.print_no_run_info(args)
            return

        # Run Gmsh
        self.gmsh_interface.run_mesh_generation(
            args.geo, 
            args.mesh, 
            gui_mode=args.gui, 
            verbose=args.verbose
        )
        
        # Display summary if not in GUI mode
        if not args.gui:
            self.display_manager.print_summary(args)
    
    def _generate_geometry_file(self, args):
        """Generate and write the geometry file."""
        geometry_generator = GeometryGenerator(
            args.ml,
            args.radius,
            args.layers,
            args.subdivisions,
            getattr(args, 'layer_names', None)
        )
        
        geo_content = geometry_generator.generate_geo_script()
        self.gmsh_interface.write_geometry_file(geo_content, args.geo)


def main():
    """Entry point for the command line interface."""
    from . import __version__, __author__, __date__
    
    app = MeshGeneratorApp(__version__, __author__, __date__)
    app.run()


if __name__ == "__main__":
    main()
