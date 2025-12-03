import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from core.calculator import Calculator
from core.parser import Parser
from core.validator import ExpressionValidator

def test_valid_expressions():
    validator = ExpressionValidator()
    valid_cases = [
        "A", "1", "NOT A", "A AND B", "(A OR B) → C",
        "A ≡ B", "A ↓ B", "A | B", "NOT (A AND B)", "A XOR B"
    ]
    for expr in valid_cases:
        is_valid, m = validator.validate(expr)
        assert is_valid, f"'{expr}' должно быть валидным, но ошибка: {m}"


def test_invalid_expressions():
    validator = ExpressionValidator()
    invalid_cases = [
        ("", "пустое"),
        ("A B", "пробел вместо оператора"),
        ("AND A", "оператор в начале"),
        ("A AND", "оператор в конце"),
        ("()", "пустые скобки"),
        ("(A", "незакрытая скобка"),
        ("A & B", "недопустимый символ"),
        ("F", "недопустимая переменная")
    ]
    for expr, _ in invalid_cases:
        is_valid, _ = validator.validate(expr)
        assert not is_valid, f"'{expr}' должно быть НЕвалидным"


def test_parser():
    parser = Parser()
    assert parser.parsing("A AND B") == ["A", "B"]
    assert parser.parsing("NOT C") == ["C"]
    assert parser.parsing("(A → B) ≡ C") == ["A", "B", "C"]
    assert parser.parsing("1 OR 0") == []
    assert parser.parsing("A XOR A") == ["A"]


def test_calculator_constants():
    calc = Calculator()
    assert calc.calculate("1", {}) == 1
    assert calc.calculate("0", {}) == 0


def test_calculator_not():
    calc = Calculator()
    assert calc.calculate("NOT A", {"A": 1}) == 0
    assert calc.calculate("NOT 0", {}) == 1


def test_calculator_and_or():
    calc = Calculator()
    env = {"A": 1, "B": 0}
    assert calc.calculate("A AND B", env) == 0
    assert calc.calculate("A OR B", env) == 1


def test_calculator_implication():
    calc = Calculator()
    assert calc.calculate("A → B", {"A": 1, "B": 0}) == 0
    assert calc.calculate("A → B", {"A": 0, "B": 0}) == 1


def test_calculator_equivalence():
    calc = Calculator()
    assert calc.calculate("A ≡ B", {"A": 1, "B": 1}) == 1
    assert calc.calculate("A ≡ B", {"A": 1, "B": 0}) == 0


def test_calculator_nor_nand():
    calc = Calculator()
    assert calc.calculate("A ↓ B", {"A": 0, "B": 0}) == 1
    assert calc.calculate("A ↓ B", {"A": 1, "B": 0}) == 0
    assert calc.calculate("A | B", {"A": 1, "B": 1}) == 0
    assert calc.calculate("A | B", {"A": 1, "B": 0}) == 1
    assert calc.calculate("A | B", {"A": 0, "B": 0}) == 1


def test_calculator_complex():
    calc = Calculator()
    env = {"A": 1, "B": 0, "C": 1}
    result = calc.calculate("(A AND NOT B) → C", env)
    assert result == 1