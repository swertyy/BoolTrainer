import re

class Calculator:
    # получает выражение и значения
    def calculate(self, expr: str, env: dict):
        ts = re.findall(r'NOT|OR|AND|XOR|→|≡|↓|\||[()]|[A-E]|[01]', expr.upper())
        return self.eval(ts, env)
    
    # рассчитывает result
    def eval(self, ts, env):
        output = []
        stack = []
        precedence = {
            '(': 0,
            'OR': 1, '→': 1,
            'AND': 2,
            'XOR': 3, '≡': 3,
            '↓': 4, '|': 4,
            'NOT': 5
        }
        right_assoc = {'NOT'}

        for t in ts:
            if t in '01':
                output.append(int(t))
            elif t in 'ABCDE':
                output.append(env[t])
            elif t == '(':
                stack.append(t)
            elif t == ')':
                while stack and stack[-1] != '(':
                    output.append(stack.pop())
                if stack:
                    stack.pop()
                else:
                    raise ValueError("Несбалансированные скобки")
            elif t in precedence:
                prec = precedence[t]
                while (
                    stack and
                    stack[-1] != '(' and
                    stack[-1] in precedence and
                    (precedence[stack[-1]] > prec or
                     (precedence[stack[-1]] == prec and t not in right_assoc))
                ):
                    output.append(stack.pop())
                stack.append(t)
            else:
                raise ValueError(f"Неизвестный токен: {t}")

        while stack:
            if stack[-1] in '()':
                raise ValueError("Несбалансированные скобки")
            output.append(stack.pop())

        stack = []
        for t in output:
            if isinstance(t, int):
                stack.append(t)
            elif t == 'NOT':
                a = stack.pop()
                stack.append(1 - a)
            elif t == 'AND':
                b, a = stack.pop(), stack.pop()
                stack.append(a & b)
            elif t == 'OR':
                b, a = stack.pop(), stack.pop()
                stack.append(a | b)
            elif t == 'XOR':
                b, a = stack.pop(), stack.pop()
                stack.append(a ^ b)
            elif t == '→':
                b, a = stack.pop(), stack.pop()
                stack.append(int((not a) or b))
            elif t == '≡':
                b, a = stack.pop(), stack.pop()
                stack.append(int(a == b))
            elif t == '↓':
                b, a = stack.pop(), stack.pop()
                stack.append(int(not (a or b)))
            elif t == '|':
                b, a = stack.pop(), stack.pop()
                stack.append(int(not (a and b)))
            else:
                raise ValueError(f"Неизвестная операция в постфиксе: {t}")

        if len(stack) != 1:
            raise ValueError("Ошибка вычисления: неверное выражение")
        return stack[0]