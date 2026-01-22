# src/evaluation.py
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
    """
    Klasyczna odległość Levenshteina (dynamic programming).
    Działa szybko dla krótkich stringów (5–8 znaków).
    """
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
    """
    Accuracy w %.
    Uznajemy trafienie, jeśli po normalizacji konfuzji:
    - pred == gt
    - albo Levenshtein(pred, gt) <= max_edit_distance (domyślnie 1)
    """
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


def calculate_final_grade(accuracy: float, processing_time: float) -> float:
    """
    Zostawiamy Twoją logikę oceniania (jeśli już była).
    Jeśli w Twoim projekcie masz inną tabelę ocen, podmień to na swoją.
    """
    # Minimalna, bezpieczna wersja (żeby projekt działał):
    # Jeśli masz w swoim pliku dokładną skalę z zaliczenia, wklej ją tu.
    if processing_time > 60:
        return 2.0

    # Przykładowe progi – dopasuj do wymagań z PDF / prowadzącego
    if accuracy >= 90:
        return 5.0
    if accuracy >= 75:
        return 4.5
    if accuracy >= 60:
        return 4.0
    if accuracy >= 45:
        return 3.5
    if accuracy >= 30:
        return 3.0
    if accuracy >= 15:
        return 2.5
    return 2.0
