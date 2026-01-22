import re
import cv2
import easyocr

_READER = easyocr.Reader(["en"], gpu=True)


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
            out.add(s[i : i + L])
    return list(out) if out else []


def _hard_filter(s: str) -> bool:
    if not s:
        return False
    if not (5 <= len(s) <= 8):
        return False
    if s[0].isdigit():
        return False
    digits = sum(ch.isdigit() for ch in s)
    if digits < 2:
        return False
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

    for i in range(min(3, n)):
        score += 3 if s[i].isalpha() else -2

    for i in range(max(3, n - 3), n):
        score += 2 if s[i].isdigit() else -1

    if any(ch.isalpha() for ch in s) and any(ch.isdigit() for ch in s):
        score += 4

    return score


def _preprocess_gray(plate_bgr):
    gray = cv2.cvtColor(plate_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
    return gray


def recognize_plate(plate_img) -> str:
    gray = _preprocess_gray(plate_img)

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

    return _norm(best)
