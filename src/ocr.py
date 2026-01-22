# src/ocr.py
import re
import cv2
import easyocr

_READER = easyocr.Reader(["en"], gpu=True)

ALNUM_RE = re.compile(r"[A-Z0-9]+")


def _norm(s: str) -> str:
    if not s:
        return ""
    s = s.upper()
    s = re.sub(r"[^A-Z0-9]", "", s)
    return s


def _max_run_letters(s: str) -> int:
    best = cur = 0
    for ch in s:
        if ch.isalpha():
            cur += 1
            best = max(best, cur)
        else:
            cur = 0
    return best


def _windows_5_8(s: str):
    s = _norm(s)
    out = set()
    for L in range(5, 9):
        for i in range(0, max(0, len(s) - L + 1)):
            out.add(s[i:i+L])
    return list(out) if out else []


def _hard_filter(s: str) -> bool:
    if not s:
        return False
    if not (5 <= len(s) <= 8):
        return False
    # w datasetach PL zwykle start literą
    if s[0].isdigit():
        return False
    # minimum cyfr (żeby wycinać „same litery”)
    digits = sum(ch.isdigit() for ch in s)
    if digits < 2:
        return False
    # wycina halucynacje typu BMWXXXX
    if _max_run_letters(s) >= 4:
        return False
    return True


def _positional_score(s: str) -> int:
    s = _norm(s)
    if not s:
        return -10_000
    n = len(s)
    score = 0
    score -= abs(n - 7) * 2

    # preferuj litery na początku
    for i in range(min(3, n)):
        score += 3 if s[i].isalpha() else -2

    # preferuj cyfry na końcu
    for i in range(max(3, n - 3), n):
        score += 2 if s[i].isdigit() else -1

    # bonus za mix liter i cyfr
    if any(ch.isalpha() for ch in s) and any(ch.isdigit() for ch in s):
        score += 4

    return score


def _preprocess_gray(plate_bgr):
    gray = cv2.cvtColor(plate_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    return gray


def _inner_crop(gray):
    """
    Spróbuj wyciąć wnętrze tablicy (bez ramki/śrub):
    - binarizacja
    - znajdź największy jasny obszar
    - przytnij z marginesem
    Jeśli się nie da, zwróć None.
    """
    # Otsu
    _, thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # zakładamy: znaki ciemne, tło jasne -> bierz jasne jako maskę
    # domknij, żeby tło było spójne
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 5))
    mask = cv2.morphologyEx(thr, cv2.MORPH_CLOSE, kernel, iterations=1)

    # znajdź kontury jasnych obszarów
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    h, w = gray.shape[:2]
    best = None
    best_area = 0

    for c in contours:
        x, y, cw, ch = cv2.boundingRect(c)
        area = cw * ch
        # odrzuć zbyt małe i zbyt wąskie
        if area < 0.15 * w * h:
            continue
        if cw < 0.5 * w:
            continue
        if ch < 0.3 * h:
            continue
        if area > best_area:
            best_area = area
            best = (x, y, cw, ch)

    if best is None:
        return None

    x, y, cw, ch = best
    pad = 6
    x1 = max(0, x + pad)
    y1 = max(0, y + pad)
    x2 = min(w, x + cw - pad)
    y2 = min(h, y + ch - pad)
    if x2 <= x1 or y2 <= y1:
        return None

    return gray[y1:y2, x1:x2]


def _ocr_one(gray):
    texts = _READER.readtext(
        gray,
        detail=0,
        paragraph=False,
        allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789",
        decoder="greedy",
    )

    best = ""
    best_score = -10_000_000

    for t in texts:
        t = _norm(t)
        if not t:
            continue

        candidates = _windows_5_8(t) if len(t) > 8 else [t]
        for c in candidates:
            c = _norm(c)
            if not _hard_filter(c):
                continue
            sc = _positional_score(c)
            if sc > best_score:
                best_score = sc
                best = c

    return best, best_score


def recognize_plate(plate_img) -> str:
    gray = _preprocess_gray(plate_img)

    # OCR na normalnym gray
    best1, sc1 = _ocr_one(gray)

    # OCR na „wnętrzu tablicy”
    inner = _inner_crop(gray)
    if inner is not None:
        best2, sc2 = _ocr_one(inner)
        if sc2 > sc1:
            return _norm(best2)

    return _norm(best1)
