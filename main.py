import re
import unicodedata

def is_palindrome(text: str) -> bool:
    cleaned = ''.join(ch.lower() for ch in text if ch.isalnum())
    return cleaned == cleaned[::-1]

def fibbonaci(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    elif n < 0:
        raise ValueError("Liczba powinna byc dodatnia")
    else:
        a, b = 0, 1
        for _ in range(2, n + 1):
            a, b = b, a + b
    return b

def count_vowels(text: str) -> int:
    vowels = 'aeiouyąęó'
    return sum(1 for ch in text.lower() if ch in vowels)

def calculate_discount(price: float, discount:float) -> float:
    if not (0 <= discount <= 1):
        raise ValueError("Zniżka powinna być w przedziale 0-1")
    return price * (1 - discount)

def flatten_list(nested_list):
    flat_list = []
    for item in nested_list:
        if isinstance(item, list):
            flat_list.extend(flatten_list(item))
        else:
            flat_list.append(item)
    return flat_list

def remove_znaki(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return ''.join(ch for ch in normalized if unicodedata.category(ch) != 'Mn')

def word_frequency(text: str) -> dict:
    clean_text = remove_znaki(text.lower())
    words = re.findall(r'\b\w+\b', clean_text)

    frequency = {}
    for word in words:
        frequency[word] = frequency.get(word, 0) + 1

    return frequency