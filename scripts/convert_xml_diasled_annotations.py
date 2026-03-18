import xml.etree.ElementTree as ET
import argparse
import sys
from pathlib import Path

def _get_image_dimensions(image_file):
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow is required to read image size. Install it with: pip install Pillow")
        return None

    try:
        with Image.open(image_file) as image:
            width, height = image.size
            return width, height
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_file}")
        return None
    except Exception as e:
        print(f"Error: Could not read image dimensions from {image_file}: {e}")
        return None


def _parse_label_map(label_map_arg):
    if not label_map_arg:
        return {}

    mapping = {}
    for chunk in label_map_arg.split(','):
        pair = chunk.strip()
        if not pair:
            continue
        if '=' not in pair:
            raise ValueError(
                f"Invalid --label-map entry '{pair}'. Expected format: source=target"
            )
        source_label, target_label = pair.split('=', 1)
        source_label = source_label.strip()
        target_label = target_label.strip()
        if not source_label or not target_label:
            raise ValueError(
                f"Invalid --label-map entry '{pair}'. Source and target must be non-empty"
            )
        mapping[source_label] = target_label

    return mapping


def _resolve_output_label(input_label, target_label=None, label_map=None):
    if target_label:
        return target_label
    if label_map and input_label in label_map:
        return label_map[input_label]
    return input_label


def _transform_coordinates(x_value, y_value, image_width, image_height, flip_y=False):
    transformed_x = x_value
    transformed_y = y_value
    if flip_y:
        transformed_y = image_height - y_value
    return transformed_x, transformed_y


def convert_diasled_to_cvat(
    input_file,
    output_file,
    image_file,
    image_name=None,
    target_label=None,
    label_map=None,
    flip_y=False,
):
    """
    Converts Diasled XML point data to CVAT for points XML format.
    """
    dimensions = _get_image_dimensions(image_file)
    if dimensions is None:
        return 1

    image_width, image_height = dimensions
    resolved_image_name = image_name if image_name else Path(image_file).name

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_data = f.read()
        
        # The input XML has some quirks like "" for quotes, let's clean it.
        # A more robust solution might be needed if the format varies.
        cleaned_xml_data = xml_data.replace('""', '"')
        
        # The provided snippet is a fragment, let's wrap it to make it valid XML
        if not cleaned_xml_data.strip().startswith('<'):
            raise ValueError("Input file does not appear to be valid XML.")

        # Check if it's a full document or a fragment
        try:
            root = ET.fromstring(cleaned_xml_data)
        except ET.ParseError:
            # If parsing fails, it might be a fragment. Let's try wrapping it.
            try:
                # Assuming the fragment is the content of a root element
                # Let's create a dummy root to wrap the content
                valid_xml_string = f"<root>{cleaned_xml_data}</root>"
                root = ET.fromstring(valid_xml_string)
            except ET.ParseError:
                print("Error: Could not parse the XML. It might be malformed.")
                return 1


    except FileNotFoundError:
        print(f"Error: Input file not found at {input_file}")
        return 1
    except Exception as e:
        print(f"An error occurred: {e}")
        return 1

    # CVAT XML structure
    annotations = ET.Element('annotations')
    version = ET.SubElement(annotations, 'version')
    version.text = '1.1'
    
    meta = ET.SubElement(annotations, 'meta')
    task = ET.SubElement(meta, 'task')
    ET.SubElement(task, 'id').text = '1'
    ET.SubElement(task, 'name').text = 'diasled_annotation'
    ET.SubElement(task, 'size').text = str(len(root.findall('.//PointV1')))
    ET.SubElement(task, 'mode').text = 'annotation'
    ET.SubElement(task, 'start_frame').text = '0'
    ET.SubElement(task, 'stop_frame').text = '0'
    ET.SubElement(task, 'frame_filter').text = ''
    
    source = ET.SubElement(task, 'source')
    source.text = resolved_image_name

    labels = ET.SubElement(task, 'labels')
    mapped_labels = set()
    for source_point in root.findall('.//PointV1'):
        source_name = source_point.get('Name')
        if source_name:
            mapped_labels.add(_resolve_output_label(source_name, target_label, label_map))

    for label_name in sorted(list(mapped_labels)):
        label_elem = ET.SubElement(labels, 'label')
        ET.SubElement(label_elem, 'name').text = label_name
        ET.SubElement(label_elem, 'color').text = '#000000' # Default color
        ET.SubElement(label_elem, 'type').text = 'points'


    image = ET.SubElement(annotations, 'image', {
        'id': '0',
        'name': resolved_image_name,
        'width': str(image_width),
        'height': str(image_height)
    })

    points_elements = root.findall('.//PointV1')
    if not points_elements:
        # If the wrapper was used, the path will be different
        points_elements = root.findall('./Points/PointV1')

    out_of_bounds_points = []
    used_output_labels = set()

    for point in points_elements:
        point_id = point.get('id')
        x = point.get('x')
        y = point.get('y')
        name = point.get('Name')

        if x is not None and y is not None and name is not None:
            output_label = _resolve_output_label(name, target_label, label_map)
            try:
                x_value = float(x)
                y_value = float(y)
            except ValueError:
                print(f"Error: Non-numeric coordinates for point id={point_id}, label={name}: x={x}, y={y}")
                return 1

            transformed_x, transformed_y = _transform_coordinates(
                x_value,
                y_value,
                image_width,
                image_height,
                flip_y=flip_y,
            )

            if not (0 <= transformed_x < image_width and 0 <= transformed_y < image_height):
                out_of_bounds_points.append({
                    'id': point_id,
                    'label': name,
                    'x': transformed_x,
                    'y': transformed_y,
                })
                continue

            cvat_point = ET.SubElement(image, 'points', {
                'label': output_label,
                'occluded': '0',
                'source': 'manual',
                'points': f'{transformed_x:g},{transformed_y:g}',
                'z_order': '0',
                'group_id': '0'
            })
            used_output_labels.add(output_label)

    if out_of_bounds_points:
        print(
            f"Error: Found {len(out_of_bounds_points)} point(s) outside the image bounds "
            f"for image '{resolved_image_name}' ({image_width}x{image_height})."
        )
        for point in out_of_bounds_points[:10]:
            print(
                f"  - id={point['id']}, label={point['label']}, "
                f"x={point['x']}, y={point['y']}"
            )
        if len(out_of_bounds_points) > 10:
            print(f"  ... and {len(out_of_bounds_points) - 10} more")
        return 1

    tree = ET.ElementTree(annotations)
    ET.indent(tree, space="\t", level=0)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)
    print(
        f"Successfully converted annotations to {output_file} "
        f"using image '{resolved_image_name}' ({image_width}x{image_height})"
    )
    print(f"Coordinate transform: flip_y={flip_y}")
    print(f"Labels in output: {', '.join(sorted(used_output_labels))}")
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert Diasled XML to CVAT annotations.')
    parser.add_argument('input_file', help='Path to the input XML file.')
    parser.add_argument('output_file', help='Path for the output CVAT XML file.')
    parser.add_argument('image_file', help='Path to the image file used for annotation.')
    parser.add_argument(
        '--image-name',
        help='Optional image name to store in CVAT XML. Defaults to the image file basename.'
    )
    parser.add_argument(
        '--target-label',
        help='Force all points to use one CVAT label name (must exist in the destination task).'
    )
    parser.add_argument(
        '--label-map',
        help='Map source labels to CVAT labels, e.g.: "L=landmark,L_=landmark,G=grid"'
    )
    parser.add_argument(
        '--flip-y',
        action='store_true',
        help='Flip Y axis (use when source coordinates are from bottom-left origin).'
    )

    args = parser.parse_args()

    try:
        parsed_label_map = _parse_label_map(args.label_map)
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    exit_code = convert_diasled_to_cvat(
        args.input_file,
        args.output_file,
        args.image_file,
        args.image_name,
        args.target_label,
        parsed_label_map,
        args.flip_y,
    )
    sys.exit(exit_code)
