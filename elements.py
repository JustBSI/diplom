from tkinter import *

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

    def reset(self):
        for i in range(len(self.data)):
            self.data[i]=0

    def display(self, x, y, c, wc):
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

    def display(self, x, y, c, wc):
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

    def display(self, x, y, c, wc):
        c.create_text((wc/2)+x,y+10,text=self.name, anchor=CENTER)
        c.create_polygon(x+((wc/2)-50), y+20, x+40+((wc/2)-50), y+20, x+50+((wc/2)-50), y+30, x+60+((wc/2)-50), y+20, x+100+((wc/2)-50), y+20, x+80+((wc/2)-50), y+43, x+20+((wc/2)-50), y+43, outline='black', fill='white')
        #print (x)

    def reset(self):
        i=0