import re

class ExpressionValidator:
    # определяет все "верные" символы и их комбинации
    def __init__(self):
        self.allowed_tokens = {
            'A', 'B', 'C', 'D', 'E',
            '0', '1',
            '(', ')',
            '↓', '|',
            'NOT', 'OR', 'AND', 'XOR', '→', '≡'
        }
        self.binary_ops = ['OR', 'AND', 'XOR', '→', '≡', '↓', '|']
        self.op_names = {
            'OR': 'OR', 'AND': 'AND', 'XOR': 'XOR',
            '→': 'Импликация (→)', '≡': 'Эквиваленция (≡)',
            '↓': 'Стрелка Пирса (↓)', '|': 'Штрих Шеффера (|)'
        }

    # запускает проверки
    def validate(self, expr):
        if not expr or not expr.strip():
            return False, "Выражение пустое."

        expr = expr.upper()
        tokens = re.findall(r'NOT|OR|AND|XOR|→|≡|↓|\||[()]|[A-Z]|[01]', expr.upper())
        
        if len(tokens) == 0:
            return False, "Нет корректных элементов в выражении."

        ok, msg = self._check_characters(tokens)
        if not ok:
            return False, msg

        ok, msg = self._check_brackets(tokens)
        if not ok:
            return False, msg

        ok, msg = self._check_sequence(tokens)
        if not ok:
            return False, msg

        ok, msg = self._check_edges(tokens)
        if not ok:
            return False, msg

        return True, ""

    # проверяет, что в выражении только разрешенные символы
    def _check_characters(self, tokens):
        for token in tokens:
            if token not in self.allowed_tokens:
                if len(token) == 1 and token.isalpha() and token not in 'ABCDE':
                    return False, f"Недопустимая переменная '{token}'. Допустимы: A, B, C, D, E."
                return False, f"Недопустимый символ или слово: '{token}'."
        return True, ""

    # проверяет, что скобки сбалансированны
    def _check_brackets(self, tokens):
        stack = []
        for i, token in enumerate(tokens):
            if token == '(':
                stack.append(i)
            elif token == ')':
                if not stack:
                    return False, "Закрывающая скобка ')' без открывающей."
                stack.pop()
                if i > 0 and tokens[i-1] == '(':
                    return False, "Пустые скобки: '()'."
        if stack:
            return False, "Есть незакрытые открывающие скобки '('."
        return True, ""

    # проверяет порядок токенов
    def _check_sequence(self, tokens):
        for i in range(len(tokens) - 1):
            curr, next_t = tokens[i], tokens[i + 1]

            if curr in 'ABCDE01)' and next_t in 'ABCDE01(':
                return False, f"Пропущен оператор между '{curr}' и '{next_t}'."
            if curr in 'ABCDE01' and next_t == 'NOT':
                return False, "Оператор 'NOT' должен стоять перед операндом, а не после переменной."

            if curr in self.binary_ops and next_t in self.binary_ops + [')']:
                op_name = self.op_names.get(curr, curr)
                return False, f"Оператор '{op_name}' не может стоять перед '{next_t}'."

            if curr == 'NOT' and next_t in self.binary_ops + [')']:
                return False, f"Оператор 'NOT' должен применяться к переменной, константе или выражению в скобках, а не к '{next_t}'."

            if curr in self.binary_ops:
                if i == 0 or i == len(tokens) - 1:
                    op_name = self.op_names.get(curr, curr)
                    return False, f"Оператор '{op_name}' не может быть в начале или конце выражения."
                left_ok = tokens[i - 1] in 'ABCDE01)'
                right_ok = tokens[i + 1] in 'ABCDE01(' or tokens[i + 1] == 'NOT'
                if not (left_ok and right_ok):
                    return False, f"Некорректное окружение оператора '{curr}'. Ожидалось: <операнд> {curr} <операнд>."

        return True, ""

    # проверяет начало и конец выражения
    def _check_edges(self, tokens):
        if tokens[0] in self.binary_ops + [')']:
            if tokens[0] in self.binary_ops:
                op_name = self.op_names.get(tokens[0], tokens[0])
                return False, f"Выражение не может начинаться с оператора '{op_name}'."
            else:
                return False, "Выражение не может начинаться с закрывающей скобки ')'."
        if tokens[-1] in self.binary_ops + ['NOT', '(']:
            if tokens[-1] in self.binary_ops:
                op_name = self.op_names.get(tokens[-1], tokens[-1])
                return False, f"Выражение не может заканчиваться оператором '{op_name}'."
            elif tokens[-1] == 'NOT':
                return False, "Выражение не может заканчиваться 'NOT'."
            else:
                return False, "Выражение не может заканчиваться открывающей скобкой '('."
        return True, ""