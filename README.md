# AI Usage Decalaration

This tool is fully vibecoded using Claude.ai on the Claude 3.7 Sonnet mode with Reasoning. I wrote nothing myself, I just created this because I required a quick conversion of IFC files to PointCloud. I figured I'd upload it here in case someone requires something similar. 

The code in this project does not represent my personal coding standards :^)

# IFC to Point Cloud Converter

A high-performance Python tool for converting IFC (Industry Foundation Classes) files to point clouds with parallel processing, element filtering, and interactive visualization capabilities.

## Overview

This tool processes Building Information Modeling (BIM) data from IFC files and generates point cloud representations. It's particularly useful for:

- Creating point cloud datasets from BIM models
- Filtering specific building elements (doors, windows, walls, etc.)
- Visualizing building models with color-coded element types
- Preprocessing BIM data for machine learning applications
- Converting architectural models for 3D scanning comparisons

## Features

- **Parallel Processing**: Utilizes multiple CPU cores for faster conversion
- **Element Filtering**: Exclude specific IFC element types (e.g., doors, windows)
- **Interactive Visualization**: 
  - Color-coded mesh view by element type
  - Wireframe view for internal structure inspection
  - Final point cloud visualization
- **Element Analysis**: List and count all element types in an IFC file
- **Interactive Filtering Mode**: Interactively select which elements to exclude
- **Customizable Output**: Control point cloud density and output formats

## Requirements

- Python 3.7+
- Required packages:
  ```
  ifcopenshell
  open3d
  numpy
  ```

## Installation

1. Clone this repository or download `main.py`

2. Install required packages:
   ```bash
   pip install ifcopenshell open3d numpy
   ```

   or

  ```bash
   pip install -r requirements.txt
   ```
   

   **Note**: Installing IfcOpenShell can sometimes be tricky. If you encounter issues:
   - For Windows: Consider using conda: `conda install -c conda-forge ifcopenshell`
   - For Linux/Mac: You may need to install from the official IfcOpenShell website

## Usage

### Basic Usage

Convert an IFC file to a point cloud:
```bash
python main.py path/to/building.ifc
```

### Command-Line Options

```
usage: main.py [-h] [--output OUTPUT] [--mesh_output MESH_OUTPUT] 
               [--points POINTS] [--processes PROCESSES] 
               [--exclude EXCLUDE [EXCLUDE ...]] [--list-types] 
               [--no-display] [--interactive-filter] ifc_path

Arguments:
  ifc_path              Path to the IFC file

Options:
  -h, --help            Show help message
  -o, --output          Output point cloud file path (default: pointcloud.ply)
  -m, --mesh_output     Output mesh file path (default: mesh.ply)
  -p, --points          Number of points to sample (default: 100000)
  -n, --processes       Number of parallel processes (default: CPU count - 1)
  -e, --exclude         List of element types to exclude (e.g., IfcDoor IfcWindow)
  -l, --list-types      List all element types in the IFC file and exit
  -nd, --no-display     Don't display visual results
  -i, --interactive-filter  Interactively select element types to exclude
```

### Example Commands

1. **List all element types in an IFC file:**
   ```bash
   python main.py building.ifc --list-types
   ```

2. **Convert with specific output and point count:**
   ```bash
   python main.py building.ifc -o output.pcd -p 500000
   ```

3. **Exclude doors and windows from the conversion:**
   ```bash
   python main.py building.ifc --exclude IfcDoor IfcWindow
   ```

4. **Use interactive filtering mode:**
   ```bash
   python main.py building.ifc --interactive-filter
   ```

5. **Process without visualization (for batch processing):**
   ```bash
   python main.py building.ifc --no-display -o building_cloud.ply
   ```

## Workflow Examples

### 1. Basic Conversion Workflow

```bash
# First, analyze what's in your IFC file
python main.py mybuilding.ifc --list-types

# Convert to point cloud with default settings
python main.py mybuilding.ifc -o mybuilding_cloud.ply
```

### 2. Filtered Conversion Workflow

```bash
# List element types
python main.py mybuilding.ifc --list-types

# Convert excluding furniture and equipment
python main.py mybuilding.ifc --exclude IfcFurnishingElement IfcFlowTerminal -o structural_only.ply
```

### 3. High-Detail Conversion

```bash
# Generate a dense point cloud with 1 million points
python main.py mybuilding.ifc -p 1000000 -o detailed_cloud.ply
```

## Visualization Steps

When running the tool with visualization enabled (default), you'll see three stages:

1. **Colored Mesh View**: Building elements colored by type
   - Red, green, blue, etc. represent different IFC element types
   - Close the window to proceed to the next view

2. **Wireframe View**: Shows the internal structure
   - Useful for inspecting complex geometries
   - Close the window to continue

3. **Point Cloud View**: Final point cloud result
   - Shows the sampled points
   - Close the window to complete the process

## Common IFC Element Types

Here are some common element types you might want to filter:

- `IfcWall` - Walls
- `IfcSlab` - Floors and ceilings
- `IfcDoor` - Doors
- `IfcWindow` - Windows
- `IfcColumn` - Columns
- `IfcBeam` - Beams
- `IfcStair` - Stairs
- `IfcRoof` - Roof elements
- `IfcFurnishingElement` - Furniture
- `IfcFlowTerminal` - MEP terminals (outlets, fixtures)
- `IfcSpace` - Spatial elements (rooms)

## Output Formats

The tool supports multiple output formats through Open3D:
- `.ply` - Polygon File Format (default)
- `.pcd` - Point Cloud Data format
- `.xyz` - Simple XYZ format
- `.pts` - PTS format

Simply change the file extension in the output parameter.
