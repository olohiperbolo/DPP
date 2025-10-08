import re

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