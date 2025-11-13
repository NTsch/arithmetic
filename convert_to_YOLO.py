import os
import xml.etree.ElementTree as ET
import glob

namespace = {'ns': 'http://schema.primaresearch.org/PAGE/gts/pagecontent/2013-07-15'}

def get_width_height(root):
    # get <Page> element from root
    page = root.find('.//ns:Page', namespace)
    if page is not None:
        # extract width and height attributes
        width = int(page.get('imageWidth'))
        height = int(page.get('imageHeight'))
        return width, height
    else:
        print('No Page ancestor found')

def get_box_coords(coords):
    # extract points from <Coords> element
    points = coords.get('points')
    point_list = points.split()
    x_values = []
    y_values = []
    for point in point_list:
        x, y = map(int, point.split(','))
        x_values.append(x)
        y_values.append(y)
    # calculate bounding box coordinates
    x_min = min(x_values)
    x_max = max(x_values)
    y_min = min(y_values)
    y_max = max(y_values)
    return x_min, y_min, x_max, y_max

def convert_box_to_YOLO(box_coords, width, height):
    x_min, y_min, x_max, y_max = box_coords
    # calculate YOLO format values
    x_center = (x_min + x_max) / 2.0 / width
    y_center = (y_min + y_max) / 2.0 / height
    box_width = (x_max - x_min) / width
    box_height = (y_max - y_min) / height
    return x_center, y_center, box_width, box_height

def copy_image(dirpath, filename):
    # find image file with same base name in parent folder and copy to images directory
    img_base_name = os.path.splitext(filename)[0]
    parent_path = os.path.dirname(dirpath)
    glob_pattern = os.path.join(parent_path, img_base_name + '.*')
    img_files = glob.glob(glob_pattern)
    if img_files:
        img_file = img_files[0]
        dest_path = os.path.join('images', os.path.basename(img_file))
        with open(img_file, 'rb') as src_file:
            with open(dest_path, 'wb') as dest_file:
                dest_file.write(src_file.read())
    else:
        print(f'Image file for {filename} not found.')


# create annotations directory if it doesn't exist
if not os.path.exists('annotations'):
    os.makedirs('annotations')

# create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

class_name = 'multiplication'

# iterate recursively through all files in current directory, check for .xml extension
for dirpath, dirnames, filenames in os.walk('export_job_19138314'):
    for filename in filenames:
        if filename.endswith('.xml'):
            # traverse each .xml file and check for <TextRegion> element
            tree = ET.parse(os.path.join(dirpath, filename))
            root = tree.getroot()
            for region in root.findall('.//ns:TextRegion', namespace) + root.findall('.//ns:MathsRegion', namespace) + root.findall('.//ns:TableRegion', namespace):
                # check if custom attribute contains class name
                custom_attr = region.get('custom', '')
                if f'type:{class_name};' not in custom_attr:
                    continue
                yolo_boxes = []
                # if contains <Coords> child element, make YOLO bounding box
                coords = region.find('ns:Coords', namespace)
                if coords is not None:
                   width, height = get_width_height(root)
                   box_coords = get_box_coords(coords)
                   yolo_boxes.append((0, *convert_box_to_YOLO(box_coords, width, height)))
                   copy_image(dirpath, filename)
                    # copy corresponding image to images directory
                else:
                    print(f'File: {filename} - No Coords found in region')
                    continue

                # write YOLO bounding boxes to .txt file in labels directory
                txt_filename = os.path.splitext(filename)[0] + '.txt'
                with open(os.path.join('labels', txt_filename), 'w') as txt_file:
                    for box in yolo_boxes:
                        txt_file.write(' '.join(map(str, box)) + '\n')