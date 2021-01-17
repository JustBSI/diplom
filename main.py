import re
from tkinter import *
from tkinter.filedialog import *
import fileinput
root = Tk()

def convert(str):
    list=[0]*len(str)
    for i, l in enumerate(str):
        if l=="1":
            list[i]=1
    return list

class Trigger:
    def __init__(self, name):
        self.sign=0
        self.name=name
    def set(self, sign):
        self.sign=sign
    def reset(self):
        self.sign=0

class Register:
    def __init__(self, n, name):
        self.data=[0]*n
        self.name=name
    def set(self, data):
        if len(self.data)==len(data):
            for i in range(len(data)):
                self.data[i]=data[i]
        # else:
        #     print(len(self.data),len(data),data)
    def reset(self):
        for i in self.data:
            i=0
    def display(self, x, y, c):
        c.create_text((wc/2)+x, y+10, text=self.name, anchor=CENTER)
        c.create_rectangle((wc/2)+x-(125/2), y+20, (wc/2)+x+(125/2), y+40, fill='white')
        xa = 0+(wc/2)+x-(145/2)
        xb = 10+(wc/2)+x-(145/2)
        dx = 15
        for i in self.data:
            xa+=dx
            xb+=dx
            if i == 0:
                c.create_oval(xa, 25+y, xb, 35+y, fill='white')
            else:
                c.create_oval(xa, 25+y, xb, 35+y, fill='red')

class Counter:
    def __init__(self):
        self.count=0
    def incr(self):
        self.count+=1
    def reset(self):
        self.count=0
    def display(self, x, y, c):
        c.create_text((x + wc) / 2, y + 10, text=self.count, anchor=CENTER)
        c.create_rectangle(60, 0, 74, 14)
class Adder:
    def __init__(self,n,name):
        self.length=n
        self.name=name
    def add(self,a,b,carry_in):
        if len(a)==self.length and len(b)==self.length:
            c=[0]*self.length
            carry=carry_in
            for i in reversed(range(self.length)):
                c[i]=(a[i]+b[i]+carry)%2
                carry=1 if (a[i]+b[i]+carry)>1 else 0
                if i==1:
                    overflow=carry
                if i==0:
                    overflow=overflow^carry
            return(c,carry,overflow)
    def display(self, x, y, c):
        c.create_text((wc/2)+x,y+10,text=self.name, anchor=CENTER)
        c.create_polygon(x+((wc/2)-50), y+20, x+40+((wc/2)-50), y+20, x+50+((wc/2)-50), y+30, x+60+((wc/2)-50), y+20, x+100+((wc/2)-50), y+20, x+80+((wc/2)-50), y+43, x+20+((wc/2)-50), y+43, outline='black', fill='white')
        print (x)
# rg_in=Register(8)
# rg_a=Register(8)
# rg_b=Register(8)
# rg_sm=Register(8)
# sum=Adder(8)

a=[1,0,1,1,0,1,1,0]
b=[1,0,1,0,1,1,0,0]

# rg_in.set(a)
# rg_a.set(rg_in.data)
# rg_in.set(b)
# rg_b.set(rg_in.data)
# rg_sm.set(sum.add(rg_a.data,rg_b.data,0)[0])
# result=sum.add(rg_a.data,rg_b.data,0)
# print(rg_a.data)
# print(rg_b.data)
# print(rg_sm.data)
# print(result)

# f=open('test.txt',"r")
# line = f.readline()
# while line:
#     print(line),
#     line = f.readline()
# f.close()

# def parser(filename):
#     f=open(filename,'r',encoding='utf-8')
#     line = f.readline()
#     while line:
#         if line.strip()=='РгА:=РгВх':
#             rg_a.set(rg_in.data)
#         elif line.strip()=='РгБ:=РгВх':
#             rg_b.set(rg_in.data)
#         elif line.strip()=='РгСМ:=РгА+РгБ':
#             rg_sm.set(sum.add(rg_a.data, rg_b.data, 0)[0])
#         elif re.search('^РгВх:=',line):
#             rg_in.set(convert(re.split(":=",line)[1].strip()))
#         line = f.readline()
#     f.close()
# parser('test.txt')
# print(rg_sm.data)

dict={}

f=open('elements.txt','r',encoding='utf-8')
for row in f:
    if 'Регистр'in row:
        str=re.split(' ',row)
        name=(re.split('\(',str[1])[0])
        capacity=(re.search('\d',(re.split('\(',str[1])[1])))
        dict[name]=Register(int(capacity.group(0)),name)
    elif 'Сумматор'in row:
        str = re.split(' ', row)
        name = (re.split('\(', str[1])[0])
        capacity = (re.search('\d', (re.split('\(', str[1])[1])))
        dict[name] = Adder(int(capacity.group(0)), name)
f.close()
class Lexer:
    ASSIG, ELEM, ADD, NUM = range(4)
    symbols = {':=': ASSIG, '+': ADD}
    def lex(self,row):
        #f=open('test.txt','r',encoding='utf-8')
        str = row.split()
        result=[]
        for roow in str:
            if roow in dict.keys():
                result.append(self.ELEM)
            elif roow in self.symbols.keys():
                result.append(self.symbols[roow])
            elif len(roow.replace('0','').replace('1',''))==0:
                result.append(self.NUM)
        return result
#print(dict)
a=Lexer()

def execute(row):
    b=a.lex(row)
    c=row.split()
    if b==[1,0,3]:
        dict[c[0]].set(convert(c[2]))
    elif b==[1,0,1]:
        dict[c[0]].set(dict[c[2]].data)
    elif b==[1,0,1,2,1]:
        dict[c[0]].set(dict['СМ'].add(dict[c[2]].data,dict[c[4]].data,0)[0])

# f=open('test.txt','r',encoding='utf-8')
# for row in f:
#     execute(row)
print(dict['РгА'].data,dict['РгБ'].data)
print(dict['РгСМ'].data)
# row='Регистр РгА(8)'
# str=re.split(' ',row)
# name=(re.split('\(',str[1])[0])
# capacity=(re.search('\d',(re.split('\(',str[1])[1])))
# print(name,capacity.group(0))

# print(c[0])
# print(c[1])
# print(c[2])
#print(convert("1001"))
wc=350
hc=290
c = Canvas(root, width=wc, height=hc, bg='white')
c.pack(side=LEFT)
dict['РгВх'].display(0,0,c)
c.create_line((wc/2), 45, (wc/2), 60)
c.create_line((wc/2)-80, 60, (wc/2)+80, 60)
c.create_line((wc/2)-80, 60, (wc/2)-80, 80, arrow=LAST)
c.create_line((wc/2)+80, 60, (wc/2)+80, 80, arrow=LAST)
dict['РгА'].display(-80,80,c)
c.create_line((wc/2)-80, 125, (wc/2)-80, 150)
c.create_line((wc/2)-80, 150, (wc/2)-35, 150)
c.create_line((wc/2)-35, 150, (wc/2)-35, 175, arrow=LAST)
dict['РгБ'].display(80,80,c)
c.create_line((wc/2)+80, 125, (wc/2)+80, 150)
c.create_line((wc/2)+80, 150, (wc/2)+35, 150)
c.create_line((wc/2)+35, 150, (wc/2)+35, 175, arrow=LAST)
dict['СМ'].display(0,160,c)
c.create_line((wc/2), 210, (wc/2), 240, arrow=LAST)
dict['РгСМ'].display(0,240,c)

def step():
    c.move('mark', 0,18)
    with open('test.txt','r',encoding='utf-8') as f:
        rows=f.readlines()
        rows=[line.rstrip('\n') for line in open('test.txt','r',encoding='utf-8')]
    execute(rows[i])


def reset():
    c.coords('mark',335, 65, 350, 65)

#c.create_rectangle(335, 10, 350, 280, outline='white')
c.create_line(335, 65, 350, 65, arrow=LAST, tag='mark')
step=Button(text='Шаг', command=step)
reset=Button(text='Сброс', command=reset)
step.place(x=400, y=250)
reset.place(x=500, y=250)


step.bind=('<Button-1>', step)
txt = Text(root, width=30, height=10, font="14", bg='yellow')
txt.pack(side=RIGHT)
op = askopenfilename(filetypes=[("Text files","*.txt")])
for i in fileinput.input(op, openhook=fileinput.hook_encoded("utf-8")):
   txt.insert(END, i)
#Counter.display(0,0,c)
root.mainloop()