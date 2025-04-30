# AI Usage Decalaration

This tool is fully vibecoded using Claude.ai on the Claude 3.7 Sonnet mode with Reasoning. I wrote nothing myself, I just created this because I required a quick conversion of IFC files to PointCloud. I figured I'd upload it here in case someone requires something similar. 

The code in this project does not represent my personal coding standards :^)

# IFCToPointCloud Converter

A robust Python tool for converting Industry Foundation Classes (IFC) files into Open3D pointcloud representations, with parallel processing capabilities for efficient handling of large models.

## Overview

This utility processes IFC files (commonly used in Building Information Modeling) and creates point cloud representations that can be used for various analysis and visualization purposes. It features element type filtering, parallel processing for performance, and interactive visualization of results at multiple stages.

## Features

- **Parallel Processing**: Efficiently processes large IFC files using multiple CPU cores
- **Element Type Filtering**: Selectively include/exclude specific IFC element types
- **Interactive Filtering Mode**: Select element types to exclude through a user-friendly interface
- **Detailed Element Analysis**: Lists all element types present in an IFC file with their counts
- **Multi-stage Visualization**:
  - Colored 3D model with different colors for different element types
  - Wireframe view to see internal structures
  - Final point cloud result
- **Configurable Point Density**: Control the number of points sampled for the output
- **Voxel Downsampling**: Ensures even distribution of points

## Prerequisites

The script requires the following dependencies:

```
ifcopenshell
open3d
numpy
```

## Installation

1. Clone the repository or download the script
2. Install the required dependencies:

```bash
pip install ifcopenshell open3d numpy
```

## Usage

### Basic Usage

```bash
python main.py path/to/your/file.ifc
```

This will process the IFC file with default settings and save the result as "pointcloud.ply".

### Command Line Arguments

```
usage: main.py [-h] [--output OUTPUT] [--points POINTS] [--processes PROCESSES]
               [--exclude EXCLUDE [EXCLUDE ...]] [--list-types] [--no-display]
               [--interactive-filter]
               ifc_path

Convert IFC file to pointcloud with filtering options

positional arguments:
  ifc_path              Path to the IFC file

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output pointcloud file path
  --points POINTS, -p POINTS
                        Number of points to sample
  --processes PROCESSES, -n PROCESSES
                        Number of parallel processes
  --exclude EXCLUDE [EXCLUDE ...], -e EXCLUDE [EXCLUDE ...]
                        List of element types to exclude (e.g. IfcDoor IfcWindow)
  --list-types, -l      List all element types in the IFC file and exit
  --no-display, -nd     Don't display visual results
  --interactive-filter, -i
                        Interactively select element types to exclude after listing
```

### Examples

**List all element types in an IFC file:**
```bash
python main.py path/to/file.ifc --list-types
```

**Generate a pointcloud excluding doors and windows:**
```bash
python main.py path/to/file.ifc --exclude IfcDoor IfcWindow
```

**Interactive filtering mode:**
```bash
python main.py path/to/file.ifc --interactive-filter
```

**Custom output file and higher point density:**
```bash
python main.py path/to/file.ifc --output building_cloud.ply --points 500000
```

**Process with specific number of CPU cores:**
```bash
python main.py path/to/file.ifc --processes 4
```

**Generate pointcloud without visualization:**
```bash
python main.py path/to/file.ifc --no-display
```

## Workflow

1. **Analysis Phase**: The script begins by analyzing the IFC file to identify all element types present
2. **Geometry Processing**: Each IFC element is processed to extract its 3D geometry
3. **Visualization 1**: The extracted model is displayed with different colors for each element type
4. **Visualization 2**: A wireframe view is shown to reveal internal structures
5. **Point Sampling**: Points are uniformly sampled from the model's surface
6. **Output Generation**: The final pointcloud is saved to the specified file
7. **Visualization 3**: The resulting pointcloud is displayed

## Programmatic Usage

You can also import and use the main functions in your own Python code:

```python
from main import ifc_to_pointcloud, list_element_types

# List all element types in an IFC file
element_types = list_element_types("path/to/model.ifc")

# Convert an IFC file to a pointcloud
pointcloud = ifc_to_pointcloud(
    ifc_path="path/to/model.ifc",
    output_path="result.ply",
    num_points=100000,
    show_result=True,
    num_processes=4,
    exclude_types=["IfcDoor", "IfcWindow"]
)
```

## Performance Considerations

- The script automatically determines the optimal number of processes based on your CPU
- For very large IFC files, consider using the `--exclude` option to filter out unnecessary elements
- Adjust the number of sampled points based on your needs and available memory
- Set `--no-display` for batch processing or when running on headless servers

## Troubleshooting

If you encounter issues:

1. Ensure all dependencies are correctly installed
2. Check if your IFC file is valid and contains 3D geometry
3. Try processing a subset of the model by excluding certain element types
4. If memory errors occur, reduce the number of processes or sample points

## License

[MIT License](LICENSE)