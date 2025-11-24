import os
import cv2

# ---- CONFIG ----
IMAGE_DIR = "images"
LABEL_DIR = "labels"
OUTPUT_DIR = "crops"

os.makedirs(OUTPUT_DIR, exist_ok=True)

def yolo_to_xyxy(x_center, y_center, w, h, img_w, img_h):
    """
    Convert normalized YOLOv5 coordinates to pixel coordinates (xmin, ymin, xmax, ymax).
    """
    x_center *= img_w
    y_center *= img_h
    w *= img_w
    h *= img_h

    xmin = int(x_center - w / 2)
    ymin = int(y_center - h / 2)
    xmax = int(x_center + w / 2)
    ymax = int(y_center + h / 2)

    # Clip to image boundaries
    xmin = max(0, xmin)
    ymin = max(0, ymin)
    xmax = min(img_w - 1, xmax)
    ymax = min(img_h - 1, ymax)

    return xmin, ymin, xmax, ymax


for label_file in os.listdir(LABEL_DIR):
    if not label_file.endswith(".txt"):
        continue

    label_path = os.path.join(LABEL_DIR, label_file)

    # corresponding image (support JPG/PNG/TIF)
    base = os.path.splitext(label_file)[0]
    img_path = None
    for ext in [".jpg", ".jpeg", ".png", ".tif", ".tiff", ".bmp"]:
        candidate = os.path.join(IMAGE_DIR, base + ext)
        if os.path.exists(candidate):
            img_path = candidate
            break

    if img_path is None:
        print(f"WARNING: No image found for {label_file}")
        continue

    img = cv2.imread(img_path)
    if img is None:
        print(f"ERROR: Could not load image {img_path}")
        continue

    img_h, img_w = img.shape[:2]

    # read each label line
    with open(label_path, "r") as f:
        for idx, line in enumerate(f):
            parts = line.strip().split()
            if len(parts) != 5:
                continue

            cls_id = int(parts[0])
            x, y, w, h = map(float, parts[1:])

            xmin, ymin, xmax, ymax = yolo_to_xyxy(x, y, w, h, img_w, img_h)
            crop = img[ymin:ymax, xmin:xmax]

            # skip empty crops
            if crop.size == 0:
                continue

            # Make class subfolder
            class_dir = os.path.join(OUTPUT_DIR, f"class_{cls_id}")
            os.makedirs(class_dir, exist_ok=True)

            # save crop
            crop_filename = f"{base}_{idx}.png"
            cv2.imwrite(os.path.join(class_dir, crop_filename), crop)

print("Done! Crops saved under:", OUTPUT_DIR)