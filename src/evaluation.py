import time

def calculate_accuracy(predictions, ground_truth):
    correct = sum(p == g for p, g in zip(predictions, ground_truth))
    return correct / len(ground_truth) * 100

def calculate_final_grade(accuracy_percent, processing_time_sec):
    if accuracy_percent < 60 or processing_time_sec > 60:
        return 2.0

    accuracy_norm = (accuracy_percent - 60) / 40
    time_norm = (60 - processing_time_sec) / 50

    score = 0.7 * accuracy_norm + 0.3 * time_norm
    grade = 2.0 + 3.0 * score
    return round(grade * 2) / 2
