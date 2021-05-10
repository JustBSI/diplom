from tkinter import *

def invert(data): # инвертирование
    res = [1]*len(data)
    for i in range(len(data)):
        if data[i]:
            res[i] = 0
    return res

class Trigger: # триггер

    def __init__(self, name):
        self.sign=0
        self.name=name

    def set(self, sign):
        self.sign=sign

    def reset(self):
        self.sign=0


class Register: # регистр

    def __init__(self, n, name):
        self.data=[0]*n
        self.name=name

    #def set(self, data):
    #    l = len(self.data)
    #    if l == len(data):
    #        for i in range(l):
    #            self.data[i] = int(data[i])
    #    elif int(data) < 2**l:
    #        current = int(data)
    #        for b in self.data:
    #            b = current % 2
    #            current -= current % 2
    #            current /= 2
    #        self.data.reverse()

    def reset(self): # сброс (очистка) регистра
        for i in range(len(self.data)):
            self.data[i]=0

    def value(self, slice=None): # получение значения регистра
        if slice and ':' not in slice: # если один разряд
            return self.data[int(slice.strip())]
        else:
            if slice: # если срез
                v = slice.strip().split(':')
                d = self.data[int(v[0]):int(v[1])]
            else:
                d = self.data
            result = 0
            factor = 1
            for digit in reversed(d):
                if digit:
                    result += factor
                factor *= 2
            return result

    # def slice_value(self, slice):
    #     if ':' not in slice:
    #         return self.data[int(slice.strip())]
    #     else:
    #         res = 0
    #         count = 0
    #         v = slice.strip().split(':')
    #         for bit in reversed(self.data[int(v[0]):int(v[1])]):
    #             res += bit*(2**count)
    #             count += 1
    #         return res

    def get(self, slice=None, inv=False): # получение значения регистра
        if not slice:
            return invert(self.data) if inv else self.data
        if ':' not in slice:
            return invert(self.data[int(slice.strip())]) if inv else self.data[int(slice.strip())]
        else:
            v = slice.strip().split(':')
            print(invert(self.data[int(v[0]):int(v[1])+1]))
            print(self.data[int(v[0]):int(v[1])+1])
            return invert(self.data[int(v[0]):int(v[1])+1]) if inv else self.data[int(v[0]):int(v[1])+1]

    def set(self, data, slice=None): # устанвливает значение для регистра
        #if type(data).__name__=='str':
        #    if not slice:
        #        for i in range(len(data)):
        #            self.data[i] = int(data[i])
        #    elif ':' not in slice:
        #        self.data[int(slice.strip())] = int(data)
        #    else:
        #        count = 0
        #        v = slice.strip().split(':')
        #        for bit in self.data[int(v[0]):int(v[1])+1]:
        #            self.data[int(v[0])+count] = int(data[count])
        #            count += 1
        #elif type(data).__name__=='list':
        #    if not slice:
        #        count = 0
        #        for bit in self.data:
        #            self.data[count] = data[count]
        #            count += 1
        #    elif ':' not in slice:
        #        self.data[int(slice.strip())] = int(data)
        #    else:
        #        count = 0
        #        v = slice.strip().split(':')
        #        for bit in self.data[int(v[0]):int(v[1])+1]:
        #            self.data[int(v[0])+count] = data[count]
        #            count += 1
        if not slice:
            for i in range(len(data)):
                self.data[i] = int(data[i])
        elif ':' not in slice:
            self.data[int(slice.strip())] = int(data)
        else:
            count = 0
            v = slice.strip().split(':')
            for bit in self.data[int(v[0]):int(v[1])+1]:
                self.data[int(v[0])+count] = int(data[count])
                count += 1


    def display_struct(self, x, y, c, wc): # рисование структурки
        xa = 5
        xb = 0
        ya = 15
        yb = 25
        count = 0
        space = 2
        print(self.data)
        for i in self.data:
            xa += 5
            xb += 5
            if not count%8:
                xa += space
                xb += space
            count += 1
            if i == 0:
                c.create_rectangle(xa+x, ya+y, xb+x, yb+y, fill='white', tag='reg')
            else:
                c.create_rectangle(xa+x, ya+y, xb+x, yb+y, fill='red', tag='reg')
        c.create_text(x+(xb/2), y+7, text=self.name, tag='reg')
        c.create_rectangle(x-2, y-2, xb+x+12, yb+y+5, tag='reg')


    def display_simple(self, x, y, c, wc): # рисование упрощённой схемы
        c.create_text(x+20, y+20, text=self.name, anchor=W, tag='reg')
        #c.create_rectangle(x+70, y+10, (wc/2)+x+(125/2), y+30, fill='white')
        xa = 70
        xb = 75
        dx = 5
        r = 0
        space = 2
        #print(self.data)
        for i in self.data:
            if r%8 != 0:
                xa+=dx
                xb+=dx
                r+=1
            else:
                xa += dx+space
                xb += dx+space
                r+=1
            if i == 0:
                c.create_rectangle(xa, 15+y, xb, 25+y, fill='white', tag='reg')
            else:
                c.create_rectangle(xa, 15+y, xb, 25+y, fill='red', tag='reg')


class Counter: # счётчик

    def __init__(self, name, limit=None):
        self.name = name
        self.limit = limit
        self.count = 0

    def inc(self): # инкрементирование
        if self.limit:
            if self.count < self.limit:
                self.count += 1
            else:
                self.reset()
        else:
            self.count += 1

    def dec(self): # декрементирование
        if self.count > 0:
            self.count -= 1
        else:
            print("Предупреждение: значение счётчика уже опустилось до нуля и не будет изменено")

    def set(self, data): # установка значения
        self.count = int(data)

    def reset(self): # сброс
        self.count = 0

    def value(self): # получить значение
        return self.count

    def display_struct(self, x, y, c, wc): # показ на структурной схеме
        c.create_text(x + 20, y + 10, text=self.name, anchor=CENTER, tag='reg')
        c.create_text(x + 20, y + 35, text=self.count, anchor=CENTER, tag='reg', font=('Helevtica', 30))
        c.create_rectangle(x, y+0, x+40, y+60)

    def display_simple(self, x, y, c, wc): # показ на простой схеме
        c.create_text(x+20, y+20, text=self.name, anchor=W, tag='reg')
        c.create_text(x+70, y+20, text=str(self.count), anchor=W, tag='reg')


class Adder: # сумматор

    def __init__(self,n,name):
        self.length=n
        self.name=name

    def add(self,a,b,carry_in): # сложение
        #print(a)
        #print(b)
        if len(a)==self.length and len(b)==self.length: # если длина операндов и сумматора одинаковые
            c=[0]*self.length # результат
            carry=carry_in # перенос
            for i in reversed(range(self.length)): # с младших разрядов
                #c[i]=(a[i]+b[i]+carry)%2
                c[i]=a[i]^b[i]^carry
                carry=1 if (a[i]+b[i]+carry)>1 else 0
                if i==1:
                    overflow=carry
                if i==0:
                    overflow=overflow^carry
            return(c,carry,overflow)


    def display_struct(self, x, y, c, wc): # рисование сумматора на структурктурной схеме
        c.create_text((wc/2)+x,y+10,text=self.name, anchor=CENTER)
        c.create_polygon(x+((wc/2)-50), y+20, x+40+((wc/2)-50), y+20, x+50+((wc/2)-50), y+30, x+60+((wc/2)-50), y+20, x+100+((wc/2)-50), y+20, x+80+((wc/2)-50), y+43, x+20+((wc/2)-50), y+43, outline='black', fill='white')
        #print (x)

    def display_simple(self, x, y, c, wc): # рисование сумматора на простой схеме
        c.create_text(x+20, y+20, text=self.name, anchor=W, tag='reg')

    def reset(self): # сброс
        i=0