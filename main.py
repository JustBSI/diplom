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
c.create_text((CANVAS_WIDTH/2), 15, text='Шина', anchor=CENTER)
c.create_line((CANVAS_WIDTH/2), 30, (CANVAS_WIDTH/2), 55, arrow=LAST)
c.create_line((CANVAS_WIDTH/2), 105, (CANVAS_WIDTH/2), 120)
c.create_line((CANVAS_WIDTH/2)-80, 120, (CANVAS_WIDTH/2)+80, 120)
c.create_line((CANVAS_WIDTH/2)-80, 120, (CANVAS_WIDTH/2)-80, 140, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)+80, 120, (CANVAS_WIDTH/2)+80, 140, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)-80, 185, (CANVAS_WIDTH/2)-80, 210)
c.create_line((CANVAS_WIDTH/2)-80, 210, (CANVAS_WIDTH/2)-35, 210)
c.create_line((CANVAS_WIDTH/2)-35, 210, (CANVAS_WIDTH/2)-35, 235, arrow=LAST)
c.create_line((CANVAS_WIDTH/2)+80, 185, (CANVAS_WIDTH/2)+80, 210)
c.create_line((CANVAS_WIDTH/2)+80, 210, (CANVAS_WIDTH/2)+35, 210)
c.create_line((CANVAS_WIDTH/2)+35, 210, (CANVAS_WIDTH/2)+35, 235, arrow=LAST)
c.create_line((CANVAS_WIDTH/2), 270, (CANVAS_WIDTH/2), 300, arrow=LAST)
display(c)


cc = classCounter()


c.create_line(335, 65, 350, 65, arrow=LAST, tag='mark')
step_entry_btn_icon=PhotoImage(file='2.png')
step_detour_btn_icon=PhotoImage(file='3.png')
step_exit_btn_icon=PhotoImage(file='1.png')
reset_btn_icon=PhotoImage(file='4.png')

step_entry_btn = Button(width="20",height="20", image=step_entry_btn_icon)
step_detour_btn = Button(width="20",height="20", image=step_detour_btn_icon)
step_exit_btn = Button(width="20",height="20", image=step_exit_btn_icon)
reset_btn = Button(width="20",height="20", image=reset_btn_icon)

step_entry_btn.bind('<Button-1>', lambda e, f="Verdana": step(e, rows, cc))
reset_btn.bind('<Button-1>', lambda e, f="Verdana": reset(cc))

step_entry_btn.place(x=370, y=310)
step_detour_btn.place(x=410, y=310)
step_exit_btn.place(x=450, y=310)
reset_btn.place(x=560, y=310)

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