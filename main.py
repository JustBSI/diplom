import re
from config import *
from tkinter.filedialog import *
import fileinput
from elements import *
import tkinter as tk


dict = {} # словарь с элементами

# Лексический анализ кода
class Lexer:
    # типы слов в строках
    words = ['ASSIG', 'ELEM', 'ADD', 'NUM', 'IF', 'ELSE', 'WHILE', 'EQU', 'MORE', 'LESS', 'NOT_EQU', 'MORE_EQU', 'LESS_EQU']
    # объявление кортежа (каждому типу слов свой номер)
    ASSIG, ELEM, ADD, NUM, IF, ELSE, WHILE, EQU, MORE, LESS, NOT_EQU, MORE_EQU, LESS_EQU, ELEM_SLICE, RIGHT_SHIFT, LEFT_SHIFT = range(16)
    # типы операций и их обозначения
    symbols = {':=': ASSIG, '+': ADD, '=': EQU, '>': MORE, '<': LESS, '!=': NOT_EQU, '>=': MORE_EQU, '<=': LESS_EQU, '>>': RIGHT_SHIFT, '<<': LEFT_SHIFT}
    # ключевые слова (циклы и условия)
    keywords = {'если': IF, 'иначе': ELSE, 'пока': WHILE}

    @classmethod # метод класса, который вызывается без создания экземпляра класса
    def is_elem(cls, word): # проверка, является ли слово в строке элементом
        w = word
        if w[0] == '-':
            w = w[1:] # убираем минус
        if '[' in w:
            w = w.split('[')[0]
        return w in dict.keys() # проверка, есть ли элемент в словаре


    @classmethod
    def parse(self, row): # анализирует строку и составляет лексический макет. РгА := РгА + 1 --> [1, 0, 1, 2, 3]
        string = row.split()
        result = []
        for word in string:
            if   self.is_elem(word):
                result.append(self.ELEM)
            elif word.split('[')[0] in dict.keys():
                result.append(self.ELEM_SLICE)
            elif word in self.keywords.keys():
                result.append(self.keywords[word])
            elif word in self.symbols.keys():
                result.append(self.symbols[word])
            #elif len(word.replace('0', '').replace('1', '')) == 0:
            elif len(re.sub(r"\d+", "", word, flags=re.UNICODE)) == 0:
                result.append(self.NUM)
        return result # возвращает макет строки

# управление узлами. Узлом является абстрактная модель, представляющая исполняемую инструкцию и возможные переходы к другим инструкциям.
class Node:

    # типы узлов
    types = ['ACT', 'IF', 'ELSE', 'WHILE']
    ACT, IF, ELSE, WHILE = range(4)

    def __init__(self, row=None, out=None, rownum=None): # функция инициализации узла.
        if row:
            self.row     = row # рассматриваемая сырая строка из кода: РгА := РгА + 1
            self.pattern = Lexer.parse(row) # передаём паттерну полученную пропарсенную лексером строку: [1, 0, 1, 2, 3]
            if Lexer.IF in self.pattern: # если паттерн содержит 4 (IF), то значит строка содержит условие
                self.type = Node.IF
            elif Lexer.ELSE in self.pattern:
                self.type = Node.ELSE
            elif Lexer.WHILE in self.pattern:
                self.type = Node.WHILE
            else:
                self.type = Node.ACT # если это не условия и не цикл, то это операция
        if out:
            self.out = out # ссылка на выход
        if rownum:
            self.rownum = rownum # номер рассматриваемой строки, нужен для маркера

    @staticmethod # метод класса, который ...
    def parse(rows, out=None, bias=0): #

        current = Node()
        first = current
        i = 0 # счётчик для маркера
        while i < len(rows): # перебор по строкам кода
            if not rows[i].strip(): # если строка пустая
                i += 1 # сдвигаем маркер
            elif rows[i][0:4]!="    ": # если нет сдвига, значит это всё ещё тот же уровень
                current.next = Node(rows[i], out, bias+i) # создаём ссылку на следующий узел
                current = current.next # переходим на него
                current.rownum = bias+i # высчитывание глобальной строки
                i += 1 # сдвигаем маркер
            else: # если находим сдвиг (таб)
                inside_rows = [] # строку закидываем в массив внутренних строк
                while i<len(rows) and rows[i][0:4]=="    ": # пока сдвиг есть
                    inside_rows.append(rows[i][4:]) # добавлять строки в массив уровня
                    i += 1 # сдвигаем маркер
                current.inside = Node.parse(inside_rows, current, i-len(inside_rows)+bias) # ссылка на первый узел внутреннего уровня

        return first.next # возвращает текущий узел

    def step(self): # функция шага
        if self.type == Node.ACT: # если узел -- это действие
            self.execute # выполнять
            return self.find_next()
        elif self.type == Node.IF: # если узел -- это условие
            if self.execute:
                self.inside.execute_all()
                if hasattr(self, "next"):
                    if self.next.type == Node.ELSE:
                        return self.next.find_next()
                    else:
                        return self.next
                else:
                    return self.find_out()
            else:
                if hasattr(self, "next"):
                    if self.next.type == Node.ELSE:
                        self.next.inside.execute_all()
                        return self.next.find_next()
                    else:
                        return self.next
                else:
                    return self.find_out()
        elif self.type == Node.WHILE:
            while self.execute:
                self.inside.execute_all()
            return self.find_next()
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None

    def step_inside(self): # функция
        if self.type == Node.ACT:
            self.execute
            return self.find_next()
        elif self.type == Node.IF:
            if self.execute:
                return self.inside
            else:
                if hasattr(self, "next"):
                    if self.next.type == Node.ELSE:
                        return self.next.inside
                    else:
                        return self.next
                else:
                    return self.find_out()
        elif self.type == Node.WHILE:
            if self.execute:
                return self.inside
            else:
                return self.find_next()
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None


    def step_outside(self): # функция шага с выходом
        last = self.execute_all()
        current = last.find_out()
        if current.type==Node.WHILE and last.out is current:
            while current.execute:
                current.inside.execute_all()
            return current.find_next()
        else:
            return current



    def find_next(self):
        if hasattr(self, "next"):
            return self.next
        else:
            return self.find_out()


    def find_out(self):
        if hasattr(self, "out"):
            if self.out.type == Node.WHILE:
                return self.out
            elif self.out.type == Node.IF:
                if hasattr(self.out, "next"):
                    if self.out.next.type == Node.ELSE:
                        if hasattr(self.out.next, "next"):
                            return self.out.next.next
                        else:
                            return self.out.next.find_out()
                    else:
                        return self.out.next
                else:
                    return self.out.find_out()
            elif self.out.type == Node.ELSE:
                if hasattr(self.out, "next"):
                    return self.out.next
                else:
                    return self.out.find_out()
            else:
                print("Ошибка: недопустимый тип узла -- " + Node.types[self.out.type])
                return None
        else:
            return None


    def display(self, indent=0): # функция для отображения макета кода в консоли
        ans = ''
        try:
            print(str(self.rownum)+' '+'| '*indent+Node.types[self.type]+' '+self.row+' '+str(self.pattern)+' '+str(hasattr(self, "next")))
        #print(str(self.rownum))
        except Exception as e:
            #print(e)
            print('strange node')
        if hasattr(self, "inside"):
            self.inside.display(indent+1)
        if hasattr(self, "next"):
            self.next.display(indent)

    @staticmethod
    def pure_name(word): # функция выцепляет название элемента из слова
        res = word.strip() # делит по пробелам
        if res[0] == '-': # отбрасывает минус
            res = res[1:]
        if '[' in res: # отбрасывает скобки
            res = res.split('[')[0]
        return res

    @staticmethod
    def pure_slice(word): # функция получает диапазон среза из кода (если есть)
        if '[' in word:
            #s = word.split('[')[1].split(']')[0].strip()
            #ss = s.split(':')
            #return int(ss[0]), int(ss[1]), s
            return word.split('[')[1].split(']')[0].strip()
        return None


    @staticmethod
    def set_elem(elem, val): # функция установки значения элемента
        if '[' in elem: # если срез
            #f, t, s = Node.pure_slice(elem)
            dict[Node.pure_name(elem)].set(val, Node.pure_slice(elem))
        else: # если просто значение
            dict[Node.pure_name(elem)].set(val)


    @staticmethod
    def get_elem(elem): # функция получает значение элемента
        if '[' in elem: # если срез
            #f, t, s = Node.pure_slice(elem)
            return dict[Node.pure_name(elem)].get(slice=Node.pure_slice(elem), inv=elem[0]=='-')
        else: # если просто значение
            return dict[Node.pure_name(elem)].get(inv=elem[0]=='-')


    # исполнение
    @property
    def execute(self): # функция выполнения
        c = self.row.split() # сплитит строку, с которой работаем
        p = self.pattern # закидываем паттерн для сравнения
        if p[1] == 0: # если это инструкция присвоения :=
            if p[0] == 1: # если слева элемент
                if   len(p) == 3: # проверка на правильность операции (РгА := 1)
                    if   p[2] == 3: # если справа значение
                        #dict[c[0]].set(c[2])
                        Node.set_elem(c[0], c[2]) # присваивает значение переменной
                    elif p[2] == 1: # если справа элемент
                        #dict[c[0]].set(dict[c[2]].data)
                        Node.set_elem(c[0], Node.get_elem(c[2])) # присваивает переменной значение другой переменной
                elif len(p) == 5: # если строка вида РгА := РгБ + 1
                    if p[3] == 2: # если это сложение
                        if p[2] == 1: # если первый операнд элемент
                            if p[4] == 1: # если второй операнд элемент
                                dict[c[0]].set(dict['СМ'].add(dict[c[2]].data, dict[c[4]].data, 0)[0]) # присвоить элементу сумму значений операндов
                            elif p[4] == 3: # если второй операнд это значение
                                if type(dict[c[2]]).__name__ == 'Counter': # если второй операнд счётчик
                                    dict[c[2]].count += int(c[4]) # увеличить счётчик на значение
                    elif p[3] == 14: # если сдвиг вправо
                        if type(dict[c[2]]).__name__ == 'Register': # если слева регистр
                            new_data = [0]+dict[c[2]].data[:-1]
                            for i in range(len(new_data)):
                                dict[c[0]].data[i] = new_data[i]
                    elif p[3] == 15: # если сдвиг влево
                        if type(dict[c[2]]).__name__ == 'Register': # если слева регистр
                            new_data = dict[c[2]].data[1:]
                            new_data.append(0)
                            for i in range(len(new_data)):
                                dict[c[0]].data[i] = new_data[i]
                elif len(p) == 7:
                    #print(dict[c[2]]).data
                    dict[c[0]].set(dict['СМ'].add(dict[c[2]].data, dict[c[4]].data, 1)[0])
        elif p[0] == Lexer.IF: # если строка содержит условие
            return self.condition()
        elif p[0] == Lexer.WHILE: # если строка содержит цикл
            return self.condition()
        #else:
            #print('nothing was done')

    def execute_all(self): # функция для выполнения всего
        current = self
        while hasattr(current, "next"):
            if current.type == Node.ACT:
                current.execute
                current = current.next
            elif current.type == Node.IF:
                if current.execute:
                    current.inside.execute_all()
                    if current.next.type == Node.ELSE:
                        if hasattr(current.next, "next"):
                            current = current.next.next
                    else:
                        current = current.next
                else:
                    current = current.next
                    if current.type == Node.ELSE:
                        current.inside.execute_all()
                        if hasattr(current, "next"):
                            current = current.next
            elif current.type == Node.WHILE:
                while current.execute:
                    current.inside.execute_all()
                current = current.next
            else:
                print("Ошибка: недопустимый тип узла -- " + Node.types[current.type])
        if current.type == Node.ACT:
            current.execute
        elif current.type == Node.IF:
            if current.execute:
                current.inside.execute_all()
        elif current.type == Node.WHILE:
            while current.execute:
                current.inside.execute_all()
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[current.type])
        return current

    def get_pattern_value(self, num, c):
        if    self.pattern[num] == Lexer.ELEM:
            if '[' in c[num]:
                return dict[c[num].split('[')[0]].value(c[num].split('[')[1].split(']')[0].strip())
            else:
                return dict[c[num]].value()
        elif  self.pattern[num] == Lexer.ELEM_SLICE:
            v = c[num].split('[')
            return dict[v[0]].slice_value(v[1][:-1].strip())
        elif  self.pattern[num] == Lexer.NUM:
            return int(c[num])


    def condition(self): # функция сравнения
        c = self.row.split() # строка, с которой работаем
        op1 = self.get_pattern_value(1, c) # значение первого операнда
        op2 = self.get_pattern_value(3, c) # значение второго операнда
        #print(op1 == op2)
        # проверка всех вариантов сравнений и возврат результата сравнения
        if   c[2] == '=':
            return op1 == op2
        elif c[2] == '>':
            return op1  > op2
        elif c[2] == '<':
            return op1  < op2
        elif c[2] == '!=':
            return op1 != op2
        elif c[2] == '>=':
            return op1 >= op2
        elif c[2] == '<=':
            return op1 <= op2
        else:
            return False


class classCounter: # счетчик

    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def __repr__(self):
        return self.count


def convert(string): # конвертер из str в int
    list=[0]*len(string)
    for i, l in enumerate(string):
        if l=="1":
            list[i]=1
    return list


def reset(i): # функция сброса всего
    #pointer_canvas.delete('pointer')
    pointer_canvas.delete(1.0, END) # очистка канваса
    txt.configure(state=NORMAL) # включает возможность редактирования текста в поле
    step_entry_btn.place_forget() # прячет кнопку
    step_detour_btn.place_forget() # прячет кнопку
    step_exit_btn.place_forget() # прячет кнопку
    reset_btn.place_forget() # прячет кнопку
    start_btn.place(x=20, y=7) # возвращает кнопку "старт"
    #rows = txt.get("1.0", END).splitlines()
    #c.coords('mark',335, 65, 350, 65)
    i.reset()
    for key in dict: # сбрасывает значения всех элементов путём вызова соответствующей функции в экземпляре каждого элемента
        dict[key].reset()
        #print(key)
    if mode == 1: # если открыта простая схема
        scheme_simple_display(scheme_canvas) # то перерисовать её (сбросить)
    elif mode == 2: # если открыта структурная схема
        scheme_struct_display(scheme_canvas) # то перерисовать её (сбросить)
    #drawer_default_scheme()
    #display(c)

root = Tk() # создание экземпляра Tkinter
root.geometry('480x900') #размер окна

def scheme_simple(): #
    return tk.Toplevel(root)
'''new_tk = scheme_simple()
c = Canvas(new_tk, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
c.delete('reg')'''

def scheme_struct(): #
    return tk.Toplevel(root)


def scheme_struct_display(c, file): # рисование структурной схемы по файлу
    c.delete('reg') # очистка окна перед рисованием (обновление)
    c.pack(side=LEFT) # помещение канваса в окне
    for row in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")): # открытие файла
        string = re.split (' ', row) # деление строки на куски
        name = re.split ('\(', string[0])[0] # выделение названия
        coords = re.split('\,', string[1]) # выделение координатов
        if 'Линия' in name: # если это линия
            #print('Линия')
            # выделение пары пар координат для начала и конца линии
            xa = re.findall(r'\d+', coords[0])
            ya = re.findall(r'\d+', coords[1])
            xb = re.findall(r'\d+', coords[2])
            yb = re.findall(r'\d+', coords[3])
            c.create_line(xa, ya, xb, yb, tag='reg') # рисование линии по заданным координатам
        elif 'Стрелка' in name: # если это стрелка
            #print('Стрелка')
            # выделение пары пар координат для начала и конца линии
            xa = re.findall(r'\d+', coords[0])
            ya = re.findall(r'\d+', coords[1])
            xb = re.findall(r'\d+', coords[2])
            yb = re.findall(r'\d+', coords[3])
            c.create_line(xa, ya, xb, yb, tag='reg', arrow=LAST) # рисование стрелки по координатам
        elif 'Инверсия' in name: # если это инверсия (пририсовывает кружок)
            size = 6
            x = int(re.findall(r'\d+', coords[0])[0])
            y = int(re.findall(r'\d+', coords[1])[0])
            c.create_oval(x-size/2, y-size/2, x+size/2, y+size/2, outline="#000", fill="#fff", width=2)
        else: # в остальных случаях -- это кооринаты элемента
            x = re.findall(r'\d+', coords[0])
            y = re.findall(r'\d+', coords[1])
            #print (x,y)
            if name in dict: # если элемент есть в словаре
                dict[name].display_struct(int(x[0]), int(y[0]), c, CANVAS_WIDTH) # вызов функции рисования элемента в структурной схеме


def scheme_simple_display(c): # автоматическое рисование упрощённой схемы
    c.delete('reg') # очистка окна перед рисованием (обновление)
    c.pack(side=LEFT) # помещение канваса в окне
    j = 0 # нужно для отступа по вертикали между элементами
    for i in dict: # перебор всех элементов словаря
        dict[i].display_simple(0, j, c, CANVAS_WIDTH) # вызов функции рисования элемента в простой схеме
        j += 20 # сдвиг по вертикали
#scheme_simple_display(scheme_simple())
#окно

def create_scheme_struct(): # создание поля для структурной схемы
    global scheme_canvas
    global mode
    global draw_file
    mode = 2 # режим окна рисования
    #elements = len(dict)
    draw_file = askopenfilename(filetypes=[("Text files", "*.txt")]) # запрос на открытие файла конфигурации
    print(draw_file)
    #print(fileinput.input(draw_file, openhook=fileinput.hook_encoded("utf-8"))[0])
    # размеры канваса по-умолчанию
    w = 450
    h = 350
    with open(draw_file, 'r', encoding="utf-8") as f:
        for row in f: # перебор строк файла конфигурации
            if 'Размер' in row: # если находит размеры
                arguments = row.split()[1].split(',') # делит на ширину и высоту
                # и присваивает новые значения окну
                w = int(re.findall(r'\d+', arguments[0])[0])
                h = int(re.findall(r'\d+', arguments[1])[0])
    new_tk = scheme_simple()
    scheme_canvas = Canvas(new_tk, width=w, height=h, bg='white') # канвас для схем
    scheme_struct_display(scheme_canvas, draw_file) # открытие окна и запрос файла конфигурации

def create_scheme_simple(): # создание поля для простой схемы
    new_tk = scheme_simple()
    global scheme_canvas
    global mode
    mode = 1 # режим окна рисования
    w = 1
    for d in dict:
        if type(dict[d]).__name__ == 'Register':
            if len(dict[d].data) > w:
                w = len(dict[d].data)
    w *= 6
    w += 100
    h = len(dict)*20+30
    scheme_canvas = Canvas(new_tk, width=w, height=h, bg='white')
    scheme_simple_display(scheme_canvas)


#with open('test2.txt','r',encoding='utf-8') as f:
#    start = Node.parse(list(f))
#    start.display()

#анализ элементной базы
#ARCH = 'elements.txt'
ARCH = 'sub_m32_imm8.arch.txt' # выбор файла элементной базы
f = open(ARCH,'r',encoding='utf-8') # открытие файла
for row in f: # перебор всех строк
    if   'Регистр'  in row: # если регистр, то делим на
        string     = re.split (' ', row)
        name       = re.split ('\(', string[1])[0] # название
        capacity   = re.findall(r'\d+', string[1]) # значение
        dict[name] = Register(int(capacity[0]), name) # создаём элемент в регистре с таким названием и значением
    elif 'Сумматор' in row:
        string     = re.split (' ', row)
        name       = re.split ('\(', string[1])[0]
        capacity   = re.findall(r'\d+', string[1])
        dict[name] = Adder(int(capacity[0]), name)
    elif 'Счётчик' in row:
        string     = re.split (' ', row)
        name       = re.split ('\(', string[1])[0]
        capacity   = re.findall(r'\d+', string[1])
        if capacity:
            dict[name] = Counter(name, int(capacity[0]))
        else:
            dict[name] = Counter(name)
f.close()


cc = classCounter() # счётчик

def add_pointer(num, length): # добавление маркера
    return str(num)+' '*(length-len(str(num))-2)+'⯈'

def start(): # функция старта (кнопки "старт")
    txt.configure(state=DISABLED) # запрет на редактирование кода в поле
    start_btn.place_forget() # прячет кнопку
    # размещает кнопки
    step_entry_btn.place(x=20, y=7)
    step_detour_btn.place(x=60, y=7)
    step_exit_btn.place(x=100, y=7)
    reset_btn.place(x=170, y=7)
    #global pointer
    #pointer = pointer_canvas.create_line(0, ROWHEIGHT / 2 + 2, 10, ROWHEIGHT / 2 + 2, arrow=LAST, tag='pointer')
    global currentnode
    rows = txt.get("1.0", END).splitlines() # создаёт массив строк кода из поля (не из файла)
    size = len(rows) # количество строк
    currentnode = Node.parse(rows) # текущий узел
    currentnode.display()
    #print(size)
    pointer_canvas.insert(END, '1  ⯈\n') # вставка маркера
    for i in range(size-2): # нумирование строк
        #pointer_canvas.insert(END, '⯈\n')
        pointer_canvas.insert(END, str(i+2)+'\n')
    pointer_canvas.insert(END, str(size))


def step_inside(e):
    global currentnode
    currentnode = currentnode.step_inside()
    if currentnode:
        pointer_canvas.delete(1.0, END)
        p=''
        for i in range(currentnode.rownum):
            p += str(i+1)+'\n'
        p += add_pointer(currentnode.rownum+1, 5) + '\n'
        for i in range(currentnode.rownum+1, len(txt.get("1.0", END).splitlines())):
            p += str(i+1)+'\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        #pointer_canvas.delete('pointer')
        reset(cc)


def step_outside(e):
    global currentnode
    currentnode = currentnode.step_outside()
    if currentnode:
        pointer_canvas.delete(1.0, END)
        p=''
        for i in range(currentnode.rownum):
            p += str(i+1)+'\n'
        p += add_pointer(currentnode.rownum+1, 5) + '\n'
        for i in range(currentnode.rownum+1, len(txt.get("1.0", END).splitlines())):
            p += str(i+1)+'\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        #pointer_canvas.delete('pointer')
        reset(cc)


def step_bypass(e):
    global currentnode
    currentnode = currentnode.step()
    if currentnode:
        pointer_canvas.delete(1.0, END)
        p=''
        for i in range(currentnode.rownum):
            p += str(i+1)+'\n'
        p += add_pointer(currentnode.rownum+1, 5) + '\n'
        for i in range(currentnode.rownum+1, len(txt.get("1.0", END).splitlines())):
            p += str(i+1)+'\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        #pointer_canvas.delete('pointer')
        reset(cc)



def open_file(): # открытие файла
    global rows
    global size
    txt.delete(1.0, END) # очистка поля
    file=askopenfilename(filetypes=[("Text files", "*.txt")]) # выбор файла
    for i in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")): # перенос содержимого файла в поле
        txt.insert(END, i)
    size = sum(1 for line in open(file, 'r')) # подсчёт количества строк
    #rows = [line.rstrip('\n') for line in open(file, 'r', encoding='utf-8')]
    rows = txt.get("1.0", END).splitlines() # получение массива строк
    print(file)
    #drawer_default_scheme()

#рисование схемы с очисткой канваса
#def drawer_default_scheme():



def save_as_file(): # сохранить как
    file=asksaveasfile(mode='w', filetypes=[("Text files", "*.txt")], defaultextension=".txt") # сохранить как и куда
    if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    print(file)
    text2save = str(txt.get(1.0, END)) # кидает в переменную всё из поля
    file.write(text2save) # записывает
    file.close() # закрывает файл

# настройки верхнего меню
mainmenu = Menu(root)
root.config(menu=mainmenu)
filemenu = Menu(mainmenu, tearoff=0)
schememenu = Menu(mainmenu, tearoff=0)
mainmenu.add_cascade(label="Файл", menu=filemenu)
filemenu.add_command(label="Открыть...", command=open_file)
#filemenu.add_command(label="Сохранить...", command=save_file)
filemenu.add_command(label="Сохранить как...", command=save_as_file)
mainmenu.add_cascade(label="Схема", menu=schememenu)
schememenu.add_command(label="Структурная схема", command=create_scheme_struct)
schememenu.add_command(label="Упрощённая схема", command=create_scheme_simple)

# картинки кнопок
step_entry_btn_icon  = PhotoImage(file='media/2.png')
step_detour_btn_icon = PhotoImage(file='media/3.png')
step_exit_btn_icon   = PhotoImage(file='media/1.png')
reset_btn_icon       = PhotoImage(file='media/4.png')
start_btn_icon       = PhotoImage(file='media/5.png')

# размеры кнопок
step_entry_btn  = Button(width="20",height="20", image=step_entry_btn_icon)
step_detour_btn = Button(width="20",height="20", image=step_detour_btn_icon)
step_exit_btn   = Button(width="20",height="20", image=step_exit_btn_icon)
reset_btn       = Button(width="20",height="20", image=reset_btn_icon)
start_btn       = Button(width="20",height="20", image=start_btn_icon)

# функционал кнопок
#step_entry_btn .bind('<Button-1>', lambda e, f="Verdana": step(e, rows, cc))
step_entry_btn .bind('<Button-1>', step_bypass)
step_detour_btn.bind('<Button-1>', step_inside)
step_exit_btn  .bind('<Button-1>', step_outside)
reset_btn.bind('<Button-1>', lambda e, f="Verdana": reset(cc))
start_btn.bind('<Button-1>', lambda e, f="Verdana": start())

# размещение кнопок
step_entry_btn .place_forget  #(x=20, y=7)
step_detour_btn.place_forget  #(x=60, y=7)
step_exit_btn  .place_forget  #(x=100, y=7)
reset_btn      .place_forget  #(x=170, y=7)
start_btn      .place(x=20, y=7)

# конфигурация текстового поля
ROWHEIGHT = 18 # количество строк
mainframe = Frame(root)
scroll = Scrollbar(mainframe)
pointer_canvas = Text(mainframe, width=5, height=35, bg='white',spacing1=2, yscrollcommand=scroll.set) # метка
txt = Text(mainframe, width=45, height=35, font="14", bg='white', yscrollcommand=scroll.set) # текст поля
#pointer_canvas.create_line(0,ROWHEIGHT/2+2,10,ROWHEIGHT/2+2, arrow=LAST, tag='pointer')

def OnMouseWheel(event): #
    pointer_canvas.yview("scroll", event.delta, "units")
    txt.yview("scroll", event.delta, "units")
    return "break"

pointer_canvas.bind("<MouseWheel>", OnMouseWheel)
txt.bind("<MouseWheel>", OnMouseWheel)

def onScroll(*args): #
    pointer_canvas.yview(*args)
    txt.yview(*args)

scroll.config(command=onScroll)

pointer_canvas.pack(side=LEFT)
mainframe.pack(side=LEFT)
#txt.pack(side=LEFT, padx=0, pady=10)
txt.pack(side=LEFT)
scroll.pack(side=LEFT, fill=Y)
#txt.config(yscrollcommand=scroll.set)

root.mainloop()