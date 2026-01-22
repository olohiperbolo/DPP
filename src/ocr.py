# src/ocr.py
import re
import cv2
import easyocr

# GPU ON
_READER = easyocr.Reader(['en'], gpu=True)

PLATE_PATTERN = re.compile(r"[A-Z]{1,3}[A-Z0-9]{3,5}")


def _norm(s: str) -> str:
    if not s:
        return ""
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s


def _preprocess(plate_bgr):
    gray = cv2.cvtColor(plate_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    return gray


def _extract_best_plate(texts):
    best = ""
    for t in texts:
        s = _norm(t)
        if not s:
            continue

        matches = PLATE_PATTERN.findall(s)
        if matches:
            matches.sort(key=lambda x: (abs(len(x) - 7), -len(x)))
            cand = matches[0]
        else:
            cand = s[:8]

        if len(cand) > len(best):
            best = cand
    return best


def recognize_plate(plate_img) -> str:
    img = _preprocess(plate_img)

    texts = _READER.readtext(
        img,
        detail=0,
        paragraph=False,
        allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    return _extract_best_plate(texts)
