import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import main, pytest


from main import is_palindrome

def test_is_palindrome():
    assert is_palindrome("kajak")
    assert is_palindrome("Kobyła ma mały bok")
    assert not is_palindrome("python")
    assert is_palindrome("")
    assert is_palindrome("A")

def test_fibbonaci():
    assert main.fibbonaci(0) == 0
    assert main.fibbonaci(1) == 1
    assert main.fibbonaci(5) == 5
    assert main.fibbonaci(10) == 55
    with pytest.raises(ValueError):
        main.fibbonaci(-1)