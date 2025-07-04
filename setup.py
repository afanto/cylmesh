"""
Setup script for the CylMesh package.
"""

from setuptools import setup, find_packages

# Read the version from the package
with open("cylmesh/__init__.py", "r") as f:
    for line in f:
        if line.startswith("__version__"):
            version = line.split("=")[1].strip().strip('"').strip("'")
            break

long_description = "A flexible mesh generator for cylindrical multilayer structures using Gmsh."

setup(
    name="cylmesh",
    version=version,
    author="Afan",
    description="A flexible mesh generator for cylindrical multilayer structures using Gmsh",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/afanto/cylmesh",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    python_requires=">=3.7",
    install_requires=[
        "gmsh",
    ],
    entry_points={
        "console_scripts": [
            "cylmesh=cylmesh.app:main",
        ],
    },
)
