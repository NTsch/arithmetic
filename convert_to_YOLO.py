import os
import xml.etree.ElementTree as ET
import glob
import argparse

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

def copy_image(dirpath, filename, target):
    # find image file with same base name in parent folder and copy to images directory
    img_base_name = os.path.splitext(filename)[0]
    parent_path = os.path.dirname(dirpath)
    glob_pattern = os.path.join(parent_path, img_base_name + '.*')
    img_file = glob.glob(glob_pattern)[0]
    if img_file:
        dest_path = os.path.join(target, os.path.basename(img_file))
        with open(img_file, 'rb') as src_file:
            with open(dest_path, 'wb') as dest_file:
                dest_file.write(src_file.read())
    else:
        print(f'Image file for {filename} not found.')
        return None

def write_label_file(filename, yolo_boxes, target):
    txt_filename = os.path.splitext(filename)[0] + '.txt'
    with open(os.path.join(target, txt_filename), 'w') as txt_file:
        for box in yolo_boxes:
            txt_file.write(' '.join(map(str, box)) + '\n')

def create_output(yolo_boxes, dirpath, filename):
    copy_image(dirpath, filename, 'images')
    write_label_file(filename, yolo_boxes, 'labels')

# create annotations directory if it doesn't exist
if not os.path.exists('labels'):
    os.makedirs('labels')

# create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# set desired_class mode or binary mode per argument parsing
parser = argparse.ArgumentParser(description='Convert XML annotations to YOLO format.')
parser.add_argument('--mode', choices=['desired_class', 'binary'], default='desired_class', help='Choose annotation mode: desired_class or binary')
args = parser.parse_args()

desired_class_mode = (args.mode == 'desired_class')

class_names = []
desired_classes = ['multiplication', 'multiplication_table', 'starting_variable', 'number_line']
input_dir = 'export_job_19138314'

# iterate recursively through all files in current directory, check for .xml extension
for dirpath, dirnames, filenames in os.walk(input_dir):
    for filename in filenames:
        if filename.endswith('.xml'):
            # traverse each .xml file and check for <TextRegion> element
            tree = ET.parse(os.path.join(dirpath, filename))
            root = tree.getroot()
            yolo_boxes = []
            # get all regions, i.e. elements with Coords child
            regions = [elem for elem in root.findall('.//*') if elem.find('ns:Coords', namespace) is not None]
            # check if any of the desired classes are present
            desired_class_present = any(
                any('type:' + desired_class + ';' in region.get('custom', '') for desired_class in desired_classes)
                for region in regions
            )
            
            # get full image width and height if possible, else continue to next file
            dimensions = get_width_height(root)
            if dimensions is None:
                continue
            width, height = dimensions
            
            if desired_class_mode and desired_class_present:
                # process coords for each region
                for region in regions:
                    custom_attr = region.get('custom', '')
                    if 'type:' not in custom_attr:
                        continue
                    
                    class_name = custom_attr.split('type:')[1].split(';')[0]
                    if class_name not in class_names:
                        class_names.append(class_name)
                    
                    coords = region.find('ns:Coords', namespace)
                    if coords is not None:
                        box_coords = get_box_coords(coords)
                        yolo_boxes.append((class_names.index(class_name), *convert_box_to_YOLO(box_coords, width, height)))
                        #yolo_boxes.append(('1' if class_name == 'paragraph' else '0', *convert_box_to_YOLO(box_coords, width, height)))

                # copy image and write label file if at least one box was found
                create_output(yolo_boxes, dirpath, filename) if yolo_boxes else None

                # add class names from yolo_boxes to desired_class_names list
                for box in yolo_boxes:
                    class_name = class_names[box[0]]
                    if class_name not in class_names:
                        class_names.append(class_name)
            elif desired_class_mode and not desired_class_present:
                continue
            else:
                # process coords for each region
                for region in regions:
                    custom_attr = region.get('custom', '')
                    if 'type:' not in custom_attr:
                        continue
                    
                    class_name = custom_attr.split('type:')[1].split(';')[0]

                    coords = region.find('ns:Coords', namespace)  
                    if coords is not None:
                        box_coords = get_box_coords(coords)
                        yolo_boxes.append(('1' if class_name == 'paragraph' else '0', *convert_box_to_YOLO(box_coords, width, height)))

                # copy image and write label file if at least one box was found
                create_output(yolo_boxes, dirpath, filename) if yolo_boxes else None
                    
# save class names and indices to classes.txt
with open('classes.txt', 'w') as class_file:
    for class_name in class_names:
        class_file.write('"' + class_name + '"\n')
