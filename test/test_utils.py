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


def test_count_vowels():
    assert main.count_vowels("Python") == 2
    assert main.count_vowels("AEIOUY") == 6
    assert main.count_vowels("bcd") == 0
    assert main.count_vowels("") == 0
    assert main.count_vowels("Próba żółwia") == 5

def test_calculate_discount():
    assert main.calculate_discount(100, 0.2) == 80
    assert main.calculate_discount(50, 0) == 50
    assert main.calculate_discount(200, 1) == 0
    with pytest.raises(ValueError):
        main.calculate_discount(100, -0.1)
    with pytest.raises(ValueError):
        main.calculate_discount(100, 1.5)

def test_flatten_list():
    assert main.flatten_list([1,2,3]) == [1,2,3]
    assert main.flatten_list([1,[2,3],[4,[5]]]) == [1,2,3,4,5]
    assert main.flatten_list([]) == []
    assert main.flatten_list([[[1]]]) == [1]
    assert main.flatten_list([1,[2,[3,[4]]]]) == [1,2,3,4]

def test_word_frequency():
    assert main.word_frequency("To be or not to be") == {'to': 2, 'be': 2, 'or': 1, 'not': 1}
    assert main.word_frequency("") == {}
    assert main.word_frequency("Hello, hello!") == {'hello': 2}
    assert main.word_frequency(" Python Python python") == {'python': 3}
    assert main.word_frequency("Ala ma kota, a kot ma Ale.") == {'ala': 1, 'ma': 2, 'kota': 1, 'a': 1, 'kot': 1, 'ale': 1}


def test_is_prime():
    assert main.is_prime(2)
    assert main.is_prime(3)
    assert not main.is_prime(4)
    assert not main.is_prime(0)
    assert main.is_prime(5)
    assert main.is_prime(97)