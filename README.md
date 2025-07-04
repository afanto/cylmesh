# CylMesh

A mesh generator for cylindrical multilayer structures using Gmsh, designed for finite element simulations.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Gmsh](https://img.shields.io/badge/gmsh-4.8+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Features

- **Complete mesh information**: Returns vertex counts, element counts, and physical group details
- **Clean naming**: Surfaces named as `FM1_bottom`, `FM1_top`; volumes as `FM1`, `Spacer`, etc.
- **Multiple interfaces**: Python API and command-line tool
- **Flexible configuration**: JSON config files or direct parameters

## Installation

Requires [Gmsh](https://gmsh.info/) to be installed.

```bash
git clone https://github.com/afanto/cylmesh.git
cd cylmesh
pip install . # or ./install.sh
```

## Quick Start

### Python API

```python
from cylmesh import create_mesh, print_mesh_summary

# Create mesh with layer names
result = create_mesh(
    ml=2.0,
    radius=10.0,
    layers=[2.0, 1.0, 1.5],
    layer_names=["FM1", "MgO", "FM2"],
    output_name="device"
)

# Display comprehensive mesh information
print_mesh_summary(result)
```

### Command Line

```bash
# Generate mesh with detailed output
cylmesh --ml 2.0 --radius 8.0 --layers 1.0 0.9 1.5 \
        --layer-names FM1 MgO FM2 --mesh device.msh
```

Both interfaces display:
- Vertex count (number of degrees of freedom for FEM)
- Element count (tetrahedral elements)
- Physical groups (surfaces and volumes with tags)

## API Reference

### `create_mesh(ml, radius, layers, **kwargs)`

**Parameters:**
- `ml` (float): Characteristic mesh length (nm)
- `radius` (float): Cylinder radius (nm)
- `layers` (list): Layer thicknesses (nm)
- `layer_names` (list, optional): Names for layers
- `subdivisions` (list, optional): Vertical subdivisions per layer
- `output_name` (str, optional): Base name for output files

**Returns:**
Dictionary containing:
- `success` (bool): Whether mesh generation succeeded
- `parameters` (dict): All input parameters used
- `geo_file`, `msh_file` (str): Output file paths
- `geo_size`, `msh_size` (int): File sizes in bytes
- `mesh_info` (dict): Mesh statistics including:
  - `num_vertices` (int): Number of vertices/nodes
  - `num_elements` (int): Number of tetrahedral elements
  - `physical_groups` (dict): Surface and volume information

### `create_mesh_from_config(config_file, **kwargs)`

Load parameters from JSON configuration file.

**Config file format:**
```json
{
    "ml": 3.0,
    "radius": 15.0,
    "layers": [3.0, 1.0, 2.0],
    "layer_names": ["FM1", "MgO", "FM2"],
    "subdivisions": [2, 1, 1]
}
```

### `print_mesh_summary(result)`

Pretty-print mesh generation results with organized output showing surfaces, volumes, and mesh statistics.

## Physical Group Naming

**Surfaces:**
- Bottom: `{first_layer}_bottom` (e.g., `FM1_bottom`)
- Tops: `{layer}_top` (e.g., `FM1_top`, `MgO_top`, `FM2_top`)
- Default (no names): `1_bottom`, `1_top`, `2_top`, etc.

**Volumes:**
- Named: `FM1`, `MgO`, `FM2`
- Default: `1`, `2`, `3`

## Command Line Options

```
cylmesh --ml FLOAT --radius FLOAT --layers FLOAT [FLOAT ...]
        [--layer-names STR [STR ...]]
        [--subdivisions INT [INT ...]]
        [--config FILE] [--mesh FILE] [--geo FILE]
        [--no-run] [--gui] [--verbose]
```

Use `cylmesh --help` for complete option details.

## Requirements

- Python 3.8+
- Gmsh 4.8+

## License

MIT License