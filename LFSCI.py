import os
import laspy
import numpy as np
import csv
from tqdm import tqdm


def calculate_normalized_point_density(points_before, points_after, LFSCI_layers, LFSCI_min_height):
    """
    Calculate normalized point density curve considering unified layering of two point clouds
    """
    all_points = np.vstack((points_before, points_after))
    all_points = all_points[all_points[:, 2] >= LFSCI_min_height]

    if len(all_points) == 0:
        raise ValueError("No points remain after applying LFSCI_min_height filter.")

    min_z = np.min(all_points[:, 2])
    max_z = np.max(all_points[:, 2])
    layer_height = (max_z - min_z) / LFSCI_layers

    points_per_layer_before = np.zeros(LFSCI_layers)
    points_per_layer_after = np.zeros(LFSCI_layers)

    points_before = points_before[points_before[:, 2] >= LFSCI_min_height]
    points_after = points_after[points_after[:, 2] >= LFSCI_min_height]

    for i in range(LFSCI_layers):
        layer_min_z = min_z + i * layer_height
        layer_max_z = min_z + (i + 1) * layer_height

        points_per_layer_before[i] = np.sum((points_before[:, 2] >= layer_min_z) & (points_before[:, 2] < layer_max_z))
        points_per_layer_after[i] = np.sum((points_after[:, 2] >= layer_min_z) & (points_after[:, 2] < layer_max_z))

    if np.ptp(points_per_layer_before) > 0:
        normalized_points_before = (points_per_layer_before - np.min(points_per_layer_before)) / np.ptp(points_per_layer_before)
    else:
        normalized_points_before = points_per_layer_before

    if np.ptp(points_per_layer_after) > 0:
        normalized_points_after = (points_per_layer_after - np.min(points_per_layer_after)) / np.ptp(points_per_layer_after)
    else:
        normalized_points_after = points_per_layer_after

    return normalized_points_before, normalized_points_after


def calculate_crown_initiation_layer(normalized_points_per_layer):
    """
    Calculate crown initiation layer based on growth rate of point density curve
    """
    growth_rates = np.gradient(normalized_points_per_layer)
    max_growth_rate = np.max(growth_rates)
    threshold = 0.2 * max_growth_rate
    for i, rate in enumerate(growth_rates):
        if rate >= threshold:
            return max(i, 30)
    return 40


def calculate_area_between_curves_with_direction(x, curve1, curve2, crown_initiation_layer=None):
    """
    Calculate area between two curves, distinguishing areas below and above crown initiation layer
    """
    areas = []  # Areas of small polygons in each layer
    lower_areas = []  # Areas below crown initiation layer
    upper_areas = []  # Areas above crown initiation layer
    lower_area_total = 0  # Total area below crown initiation layer
    upper_area_total = 0  # Total area above crown initiation layer

    for i in range(len(x) - 1):
        width = x[i + 1] - x[i]
        height_avg = (curve1[i] + curve2[i]) / 2

        if crown_initiation_layer is not None and x[i] <= crown_initiation_layer:
            direction = np.sign(curve2[i] - curve1[i])
            lower_area = width * height_avg * direction
            lower_areas.append(lower_area)
            lower_area_total += lower_area
            areas.append(lower_area)
        else:
            direction = np.sign(curve1[i] - curve2[i])
            upper_area = width * height_avg * direction
            upper_areas.append(upper_area)
            upper_area_total += upper_area
            areas.append(upper_area)

    total_area = lower_area_total + upper_area_total
    return total_area, lower_area_total, upper_area_total, areas


# Set input/output paths
input_T1_folder = "./point_clouds/T1"
input_T2_folder = "./point_clouds/T2"
output_csv_file = "./results/results.csv"

# Ensure output directory exists
output_dir = os.path.dirname(output_csv_file)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

file_list = os.listdir(input_T1_folder)

# Process each file
for filename in tqdm(file_list, desc="Processing"):
    if filename.endswith(".las"):
        las_file_path = os.path.join(input_T1_folder, filename)
        inFile = laspy.read(las_file_path)
        points = np.vstack([inFile.x, inFile.y, inFile.z]).transpose()

        matching_filename = os.path.join(input_T2_folder, filename)
        file_name = filename.split('.')[0]

        if os.path.exists(matching_filename):
            matching_inFile = laspy.read(matching_filename)
            matching_points = np.vstack([matching_inFile.x, matching_inFile.y, matching_inFile.z]).transpose()

            norm_before, norm_after = calculate_normalized_point_density(
                points, matching_points, LFSCI_layers=100, LFSCI_min_height=0
            )

            crown_initiation_layer = calculate_crown_initiation_layer(norm_before)
            layer_heights = np.linspace(0, 100, len(norm_before))

            total_area, lower_area, upper_area, areas = calculate_area_between_curves_with_direction(
                layer_heights, norm_before, norm_after, crown_initiation_layer
            )

            # Write to CSV file
            file_exists = os.path.exists(output_csv_file)
            with open(output_csv_file, mode='a', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['ID', 'LFSCI', 'LFSCI_C', 'LFSCI_U'])
                if not file_exists:
                    writer.writeheader()
                writer.writerow({'ID': file_name, 'LFSCI': total_area, 'LFSCI_C': upper_area, 'LFSCI_U': lower_area})