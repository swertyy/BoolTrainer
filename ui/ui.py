import os
import json
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import tkinter.font as tkfont
from core.parser import Parser
from core.calculator import Calculator
from core.validator import ExpressionValidator

BG_COLOR = "#E3EED4"
BUTTON_COLOR = "#6B9071"
BUTTON_HOVER = "#375534"
BUTTON_PRESS = "#0F2A1D"
BUTTON_TEXT_COLOR = "white"
LABEL_COLOR = "#0F2A1D" 
ENTRY_BG = "white"
ENTRY_FG = "black"
FONT_NAME = "Arial"

# находит путь к JSON-файлам
def resource_path(relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, relative_path)
theory_dir = resource_path("theory_cards")

p = Parser()

class ErrorDialog:
    # создает окно с сообщением об ошибке
    def __init__(self, parent, error):
        win = tk.Toplevel(parent, bg=BG_COLOR)
        win.title("Ошибка")
        win.geometry("400x150")
        win.configure(bg=BG_COLOR)
        ttk.Label(win, text="Ошибка:", font=(FONT_NAME, 12, 'bold'), background=BG_COLOR).pack(pady=10)
        ttk.Label(win, text=error, wraplength=350, background=BG_COLOR).pack(pady=5)
        ttk.Button(win, text="OK", command=win.destroy).pack(pady=10)
        win.grab_set()

class ConstructorWindow:
    # инициализация окна Конструктор
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel()
        self.win.title("Конструктор функций")
        self.win.state('zoomed')
        self.win.configure(bg=BG_COLOR)
        self.win.protocol("WM_DELETE_WINDOW", self.go_back)
        self.t = None
        self.setup_ui()

    # создает интерфейс
    def setup_ui(self):

        s = ttk.Style()
        s.theme_use('clam')
        s.configure('B.TButton', padding=(10, 8), font=(FONT_NAME, 10), background=BUTTON_COLOR, foreground=BUTTON_TEXT_COLOR)
        s.map('B.TButton', background=[('active', BUTTON_HOVER), ('pressed', BUTTON_PRESS)])
        s.configure('W.TButton', padding=(20, 10), font=(FONT_NAME, 11), background=BUTTON_COLOR, foreground=BUTTON_TEXT_COLOR)
        s.map('W.TButton', background=[('active', BUTTON_HOVER), ('pressed', BUTTON_PRESS)])
        s.configure('Treeview', font=(FONT_NAME, 12), background=ENTRY_BG, fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
        s.configure('Treeview.Heading', font=(FONT_NAME, 11, 'bold'))

        main = ttk.Frame(self.win, style='Main.TFrame')
        main.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)

        s.configure('Main.TFrame', background=BG_COLOR)
        s.configure('Card.TLabelframe', background=BG_COLOR, font=(FONT_NAME, 12, 'bold'), labeloutside=False)
        s.configure('Card.TLabelframe.Label', background=BG_COLOR, font=(FONT_NAME, 12, 'bold'))

        left = ttk.Frame(main, width=800, style='Card.TFrame')
        left.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 20))
        left.configure(style='Card.TFrame')

        self.right = ttk.Frame(main, style='Card.TFrame')
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.right.configure(style='Card.TFrame')

        ttk.Label(left, text="Конструктор функций", font=(FONT_NAME, 20, 'bold'), background=BG_COLOR, foreground=LABEL_COLOR).pack(pady=20)

        inp = tk.LabelFrame(left, text="Введите выражение", font=(FONT_NAME, 12, 'bold'), padx=15, pady=15, bg=BG_COLOR, fg=LABEL_COLOR)
        inp.pack(fill=tk.X, pady=10)
        self.e = ttk.Entry(inp, font=(FONT_NAME, 14), width=40)
        self.e.pack(fill=tk.X, pady=5)
        self.e.bind('<Control-a>', lambda e: self.e.select_range(0, 'end'))
        self.e.bind('<Control-A>', lambda e: self.e.select_range(0, 'end'))

        ttk.Label(left, text="Операции", font=(FONT_NAME, 12, 'bold'), background=BG_COLOR, foreground=LABEL_COLOR).pack(anchor='w', pady=(20, 5))
        ops1 = ttk.Frame(left, style='Card.TFrame')
        ops1.pack(fill=tk.X, pady=5)
        for op in ['NOT', 'OR', 'AND', 'XOR', '→', '≡']:
            ttk.Button(ops1, text=op, style='B.TButton', command=lambda o=op: self.ins(f' {o} ')).pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        ops2 = ttk.Frame(left, style='Card.TFrame')
        ops2.pack(fill=tk.X, pady=5)
        for op in ['↓', '|']:
            ttk.Button(ops2, text=op, style='B.TButton', command=lambda o=op: self.ins(f' {o} ')).pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)
        for op in ['1', '0', '(', ')']:
            ttk.Button(ops2, text=op, style='B.TButton', command=lambda o=op: self.ins(f'{o}')).pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        ttk.Label(left, text="Переменные", font=(FONT_NAME, 12, 'bold'), background=BG_COLOR, foreground=LABEL_COLOR).pack(anchor='w', pady=(20, 5))
        vars_frame = ttk.Frame(left, style='Card.TFrame')
        vars_frame.pack(fill=tk.X, pady=5)
        for v in 'ABCDE':
            ttk.Button(vars_frame, text=v, style='B.TButton', command=lambda x=v: self.ins(x)).pack(side=tk.LEFT, padx=2, pady=2, fill=tk.X, expand=True)

        act = ttk.Frame(left, style='Card.TFrame')
        act.pack(fill=tk.X, pady=30)
        ttk.Button(act, text="Рассчитать таблицу истинности", style='W.TButton', command=self.calc).pack(fill=tk.X, pady=5)
        ttk.Button(act, text="Очистить всё", style='W.TButton', command=self.clr).pack(fill=tk.X, pady=5)
        ttk.Button(act, text="Назад в меню", style='W.TButton', command=self.go_back).pack(fill=tk.X, pady=5)
        ttk.Button(act, text="Экспорт таблицы в PNG", style='W.TButton', command=self.export_table).pack(fill=tk.X, pady=5)

        ttk.Label(self.right, text="Таблица истинности", font=(FONT_NAME, 20, 'bold'), background=BG_COLOR, foreground=LABEL_COLOR).pack(pady=20)

    # закрывает окно и возвращает на Стартовый экран
    def go_back(self):
        self.win.destroy()
        self.root.deiconify()
        self.root.state('zoomed')
        self.root.configure(bg=BG_COLOR)

    # вставка текста в поле ввода
    def ins(self, text):
        pos = self.e.index(tk.INSERT)
        self.e.insert(pos, text)
        self.e.focus()

    # расчет введенного выражения    
    def calc(self):
        ex = self.e.get()
        if not ex.strip():
            ErrorDialog(self.win, "Введите выражение")
            return
        
        validator = ExpressionValidator()
        is_valid, error_msg = validator.validate(ex)
        if not is_valid:
            ErrorDialog(self.win, error_msg)
            return
        
        vars = p.parsing(ex)
        n = len(vars)
        result = []
        calculator = Calculator()

        for i in range(2**n):
            env = {}
            for j, var in enumerate(vars):
                env[var] = (i >> (n - 1 - j)) & 1
            res = calculator.calculate(ex, env)  
            result.append(res)

        self.update_truth_table(vars, result)   
        self.last_expression = ex
        self.last_vars = vars
        self.last_result = result

    # строит таблицу истинности
    def update_truth_table(self, vars, result):
        if self.t:
            self.t.destroy()
        n = len(vars)
        self.t = ttk.Treeview(self.right, show='headings', height=2**n)
        self.t.pack(padx=10)
        cols = vars + ['RESULT']
        self.t['columns'] = cols
        for col in cols:
            self.t.heading(col, text=col, anchor='center')
            w = 100 if col == 'RESULT' else 70
            self.t.column(col, width=w, anchor='center', minwidth=w)
        if n == 0:
            return
        for i in range(2**n):
            row = []
            for j in range(n):
                row.append((i >> (n - 1 - j)) & 1)
            full_row = row + [result[i]]
            self.t.insert('', 'end', values=full_row)

    # экспорт таблицы истинности
    def export_table(self):
        if not hasattr(self, 'last_vars') or not hasattr(self, 'last_result') or not hasattr(self, 'last_expression'):
            ErrorDialog(self.win, "Сначала рассчитайте таблицу истинности.")
            return

        expression = self.last_expression
        vars = self.last_vars
        result = self.last_result

        n = len(vars)
        data = []
        for i in range(2**n):
            row = []
            for j in range(n):
                row.append((i >> (n - 1 - j)) & 1)
            row.append(result[i])
            data.append(row)

        cols = vars + ['RESULT']
        df = pd.DataFrame(data, columns=cols)

        file_path = filedialog.asksaveasfilename(parent=self.win, defaultextension=".png", filetypes=[("PNG файлы", "*.png"), ("Все файлы", "*.*")], 
                                                 title="Сохранить таблицу истинности как PNG")
        if not file_path:
            return
        try:
            fig_height = max(5, len(data) * 0.35 + 1.5)
            fig, ax = plt.subplots(figsize=(max(6, len(cols) * 1.2), fig_height))
            ax.axis('tight')
            ax.axis('off')
            ax.text(0.5, 1.05, f"Выражение: {expression}", 
                    transform=ax.transAxes, 
                    fontsize=14, 
                    weight='bold', 
                    ha='center')
            table = ax.table(cellText=df.values, colLabels=df.columns, cellLoc='center', loc='center')
            table.auto_set_font_size(False)
            table.set_fontsize(12)
            table.scale(1, 1.5)
            plt.savefig(file_path, bbox_inches='tight', dpi=150)
            plt.close(fig)
            messagebox.showinfo("Экспорт завершён", f"Таблица сохранена:\n{file_path}")
        except Exception as e:
            ErrorDialog(self.win, f"Ошибка экспорта:\n{str(e)}")

    # очищает поле ввода и удаляет таблицу
    def clr(self):
        self.e.delete(0, tk.END)
        if self.t:
            self.t.destroy()
            self.t = None
    

class InteractiveLearning:
    # инициализация окна Интерактивное обучение
    def __init__(self, root):
        self.root = root
        self.win = tk.Toplevel(root)
        self.win.title("Интерактивное обучение")
        self.win.state('zoomed')
        self.win.configure(bg=BG_COLOR)
        self.win.protocol("WM_DELETE_WINDOW", self.go_back)
        self.setup_ui()

    # создает интерфейс
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('W.TButton', padding=(20, 10), font=(FONT_NAME, 11), background=BUTTON_COLOR, foreground=BUTTON_TEXT_COLOR)
        style.map('W.TButton', background=[('active', BUTTON_HOVER), ('pressed', BUTTON_PRESS)])
        style.configure('Treeview', font=(FONT_NAME, 12), background=ENTRY_BG, fieldbackground=ENTRY_BG, foreground=ENTRY_FG)
        style.configure('Treeview.Heading', font=(FONT_NAME, 11, 'bold'))

        main = ttk.Frame(self.win, style='Main.TFrame')
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        style.configure('Main.TFrame', background=BG_COLOR)

        left = ttk.Frame(main, width=350, style='Card.TFrame')
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left.pack_propagate(False)
        left.configure(style='Card.TFrame')
        ttk.Label(left, text="Теория и задания", font=(FONT_NAME, 16, 'bold'), background=BG_COLOR, foreground=LABEL_COLOR).pack(pady=(0, 10))

        self.tree = ttk.Treeview(left, show='tree')
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.sections = {
            'БАЗОВЫЕ ФУНКЦИИ': ['AND', 'OR', 'NOT', 'Эквиваленция'],
            'СОСТАВНЫЕ ФУНКЦИИ': ['XOR', 'NAND', 'NOR', 'Импликация'],
            'ЗАКОНЫ': ['Двойного отрицания', 'Исключение третьего', 'Исключение констант', 
                       'Повторения', 'Поглощения', 'Переместительный',
                       'Сочетательный', 'Распределительный', 'Де Моргана'], 
            'СИНТАКСИС': ['Приоритеты логических операций']}
        
        for section, items in self.sections.items():
            sec_id = self.tree.insert('', tk.END, text=section, open=True)
            for item in items:
                self.tree.insert(sec_id, tk.END, text=item, tags=(item,))
            self.tree.insert(sec_id, tk.END, open=False, tags=('separator',))

        act = ttk.Frame(left, style='Card.TFrame')
        act.pack(fill=tk.X, pady=30)
        ttk.Button(act, text="Назад в меню", style='W.TButton', command=self.go_back).pack(fill=tk.X, pady=5)

        self.tree.bind('<<TreeviewSelect>>', self.on_select)

        self.right = ttk.Frame(main, style='Card.TFrame')
        self.right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.right.configure(style='Card.TFrame')

        self.current_content = None
        self.current_task = None

    # закрывает окно и возвращает на Стартовый экран
    def go_back(self):
        self.win.destroy()
        self.root.deiconify()
        self.root.state('zoomed')
        self.root.configure(bg=BG_COLOR)

    # читает данные из выбранного файла JSON
    def on_select(self, event):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        if 'separator' in self.tree.item(sel[0], 'tags'):
            self.tree.selection_remove(sel[0])
            return
        parent = self.tree.parent(sel[0])
        if not parent:
            return
        name = item['text']
        path = os.path.join(resource_path("theory_cards"), f"{name}.json")

        if not os.path.isfile(path):
            ErrorDialog(self.win, "Файл теории не найден.")
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Проверка структуры
            if not isinstance(data, dict):
                raise ValueError("Файл должен содержать объект (словарь)")
            if 'title' not in data:
                raise ValueError("Поле 'title' отсутствует")
            if 'text' not in data:
                raise ValueError("Поле 'text' отсутствует")
            if 'task' not in data:
                raise ValueError("Поле 'task' отсутствует")
            if 'answer' not in data:
                raise ValueError("Поле 'answer' отсутствует")

        except json.JSONDecodeError as e:
            ErrorDialog(self.win, f"Некорректный JSON: {str(e)[:100]}")
        except ValueError as e:
            ErrorDialog(self.win, f"Ошибка структуры: {e}")
        except Exception as e:
            ErrorDialog(self.win, f"Не удалось загрузить файл: {e}")
        else:
            self.show_content(data)

    # отрисовывает теория и задания из файла JSON
    def show_content(self, data):
        if self.current_content:
            self.current_content.destroy()
        if self.current_task:
            self.current_task.destroy()

        self.current_content = ttk.Frame(self.right, style='Card.TFrame')
        self.current_content.pack(fill=tk.BOTH, expand=True)
        style = ttk.Style()
        style.configure('Card.TFrame', background=BG_COLOR)

        title = data.get('title', 'Без названия')
        text_items = data.get('text', [])
        tasks = data.get('task', [])
        answers = data.get('answer', [])

        if isinstance(text_items, str):
            text_items = [text_items]
        elif not isinstance(text_items, list):
            text_items = []

        if not isinstance(tasks, list):
            tasks = []
        if not isinstance(answers, list):
            answers = []

        ttk.Label(self.current_content, text=title, font=(FONT_NAME, 18, 'bold'),
                  background=BG_COLOR, foreground=LABEL_COLOR).pack(anchor='w', pady=(0, 10))

        for txt in text_items:
            ttk.Label(self.current_content, text=txt, wraplength=700, justify=tk.LEFT, font=(FONT_NAME, 12), 
                      background=BG_COLOR).pack(anchor='w', pady=(0, 5))

        self.answer_vars = []
        self.result_labels = []
        self.current_answers_display = []

        if not tasks:
            return

        sep = ttk.Separator(self.current_content, orient='horizontal')
        sep.pack(fill=tk.X, pady=20)

        self.current_task = ttk.Frame(self.current_content, style='Card.TFrame')
        self.current_task.pack(fill=tk.X, pady=10)

        while len(answers) < len(tasks):
            answers.append([])

        for i, task in enumerate(tasks):
            task_block = ttk.Frame(self.current_task, style='Card.TFrame')
            task_block.pack(anchor='w', fill=tk.X, pady=(0, 15))

            ttk.Label(task_block, text=f"Задание {i+1}:", font=(FONT_NAME, 14, 'bold'), background=BG_COLOR, foreground=LABEL_COLOR).pack(anchor='w')
            ttk.Label(task_block, text=task, wraplength=700, justify=tk.LEFT, font=(FONT_NAME, 12), background=BG_COLOR).pack(anchor='w', pady=(5, 10))

            ans_var = tk.StringVar()
            self.answer_vars.append(ans_var)
            entry = ttk.Entry(task_block, textvariable=ans_var, font=(FONT_NAME, 12), width=50)
            entry.pack(anchor='w', pady=5)

            res_label = ttk.Label(task_block, text="", font=(FONT_NAME, 12), background=BG_COLOR)
            res_label.pack(anchor='w', pady=(5, 0))
            self.result_labels.append(res_label)

            orig_ans_list = answers[i]
            if isinstance(orig_ans_list, str):
                orig_ans_list = [orig_ans_list]
            self.current_answers_display.append(orig_ans_list[0] if orig_ans_list else "—")
            normalized_correct = [str(a).replace(" ", "").lower() for a in orig_ans_list]

            btn = ttk.Button(task_block, text="Проверить", style='W.TButton', command=lambda idx=i, norm=normalized_correct: 
                             self.check_single_answer(idx, norm))
            btn.pack(anchor='w', pady=5)
            btn.pack(anchor='w', pady=5)

    # проверяет ответ пользователя
    def check_single_answer(self, index, normalized_correct):
        user_input = self.answer_vars[index].get().replace(" ", "").lower()
        label = self.result_labels[index]

        if user_input in normalized_correct:
            label.config(text="Правильно!", foreground="green", background=BG_COLOR)
        else:
            example = self.current_answers_display[index]
            label.config(text=f"Неправильно. Правильный ответ: {example}", foreground="red", background=BG_COLOR)

    # показывает сообщения
    def show_message(self, msg):
        if self.current_content:
            self.current_content.destroy()
        if self.current_task:
            self.current_task.destroy()
        frame = ttk.Frame(self.right, style='Card.TFrame')
        frame.pack()
        ttk.Label(frame, text=msg, font=(FONT_NAME, 12), background=BG_COLOR).pack(pady=20)
        self.current_content = frame


# создает Стартовый экран
def main():
    global FONT_NAME
    root = tk.Tk()
    root.title("BoolTrainer")
    root.state('zoomed')
    root.configure(bg=BG_COLOR)
    style = ttk.Style()
    style.theme_use('clam')

    style.configure('TFrame', background=BG_COLOR)
    style.configure('TLabel', background=BG_COLOR, foreground=LABEL_COLOR)
    style.configure('TLabelframe', background=BG_COLOR, borderwidth=0)
    style.configure('TLabelframe.Label', background=BG_COLOR, font=(FONT_NAME, 12, 'bold'))

    style.configure('S.TButton', font=(FONT_NAME, 14), width=30, padding=(0, 20), background=BUTTON_COLOR, foreground=BUTTON_TEXT_COLOR, borderwidth=0)
    style.map('S.TButton', background=[('active', BUTTON_HOVER), ('pressed', BUTTON_PRESS)])

    ttk.Label(root, text="BoolTrainer", font=(FONT_NAME, 40)).pack(pady=100)
    
    def open_constructor():
        root.withdraw()
        ConstructorWindow(root)

    def open_learning():
        root.withdraw()
        InteractiveLearning(root)
    
    ttk.Button(root, text="Конструктор", style='S.TButton', command=open_constructor).pack(pady=10)
    ttk.Button(root, text="Интерактивное обучение", style='S.TButton', command=open_learning).pack(pady=10)
    ttk.Button(root, text="Выход", style='S.TButton', command=root.destroy).pack(pady=10)
    root.mainloop()