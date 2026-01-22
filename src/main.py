import os
import re
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import cv2

from ocr import recognize_plate
from evaluation import calculate_accuracy, calculate_final_grade


def _norm_plate(s: str) -> str:
    if not s:
        return ""
    s = s.strip().upper()
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s


def parse_cvat_xml(xml_path: Path):

    tree = ET.parse(str(xml_path))
    root = tree.getroot()

    records = []
    for img in root.findall("image"):
        filename = (img.attrib.get("name", "") or "").strip()
        if not filename:
            continue

        for box in img.findall("box"):
            xtl = float(box.attrib["xtl"])
            ytl = float(box.attrib["ytl"])
            xbr = float(box.attrib["xbr"])
            ybr = float(box.attrib["ybr"])

            plate_text = ""
            for attr in box.findall("attribute"):
                if (attr.attrib.get("name", "") or "").strip().lower() == "plate number":
                    plate_text = attr.text or ""
                    break

            rotation = float(box.attrib.get("rotation", "0") or 0)

            records.append({
                "filename": filename,
                "plate_gt": _norm_plate(plate_text),
                "bbox": (xtl, ytl, xbr, ybr),
                "rotation": rotation
            })

    return records


def crop_bbox(img, bbox, pad=18):

    #Wycinanie tablicy po bbox + margines (pad).

    h, w = img.shape[:2]
    xtl, ytl, xbr, ybr = bbox

    x1 = max(0, int(round(xtl)) - pad)
    y1 = max(0, int(round(ytl)) - pad)
    x2 = min(w, int(round(xbr)) + pad)
    y2 = min(h, int(round(ybr)) + pad)

    if x2 <= x1 or y2 <= y1:
        return None
    return img[y1:y2, x1:x2]


def rotate_image(img, angle_deg):
    """
    Obrót wycinka tablicy o angle_deg (stopnie).
    """
    if abs(angle_deg) < 0.01:
        return img
    h, w = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, angle_deg, 1.0)
    return cv2.warpAffine(
        img, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )


def main():
    # ROOT projektu: folder nadrzędny względem src/
    ROOT = Path(__file__).resolve().parents[1]
    IMG_DIR = ROOT / "data" / "photos"
    ANN_PATH = ROOT / "data" / "annotations.xml"

    print("ROOT:", ROOT)
    print("IMG_DIR:", IMG_DIR, "| exists:", IMG_DIR.exists())
    print("ANN_PATH:", ANN_PATH, "| exists:", ANN_PATH.exists())

    if not IMG_DIR.exists():
        raise FileNotFoundError(f"Brak folderu ze zdjęciami: {IMG_DIR}")
    if not ANN_PATH.exists():
        raise FileNotFoundError(f"Brak pliku adnotacji: {ANN_PATH}")

    records = parse_cvat_xml(ANN_PATH)
    if not records:
        raise ValueError("Nie znaleziono rekordów <image>/<box> w annotations.xml.")

    # filtruj tylko rekordy, dla których zdjęcie istnieje
    filtered = []
    for r in records:
        p = IMG_DIR / r["filename"]
        if p.exists():
            r["img_path"] = p
            filtered.append(r)

    print(f"Rekordów w XML: {len(records)} | Rekordów z istniejącymi zdjęciami: {len(filtered)}")

    if not filtered:
        example_names = [r["filename"] for r in records[:10]]
        raise ValueError(
            "Żaden plik z XML nie pasuje do plików w data/photos.\n"
            f"Przykładowe nazwy z XML: {example_names}\n"
            f"Sprawdź czy zdjęcia są w: {IMG_DIR}"
        )

    # deterministycznie wybierz 100 rekordów (stabilnie na prezentacji)
    test = sorted(filtered, key=lambda r: r["filename"])[: min(100, len(filtered))]

    predictions = []
    ground_truth = []

    start = time.time()

    for r in test:
        img = cv2.imread(str(r["img_path"]))
        gt = r["plate_gt"]

        if img is None:
            predictions.append("")
            ground_truth.append(gt)
            continue

        plate_crop = crop_bbox(img, r["bbox"], pad=18)
        if plate_crop is None:
            predictions.append("")
            ground_truth.append(gt)
            continue

        # CVAT rotation: prostujemy w przeciwną stronę
        plate_crop = rotate_image(plate_crop, -r.get("rotation", 0.0))

        pred = recognize_plate(plate_crop)
        predictions.append(_norm_plate(pred))
        ground_truth.append(gt)

    end = time.time()

    accuracy = calculate_accuracy(predictions, ground_truth)
    processing_time = end - start
    grade = calculate_final_grade(accuracy, processing_time)

    print("\n=== WYNIKI ===")
    print(f"Liczba testowanych zdjęć: {len(test)}")
    print(f"Accuracy: {accuracy:.2f}%")
    print(f"Czas dla {len(test)} zdjęć: {processing_time:.2f}s")
    print(f"Final grade: {grade}")

    print("\nPróbka (GT -> PRED):")
    for i in range(min(10, len(test))):
        print(f"{ground_truth[i]:>10} -> {predictions[i]}")


if __name__ == "__main__":
    main()
