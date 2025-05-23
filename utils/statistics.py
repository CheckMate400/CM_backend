import math

def calculate_grade_distribution(grades: list[int]) -> dict[str, float]:
    total = len(grades)
    if total == 0:
        return {'A': 0.0, 'B': 0.0, 'C': 0.0, 'D': 0.0, 'F': 0.0}

    distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
    for grade in grades:
        if grade >= 90:
            distribution['A'] += 1
        elif grade >= 80:
            distribution['B'] += 1
        elif grade >= 70:
            distribution['C'] += 1
        elif grade >= 60:
            distribution['D'] += 1
        else:
            distribution['F'] += 1

    for k in distribution:
        distribution[k] = round(distribution[k] / total * 100, 2)

    return distribution


def calculate_average(grades: list[int]) -> float:
    if not grades:
        return 0.0
    return round(sum(grades) / len(grades), 2)


def calculate_std_dev(grades: list[int]) -> float:
    n = len(grades)
    if n == 0:
        return 0.0
    mean = sum(grades) / n
    variance = sum((g - mean) ** 2 for g in grades) / n
    return round(math.sqrt(variance), 2)


def calculate_median(grades: list[int]) -> float:
    n = len(grades)
    if n == 0:
        return 0.0
    grades_sorted = sorted(grades)
    mid = n // 2
    if n % 2 == 0:
        return round((grades_sorted[mid - 1] + grades_sorted[mid]) / 2, 2)
    else:
        return grades_sorted[mid]
