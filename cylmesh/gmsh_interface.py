"""
Interface for interacting with Gmsh mesh generation software.
"""

import os
import subprocess
import sys
from pathlib import Path

from .utils import ColorFormatter


class GmshInterface:
    """Handles Gmsh operations including checking availability and running mesh generation."""
    
    @staticmethod
    def check_availability():
        """Check if Gmsh is available in the system PATH."""
        try:
            result = subprocess.run(["gmsh", "--version"], 
                                  capture_output=True, text=True, check=True)
            version = result.stdout.strip().split('\n')[0]
            return version
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    @staticmethod
    def write_geometry_file(geo_content, geo_path):
        """Write geometry content to a .geo file."""
        try:
            # Ensure output directory exists
            Path(geo_path).parent.mkdir(parents=True, exist_ok=True)
            
            with open(geo_path, "w") as f:
                f.write(geo_content)
            print(f"✓ Wrote {geo_path}")
            
            # Validate the geo file size
            file_size = os.path.getsize(geo_path)
            if file_size < 100:  # Suspiciously small
                print(f"⚠️  Warning: Generated .geo file is very small ({file_size} bytes)")
                
        except Exception as e:
            sys.exit(f"✗ Failed to write geometry file: {e}")
    
    @staticmethod
    def run_mesh_generation(geo_path, mesh_path, gui_mode=False, verbose=False):
        """Run Gmsh to generate mesh from geometry file."""
        # Ensure output directory exists
        Path(mesh_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Build command
        if gui_mode:
            cmd = ["gmsh", geo_path]
            print("→ Opening Gmsh GUI...")
        else:
            cmd = ["gmsh", geo_path, "-3", "-o", mesh_path]
            # Add verbosity control
            if verbose:
                cmd.extend(["-v", "2"])
            else:
                cmd.extend(["-v", "0"])  # Quiet mode
        
        print("→ Running:", " ".join(cmd))
        
        try:
            if gui_mode:
                # For GUI, don't wait for completion
                subprocess.Popen(cmd)
                print("✓ Gmsh GUI opened. Mesh generation depends on user actions.")
            else:
                # Handle verbose output differently
                if verbose:
                    # Show Gmsh output in real-time
                    result = subprocess.run(cmd, check=True, text=True)
                else:
                    # Capture output to keep it quiet
                    result = subprocess.run(cmd, check=True, capture_output=True, text=True)
                
                # Check if mesh file was created and has reasonable size
                if os.path.exists(mesh_path):
                    mesh_size = os.path.getsize(mesh_path)
                    if mesh_size > 0:
                        print(f"✓ Mesh generated → {mesh_path} ({mesh_size:,} bytes)")
                    else:
                        print(f"⚠️  Warning: Mesh file is empty")
                else:
                    print(f"⚠️  Warning: Mesh file not found at {mesh_path}")
                    
        except subprocess.CalledProcessError as e:
            error_msg = f"✗ Gmsh failed (exit code {e.returncode})"
            if hasattr(e, 'stderr') and e.stderr:
                error_msg += f"\nStderr: {e.stderr}"
            sys.exit(error_msg)
    
    @staticmethod
    def display_installation_help():
        """Display help for installing Gmsh."""
        C = ColorFormatter
        print(f"{C.YELLOW}⚠️  Warning: Gmsh not found in PATH. Install with:{C.RESET}")
        print("   - conda install gmsh")
        print("   - or download from https://gmsh.info/")
