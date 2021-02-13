import re
from config import *
from tkinter.filedialog import *
import fileinput
from elements import *


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
    types = ['START', 'ACT', 'IF', 'ELSE', 'WHILE', 'END']
    ACT, IF, ELSE, WHILE = range(4)

    def __init__(self, row=None, out=None, type=None):
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
        if type:
            self.type = type

    @staticmethod
    def parse(rows, out=None):

        current = Node()
        first = current
        i = 0
        while ("" in rows):
            rows.remove("")
        while i < len(rows):
            if rows[i][0:4]!="    ":
                current.next = Node(rows[i][:-1], out)
                current = current.next
                i += 1
            else:
                inside_rows = []
                while i<len(rows) and rows[i][0:4]=="    ":
                    inside_rows.append(rows[i][4:])
                    i += 1
                current.inside = Node.parse(inside_rows, current)

        return first.next

    def step(self):
        if self.type == Node.ACT:
            self.execute()
            if hasattr(self, "next"):
                return self.next
            else:
                return None
        elif self.type == Node.IF:
            if self.execute():
                self.inside.execute_all()
                if hasattr(self, "next"):
                    if self.next.type == Node.ELSE:
                        if hasattr(self.next, "next"):
                            return self.next.next
                        else:
                            return None
                    else:
                        return self.next
                else:
                    return None
            else:
                if hasattr(self, "next"):
                    if self.next.type == Node.ELSE:
                        self.next.inside.execute_all()
                        if hasattr(self.next, "next"):
                            return self.next.next
                        else:
                            return None
                    else:
                        return self.next
                else:
                    return None
        elif self.type == Node.WHILE:
            while self.execute():
                self.inside.execute_all()
            if hasattr(self, "next"):
                return self.next
            else:
                return None
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None



    def display(self, indent=0):
        try:
            print('| '*indent+Node.types[self.type]+' '+self.raw+' '+str(self.pattern)+' '+str(hasattr(self, "next")))
        except Exception:
            print('strange node')
        if hasattr(self, "inside"):
            self.inside.display(indent+1)
        if hasattr(self, "next"):
            self.next.display(indent)

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



class classCounter:

    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def __repr__(self):
        return self.count


def convert(str):
    list=[0]*len(str)
    for i, l in enumerate(str):
        if l=="1":
            list[i]=1
    return list


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


def display(c):
    dict['РгВх'].display(0, 60, c, CANVAS_WIDTH)
    dict['РгА'].display(-80, 140, c, CANVAS_WIDTH)
    dict['РгБ'].display(80, 140, c, CANVAS_WIDTH)
    dict['СМ'].display(0, 220, c, CANVAS_WIDTH)
    dict['РгСМ'].display(0, 300, c, CANVAS_WIDTH)


def step(e, rows, i):
    if i.count<size:
        c.move('mark', 0,18)
        execute(rows[i.count])
        i.inc()
        display(c)


def reset(i):
    c.coords('mark',335, 65, 350, 65)
    i.reset()
    for key in dict:
        dict[key].reset()
        #print(key)
    display(c)


root = Tk()

dict = {}


with open('test2.txt','r',encoding='utf-8') as f:
    start = Node.parse(list(f))
    start.display()


#анализ элементной базы
f = open('elements.txt','r',encoding='utf-8')
for row in f:
    if   'Регистр'  in row:
        str        = re.split (' ', row)
        name       = re.split ('\(', str[1])[0]
        capacity   = re.search('\d', (re.split('\(', str[1])[1]))
        dict[name] = Register(int(capacity.group(0)), name)
    elif 'Сумматор' in row:
        str        = re.split (' ', row)
        name       = re.split ('\(', str[1])[0]
        capacity   = re.search('\d', (re.split('\(', str[1])[1]))
        dict[name] = Adder(int(capacity.group(0)), name)
f.close()


c = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
c.pack(side=LEFT)
c.create_text((CANVAS_WIDTH/2)   ,  15, text='Шина', anchor=CENTER)
c.create_line((CANVAS_WIDTH/2)   ,  30, (CANVAS_WIDTH/2)   ,  55, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)   , 105, (CANVAS_WIDTH/2)   , 120            )
c.create_line((CANVAS_WIDTH/2)-80, 120, (CANVAS_WIDTH/2)+80, 120            )
c.create_line((CANVAS_WIDTH/2)-80, 120, (CANVAS_WIDTH/2)-80, 140, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)+80, 120, (CANVAS_WIDTH/2)+80, 140, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)-80, 185, (CANVAS_WIDTH/2)-80, 210            )
c.create_line((CANVAS_WIDTH/2)-80, 210, (CANVAS_WIDTH/2)-35, 210            )
c.create_line((CANVAS_WIDTH/2)-35, 210, (CANVAS_WIDTH/2)-35, 235, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)+80, 185, (CANVAS_WIDTH/2)+80, 210            )
c.create_line((CANVAS_WIDTH/2)+80, 210, (CANVAS_WIDTH/2)+35, 210            )
c.create_line((CANVAS_WIDTH/2)+35, 210, (CANVAS_WIDTH/2)+35, 235, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)   , 270, (CANVAS_WIDTH/2)   , 300, arrow=LAST)
display(c)


cc = classCounter()


c.create_line(335, 65, 350, 65, arrow=LAST, tag='mark')
step_entry_btn_icon  = PhotoImage(file='media/2.png')
step_detour_btn_icon = PhotoImage(file='media/3.png')
step_exit_btn_icon   = PhotoImage(file='media/1.png')
reset_btn_icon       = PhotoImage(file='media/4.png')

step_entry_btn = Button(width="20",height="20", image=step_entry_btn_icon)
step_detour_btn = Button(width="20",height="20", image=step_detour_btn_icon)
step_exit_btn = Button(width="20",height="20", image=step_exit_btn_icon)
reset_btn = Button(width="20",height="20", image=reset_btn_icon)

step_entry_btn.bind('<Button-1>', lambda e, f="Verdana": step(e, rows, cc))
reset_btn.bind('<Button-1>', lambda e, f="Verdana": reset(cc))

step_entry_btn .place(x=370, y=310)
step_detour_btn.place(x=410, y=310)
step_exit_btn  .place(x=450, y=310)
reset_btn      .place(x=560, y=310)

txt = Text(root, width=30, height=10, font="14", bg='yellow')
txt.pack(side=RIGHT)

def open_file():
    txt.delete(1.0, END)
    file=askopenfilename(filetypes=[("Text files", "*.txt")])
    for i in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")):
        txt.insert(END, i)
    size = sum(1 for line in open(file, 'r'))
    rows = [line.rstrip('\n') for line in open(file, 'r', encoding='utf-8')]
    print(file)


def save_as_file():
    file=asksaveasfile(mode='w', filetypes=[("Text files", "*.txt")], defaultextension=".txt")
    if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    print(file)
    text2save = str(txt.get(1.0, END)) # starts from `1.0`, not `0.0`
    file.write(text2save)
    file.close() # `()` was missing.


mainmenu = Menu(root)
root.config(menu=mainmenu)
filemenu = Menu(mainmenu, tearoff=0)
filemenu.add_command(label="Открыть...", command=open_file)
#filemenu.add_command(label="Сохранить...", command=save_file)
filemenu.add_command(label="Сохранить как...", command=save_as_file)
mainmenu.add_cascade(label="Файл", menu=filemenu)





root.mainloop()