# src/ocr.py
import re
import cv2
import pytesseract


PLATE_RE = re.compile(r"[A-Z]{1,3}[A-Z0-9]{3,5}")  # typowe PL: 4–8 znaków, start literami


def _normalize(s: str) -> str:
    if not s:
        return ""
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s


def _preprocess_for_ocr(plate_bgr):
    """
    Preprocessing pod Tesseract:
    - skala w górę (OCR lubi większe litery),
    - odszum,
    - wzmocnienie kontrastu,
    - threshold,
    - lekkie domknięcie morfologiczne.
    """
    gray = cv2.cvtColor(plate_bgr, cv2.COLOR_BGR2GRAY)

    # upscale 2x (często mocno poprawia)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # odszum
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

    # kontrast (CLAHE)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)

    # threshold adaptacyjny
    thr = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        35, 5
    )

    # morfologia - lekkie domknięcie (łączy przerwy w znakach)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    thr = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel, iterations=1)

    return thr


def _extract_best_plate_candidate(raw_text: str) -> str:
    """
    Postprocessing:
    - normalizacja,
    - próba znalezienia w tekście fragmentu pasującego do wzorca tablicy.
    Dzięki temu z 'BST6666U' wyciągnie 'ST6666U', a z 'IASL83861' -> 'SL83861'.
    """
    s = _normalize(raw_text)

    if not s:
        return ""

    # Najpierw spróbuj znaleźć pasujące fragmenty w oryginalnym surowym tekście po normalizacji
    matches = PLATE_RE.findall(s)
    if matches:
        # wybierz "najlepszy": najczęściej sensowna jest długość 6–7,
        # ale bierzemy najdłuższy (stabilne dla PL datasetów)
        matches.sort(key=len, reverse=True)
        return matches[0]

    # Jeśli regex nic nie znalazł, spróbuj prostego "obcięcia śmieci":
    # Weź końcówkę 8 znaków (max typowy rozmiar w PL datasetach)
    if len(s) > 8:
        s = s[-8:]

    return s


def recognize_plate(plate_img):
    img = _preprocess_for_ocr(plate_img)

    # psm 7 = pojedyncza linia tekstu
    config = (
        "--oem 1 --psm 7 "
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
        "-c classify_bln_numeric_mode=1"
    )

    raw = pytesseract.image_to_string(img, config=config)
    return _extract_best_plate_candidate(raw)
