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

def write_label_file(filename, yolo_boxes, target):
    txt_filename = os.path.splitext(filename)[0] + '.txt'
    with open(os.path.join(target, txt_filename), 'w') as txt_file:
        for box in yolo_boxes:
            txt_file.write(' '.join(map(str, box)) + '\n')

# create annotations directory if it doesn't exist
if not os.path.exists('labels'):
    os.makedirs('labels')

# create desired class labels directory if it doesn't exist
if not os.path.exists('desired_class_labels'):
    os.makedirs('desired_class_labels')

# create images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# create desired class images directory if it doesn't exist
if not os.path.exists('desired_class_images'):
    os.makedirs('desired_class_images')

class_names = []
desired_class = 'multiplication'

# iterate recursively through all files in current directory, check for .xml extension
for dirpath, dirnames, filenames in os.walk('export_job_19138314'):
    for filename in filenames:
        if filename.endswith('.xml'):
            # traverse each .xml file and check for <TextRegion> element
            tree = ET.parse(os.path.join(dirpath, filename))
            root = tree.getroot()
            yolo_boxes = []
            for region in root.findall('.//ns:TextRegion', namespace) + root.findall('.//ns:MathsRegion', namespace) + root.findall('.//ns:TableRegion', namespace):
                # check if custom attribute contains class name
                custom_attr = region.get('custom', '')
                # extract class name from custom attribute
                class_name = custom_attr.split('type:')[1].split(';')[0] if 'type:' in custom_attr else None
                if class_name is None:
                    continue  # skip if no class name found
                if class_name not in class_names:
                    class_names.append(class_name)
                # if contains <Coords> child element, make YOLO bounding box
                coords = region.find('ns:Coords', namespace)
                if coords is not None:
                   width, height = get_width_height(root)
                   box_coords = get_box_coords(coords)
                   yolo_boxes.append((class_names.index(class_name), *convert_box_to_YOLO(box_coords, width, height)))
                else:
                    print(f'File: {filename} - No Coords found in region')
                    continue

            # copy image and write label file if at least one box was found
            if yolo_boxes:  
                # copy corresponding image to images directory
                copy_image(dirpath, filename, 'images')
                write_label_file(filename, yolo_boxes, 'labels')
                # if one of the class indices in yolo_boxes matches desired class, copy to desired_class directories
                if desired_class in class_names and any(box[0] == class_names.index(desired_class) for box in yolo_boxes):
                    copy_image(dirpath, filename, 'desired_class_images')
                    write_label_file(filename, yolo_boxes, 'desired_class_labels')
                

# save class names and indices to classes.txt
with open('classes.txt', 'w') as class_file:
    for class_name in class_names:
        class_file.write(str(class_names.index(class_name)) + ': ' + class_name + '\n')