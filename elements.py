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

    def value(self):
        result = 0
        factor = 1
        for digit in reversed(self.data):
            result += digit*factor
            factor *= 2
        return result

    #рисование структурки
    def display_struct(self, x, y, c, wc):
        # c.create_rectangle((wc/2)+x-(125/2), y+20, (wc/2)+x+(125/2), y+40, fill='white')
        # xa = 0+(wc/2)+x-(145/2)
        # xb = 10+(wc/2)+x-(145/2)
        # dx = 15
        # for i in self.data:
        #     xa+=dx
        #     xb+=dx
        #     if i == 0:
        #         c.create_oval(xa, 25+y, xb, 35+y, fill='white')
        #     else:
        #         c.create_oval(xa, 25+y, xb, 35+y, fill='red')
        xa = -7
        xb = -2
        ya = 15
        yb = 25
        r = 0
        print(self.data)
        for i in self.data:
            if r%4 != 0:
                xa += 5
                xb += 5
                r += 1
            else:
                xa += 10
                xb += 10
                r += 1
            if i == 0:
                c.create_rectangle(xa+x, ya+y, xb+x, yb+y, fill='white', tag='reg')
            else:
                c.create_rectangle(xa+x, ya+y, xb+x, yb+y, fill='red', tag='reg')
        c.create_text(x+(xb/2), y+7, text=self.name, tag='reg')
        c.create_rectangle(x-2, y-2, xb+x+5, yb+y+5, tag='reg')

    #рисование упрощённой схемы
    def display_simple(self, x, y, c, wc):
        c.create_text(x+20, y+20, text=self.name, anchor=W, tag='reg')
        #c.create_rectangle(x+70, y+10, (wc/2)+x+(125/2), y+30, fill='white')
        xa = 70
        xb = 75
        dx = 5
        r = 0
        #print(self.data)
        for i in self.data:
            if r%4 != 0:
                xa+=dx
                xb+=dx
                r+=1
            else:
                xa += dx+5
                xb += dx+5
                r+=1
            if i == 0:
                c.create_rectangle(xa, 15+y, xb, 25+y, fill='white', tag='reg')
            else:
                c.create_rectangle(xa, 15+y, xb, 25+y, fill='red', tag='reg')


class Counter:

    def __init__(self, name, limit=None):
        self.name = name
        self.limit = limit
        self.count = 0

    def inc(self):
        if self.limit:
            if self.count < self.limit:
                self.count += 1
            else:
                self.reset()
        else:
            self.count += 1

    def reset(self):
        self.count = 0

    def value(self):
        return self.count

    def display(self, x, y, c, wc):
        c.create_text((x + wc) / 2, y + 10, text=self.count, anchor=CENTER)
        c.create_rectangle(60, 0, 74, 14)

    def display_simple(self, x, y, c, wc):
        c.create_text(x+20, y, text=self.name, anchor=W, tag='reg')
        c.create_text(x+70, y, text=str(self.count), anchor=W, tag='reg')


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

    #рисование элемента на структурке
    def display_struct(self, x, y, c, wc):
        c.create_text((wc/2)+x,y+10,text=self.name, anchor=CENTER)
        c.create_polygon(x+((wc/2)-50), y+20, x+40+((wc/2)-50), y+20, x+50+((wc/2)-50), y+30, x+60+((wc/2)-50), y+20, x+100+((wc/2)-50), y+20, x+80+((wc/2)-50), y+43, x+20+((wc/2)-50), y+43, outline='black', fill='white')
        #print (x)

    def display_simple(self, x, y, c, wc):
        print(" ")

    def reset(self):
        i=0