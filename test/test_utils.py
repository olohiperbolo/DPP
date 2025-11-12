import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import test.test_utils as test_main, pytest


from test.test_utils import is_palindrome

def test_is_palindrome():
    assert is_palindrome("kajak")
    assert is_palindrome("Kobyła ma mały bok")
    assert not is_palindrome("python")
    assert is_palindrome("")
    assert is_palindrome("A")

def test_fibbonaci():
    assert test_main.fibbonaci(0) == 0
    assert test_main.fibbonaci(1) == 1
    assert test_main.fibbonaci(5) == 5
    assert test_main.fibbonaci(10) == 55
    with pytest.raises(ValueError):
        test_main.fibbonaci(-1)


def test_count_vowels():
    assert test_main.count_vowels("Python") == 2
    assert test_main.count_vowels("AEIOUY") == 6
    assert test_main.count_vowels("bcd") == 0
    assert test_main.count_vowels("") == 0
    assert test_main.count_vowels("Próba żółwia") == 5

def test_calculate_discount():
    assert test_main.calculate_discount(100, 0.2) == 80
    assert test_main.calculate_discount(50, 0) == 50
    assert test_main.calculate_discount(200, 1) == 0
    with pytest.raises(ValueError):
        test_main.calculate_discount(100, -0.1)
    with pytest.raises(ValueError):
        test_main.calculate_discount(100, 1.5)

def test_flatten_list():
    assert test_main.flatten_list([1,2,3]) == [1,2,3]
    assert test_main.flatten_list([1,[2,3],[4,[5]]]) == [1,2,3,4,5]
    assert test_main.flatten_list([]) == []
    assert test_main.flatten_list([[[1]]]) == [1]
    assert test_main.flatten_list([1,[2,[3,[4]]]]) == [1,2,3,4]

def test_word_frequency():
    assert test_main.word_frequency("To be or not to be") == {'to': 2, 'be': 2, 'or': 1, 'not': 1}
    assert test_main.word_frequency("") == {}
    assert test_main.word_frequency("Hello, hello!") == {'hello': 2}
    assert test_main.word_frequency(" Python Python python") == {'python': 3}
    assert test_main.word_frequency("Ala ma kota, a kot ma Ale.") == {'ala': 1, 'ma': 2, 'kota': 1, 'a': 1, 'kot': 1, 'ale': 1}


def test_is_prime():
    assert test_main.is_prime(2)
    assert test_main.is_prime(3)
    assert not test_main.is_prime(4)
    assert not test_main.is_prime(0)
    assert test_main.is_prime(5)
    assert test_main.is_prime(97)