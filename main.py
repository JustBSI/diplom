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
    START, ACT, IF, ELSE, WHILE, END = range(6)

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
    def parse(rows, out=None, end_next=None):

        current = Node(type=Node.START)
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
                #print(inside_rows)
                current.inside = Node.parse(inside_rows, current)
                #if current.type == Node.WHILE:
                #    if i<len(rows):
                #        current.next = Node(rows[i][:-1], out)
                #        current.inside = Node.parse(inside_rows, current.next, current)
                #        current = current.next
                #        i += 1
                #elif current.type == Node.IF:
                #    if i<len(rows):
                #        current.next = Node(rows[i][:-1], out)
                #        if Lexer.ELSE in current.next.pattern:
                #            i += 1
                #            inside_rows_2 = []
                #            while i < len(rows) and rows[i][0:4] == "    ":
                #                inside_rows_2.append(rows[i][4:])
                #                i += 1

        #if end_next:
        #    current.next = end_next
        #else:
        #    previous = current
        #    current = Node(type=Node.END)
        #    previous.next = current

        return first.next

    def display(self, indent=0):
        #if self.type==Node.START:
            #print('| ' * indent+"_Start: ")
        #elif self.type==Node.END:
            #print('| ' * indent+"_End.")
        #else:
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

    def condition(self):
        return True






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
    dict['РгВх'].display(0, 0, c, CANVAS_WIDTH)
    dict['РгА'].display(-80, 80, c, CANVAS_WIDTH)
    dict['РгБ'].display(80, 80, c, CANVAS_WIDTH)
    dict['СМ'].display(0, 160, c, CANVAS_WIDTH)
    dict['РгСМ'].display(0, 240, c, CANVAS_WIDTH)


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
    if 'Регистр' in row:
        str        = re.split(' ', row)
        name       = re.split('\(', str[1])[0]
        capacity   = re.search('\d', (re.split('\(', str[1])[1]))
        dict[name] = Register(int(capacity.group(0)), name)
    elif 'Сумматор' in row:
        str        = re.split(' ', row)
        name       = (re.split('\(', str[1])[0])
        capacity   = (re.search('\d', (re.split('\(', str[1])[1])))
        dict[name] = Adder(int(capacity.group(0)), name)
f.close()


c = Canvas(root, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg='white')
c.pack(side=LEFT)
c.create_line((CANVAS_WIDTH/2), 45, (CANVAS_WIDTH/2), 60)
c.create_line((CANVAS_WIDTH/2)-80, 60, (CANVAS_WIDTH/2)+80, 60)
c.create_line((CANVAS_WIDTH/2)-80, 60, (CANVAS_WIDTH/2)-80, 80, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)+80, 60, (CANVAS_WIDTH/2)+80, 80, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)-80, 125, (CANVAS_WIDTH/2)-80, 150)
c.create_line((CANVAS_WIDTH/2)-80, 150, (CANVAS_WIDTH/2)-35, 150)
c.create_line((CANVAS_WIDTH/2)-35, 150, (CANVAS_WIDTH/2)-35, 175, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)+80, 125, (CANVAS_WIDTH/2)+80, 150)
c.create_line((CANVAS_WIDTH/2)+80, 150, (CANVAS_WIDTH/2)+35, 150)
c.create_line((CANVAS_WIDTH/2)+35, 150, (CANVAS_WIDTH/2)+35, 175, arrow=LAST)
c.create_line((CANVAS_WIDTH/2), 210, (CANVAS_WIDTH/2), 240, arrow=LAST)
display(c)


cc = classCounter()


c.create_line(335, 65, 350, 65, arrow=LAST, tag='mark')
step_btn = Button(text='Шаг')
step_btn.bind('<Button-1>', lambda e, f="Verdana": step(e, rows, cc))
reset_btn = Button(text='Сброс')
reset_btn.bind('<Button-1>', lambda e, f="Verdana": reset(cc))
step_btn.place(x=400, y=250)
reset_btn.place(x=500, y=250)


txt = Text(root, width=30, height=10, font="14", bg='yellow')
txt.pack(side=RIGHT)
op = askopenfilename(filetypes=[("Text files", "*.txt")])
for i in fileinput.input(op, openhook=fileinput.hook_encoded("utf-8")):
   txt.insert(END, i)
size = sum(1 for line in open('test.txt', 'r'))
rows = [line.rstrip('\n') for line in open('test.txt', 'r', encoding='utf-8')]
root.mainloop()