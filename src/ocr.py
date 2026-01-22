# src/ocr.py
import re
import cv2
import easyocr

# Reader tworzymy raz (to NAJWAŻNIEJSZE dla czasu)
# gpu=False -> stabilnie na CPU (na laptopach zwykle OK); jeśli masz CUDA i chcesz szybciej: gpu=True
_READER = easyocr.Reader(['en'], gpu=False)

PLATE_PATTERN = re.compile(r"[A-Z]{1,3}[A-Z0-9]{3,5}")  # typowe PL: 5–8 znaków, start literami


def _norm(s: str) -> str:
    if not s:
        return ""
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s


def _preprocess(plate_bgr):
    """
    Lekki preprocessing (bez masakrowania obrazu):
    - grayscale
    - upscale
    - delikatny contrast
    """
    gray = cv2.cvtColor(plate_bgr, cv2.COLOR_BGR2GRAY)

    # upscale (ważne)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)

    # delikatne wyostrzenie/kontrast
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.addWeighted(gray, 1.6, cv2.GaussianBlur(gray, (0, 0), 1.0), -0.6, 0)

    return gray


def _extract_best_plate(texts):
    """
    texts: lista stringów z EasyOCR (już po allowlist)
    wybieramy najlepszy fragment podobny do tablicy
    """
    best = ""
    for t in texts:
        s = _norm(t)
        if not s:
            continue

        matches = PLATE_PATTERN.findall(s)
        if matches:
            # preferuj długość bliżej 7
            matches.sort(key=lambda x: (abs(len(x) - 7), -len(x)))
            cand = matches[0]
        else:
            # fallback: weź pierwsze 8 znaków
            cand = s[:8]

        # wybierz "najlepszy" po długości (i sensowności)
        if len(cand) > len(best):
            best = cand

    return best


def recognize_plate(plate_img) -> str:
    """
    OCR tablicy EasyOCR.
    allowlist ogranicza znaki -> mniej śmieci.
    """
    img = _preprocess(plate_img)

    # detail=0 => dostajemy tylko teksty (szybciej)
    # paragraph=False => lepiej dla krótkich napisów
    texts = _READER.readtext(
        img,
        detail=0,
        paragraph=False,
        allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    )

    return _extract_best_plate(texts)
