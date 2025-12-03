import re

class Parser:
    # "вынимает переменные из выражения"
    def parsing(self, expr):
        tokens = re.findall(r'NOT|OR|AND|XOR|→|≡|↓|\||[()]|[A-E]|[01]', expr.upper())
        return sorted(set(token for token in tokens if token in 'ABCDE'))