import os
import random
import shutil
from pathlib import Path

def create_yolo_splits(
    images_dir,
    labels_dir,
    output_dir,
    train_ratio=0.9,
    val_ratio=0.1,
    test_ratio=0.0,
    seed=42
):
    random.seed(seed)

    images_dir = Path(images_dir)
    labels_dir = Path(labels_dir)
    output_dir = Path(output_dir)

    # Make sure ratios add up to 1.0
    total = train_ratio + val_ratio + test_ratio
    train_ratio /= total
    val_ratio /= total
    test_ratio /= total

    # Get all images
    image_files = list(images_dir.glob("*.jpg"))
    image_files += list(images_dir.glob("*.png"))  # just in case

    random.shuffle(image_files)
    n = len(image_files)
    n_train = int(n * train_ratio)
    n_val = int(n * val_ratio)

    splits = {
        "train": image_files[:n_train],
        "val": image_files[n_train:n_train + n_val],
        "test": image_files[n_train + n_val:]
    }

    for split_name, files in splits.items():
        print(f"📁 Creating {split_name} set with {len(files)} images")

        for subfolder in ["images", "labels"]:
            (output_dir / subfolder / split_name).mkdir(parents=True, exist_ok=True)

        for img_path in files:
            label_path = labels_dir / (img_path.stem + ".txt")
            if not label_path.exists():
                print(f"⚠️ Missing label for {img_path.name}, skipping.")
                continue

            # Copy image + label
            shutil.copy(img_path, output_dir / "images" / split_name / img_path.name)
            shutil.copy(label_path, output_dir / "labels" / split_name / label_path.name)

    print("✅ Split completed successfully!")

if __name__ == "__main__":
    images_dir = "images"
    labels_dir = "labels"
    output_dir = "yolo_dataset"

    create_yolo_splits(images_dir, labels_dir, output_dir)
