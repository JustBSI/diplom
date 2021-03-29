import re
from config import *
from tkinter.filedialog import *
import fileinput
from elements import *
import tkinter as tk


dict = {} #словарь с элементами
class Lexer:

    words = ['ASSIG', 'ELEM', 'ADD', 'NUM', 'IF', 'ELSE', 'WHILE', 'EQU', 'MORE', 'LESS', 'NOT_EQU', 'MORE_EQU', 'LESS_EQU']
    ASSIG, ELEM, ADD, NUM, IF, ELSE, WHILE, EQU, MORE, LESS, NOT_EQU, MORE_EQU, LESS_EQU, ELEM_SLICE, RIGHT_SHIFT, LEFT_SHIFT = range(16)
    symbols = {':=': ASSIG, '+': ADD, '=': EQU, '>': MORE, '<': LESS, '!=': NOT_EQU, '>=': MORE_EQU, '<=': LESS_EQU, '>>': RIGHT_SHIFT, '<<': LEFT_SHIFT}
    keywords = {'если': IF, 'иначе': ELSE, 'пока': WHILE}

    @classmethod
    def is_elem(cls, word):
        w = word
        if w[0] == '-':
            w = w[1:]
        if '[' in w:
            w = w.split('[')[0]
        return w in dict.keys()


    @classmethod
    def parse(self, row):
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
        while i < len(rows):
            if not rows[i].strip():
                i += 1
            elif rows[i][0:4]!="    ":
                current.next = Node(rows[i], out, bias+i)
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
            self.execute
            return self.find_next()
        elif self.type == Node.IF:
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

    def step_inside(self):
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


    def step_outside(self):
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


    def display(self, indent=0):
        ans = ''
        try:
            print(str(self.rownum)+' '+'| '*indent+Node.types[self.type]+' '+self.raw+' '+str(self.pattern)+' '+str(hasattr(self, "next")))
        #print(str(self.rownum))
        except Exception as e:
            #print(e)
            print('strange node')
        if hasattr(self, "inside"):
            self.inside.display(indent+1)
        if hasattr(self, "next"):
            self.next.display(indent)

    @staticmethod
    def pure_name(word):
        res = word.strip()
        if res[0] == '-':
            res = res[1:]
        if '[' in res:
            res = res.split('[')[0]
        return res

    @staticmethod
    def pure_slice(word):
        if '[' in word:
            #s = word.split('[')[1].split(']')[0].strip()
            #ss = s.split(':')
            #return int(ss[0]), int(ss[1]), s
            return word.split('[')[1].split(']')[0].strip()
        return None


    @staticmethod
    def set_elem(elem, val):
        if '[' in elem:
            #f, t, s = Node.pure_slice(elem)
            dict[Node.pure_name(elem)].set(val, Node.pure_slice(elem))
        else:
            dict[Node.pure_name(elem)].set(val)


    @staticmethod
    def get_elem(elem):
        if '[' in elem:
            #f, t, s = Node.pure_slice(elem)
            return dict[Node.pure_name(elem)].get(slice=Node.pure_slice(elem), inv=elem[0]=='-')
        else:
            return dict[Node.pure_name(elem)].get(inv=elem[0]=='-')


    # исполнение
    @property
    def execute(self):
        c = self.raw.split()
        p = self.pattern
        if p[1] == 0: # если это инструкция присвоения :=
            if p[0] == 1: # если слева элемент
                if   len(p) == 3:
                    if   p[2] == 3: # если справа значение
                        #dict[c[0]].set(c[2])
                        Node.set_elem(c[0], c[2])
                    elif p[2] == 1: # если справа элемент
                        #dict[c[0]].set(dict[c[2]].data)
                        Node.set_elem(c[0], Node.get_elem(c[2]))
                elif len(p) == 5:
                    if p[3] == 2: # если справа сложение
                        if p[2] == 1: # если первый операнд элемент
                            if p[4] == 1: # если второй операнд элемент
                                dict[c[0]].set(dict['СМ'].add(dict[c[2]].data, dict[c[4]].data, 0)[0])
                            elif p[4] == 3: # если второй операнд значение
                                if type(dict[c[2]]).__name__ == 'Counter': # если второй операнд счётчик
                                    dict[c[2]].count += int(c[4])
                    elif p[3] == 14: # если справа
                        if type(dict[c[2]]).__name__ == 'Register':
                            new_data = [0]+dict[c[2]].data[:-1]
                            for i in range(len(new_data)):
                                dict[c[0]].data[i] = new_data[i]
                    elif p[3] == 15: # если справа
                        if type(dict[c[2]]).__name__ == 'Register':
                            new_data = dict[c[2]].data[1:]
                            new_data.append(0)
                            for i in range(len(new_data)):
                                dict[c[0]].data[i] = new_data[i]
                elif len(p) == 7:
                    #print(dict[c[2]]).data
                    dict[c[0]].set(dict['СМ'].add(dict[c[2]].data, dict[c[4]].data, 1)[0])
        elif p[0] == Lexer.IF:
            return self.condition()
        elif p[0] == Lexer.WHILE:
            return self.condition()
        #else:
            #print('nothing was done')

    def execute_all(self):
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


    def condition(self):
        c = self.raw.split()
        op1 = self.get_pattern_value(1, c)
        op2 = self.get_pattern_value(3, c)
        #print(op1 == op2)
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
def convert(string):
    list=[0]*len(string)
    for i, l in enumerate(string):
        if l=="1":
            list[i]=1
    return list

#сброс
def reset(i):
    #pointer_canvas.delete('pointer')
    pointer_canvas.delete(1.0, END)
    txt.configure(state=NORMAL)
    step_entry_btn.place_forget()
    step_detour_btn.place_forget()
    step_exit_btn.place_forget()
    reset_btn.place_forget()
    start_btn.place(x=20, y=7)
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
root.geometry('480x900') #размер окна
#вызов окна упрощённой схемы
def scheme_simple():
    return tk.Toplevel(root)
'''new_tk = scheme_simple()
c = Canvas(new_tk, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
c.delete('reg')'''

def scheme_struct():
    return tk.Toplevel(root)

#рисование схемы по файлу
def scheme_struct_display(c):
    c.delete('reg')
    c.pack(side=LEFT)
    file = askopenfilename(filetypes=[("Text files", "*.txt")])
    for row in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")):
        string = re.split (' ', row)
        name = re.split ('\(', string[0])[0]
        coords = re.split('\,', string[1])
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

#автоматическое рисование упрощённой схемы
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
ARCH = 'sub_m32_imm8.arch.txt'
f = open(ARCH,'r',encoding='utf-8')
for row in f:
    if   'Регистр'  in row:
        string     = re.split (' ', row)
        name       = re.split ('\(', string[1])[0]
        capacity   = re.findall(r'\d+', string[1])
        dict[name] = Register(int(capacity[0]), name)
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


cc = classCounter() #счётчик

def add_pointer(num, length):
    return str(num)+' '*(length-len(str(num))-2)+'⯈'

def start():
    txt.configure(state=DISABLED)
    start_btn.place_forget()
    step_entry_btn.place(x=20, y=7)
    step_detour_btn.place(x=60, y=7)
    step_exit_btn.place(x=100, y=7)
    reset_btn.place(x=170, y=7)
    #global pointer
    #pointer = pointer_canvas.create_line(0, ROWHEIGHT / 2 + 2, 10, ROWHEIGHT / 2 + 2, arrow=LAST, tag='pointer')
    global currentnode
    rows = txt.get("1.0", END).splitlines()
    size = len(rows)
    currentnode = Node.parse(rows)
    currentnode.display()
    #print(size)
    pointer_canvas.insert(END, '1  ⯈\n')
    for i in range(size-2):
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
            scheme_struct_display(scheme_canvas)
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
            scheme_struct_display(scheme_canvas)
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
            scheme_struct_display(scheme_canvas)
    else:
        #pointer_canvas.delete('pointer')
        reset(cc)


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
start_btn_icon       = PhotoImage(file='media/5.png')

#размеры кнопок
step_entry_btn  = Button(width="20",height="20", image=step_entry_btn_icon)
step_detour_btn = Button(width="20",height="20", image=step_detour_btn_icon)
step_exit_btn   = Button(width="20",height="20", image=step_exit_btn_icon)
reset_btn       = Button(width="20",height="20", image=reset_btn_icon)
start_btn       = Button(width="20",height="20", image=start_btn_icon)

#функционал кнопок
#step_entry_btn .bind('<Button-1>', lambda e, f="Verdana": step(e, rows, cc))
step_entry_btn .bind('<Button-1>', step_bypass)
step_detour_btn.bind('<Button-1>', step_inside)
step_exit_btn  .bind('<Button-1>', step_outside)
reset_btn.bind('<Button-1>', lambda e, f="Verdana": reset(cc))
start_btn.bind('<Button-1>', lambda e, f="Verdana": start())

#размещение кнопок
step_entry_btn .place_forget  #(x=20, y=7)
step_detour_btn.place_forget  #(x=60, y=7)
step_exit_btn  .place_forget  #(x=100, y=7)
reset_btn      .place_forget  #(x=170, y=7)
start_btn      .place(x=20, y=7)

#конфиги текстового поля
ROWHEIGHT = 18
mainframe = Frame(root)
scroll = Scrollbar(mainframe)
pointer_canvas = Text(mainframe, width=5, height=45, bg='white',spacing1=2, yscrollcommand=scroll.set)
txt = Text(mainframe, width=45, height=45, font="14", bg='white', yscrollcommand=scroll.set)
#pointer_canvas.create_line(0,ROWHEIGHT/2+2,10,ROWHEIGHT/2+2, arrow=LAST, tag='pointer')

def OnMouseWheel(event):
    pointer_canvas.yview("scroll", event.delta, "units")
    txt.yview("scroll", event.delta, "units")
    return "break"

pointer_canvas.bind("<MouseWheel>", OnMouseWheel)
txt.bind("<MouseWheel>", OnMouseWheel)

def onScroll(*args):
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