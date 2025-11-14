import cv2
import matplotlib.pyplot as plt
from pathlib import Path

def show_yolo_annotations(image_path, label_path, class_names=None):
    img = cv2.imread(str(image_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h, w, _ = img.shape

    with open(label_path, "r") as f:
        for line in f:
            cls, x_center, y_center, width, height = map(float, line.strip().split())
            cls = int(cls)
            x1 = int((x_center - width / 2) * w)
            y1 = int((y_center - height / 2) * h)
            x2 = int((x_center + width / 2) * w)
            y2 = int((y_center + height / 2) * h)

            color = (255, 0, 0)
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            if class_names:
                cv2.putText(img, class_names[cls], (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    plt.imshow(img)
    plt.axis("off")
    plt.show()

# Example usage
image_path = Path("test/Heidelberg, Universitaetsbibliothek, Pal. germ. 618-0014.jpg")
label_path = Path("test/Heidelberg, Universitaetsbibliothek, Pal. germ. 618-0014.txt")

class_names = ["multiplication"]  # Add more class names if needed

show_yolo_annotations(image_path, label_path, class_names)
