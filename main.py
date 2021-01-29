import re
from config import *
from tkinter.filedialog import *
import fileinput
from elements import *


class Lexer:

    ASSIG, ELEM, ADD, NUM = range(4)
    symbols = {':=': ASSIG, '+': ADD}

    @classmethod
    def parse(self, row):
        str = row.split()
        result = []
        for roow in str:
            if roow in dict.keys():
                result.append(self.ELEM)
            elif roow in self.symbols.keys():
                result.append(self.symbols[roow])
            elif len(roow.replace('0', '').replace('1', '')) == 0:
                result.append(self.NUM)
        return result


class Node:

    # типы узлов
    START, ACT, END = range(3)

    def __init__(self, type):
        self.type = type

    @staticmethod
    def parse(rows):

        current = Node(Node.START)
        first = current
        i = 0
        while i < len(rows):
            if rows[i][0:4]!="    ":
                previous = current
                current = Node(Node.ACT)
                previous.next = current
                current.raw     = rows[i][:-1]
                current.pattern = Lexer.parse(current.raw)
                i += 1
            else:
                inside_rows = []
                while i<len(rows) and rows[i][0:4]=="    ":
                    inside_rows.append(rows[i][4:])
                    i += 1
                #print(inside_rows)
                current.inside = Node.parse(inside_rows)
        previous = current
        current = Node(Node.END)
        previous.next = current

        return first

    def display(self, indent=0):
        if self.type==Node.START:
            print('| ' * indent+"_Start: ")
        elif self.type==Node.END:
            print('| ' * indent+"_End.")
        else:
            print('| '*indent+self.raw+' '+str(self.pattern))
        if hasattr(self, "inside"):
            self.inside.display(indent+1)
        if hasattr(self, "next"):
            self.next.display(indent)






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