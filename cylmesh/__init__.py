"""
A flexible mesh generator for cylindrical multilayer structures using Gmsh.

Author: Afan
Date: July 2025
License: MIT License
"""

from .mesh_generator import create_mesh, create_mesh_from_config, print_mesh_summary
from .builder import MeshBuilder

__version__ = "1.0.0"
__author__ = "Afan"
__date__ = "July 2025"

__all__ = [
    'create_mesh',
    'create_mesh_from_config',
    'print_mesh_summary',
    'MeshBuilder',
    
    # Metadata
    '__version__',
    '__author__',
    '__date__'
]
