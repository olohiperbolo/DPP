import re


# typowe konfuzje OCR dla tablic
_CONFUSION_MAP = str.maketrans({
    "O": "0", "Q": "0", "D": "0",
    "I": "1", "L": "1",
    "Z": "2",
    "S": "5",
    "B": "8",
    "A": "4",
})

# czasem OCR zwraca małe litery / znaki specjalne
def _norm_plate_relaxed(s: str) -> str:
    if not s:
        return ""
    s = s.upper().strip()
    s = re.sub(r"[^A-Z0-9]", "", s)
    # mapuj litery-podobne na cyfry (tolerancyjnie)
    s = s.translate(_CONFUSION_MAP)
    return s


def _levenshtein(a: str, b: str) -> int:

    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)

    # DP po krótszym
    if len(a) < len(b):
        a, b = b, a

    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            ins = curr[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            curr.append(min(ins, dele, sub))
        prev = curr
    return prev[-1]


def calculate_accuracy(predictions, ground_truth, max_edit_distance: int = 1) -> float:

    if len(predictions) != len(ground_truth):
        raise ValueError("predictions i ground_truth muszą mieć tę samą długość.")

    total = len(ground_truth)
    if total == 0:
        return 0.0

    correct = 0
    for pred, gt in zip(predictions, ground_truth):
        p = _norm_plate_relaxed(pred)
        g = _norm_plate_relaxed(gt)

        if not p or not g:
            continue

        if p == g:
            correct += 1
        else:
            if _levenshtein(p, g) <= max_edit_distance:
                correct += 1

    return (correct / total) * 100.0


def calculate_final_grade(accuracy_percent: float, processing_time_sec: float) -> float:

    # Check minimum requirements
    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0

    accuracy_norm = (accuracy_percent - 60) / 40
    time_norm = (60 - processing_time_sec) / 50
    score = 0.7 * accuracy_norm + 0.3 * time_norm

    grade = 2.0 + 3.0 * score
    return round(grade * 2) / 2

