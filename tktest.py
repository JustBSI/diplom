from tkinter import *
root = Tk()
rg_a = LabelFrame(text="РгА")
c = Canvas(rg_a, width=150, height=40, bg='white')
c.pack()
rg_a.pack()
c.create_rectangle(10, 10, 135, 30)
xa=0
xb=10
x=15
for i in range(8):
    xa=xa+x
    xb=xb+x
    c.create_oval(xa, 15, xb, 25)

rg_b = LabelFrame(text="РгБ")
c = Canvas(rg_b, width=150, height=40, bg='white')
c.pack()
rg_b.pack()
c.create_rectangle(10, 10, 135, 30)
c.create_oval(15, 15, 25, 25)
c.create_oval(30, 15, 40, 25)
c.create_oval(45, 15, 55, 25)
c.create_oval(60, 15, 70, 25)
c.create_oval(75, 15, 85, 25)
c.create_oval(90, 15, 100, 25)
c.create_oval(105, 15, 115, 25)
c.create_oval(120, 15, 130, 25)
root.mainloop()