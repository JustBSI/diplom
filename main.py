import re
from config import *
from tkinter.filedialog import *
import fileinput
from elements import *
import tkinter as tk


dict = {} #словарь с элементами
class Lexer:

    words = ['ASSIG', 'ELEM', 'ADD', 'NUM', 'IF', 'ELSE', 'WHILE', 'EQU', 'MORE', 'LESS', 'NOT_EQU', 'MORE_EQU', 'LESS_EQU']
    ASSIG, ELEM, ADD, NUM, IF, ELSE, WHILE, EQU, MORE, LESS, NOT_EQU, MORE_EQU, LESS_EQU = range(13)
    symbols = {':=': ASSIG, '+': ADD, '=': EQU, '>': MORE, '<': LESS, '!=': NOT_EQU, '>=': MORE_EQU, '<=': LESS_EQU}
    keywords = {'если': IF, 'иначе': ELSE, 'пока': WHILE}

    @classmethod
    def parse(self, row):
        str = row.split()
        result = []
        for word in str:
            if   word in dict.keys():
                result.append(self.ELEM)
            elif word in self.keywords.keys():
                result.append(self.keywords[word])
            elif word in self.symbols.keys():
                result.append(self.symbols[word])
            elif len(word.replace('0', '').replace('1', '')) == 0:
                result.append(self.NUM)
        return result


class Node:

    # типы узлов
    types = ['ACT', 'IF', 'ELSE', 'WHILE']
    ACT, IF, ELSE, WHILE = range(4)

    def __init__(self, row=None, out=None, rownum=None): #type=None):
        if row:
            self.raw     = row
            self.pattern = Lexer.parse(row)
            if Lexer.IF in self.pattern:
                self.type = Node.IF
            elif Lexer.ELSE in self.pattern:
                self.type = Node.ELSE
            elif Lexer.WHILE in self.pattern:
                self.type = Node.WHILE
            else:
                self.type = Node.ACT
        if out:
            self.out = out
        if rownum:
            self.rownum = rownum
        #if type:
            #self.type = type

    @staticmethod
    def parse(rows, out=None, bias=0):

        current = Node()
        first = current
        i = 0
        #while ("" in rows):
            #rows.remove("")
        while i < len(rows):
            if not rows[i].strip():
                i += 1
            elif rows[i][0:4]!="    ":
                current.next = Node(rows[i][:-1], out, bias+i)
                current = current.next
                current.rownum = bias+i
                i += 1
            else:
                inside_rows = []
                while i<len(rows) and rows[i][0:4]=="    ":
                    inside_rows.append(rows[i][4:])
                    i += 1
                current.inside = Node.parse(inside_rows, current, i-len(inside_rows)+bias)

        return first.next

    def step(self):
        if self.type == Node.ACT:
            self.execute()
            return self.find_next()
        elif self.type == Node.IF:
            if self.execute():
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
            while self.execute():
                self.inside.execute_all()
            return self.find_next()
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None

    def step_inside(self):
        if self.type == Node.ACT:
            self.execute()
            return self.find_next()
        elif self.type == Node.IF:
            if self.execute():
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
            if self.execute():
                return self.inside
            else:
                return self.find_next()
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None


    def step_outside(self):
        last = self.execute_all()
        current = last.find_out()
        if current.type==Node.WHILE and last.out is current:
            while current.execute():
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


    def display(self, indent=0):
        try:
            print(str(self.rownum)+' '+'| '*indent+Node.types[self.type]+' '+self.raw+' '+str(self.pattern)+' '+str(hasattr(self, "next")))
        except Exception:
            print('strange node')
        if hasattr(self, "inside"):
            self.inside.display(indent+1)
        if hasattr(self, "next"):
            self.next.display(indent)

    # исполнение
    def execute(self):
        c = self.raw.split()
        if   self.pattern == [1, 0, 3]:
            dict[c[0]].set(convert(c[2]))
        elif self.pattern == [1, 0, 1]:
            dict[c[0]].set(dict[c[2]].data)
        elif self.pattern == [1, 0, 1, 2, 1]:
            dict[c[0]].set(dict['СМ'].add(dict[c[2]].data, dict[c[4]].data, 0)[0])
        elif self.pattern[0] == Lexer.IF:
            return self.condition()
        elif self.pattern[0] == Lexer.WHILE:
            return self.condition()

    def execute_all(self):
        current = self
        while hasattr(current, "next"):
            if current.type == Node.ACT:
                current.execute()
                current = current.next
            elif current.type == Node.IF:
                if current.execute():
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
                while current.execute():
                    current.inside.execute_all()
                current = current.next
            else:
                print("Ошибка: недопустимый тип узла -- " + Node.types[current.type])
        if current.type == Node.ACT:
            current.execute()
        elif current.type == Node.IF:
            if current.execute():
                current.inside.execute_all()
        elif current.type == Node.WHILE:
            while current.execute():
                current.inside.execute_all()
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[current.type])
        return current


    def condition(self):
        c = self.raw.split()
        if    self.pattern[1] == Lexer.ELEM:
            op1 = dict[c[1]].count
        elif  self.pattern[1] == Lexer.NUM:
            op1 = int(c[1])
        if    self.pattern[3] == Lexer.ELEM:
            op2 = dict[c[3]].count
        elif  self.pattern[3] == Lexer.NUM:
            op2 = int(c[3])
        if   c[2] == Lexer.EQU:
            return op1 == op2
        elif c[2] == Lexer.MORE:
            return op1  > op2
        elif c[2] == Lexer.LESS:
            return op1  < op2
        elif c[2] == Lexer.NOT_EQU:
            return op1 != op2
        elif c[2] == Lexer.MORE_EQU:
            return op1 >= op2
        elif c[2] == Lexer.LESS_EQU:
            return op1 <= op2
        else:
            return False

#счетчик
class classCounter:

    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def __repr__(self):
        return self.count

#конвертер
def convert(str):
    list=[0]*len(str)
    for i, l in enumerate(str):
        if l=="1":
            list[i]=1
    return list

#исполнение строки
def execute(row):
    b = Lexer.parse(row)
    c = row.split()
    if b==[1,0,3]:
        dict[c[0]].set(convert(c[2]))
    elif b==[1,0,1]:
        dict[c[0]].set(dict[c[2]].data)
    elif b==[1,0,1,2,1]:
        dict[c[0]].set(dict['СМ'].add(dict[c[2]].data, dict[c[4]].data, 0)[0])
    #print("we do exec"+row)

# def display(c):
#     dict['РгВх'].display(0, 60, c, CANVAS_WIDTH)
#     dict['РгА'].display(-80, 140, c, CANVAS_WIDTH)
#     dict['РгБ'].display(80, 140, c, CANVAS_WIDTH)
#     dict['СМ'].display(0, 220, c, CANVAS_WIDTH)
#     dict['РгСМ'].display(0, 300, c, CANVAS_WIDTH)

#шаг
def step(e, rows, i):
    rows = txt.get("1.0", END).splitlines()
    if i.count<size:
        #c.move('mark', 0,18)
        execute(rows[i.count])
        i.inc()
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas)
        #drawer_default_scheme()
        #display(c)

#сброс
def reset(i):
    #rows = txt.get("1.0", END).splitlines()
    #c.coords('mark',335, 65, 350, 65)
    i.reset()
    for key in dict:
        dict[key].reset()
        #print(key)
    if mode == 1:
        scheme_simple_display(scheme_canvas)
    elif mode == 2:
        scheme_struct_display(scheme_canvas)
    #drawer_default_scheme()
    #display(c)

root = Tk()
root.geometry('350x430') #размер окна
#вызов окна упрощённой схемы
def scheme_simple():
    return tk.Toplevel(root)
'''new_tk = scheme_simple()
c = Canvas(new_tk, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
c.delete('reg')'''

def scheme_struct():
    return tk.Toplevel(root)

def scheme_struct_display(c):
    c.delete('reg')
    c.pack(side=LEFT)
    file = askopenfilename(filetypes=[("Text files", "*.txt")])
    for row in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")):
        str = re.split (' ', row)
        name = re.split ('\(', str[0])[0]
        coords = re.split('\,', str[1])
        if 'Линия' in name:
            print('Линия')
            xa = re.findall(r'\d+', coords[0])
            ya = re.findall(r'\d+', coords[1])
            xb = re.findall(r'\d+', coords[2])
            yb = re.findall(r'\d+', coords[3])
            c.create_line(xa, ya, xb, yb, tag='reg')
        elif 'Стрелка' in name:
            print('Стрелка')
            xa = re.findall(r'\d+', coords[0])
            ya = re.findall(r'\d+', coords[1])
            xb = re.findall(r'\d+', coords[2])
            yb = re.findall(r'\d+', coords[3])
            c.create_line(xa, ya, xb, yb, tag='reg', arrow=LAST)
        else:
            x = re.findall(r'\d+', coords[0])
            y = re.findall(r'\d+', coords[1])
            print (x,y)
            if name in dict:
                dict[name].display_struct(int(x[0]), int(y[0]), c, CANVAS_WIDTH)

def scheme_simple_display(c):
    c.delete('reg')
    c.pack(side=LEFT)
    j = 0
    for i in dict:
        dict[i].display_simple(0, j, c, CANVAS_WIDTH)
        j += 20
#scheme_simple_display(scheme_simple())
#окно

def create_scheme_struct():
    new_tk = scheme_simple()
    global scheme_canvas
    global mode
    mode = 2
    #elements = len(dict)
    scheme_canvas = Canvas(new_tk, width=350, height=350, bg='white')
    scheme_struct_display(scheme_canvas)

def create_scheme_simple():
    new_tk = scheme_simple()
    global scheme_canvas
    global mode
    mode = 1
    elements = len(dict)
    scheme_canvas = Canvas(new_tk, width=150, height=elements*20, bg='white')
    scheme_simple_display(scheme_canvas)


with open('test2.txt','r',encoding='utf-8') as f:
    start = Node.parse(list(f))
    start.display()

#анализ элементной базы
f = open('elements.txt','r',encoding='utf-8')
for row in f:
    if   'Регистр'  in row:
        str        = re.split (' ', row)
        name       = re.split ('\(', str[1])[0]
        capacity   = re.findall(r'\d+', str[1])
        dict[name] = Register(int(capacity[0]), name)
    elif 'Сумматор' in row:
        str        = re.split (' ', row)
        name       = re.split ('\(', str[1])[0]
        capacity   = re.findall(r'\d+', str[1])
        dict[name] = Adder(int(capacity[0]), name)
f.close()

#рисование схемы со стрелочками и блоками
# c = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
# c.pack(side=LEFT)
# c.create_text((CANVAS_WIDTH/2)   ,  15, text='Шина', anchor=CENTER)
# c.create_line((CANVAS_WIDTH/2)   ,  30, (CANVAS_WIDTH/2)   ,  55, arrow=LAST)
# c.create_line((CANVAS_WIDTH/2)   , 105, (CANVAS_WIDTH/2)   , 120            )
# c.create_line((CANVAS_WIDTH/2)-80, 120, (CANVAS_WIDTH/2)+80, 120            )
# c.create_line((CANVAS_WIDTH/2)-80, 120, (CANVAS_WIDTH/2)-80, 140, arrow=LAST)
# c.create_line((CANVAS_WIDTH/2)+80, 120, (CANVAS_WIDTH/2)+80, 140, arrow=LAST)
# c.create_line((CANVAS_WIDTH/2)-80, 185, (CANVAS_WIDTH/2)-80, 210            )
# c.create_line((CANVAS_WIDTH/2)-80, 210, (CANVAS_WIDTH/2)-35, 210            )
# c.create_line((CANVAS_WIDTH/2)-35, 210, (CANVAS_WIDTH/2)-35, 235, arrow=LAST)
# c.create_line((CANVAS_WIDTH/2)+80, 185, (CANVAS_WIDTH/2)+80, 210            )
# c.create_line((CANVAS_WIDTH/2)+80, 210, (CANVAS_WIDTH/2)+35, 210            )
# c.create_line((CANVAS_WIDTH/2)+35, 210, (CANVAS_WIDTH/2)+35, 235, arrow=LAST)
# c.create_line((CANVAS_WIDTH/2)   , 270, (CANVAS_WIDTH/2)   , 300, arrow=LAST)
# c.create_line(335, 65, 350, 65, arrow=LAST, tag='mark')
# display(c)


cc = classCounter() #счётчик

#открытие файла, разбиение его на массив строк и рисование схемы
def open_file():
    global rows
    global size
    txt.delete(1.0, END)
    file=askopenfilename(filetypes=[("Text files", "*.txt")])
    for i in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")):
        txt.insert(END, i)
    size = sum(1 for line in open(file, 'r'))
    #rows = [line.rstrip('\n') for line in open(file, 'r', encoding='utf-8')]
    rows = txt.get("1.0", END).splitlines()
    print(file)
    #drawer_default_scheme()

#рисование схемы с очисткой канваса
#def drawer_default_scheme():


#сохранить как
def save_as_file():
    file=asksaveasfile(mode='w', filetypes=[("Text files", "*.txt")], defaultextension=".txt")
    if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    print(file)
    text2save = str(txt.get(1.0, END))
    file.write(text2save)
    file.close()

#верхнее меню
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

#картинки кнопок
step_entry_btn_icon  = PhotoImage(file='media/2.png')
step_detour_btn_icon = PhotoImage(file='media/3.png')
step_exit_btn_icon   = PhotoImage(file='media/1.png')
reset_btn_icon       = PhotoImage(file='media/4.png')

#размеры кнопок
step_entry_btn  = Button(width="20",height="20", image=step_entry_btn_icon)
step_detour_btn = Button(width="20",height="20", image=step_detour_btn_icon)
step_exit_btn   = Button(width="20",height="20", image=step_exit_btn_icon)
reset_btn       = Button(width="20",height="20", image=reset_btn_icon)

#функционал кнопок
step_entry_btn.bind('<Button-1>', lambda e, f="Verdana": step(e, rows, cc))
reset_btn.bind('<Button-1>', lambda e, f="Verdana": reset(cc))

#размещение кнопок
step_entry_btn .place(x=20, y=7)
step_detour_btn.place(x=60, y=7)
step_exit_btn  .place(x=100, y=7)
reset_btn      .place(x=170, y=7)

#конфиги текстового поля
mainframe = Frame(root)
txt = Text(mainframe, width=35, height=19, font="14", bg='white')
scroll = Scrollbar(mainframe, command=txt.yview)
poiner_canvas = Canvas(root, width=10, height=18*19, bg='white')

poiner_canvas.pack(side=LEFT)
mainframe.pack(side=LEFT)
#txt.pack(side=LEFT, padx=0, pady=10)
txt.pack(side=LEFT)
scroll.pack(side=LEFT, fill=Y)
txt.config(yscrollcommand=scroll.set)

root.mainloop()