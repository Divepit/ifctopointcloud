import ifcopenshell
import ifcopenshell.geom
import open3d as o3d
import numpy as np
import time
import concurrent.futures
import os
import multiprocessing

def process_batch(batch_data):
    """Process a batch of IFC products in a separate process."""
    batch_id, product_ids, ifc_path, exclude_types = batch_data
    
    try:
        ifc_file = ifcopenshell.open(ifc_path)
        settings = ifcopenshell.geom.settings()
        settings.set(settings.USE_WORLD_COORDS, True)
        
        # Create lists to store meshes and their element types
        mesh_data = []
        
        for product_id in product_ids:
            try:
                product = ifc_file.by_id(product_id)
                
                # Skip products without representation
                if not product.Representation:
                    continue
                
                # Get element type for filtering
                element_type = product.is_a()
                
                # Skip if this element type should be excluded
                if element_type in exclude_types:
                    continue
                
                shape = ifcopenshell.geom.create_shape(settings, product)
                verts = np.array(shape.geometry.verts).reshape(-1, 3)
                faces = np.array(shape.geometry.faces).reshape(-1, 3)
                
                if len(verts) > 0 and len(faces) > 0:
                    # Store mesh data and element type
                    mesh_data.append((verts, faces, element_type))
            except Exception as e:
                continue
        
        return batch_id, mesh_data
    
    except Exception as e:
        return batch_id, []

def ifc_to_pointcloud(ifc_path, output_path="pointcloud.pcd", mesh_output_path="mesh.ply", num_points=100000, 
                     show_result=True, num_processes=None, exclude_types=None):
    """
    Extract an evenly distributed pointcloud from an IFC file with parallel processing.
    
    Parameters:
    -----------
    ifc_path : str
        Path to the IFC file to process
    output_path : str
        Path where the output pointcloud will be saved (default: "pointcloud.ply")
    num_points : int
        Number of points to sample for the pointcloud (default: 100000)
    show_result : bool
        Whether to display the visual results (default: True)
    num_processes : int or None
        Number of parallel processes to use (default: CPU count - 1)
    exclude_types : list or None
        List of IFC element types to exclude from processing (default: None)
        Example: ["IfcDoor", "IfcWindow"] to exclude all doors and windows
    """
    # Initialize exclude_types to empty list if None
    if exclude_types is None:
        exclude_types = []
    
    print(f"Loading IFC file: {ifc_path}")
    
    # First analyze and list all element types in the file
    print("\n========== IFC ELEMENT TYPES ANALYSIS ==========")
    ifc_file = ifcopenshell.open(ifc_path)
    
    # Dictionary to count element types
    element_count = {}
    
    # Count all products with geometry
    for product in ifc_file.by_type("IfcProduct"):
        if product.Representation:
            element_type = product.is_a()
            if element_type not in element_count:
                element_count[element_type] = 0
            element_count[element_type] += 1
    
    # Print results in a table format
    print(f"\nElement types in {os.path.basename(ifc_path)}:")
    print("-" * 50)
    print(f"{'Element Type':<30} | {'Count':<10}")
    print("-" * 50)
    
    for element_type, count in sorted(element_count.items()):
        print(f"{element_type:<30} | {count:<10}")
    
    print("-" * 50)
    print(f"Total element types: {len(element_count)}")
    print(f"Total elements with geometry: {sum(element_count.values())}")
    print("=" * 45)
    print()
    
    # Now continue with the filtering information
    if exclude_types:
        print(f"Excluding element types: {', '.join(exclude_types)}")
    
    start_time = time.time()
    
    # Determine number of processes
    if num_processes is None:
        num_processes = max(1, multiprocessing.cpu_count() - 1)
    
    print(f"Using {num_processes} parallel processes")
    
    # Load IFC file in main process
    ifc_file = ifcopenshell.open(ifc_path)
    
    # Get products with geometry
    products = []
    for product in ifc_file.by_type("IfcProduct"):
        if product.Representation:
            products.append(product.id())
    
    total_products = len(products)
    print(f"Found {total_products} IFC elements with geometry representations")
    
    # Create batches for parallel processing
    batch_size = max(1, len(products) // (num_processes * 2))
    batches = []
    
    for i in range(0, len(products), batch_size):
        batch_products = products[i:i+batch_size]
        batches.append((len(batches), batch_products, ifc_path, exclude_types))
    
    print(f"Divided work into {len(batches)} batches")
    
    # Process batches in parallel
    print(f"Processing geometry in parallel...")
    processed_elements = 0
    excluded_elements = 0
    
    # Dictionary to store meshes by element type
    meshes_by_type = {}
    
    with concurrent.futures.ProcessPoolExecutor(max_workers=num_processes) as executor:
        futures = {executor.submit(process_batch, batch): batch[0] for batch in batches}
        
        for future in concurrent.futures.as_completed(futures):
            try:
                batch_id, mesh_data = future.result()
                
                # Process the mesh data
                for verts, faces, element_type in mesh_data:
                    # Create mesh for this element
                    element_mesh = o3d.geometry.TriangleMesh()
                    element_mesh.vertices = o3d.utility.Vector3dVector(verts)
                    element_mesh.triangles = o3d.utility.Vector3iVector(faces)
                    
                    # Add to dictionary by type
                    if element_type not in meshes_by_type:
                        meshes_by_type[element_type] = []
                    
                    meshes_by_type[element_type].append(element_mesh)
                    processed_elements += 1
                
                # Report progress
                percent_complete = (batch_id + 1) / len(batches) * 100
                elapsed = time.time() - start_time
                print(f"Batch {batch_id+1}/{len(batches)} complete ({percent_complete:.1f}%) - "
                      f"{processed_elements}/{total_products} elements processed - {elapsed:.1f} seconds elapsed")
                
            except Exception as e:
                print(f"Error processing batch {futures[future]}: {str(e)}")
    
    # Calculate how many elements were excluded
    excluded_elements = total_products - processed_elements
    
    print(f"Geometry extraction complete - {processed_elements}/{total_products} elements processed successfully")
    if exclude_types:
        print(f"Excluded approximately {excluded_elements} elements of types: {', '.join(exclude_types)}")
    
    # Check if we have any geometry
    if not meshes_by_type:
        print("Error: No valid geometry found in the IFC file")
        
        # Debug information
        print("\nDebug information:")
        print(f"IFC file exists: {os.path.exists(ifc_path)}")
        print(f"IFC file size: {os.path.getsize(ifc_path) / (1024*1024):.2f} MB")
        print(f"Total products with representation: {len(products)}")
        
        # Try a single element for testing
        if len(products) > 0:
            print("\nAttempting to process one element in main process for debugging:")
            try:
                test_product = ifc_file.by_id(products[0])
                settings = ifcopenshell.geom.settings()
                settings.set(settings.USE_WORLD_COORDS, True)
                shape = ifcopenshell.geom.create_shape(settings, test_product)
                print(f"Test element has {len(shape.geometry.verts)/3} vertices and {len(shape.geometry.faces)/3} faces")
            except Exception as e:
                print(f"Error processing test element: {str(e)}")
        
        return None
    
    # Prepare for visualization and pointcloud generation
    print(f"Found {len(meshes_by_type)} different element types")
    
    # Create a list of colored meshes for visualization
    colored_meshes = []
    combined_mesh = o3d.geometry.TriangleMesh()
    
    # Color palette for different element types (using distinct colors)
    colors = [
        [1, 0, 0],      # Red
        [0, 1, 0],      # Green
        [0, 0, 1],      # Blue
        [1, 1, 0],      # Yellow
        [1, 0, 1],      # Magenta
        [0, 1, 1],      # Cyan
        [0.5, 0, 0],    # Dark red
        [0, 0.5, 0],    # Dark green
        [0, 0, 0.5],    # Dark blue
        [0.5, 0.5, 0],  # Olive
        [0.5, 0, 0.5],  # Purple
        [0, 0.5, 0.5],  # Teal
        [1, 0.5, 0],    # Orange
        [0.5, 1, 0],    # Light green
        [0, 0.5, 1],    # Light blue
    ]
    
    # Print out all element types found in the model
    print("\nElement types present in the model:")
    for element_type in sorted(meshes_by_type.keys()):
        print(f"  - {element_type}: {len(meshes_by_type[element_type])} elements")
    # Color and combine meshes by type
    print("\nPreparing colored visualization...")
    combined_mesh = o3d.geometry.TriangleMesh()  # Initialize combined mesh

    for i, (element_type, meshes) in enumerate(meshes_by_type.items()):
        color_index = i % len(colors)
        type_mesh = o3d.geometry.TriangleMesh()
        
        # Combine all meshes of this type
        for mesh in meshes:
            type_mesh += mesh
        
        # Compute normals and color it
        type_mesh.compute_vertex_normals()
        type_mesh.paint_uniform_color(colors[color_index])
        
        # Add to visualization list
        colored_meshes.append(type_mesh)
        
        # Add to combined mesh for pointcloud generation
        combined_mesh += type_mesh
        
        print(f"  - {element_type}: {len(meshes)} elements (Color: {colors[color_index]})")

    # Create a coordinate frame for reference
    coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(size=1.0)

    # STEP 1: Visualize the colored solid mesh model
    print("\nSTEP 1: Displaying the extracted mesh model with colors by element type.")
    print("Colors represent different IFC element types as listed above.")
    print("Close the window when finished inspecting to continue to wireframe view.")

    # Write the combined mesh to file (not the list)
    o3d.io.write_triangle_mesh(mesh_output_path, combined_mesh)

    # Add all meshes and the coordinate frame to the visualization
    visualization_objects = colored_meshes + [coordinate_frame]
    o3d.visualization.draw_geometries(visualization_objects)
    
    # STEP 2: Visualize the wireframe view
    print("\nSTEP 2: Displaying wireframe view of the model.")
    print("This view helps to see the internal structure of the model.")
    print("Close the window when finished inspecting to continue to pointcloud generation.")
    
    # Create a visualization options object to force wireframe mode
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    
    # Add all objects to the visualizer
    for mesh in colored_meshes:
        vis.add_geometry(mesh)
    vis.add_geometry(coordinate_frame)
    
    # Get render options and set wireframe mode
    opt = vis.get_render_option()
    opt.mesh_show_wireframe = True
    opt.mesh_show_back_face = True
    
    # Reset view to fit all geometry
    vis.reset_view_point(True)
    
    # Run the visualizer
    vis.run()
    vis.destroy_window()
    
    print("Mesh inspection complete. Proceeding with pointcloud generation...")
    
    # Sample points uniformly
    print(f"Sampling {num_points} points uniformly...")
    pointcloud = combined_mesh.sample_points_uniformly(num_points)
    # pointcloud = pointcloud.voxel_down_sample(voxel_size=0.01)
    
    # Save pointcloud
    print(f"Saving pointcloud to {output_path}...")
    o3d.io.write_point_cloud(output_path, pointcloud)
    
    total_time = time.time() - start_time
    print(f"Complete! Pointcloud with {len(pointcloud.points)} points saved in {total_time:.2f} seconds")
    
    # Visualize the pointcloud result
    if show_result:
        print("STEP 3: Visualizing final pointcloud. Close the window to exit.")
        # Create a coordinate frame for reference
        o3d.visualization.draw_geometries([pointcloud, coordinate_frame])
    
    return pointcloud

def list_element_types(ifc_path):
    """
    List all element types present in an IFC file without processing the geometry.
    Useful for determining which element types to filter.
    
    Parameters:
    -----------
    ifc_path : str
        Path to the IFC file to analyze
        
    Returns:
    --------
    dict
        Dictionary of element types and their counts
    """
    print(f"Analyzing IFC file: {ifc_path}")
    
    try:
        # Load IFC file
        ifc_file = ifcopenshell.open(ifc_path)
        
        # Dictionary to count element types
        element_count = {}
        
        # Count all products with geometry
        for product in ifc_file.by_type("IfcProduct"):
            if product.Representation:
                element_type = product.is_a()
                if element_type not in element_count:
                    element_count[element_type] = 0
                element_count[element_type] += 1
        
        # Print results
        print(f"\nElement types in {os.path.basename(ifc_path)}:")
        print("-" * 50)
        print(f"{'Element Type':<30} | {'Count':<10}")
        print("-" * 50)
        
        for element_type, count in sorted(element_count.items()):
            print(f"{element_type:<30} | {count:<10}")
        
        print("-" * 50)
        print(f"Total element types: {len(element_count)}")
        print(f"Total elements with geometry: {sum(element_count.values())}")
        
        return element_count
        
    except Exception as e:
        print(f"Error analyzing IFC file: {str(e)}")
        return {}

if __name__ == "__main__":
    import sys
    import argparse
    
    # Set up argument parser for better CLI usage
    parser = argparse.ArgumentParser(description="Convert IFC file to pointcloud with filtering options")
    parser.add_argument("ifc_path", help="Path to the IFC file")
    parser.add_argument("--output", "-o", default="pointcloud.ply", help="Output pointcloud file path")
    parser.add_argument("--mesh_output", "-m", default="pointcloud.ply", help="Output pointcloud file path")
    parser.add_argument("--points", "-p", type=int, default=100000, help="Number of points to sample")
    parser.add_argument("--processes", "-n", type=int, default=None, help="Number of parallel processes")
    parser.add_argument("--exclude", "-e", nargs='+', default=[], help="List of element types to exclude (e.g. IfcDoor IfcWindow)")
    parser.add_argument("--list-types", "-l", action="store_true", help="List all element types in the IFC file and exit")
    parser.add_argument("--no-display", "-nd", action="store_true", help="Don't display visual results")
    parser.add_argument("--interactive-filter", "-i", action="store_true", 
                       help="Interactively select element types to exclude after listing")
    
    # Parse arguments
    args = parser.parse_args()
    
    # If list-types flag is set, only list element types and exit
    if args.list_types:
        list_element_types(args.ifc_path)
    elif args.interactive_filter:
        # Interactive mode: first list types, then ask which ones to exclude
        print("Interactive filtering mode:")
        element_types = list(list_element_types(args.ifc_path).keys())
        
        # Display numbered list of element types
        print("\nAvailable element types for filtering:")
        for i, element_type in enumerate(sorted(element_types), 1):
            print(f"{i}. {element_type}")
        
        # Ask user which types to exclude
        print("\nEnter the numbers of element types to EXCLUDE (comma-separated, or 'none'):")
        user_input = input("> ").strip().lower()
        
        exclude_types = []
        if user_input != "none" and user_input != "":
            try:
                selected_indices = [int(idx.strip()) - 1 for idx in user_input.split(",")]
                for idx in selected_indices:
                    if 0 <= idx < len(element_types):
                        exclude_types.append(sorted(element_types)[idx])
                
                print(f"Excluding: {', '.join(exclude_types)}")
            except ValueError:
                print("Invalid input. Proceeding without exclusions.")
        
        # Process the file with interactively selected filters
        ifc_to_pointcloud(
            args.ifc_path, 
            args.output, 
            args.mesh_output, 
            args.points, 
            not args.no_display, 
            args.processes,
            exclude_types
        )
    else:
        # Normal processing with command-line specified exclude types
        ifc_to_pointcloud(
            args.ifc_path, 
            args.output, 
            args.mesh_output, 
            args.points, 
            not args.no_display, 
            args.processes,
            args.exclude
        )