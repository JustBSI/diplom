import re
from config import *
from tkinter.filedialog import *
import fileinput
from elements import *
import tkinter as tk

dict = {}  # словарь с элементами


class Lexer:  # лексический анализ кода
    # типы слов в строках
    # объявление кортежа (каждому типу слов свой номер)
    ASSIG, ELEM, ADD, NUM, IF, ELSE, WHILE, EQU, MORE, LESS, NOT_EQU, MORE_EQU, LESS_EQU, ELEM_SLICE, RIGHT_SHIFT, LEFT_SHIFT, SUB = range(
        17)
    # типы операций и их обозначения
    symbols = {':=': ASSIG, '+': ADD, '-': SUB, '=': EQU, '>': MORE, '<': LESS, '!=': NOT_EQU, '>=': MORE_EQU,
               '<=': LESS_EQU, '>>': RIGHT_SHIFT, '<<': LEFT_SHIFT}
    # ключевые слова (циклы и условия)
    keywords = {'если': IF, 'иначе': ELSE, 'пока': WHILE}

    @classmethod  # метод класса, который вызывается без создания экземпляра класса
    def is_elem(cls, word):  # проверка, является ли кусок строки элементом
        w = word
        if w[0] == '-':
            w = w[1:]  # убираем минус
        if '[' in w:
            w = w.split('[')[0]
        return w in dict.keys()  # проверка, есть ли элемент в словаре

    @classmethod
    def parse(self, row):  # анализирует строку и составляет лексический макет. РгА := РгА + 1 --> [1, 0, 1, 2, 3]
        string = row.split()
        result = []
        for word in string:
            if self.is_elem(word):  # если это элемент
                result.append(self.ELEM)  # то добавляем его в макет
            elif word.split('[')[0] in dict.keys():  #
                result.append(self.ELEM_SLICE)
            elif word in self.keywords.keys():
                result.append(self.keywords[word])
            elif word in self.symbols.keys():
                result.append(self.symbols[word])
            # elif len(word.replace('0', '').replace('1', '')) == 0:
            elif len(re.sub(r"\d+", "", word, flags=re.UNICODE)) == 0:  # если найдено что-то кроме паттерна
                result.append(self.NUM)  # то это чисто
        return result  # возвращает макет строки


class NewLexer:

    keywords: list
    keywords_first_letters: str

    def __init__(self, keywords: str = '', symbols: str = '') -> None:
        self.keywords = keywords.split()
        self.symbols  = symbols.split()
        self.symbols.sort(key=lambda x: len(x), reverse=True)
        print(self.symbols)
        self.keywords_fl = "".join(set([keyword[0] for keyword in self.keywords])) # first letters
        self.symbols_fl  = "".join(set([ symbol[0] for  symbol in self.symbols ])) # first letters

    def parse(self, row: str) -> list:
        row = row.split('//')[0] # чистка от строчных комментариев
        row = re.sub(" +", " ", row.strip())
        new_row = ''
        row_len = len(row)
        i = 0
        while i <len(row):
            if row[i] in self.symbols_fl:
                found = False
                for symbol in self.symbols:
                    symbol_len = len(symbol)
                    if i+symbol_len <= row_len:
                        if row[i:i+symbol_len] == symbol:
                            if new_row[-1] != ' ':
                                new_row += ' '
                            new_row += symbol + ' '
                            i += symbol_len
                            found = True
                            break
                if not found:
                    i += 1
            elif row[i] == ' ':
                if row[i-1] != ' ':
                    new_row += ' '
                i += 1
            else:
                new_row += row[i]
                i += 1

        return new_row.strip().split()


NL = NewLexer('if else end', '+= = -= <=')
#print(NL.parse(' test    string  '))
print(NL.parse(' test  <=string  '))
#print(' test  string  ')


class Node:  # управление узлами. Узлом является абстрактная модель,
    # представляющая исполняемую инструкцию и возможные переходы к другим инструкциям.
    # типы узлов
    types = ['ACT', 'IF', 'ELSE', 'WHILE']
    ACT, IF, ELSE, WHILE = range(4)

    def __init__(self, row=None, out=None, rownum=None):  # функция инициализации узла.
        if row:
            self.row = row  # рассматриваемая сырая строка из кода: РгА := РгА + 1
            self.pattern = Lexer.parse(
                row)  # передаём паттерну полученную пропарсенную лексером строку: [1, 0, 1, 2, 3]
            if Lexer.IF in self.pattern:  # если паттерн содержит 4 (IF), то значит строка содержит условие
                self.type = Node.IF  # присваиваем этому узлу тип if
            elif Lexer.ELSE in self.pattern:
                self.type = Node.ELSE
            elif Lexer.WHILE in self.pattern:
                self.type = Node.WHILE
            else:
                self.type = Node.ACT  # если это не условия и не цикл, то это операция
        if out:
            self.out = out  # ссылка на выход на верхний уровень
        if rownum:
            self.rownum = rownum  # номер рассматриваемой строки, нужен для маркера

    @staticmethod  # метод класса без ссылки на метод класа или сам класс
    def parse(rows, out=None, bias=0):  # парсит строки по узлам и уровням (bias -- это смещение маркера)

        current = Node()
        first = current
        i = 0  # счётчик для маркера
        while i < len(rows):  # перебор по строкам кода
            if not rows[i].strip():  # если строка пустая
                i += 1  # сдвигаем маркер
            elif rows[i][0:4] != "    ":  # если нет сдвига, значит это всё ещё тот же уровень
                current.next = Node(rows[i], out, bias + i)  # создаём ссылку на следующий узел
                current = current.next  # переходим на него
                current.rownum = bias + i  # высчитывание глобальной строки
                i += 1  # сдвигаем маркер
            else:  # если находим сдвиг (таб)
                inside_rows = []  # строку закидываем в массив внутренних строк
                while i < len(rows) and rows[i][0:4] == "    ":  # пока сдвиг есть
                    inside_rows.append(rows[i][4:])  # добавлять строки в массив уровня
                    i += 1  # сдвигаем маркер
                current.inside = Node.parse(inside_rows, current,
                                            i - len(inside_rows) + bias)  # ссылка на первый узел внутреннего уровня

        return first.next  # возвращает текущий узел

    def step(self):  # шаг с обходом
        if self.type == Node.ACT:  # если узел -- это действие
            self.execute  # выполнять
            return self.find_next()  # ищет следующий узел
        elif self.type == Node.IF:  # если узел -- это гА' + РгБ'условие
            if self.execute:  # проверка выполнения условия (true или false)
                self.inside.execute_all()  # выполняет все узлы уровня
                if hasattr(self, "next"):  # проверка есть ли у узла ссылка на следующий
                    if self.next.type == Node.ELSE:  # если тип следующего узла "если"
                        return self.next.find_next()  # ищем следующий следующего
                    else:
                        return self.next  # возвращает ссылку на следующий узел
                else:
                    return self.find_out()  # возвращает ссылку на узел внешнего уровня
            else:  # если условие не выполняется
                if hasattr(self, "next"):  # проверка есть ли у узла ссылка на следующий
                    if self.next.type == Node.ELSE:  # если тип следующего узла "если"
                        self.next.inside.execute_all()  # выполняет все узлы уровня
                        return self.next.find_next()  # возвращает ссылку на следующий узел следующего узла
                    else:
                        return self.next  # возвращает ссылку на следующий узел
                else:
                    return self.find_out()  # возвращает ссылку на узел внешнего уровня
        elif self.type == Node.WHILE:  # если узел -- это "пока"
            while self.execute:  # пока выполняется уловие
                self.inside.execute_all()  # выполнит все узлы уровня
            return self.find_next()  # возвращает ссылку на слдующий уровень
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None

    def step_inside(self):  # шаг с заходом
        if self.type == Node.ACT:  # если узел -- это действие
            self.execute  # выполнить
            return self.find_next()  # вернуть ссылку на следующий
        elif self.type == Node.IF:  # если узел -- условие
            if self.execute:  # если выполняется условие
                return self.inside  # ссылка на первый узел тела цикла
            else:  # если условие не выполняется
                if hasattr(self, "next"):  # если у узла есть ссылка на следующий
                    if self.next.type == Node.ELSE:  # если следующий узел -- это else
                        return self.next.inside  # ссылка на тело else
                    else:  # если это не else
                        return self.next  # ссылка на следующий узел
                else:  # если ссылки на следующий узел нет
                    return self.find_out()  # ссылка на внешний уровень
        elif self.type == Node.WHILE:  # если узел -- while
            if self.execute:  # если выполняется условие
                return self.inside  # ссылка на первый узел тела цикла
            else:  # если условие не выполняется
                return self.find_next()  # вернуть ссылку на следующий
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None

    def step_outside(self):  # шаг с выходом
        last = self.execute_all()  # довыполняем всё до внешнего уровня
        current = last.find_out()  # ссылка на узел где окажемся после выполения тела
        if current.type == Node.WHILE and last.out is current:  # чтобы не проскочить возможный следущий while
            while current.execute:  # пока выполняется условие
                current.inside.execute_all()  # выполняем тело
            return current.find_next()  # ссылка на следующий узел внешнего уровня
        else:  # если это не while
            return current  # ссылка на узел, в который попали

    def find_next(self):  # ищет ссылку на следующий узгА' + РгБ'ел
        if hasattr(self, "next"):  # если есть ссылка на следующий узел
            return self.next  # ссылка на следующий узел
        else:  # если ссылки на следующий нет
            return self.find_out()  # ссылка на внешний узел

    def find_out(self):  # ищет ссылку на внешний узел
        if hasattr(self, "out"):  # если есть ссылка на внешний узел
            if self.out.type == Node.WHILE:  # и если этот узел -- while
                return self.out  # ссылка на тело while
            elif self.out.type == Node.IF:  # если этот узел -- if
                if hasattr(self.out, "next"):  # если у внешнего есть ссылка на следующий
                    if self.out.next.type == Node.ELSE:  # и если это else
                        if hasattr(self.out.next, "next"):  # если есть узел за else
                            return self.out.next.next  # ссылка на следущий за else узел
                        else:  # если за else на этом уровне ничего нет
                            return self.out.next.find_out()  # ссылка на внешний уровень
                    else:  # если это не else
                        return self.out.next  # ссылка на вншний узел
                else:  # если за if ничего нет
                    return self.out.find_out()  # ссылка на внешний узел
            elif self.out.type == Node.ELSE:  # если это else
                if hasattr(self.out, "next"):  # и если у него есть ссылка на следующий
                    return self.out.next  # ссылка на него
                else:  # если следующего нет
                    return self.out.find_out()  # ссылка на внешний
            else:
                print("Ошибка: недопустимый тип узла -- " + Node.types[self.out.type])
                return None
        else:  # если внешнего узла нет
            return None

    def display(self, indent=0):  # функция для отображения макета кода в консоли (для отладки)
        ans = ''
        try:
            print(str(self.rownum) + ' ' + '| ' * indent + Node.types[self.type] + ' ' + self.row + ' ' + str(
                self.pattern) + ' ' + str(hasattr(self, "next")))
        # print(str(self.rownum))
        except Exception as e:
            # print(e)
            print('strange node')
        if hasattr(self, "inside"):
            self.inside.display(indent + 1)
        if hasattr(self, "next"):
            self.next.display(indent)

    @staticmethod
    def pure_name(word):  # выцепляет название элемента из слова
        res = word.strip()  # делит по пробелам
        if res[0] == '-':  # отбрасывает минус
            res = res[1:]
        if '[' in res:  # отбрасывает скобки
            res = res.split('[')[0]
        return res  # возвращаем имя элемента

    @staticmethod
    def pure_slice(word):  # функция получает диапазон среза из кода (если есть)
        if '[' in word:
            return word.split('[')[1].split(']')[0].strip()
        return None

    @staticmethod
    def set_elem(elem, val):  # установка значения элемента
        if '[' in elem:  # если срез
            dict[Node.pure_name(elem)].set(val, Node.pure_slice(elem))
        else:  # если просто значение
            dict[Node.pure_name(elem)].set(val)

    @staticmethod
    def get_elem(elem):  # получает значение элемента
        if '[' in elem:  # если срез
            return dict[Node.pure_name(elem)].get(slice=Node.pure_slice(elem), inv=elem[0] == '-')
        else:  # если просто значение
            return dict[Node.pure_name(elem)].get(inv=elem[0] == '-')

    # исполнение
    @property
    def execute(self):  # функция выполнения
        c = self.row.split()  # сплитит строку, с которой работаем
        p = self.pattern  # закидываем паттерн для сравнения
        if p[1] == 0:  # если это инструкция присвоения :=
            if p[0] == 1:  # если слева элемент
                if len(p) == 3:  # проверка на правильность операции (РгА := 1)
                    if p[2] == 3:  # если справа значение
                        Node.set_elem(c[0], c[2])  # присваивает значение переменной
                    elif p[2] == 1:  # если справа элемент
                        Node.set_elem(c[0], Node.get_elem(c[2]))  # присваивает переменной значение другой переменной
                elif len(p) == 5:  # если строка вида РгА := РгБ + 1
                    if p[3] == 2:  # если это сложение
                        if p[2] == 1:  # если первый операнд элемент
                            if p[4] == 1:  # если второй операнд элемент
                                dict[c[0]].set(dict['СМ'].add(dict[c[2]].data, dict[c[4]].data, 0)[
                                                   0])  # присвоить элементу сумму значений операндов
                            elif p[4] == 3:  # если второй операнд это значение
                                if type(dict[c[2]]).__name__ == 'Counter':  # если второй операнд счётчик
                                    dict[c[2]].count += int(c[4])  # увеличить счётчик на значение
                    elif p[3] == 14:  # если сдвиг вправо
                        if type(dict[c[2]]).__name__ == 'Register':  # если слева регистр
                            new_data = [0] + dict[c[2]].data[:-1]  # формируется новое значение
                            for i in range(len(new_data)):  # записываем результат в регистр
                                dict[c[0]].data[i] = new_data[i]
                    elif p[3] == 15:  # если сдвиг влево
                        if type(dict[c[2]]).__name__ == 'Register':  # если слева регистр
                            new_data = dict[c[2]].data[1:]  # формируется новое значение
                            new_data.append(0)  # дописываем в правово края ноль
                            for i in range(len(new_data)):  # записываем результат в регистр
                                dict[c[0]].data[i] = new_data[i]
                    elif p[3] == 16:  # если вычитание
                        if type(dict[c[2]]).__name__ == 'Counter':  # если второй операнд счётчик
                            dict[c[2]].count -= int(c[4])  # уменьшить счётчик на значение
                elif len(p) == 7:  # если прибавляется единица (РгА := РгА + РгБ + 1)
                    # print(dict[c[2]]).data
                    dict[c[0]].set(dict['СМ'].add(dict[c[2]].data, dict[c[4]].data, 1)[0])
        elif p[0] == Lexer.IF:  # если строка содержит условие
            return self.condition()  # вернуть результат
        elif p[0] == Lexer.WHILE:  # если строка содержит цикл
            return self.condition()  # вернуть результат
        # else:
        # print('nothing was done')

    def execute_all(self):  # выполнение всего уровня
        current = self
        while hasattr(current, "next"):  # пока у текущего есть ссылка на следующий
            if current.type == Node.ACT:  # и если текущий -- это действие
                current.execute  # выполнить
                current = current.next  # взять ссылку на следующий
            elif current.type == Node.IF:  # если текущий -- if
                if current.execute:  # и если выполняется условие
                    current.inside.execute_all()  # выполнить тело if
                    if current.next.type == Node.ELSE:  # если следующий -- это else
                        if hasattr(current.next, "next"):  # если у него есть тело
                            current = current.next.next  # выход на внешний уровень
                    else:  # если else нет
                        current = current.next  # следующий узел
                else:  # если условие не выполняется
                    current = current.next  # переход на следующий узел
                    if current.type == Node.ELSE:  # если это else
                        current.inside.execute_all()  # выполнить тело else
                        if hasattr(current, "next"):  # если после него есть узел
                            current = current.next  # взять ссылку на следующий
            elif current.type == Node.WHILE:  # если это while
                while current.execute:  # пока выполняется условие
                    current.inside.execute_all()  # выполнить тело
                current = current.next  # взять ссылку на следующий
            else:
                print("Ошибка: недопустимый тип узла -- " + Node.types[current.type])
        if current.type == Node.ACT:  # если это действие
            current.execute  # выполнить
        elif current.type == Node.IF:  # если это условие
            if current.execute:  # если условие выполняется
                current.inside.execute_all()  # выполнить тело
        elif current.type == Node.WHILE:  # если это while
            while current.execute:  # пока выполняется условие
                current.inside.execute_all()  # выполнить тело
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[current.type])
        return current

    def get_pattern_value(self, num, c):  # получает значение элемента по паттерну
        if self.pattern[num] == Lexer.ELEM:  # если слева элемент
            if '[' in c[num]:  # если есть указатель на конкретный разряд
                return dict[c[num].split('[')[0]].value(c[num].split('[')[1].split(']')[0].strip())  # вернуть значение
            else:  # если указателя нет
                return dict[c[num]].value()  # вернуть значение
        elif self.pattern[num] == Lexer.ELEM_SLICE:  # если это срез элемента
            v = c[num].split('[')  # диапазон
            return dict[v[0]].slice_value(v[1][:-1].strip())  # берем срез
        elif self.pattern[num] == Lexer.NUM:  # если это число
            return int(c[num])  # вернуть это число

    def condition(self) -> bool:  # функция сравнения
        c = self.row.split()  # строка, с которой работаем
        op1 = self.get_pattern_value(1, c)  # значение первого операнда
        op2 = self.get_pattern_value(3, c)  # значение второго операнда
        # print(op1 == op2)
        if c[2] == '=':
            c[2] = '=='
        try:
            return eval(str(op1) + c[2] + str(op2))
        except Exception:
            print(Exception)
            return False


class classCounter:  # счетчик

    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def __repr__(self):
        return self.count


def reset(i):  # функция сброса всего
    # pointer_canvas.delete('pointer')
    pointer_canvas.delete(1.0, END)  # очистка канваса
    txt.configure(state=NORMAL)  # включает возможность редактирования текста в поле
    step_entry_btn.place_forget()  # прячет кнопку
    step_detour_btn.place_forget()  # прячет кнопку
    step_exit_btn.place_forget()  # прячет кнопку
    reset_btn.place_forget()  # прячет кнопку
    start_btn.place(x=20, y=7)  # возвращает кнопку "старт"
    # rows = txt.get("1.0", END).splitlines()
    # c.coords('mark',335, 65, 350, 65)
    i.reset()  # сброс канваса
    for key in dict:  # сбрасывает значения всех элементов путём вызова соответствующей функции в экземпляре каждого элемента
        dict[key].reset()
        # print(key)
    if mode == 1:  # если открыта простая схема
        scheme_simple_display(scheme_canvas)  # то перерисовать её (сбросить)
    elif mode == 2:  # если открыта структурная схема
        scheme_struct_display(scheme_canvas)  # то перерисовать её (сбросить)
    # drawer_default_scheme()
    # display(c)


root = Tk()  # создание экземпляра Tkinter
root.geometry('480x900')  # размер окна


def scheme_simple():  #
    return tk.Toplevel(root)


def scheme_struct():  #
    return tk.Toplevel(root)


def scheme_struct_display(c, file):  # рисование структурной схемы по файлу
    c.delete('reg')  # очистка окна перед рисованием (обновление)
    c.pack(side=LEFT)  # помещение канваса в окне
    for row in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")):  # открытие файла
        string = re.split(' ', row)  # деление строки на куски
        name = re.split('\(', string[0])[0]  # выделение названия
        coords = re.split('\,', string[1])  # выделение координатов
        if 'Линия' in name:  # если это линия
            # print('Линия')
            # выделение пары пар координат для начала и конца линии
            xa = re.findall(r'\d+', coords[0])
            ya = re.findall(r'\d+', coords[1])
            xb = re.findall(r'\d+', coords[2])
            yb = re.findall(r'\d+', coords[3])
            c.create_line(xa, ya, xb, yb, tag='reg')  # рисование линии по заданным координатам
        elif 'Стрелка' in name:  # если это стрелка
            # print('Стрелка')
            # выделение пары пар координат для начала и конца линии
            xa = re.findall(r'\d+', coords[0])
            ya = re.findall(r'\d+', coords[1])
            xb = re.findall(r'\d+', coords[2])
            yb = re.findall(r'\d+', coords[3])
            c.create_line(xa, ya, xb, yb, tag='reg', arrow=LAST)  # рисование стрелки по координатам
        elif 'Инверсия' in name:  # если это инверсия (пририсовывает кружок)
            size = 6
            x = int(re.findall(r'\d+', coords[0])[0])
            y = int(re.findall(r'\d+', coords[1])[0])
            c.create_oval(x - size / 2, y - size / 2, x + size / 2, y + size / 2, outline="#000", fill="#fff", width=2)
        else:  # в остальных случаях -- это кооринаты элемента
            #print(coords)
            x = re.findall(r'\d+', coords[0])
            y = re.findall(r'\d+', coords[1])
            # print (x,y)
            if name in dict:  # если элемент есть в словаре
                dict[name].display_struct(int(x[0]), int(y[0]), c,
                                          CANVAS_WIDTH)  # вызов функции рисования элемента в структурной схеме


def scheme_simple_display(c):  # автоматическое рисование упрощённой схемы
    c.delete('reg')  # очистка окна перед рисованием (обновление)
    c.pack(side=LEFT)  # помещение канваса в окне
    j = 0  # нужно для отступа по вертикали между элементами
    for i in dict:  # перебор всех элементов словаря
        dict[i].display_simple(0, j, c, CANVAS_WIDTH)  # вызов функции рисования элемента в простой схеме
        j += 20  # сдвиг по вертикали


# scheme_simple_display(scheme_simple())
# окно

def create_scheme_struct():  # создание поля для структурной схемы
    global scheme_canvas
    global mode
    global draw_file
    mode = 2  # режим окна рисования
    # elements = len(dict)
    draw_file = askopenfilename(filetypes=[("Text files", "*.txt")])  # запрос на открытие файла конфигурации
    print(draw_file)
    # print(fileinput.input(draw_file, openhook=fileinput.hook_encoded("utf-8"))[0])
    # размеры канваса по-умолчанию
    w = 450
    h = 350
    with open(draw_file, 'r', encoding="utf-8") as f:
        for row in f:  # перебор строк файла конфигурации
            if 'Размер' in row:  # если находит размеры
                arguments = row.split()[1].split(',')  # делит на ширину и высоту
                # и присваивает новые значения окну
                w = int(re.findall(r'\d+', arguments[0])[0])
                h = int(re.findall(r'\d+', arguments[1])[0])
    new_tk = scheme_simple()
    scheme_canvas = Canvas(new_tk, width=w, height=h, bg='white')  # канвас для схем
    scheme_struct_display(scheme_canvas, draw_file)  # открытие окна и запрос файла конфигурации
    f.close()


def create_scheme_simple():  # создание поля для простой схемы
    new_tk = scheme_simple()
    global scheme_canvas
    global mode
    mode = 1  # режим окна рисования
    w = 1
    for d in dict:  # ищем самый длинный регистр для того чтобы подогнать ширину окна
        if type(dict[d]).__name__ == 'Register':
            if len(dict[d].data) > w:
                w = len(dict[d].data)
    w *= 6
    w += 100
    h = len(dict) * 20 + 30  # настройка высоты окна в зависимости от количества элементов в словаре
    scheme_canvas = Canvas(new_tk, width=w, height=h, bg='white')
    scheme_simple_display(scheme_canvas)


cc = classCounter()  # счётчик


def add_pointer(num, length):  # добавление маркера
    return str(num) + ' ' * (length - len(str(num)) - 2) + '⯈'


def start():  # функция старта (кнопки "старт")
    txt.configure(state=DISABLED)  # запрет на редактирование кода в поле
    start_btn.place_forget()  # прячет кнопку
    # размещает кнопки
    step_entry_btn .place(x=20, y=7)
    step_detour_btn.place(x=60, y=7)
    step_exit_btn  .place(x=100, y=7)
    reset_btn      .place(x=170, y=7)
    # global pointer
    # pointer = pointer_canvas.create_line(0, ROWHEIGHT / 2 + 2, 10, ROWHEIGHT / 2 + 2, arrow=LAST, tag='pointer')
    global currentnode
    rows = txt.get("1.0", END).splitlines()  # создаёт массив строк кода из поля (не из файла)
    size = len(rows)  # количество строк
    currentnode = Node.parse(rows)  # текущий узел
    currentnode.display()
    # print(size)
    pointer_canvas.insert(END, '1  ⯈\n')  # вставка маркера
    for i in range(size - 2):  # нумирование строк
        # pointer_canvas.insert(END, '⯈\n')
        pointer_canvas.insert(END, str(i + 2) + '\n')
    pointer_canvas.insert(END, str(size))


def step_inside(e):  # обёртка шага со входом
    global currentnode
    currentnode = currentnode.step_inside()  # выполняем узла
    if currentnode:  # если есть ссылка на следующий узел
        pointer_canvas.delete(1.0, END)
        p = ''
        for i in range(currentnode.rownum):
            p += str(i + 1) + '\n'
        p += add_pointer(currentnode.rownum + 1, 5) + '\n'
        for i in range(currentnode.rownum + 1, len(txt.get("1.0", END).splitlines())):
            p += str(i + 1) + '\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        # pointer_canvas.delete('pointer')
        reset(cc)


def step_outside(e):  # обёртка для шага с выходом
    global currentnode
    currentnode = currentnode.step_outside()
    if currentnode:
        pointer_canvas.delete(1.0, END)
        p = ''
        for i in range(currentnode.rownum):
            p += str(i + 1) + '\n'
        p += add_pointer(currentnode.rownum + 1, 5) + '\n'
        for i in range(currentnode.rownum + 1, len(txt.get("1.0", END).splitlines())):
            p += str(i + 1) + '\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        # pointer_canvas.delete('pointer')
        reset(cc)


def step_bypass(e):  # обёртка для шага с обходом
    global currentnode
    currentnode = currentnode.step()
    if currentnode:
        pointer_canvas.delete(1.0, END)
        p = ''
        for i in range(currentnode.rownum):
            p += str(i + 1) + '\n'
        p += add_pointer(currentnode.rownum + 1, 5) + '\n'
        for i in range(currentnode.rownum + 1, len(txt.get("1.0", END).splitlines())):
            p += str(i + 1) + '\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        # pointer_canvas.delete('pointer')
        reset(cc)


def open_file():  # открытие файла
    global rows
    global size
    txt.delete(1.0, END)  # очистка поля
    file = askopenfilename(filetypes=[("Text files", "*.txt")])  # выбор файла
    for i in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")):  # перенос содержимого файла в поле
        txt.insert(END, i)
    size = sum(1 for line in open(file, 'r'))  # подсчёт количества строк
    # rows = [line.rstrip('\n') for line in open(file, 'r', encoding='utf-8')]
    rows = txt.get("1.0", END).splitlines()  # получение массива строк
    print(file)
    # drawer_default_scheme()


def save_as_file():  # сохранить как
    file = asksaveasfile(mode='w', filetypes=[("Text files", "*.txt")], defaultextension=".txt")  # сохранить как и куда
    if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    print(file)
    text2save = str(txt.get(1.0, END))  # кидает в переменную всё из поля
    file.write(text2save)  # записывает
    file.close()  # закрывает файл


def open_arch() -> None:  # открыть архитектуру
    arch = askopenfilename(filetypes=[("Text files", "*.txt")])
    f = open(arch, 'r', encoding='utf-8')  # открытие файла
    for row in f:  # перебор всех строк
        srow = row.split()
        srow[0] = srow[0].lower()
        match srow:
            case "регистр" | "register", inf:
                name, capacity = inf.split('(')
                capacity = int(capacity.split(')')[0])
                dict[name] = Register(capacity, name)
            case "сумматор" | "adder", inf:
                name, capacity = inf.split('(')
                capacity = int(capacity.split(')')[0])
                dict[name] = Adder(capacity, name)
            case "счётчик" | "counter", inf:
                if "(" in inf:
                    name, limit = inf.split('(')
                    limit = int(limit.split(')')[0])
                    dict[name] = Counter(name, limit)
                else:
                    dict[inf] = Counter(inf)
            case "триггер" | "trigger", inf:
                dict[inf] = Trigger(inf)
            case _:
                print("Неизвестный паттерн")
    f.close()


# настройки верхнего меню
mainmenu = Menu(root)
root.config(menu=mainmenu)
filemenu = Menu(mainmenu, tearoff=0)
schememenu = Menu(mainmenu, tearoff=0)
mainmenu.add_cascade(label="Файл", menu=filemenu)
filemenu.add_command(label="Открыть код", command=open_file)
filemenu.add_command(label="Выбрать архитектуру", command=open_arch)
# filemenu.add_command(label="Сохранить...", command=save_file)
filemenu.add_command(label="Сохранить код", command=save_as_file)
mainmenu.add_cascade(label="Схема", menu=schememenu)
schememenu.add_command(label="Структурная схема", command=create_scheme_struct)
schememenu.add_command(label="Упрощённая схема", command=create_scheme_simple)

# картинки кнопок
step_entry_btn_icon = PhotoImage(file='media/2.png')
step_detour_btn_icon = PhotoImage(file='media/3.png')
step_exit_btn_icon = PhotoImage(file='media/1.png')
reset_btn_icon = PhotoImage(file='media/4.png')
start_btn_icon = PhotoImage(file='media/5.png')

# размеры кнопок
step_entry_btn = Button(width="20", height="20", image=step_entry_btn_icon)
step_detour_btn = Button(width="20", height="20", image=step_detour_btn_icon)
step_exit_btn = Button(width="20", height="20", image=step_exit_btn_icon)
reset_btn = Button(width="20", height="20", image=reset_btn_icon)
start_btn = Button(width="20", height="20", image=start_btn_icon)

# функционал кнопок
# step_entry_btn .bind('<Button-1>', lambda e, f="Verdana": step(e, rows, cc))
step_entry_btn.bind('<Button-1>', step_bypass)
step_detour_btn.bind('<Button-1>', step_inside)
step_exit_btn.bind('<Button-1>', step_outside)
reset_btn.bind('<Button-1>', lambda e, f="Verdana": reset(cc))
start_btn.bind('<Button-1>', lambda e, f="Verdana": start())

# размещение кнопок
step_entry_btn.place_forget  # (x=20, y=7)
step_detour_btn.place_forget  # (x=60, y=7)
step_exit_btn.place_forget  # (x=100, y=7)
reset_btn.place_forget  # (x=170, y=7)
start_btn.place(x=20, y=7)

# конфигурация текстового поля
ROWHEIGHT = 18  # количество строк
mainframe = Frame(root)
scroll = Scrollbar(mainframe)
pointer_canvas = Text(mainframe, width=5, height=35, bg='white', spacing1=2, yscrollcommand=scroll.set)  # метка
txt = Text(mainframe, width=45, height=35, font="14", bg='white', yscrollcommand=scroll.set)  # текст поля


# pointer_canvas.create_line(0,ROWHEIGHT/2+2,10,ROWHEIGHT/2+2, arrow=LAST, tag='pointer')

def OnMouseWheel(event):  # привязывает одно событие к двум текстовым полям
    pointer_canvas.yview("scroll", event.delta, "units")
    txt.yview("scroll", event.delta, "units")
    return "break"


pointer_canvas.bind("<MouseWheel>", OnMouseWheel)
txt.bind("<MouseWheel>", OnMouseWheel)


def onScroll(*args):  # событие прокрутки
    pointer_canvas.yview(*args)
    txt.yview(*args)


scroll.config(command=onScroll)

pointer_canvas.pack(side=LEFT)
mainframe.pack(side=LEFT)
# txt.pack(side=LEFT, padx=0, pady=10)
txt.pack(side=LEFT)
scroll.pack(side=LEFT, fill=Y)
# txt.config(yscrollcommand=scroll.set)

#root.mainloop()
