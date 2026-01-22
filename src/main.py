import os, glob
import xml.etree.ElementTree as ET
import cv2
import pandas as pd
import time

from detector import detect_plate
from ocr import recognize_plate
from evaluation import calculate_accuracy, calculate_final_grade


def load_voc_annotations(ann_dir):
    rows = []
    for xml_path in glob.glob(os.path.join(ann_dir, "*.xml")):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        filename = root.findtext("filename")

        plate_text = None

        for obj in root.findall("object"):
            name = obj.findtext("name")

            if name and any(ch.isdigit() for ch in name):
                plate_text = name.strip().replace(" ", "")
                break

        if plate_text is None:
            plate_text = ""

        rows.append({"filename": filename, "plate": plate_text})

    return pd.DataFrame(rows)


ANN_DIR = "data/annotations"
IMG_DIR = "data/images"

df = load_voc_annotations(ANN_DIR)

df = df.sample(min(100, len(df)), random_state=42).reset_index(drop=True)
