import re
from config import *
from tkinter.filedialog import *
import fileinput
from elements import *
from nodes import *
from lexer import *
from connections import *
import globalvars as G  # отдельный файл с глобальными переменными
import tkinter as tk


#NL = NewLexer('if else end', '+= = -= <=')
#print(NL.parse(' test    string  '))
#print(NL.parse(' test  <=string  '))
#print(' test  string  ')


class classCounter:  # счетчик

    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1

    def reset(self):
        self.count = 0

    def __repr__(self):
        return self.count


def reset(i):  # функция сброса всего
    # pointer_canvas.delete('pointer')
    pointer_canvas.delete(1.0, END)  # очистка канваса
    txt.configure(state=NORMAL)  # включает возможность редактирования текста в поле
    step_entry_btn.place_forget()  # прячет кнопку
    step_detour_btn.place_forget()  # прячет кнопку
    step_exit_btn.place_forget()  # прячет кнопку
    reset_btn.place_forget()  # прячет кнопку
    start_btn.place(x=20, y=7)  # возвращает кнопку "старт"
    # rows = txt.get("1.0", END).splitlines()
    # c.coords('mark',335, 65, 350, 65)
    i.reset()  # сброс канваса
    for key in G.Elements:  # сбрасывает значения всех элементов путём вызова соответствующей функции в экземпляре каждого элемента
        G.Elements[key].reset()
        # print(key)
    if mode == 1:  # если открыта простая схема
        scheme_simple_display(scheme_canvas)  # то перерисовать её (сбросить)
    elif mode == 2:  # если открыта структурная схема
        scheme_struct_display(scheme_canvas)  # то перерисовать её (сбросить)
    # drawer_default_scheme()
    # display(c)


root = Tk()  # создание экземпляра Tkinter
root.geometry('480x900')  # размер окна


def scheme_simple():  #
    return tk.Toplevel(root)


def scheme_struct():  #
    return tk.Toplevel(root)


def scheme_struct_display(c, file):  # рисование структурной схемы по файлу
    c.delete('reg')  # очистка окна перед рисованием (обновление)
    c.pack(side=LEFT)  # помещение канваса в окне
    for row in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")):  # открытие файла
        string = re.split(' ', row)  # деление строки на куски
        name = re.split('\(', string[0])[0]  # выделение названия
        coords = re.split('\,', string[1])  # выделение координатов
        if 'Линия' in name:  # если это линия
            # print('Линия')
            # выделение пары пар координат для начала и конца линии
            xa = re.findall(r'\d+', coords[0])
            ya = re.findall(r'\d+', coords[1])
            xb = re.findall(r'\d+', coords[2])
            yb = re.findall(r'\d+', coords[3])
            c.create_line(xa, ya, xb, yb, tag='reg')  # рисование линии по заданным координатам
        elif 'Стрелка' in name:  # если это стрелка
            # print('Стрелка')
            # выделение пары пар координат для начала и конца линии
            xa = re.findall(r'\d+', coords[0])
            ya = re.findall(r'\d+', coords[1])
            xb = re.findall(r'\d+', coords[2])
            yb = re.findall(r'\d+', coords[3])
            c.create_line(xa, ya, xb, yb, tag='reg', arrow=LAST)  # рисование стрелки по координатам
        elif 'Инверсия' in name:  # если это инверсия (пририсовывает кружок)
            size = 6
            x = int(re.findall(r'\d+', coords[0])[0])
            y = int(re.findall(r'\d+', coords[1])[0])
            c.create_oval(x - size / 2, y - size / 2, x + size / 2, y + size / 2, outline="#000", fill="#fff", width=2)
        else:  # в остальных случаях -- это кооринаты элемента
            #print(coords)
            x = re.findall(r'\d+', coords[0])
            y = re.findall(r'\d+', coords[1])
            # print (x,y)
            if name in G.Elements:  # если элемент есть в словаре
                G.Elements[name].display_struct(int(x[0]), int(y[0]), c,
                                          CANVAS_WIDTH)  # вызов функции рисования элемента в структурной схеме


def scheme_simple_display(c):  # автоматическое рисование упрощённой схемы
    c.delete('reg')  # очистка окна перед рисованием (обновление)
    c.pack(side=LEFT)  # помещение канваса в окне
    j = 0  # нужно для отступа по вертикали между элементами
    for i in G.Elements:  # перебор всех элементов словаря
        G.Elements[i].display_simple(0, j, c, CANVAS_WIDTH)  # вызов функции рисования элемента в простой схеме
        j += 20  # сдвиг по вертикали


# scheme_simple_display(scheme_simple())
# окно

def create_scheme_struct():  # создание поля для структурной схемы
    global scheme_canvas
    global mode
    global draw_file
    mode = 2  # режим окна рисования
    # elements = len(G.Elements)
    draw_file = askopenfilename(filetypes=[("Text files", "*.txt")])  # запрос на открытие файла конфигурации
    print(draw_file)
    # print(fileinput.input(draw_file, openhook=fileinput.hook_encoded("utf-8"))[0])
    # размеры канваса по-умолчанию
    w = 450
    h = 350
    with open(draw_file, 'r', encoding="utf-8") as f:
        for row in f:  # перебор строк файла конфигурации
            if 'Размер' in row:  # если находит размеры
                arguments = row.split()[1].split(',')  # делит на ширину и высоту
                # и присваивает новые значения окну
                w = int(re.findall(r'\d+', arguments[0])[0])
                h = int(re.findall(r'\d+', arguments[1])[0])
    new_tk = scheme_simple()
    scheme_canvas = Canvas(new_tk, width=w, height=h, bg='white')  # канвас для схем
    scheme_struct_display(scheme_canvas, draw_file)  # открытие окна и запрос файла конфигурации
    f.close()


def create_scheme_simple():  # создание поля для простой схемы
    new_tk = scheme_simple()
    global scheme_canvas
    global mode
    mode = 1  # режим окна рисования
    w = 1
    for d in G.Elements:  # ищем самый длинный регистр для того чтобы подогнать ширину окна
        if type(G.Elements[d]).__name__ == 'Register':
            if len(G.Elements[d].data) > w:
                w = len(G.Elements[d].data)
    w *= 6
    w += 100
    h = len(G.Elements) * 20 + 30  # настройка высоты окна в зависимости от количества элементов в словаре
    scheme_canvas = Canvas(new_tk, width=w, height=h, bg='white')
    scheme_simple_display(scheme_canvas)


cc = classCounter()  # счётчик


def add_pointer(num, length):  # добавление маркера
    return str(num) + ' ' * (length - len(str(num)) - 2) + '⯈'


def start():  # функция старта (кнопки "старт")
    txt.configure(state=DISABLED)  # запрет на редактирование кода в поле
    start_btn.place_forget()  # прячет кнопку
    # размещает кнопки
    step_entry_btn .place(x=20, y=7)
    step_detour_btn.place(x=60, y=7)
    step_exit_btn  .place(x=100, y=7)
    reset_btn      .place(x=170, y=7)
    # global pointer
    # pointer = pointer_canvas.create_line(0, ROWHEIGHT / 2 + 2, 10, ROWHEIGHT / 2 + 2, arrow=LAST, tag='pointer')
    global currentnode
    rows = txt.get("1.0", END).splitlines()  # создаёт массив строк кода из поля (не из файла)
    size = len(rows)  # количество строк
    currentnode = Node.parse(rows)  # текущий узел
    currentnode.display()
    # print(size)
    pointer_canvas.insert(END, '1  ⯈\n')  # вставка маркера
    for i in range(size - 2):  # нумирование строк
        # pointer_canvas.insert(END, '⯈\n')
        pointer_canvas.insert(END, str(i + 2) + '\n')
    pointer_canvas.insert(END, str(size))


def step_inside(e):  # обёртка шага со входом
    global currentnode
    currentnode = currentnode.step_inside()  # выполняем узла
    if currentnode:  # если есть ссылка на следующий узел
        pointer_canvas.delete(1.0, END)
        p = ''
        for i in range(currentnode.rownum):
            p += str(i + 1) + '\n'
        p += add_pointer(currentnode.rownum + 1, 5) + '\n'
        for i in range(currentnode.rownum + 1, len(txt.get("1.0", END).splitlines())):
            p += str(i + 1) + '\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        # pointer_canvas.delete('pointer')
        reset(cc)


def step_outside(e):  # обёртка для шага с выходом
    global currentnode
    currentnode = currentnode.step_outside()
    if currentnode:
        pointer_canvas.delete(1.0, END)
        p = ''
        for i in range(currentnode.rownum):
            p += str(i + 1) + '\n'
        p += add_pointer(currentnode.rownum + 1, 5) + '\n'
        for i in range(currentnode.rownum + 1, len(txt.get("1.0", END).splitlines())):
            p += str(i + 1) + '\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        # pointer_canvas.delete('pointer')
        reset(cc)


def step_bypass(e):  # обёртка для шага с обходом
    global currentnode
    currentnode = currentnode.step()
    if currentnode:
        pointer_canvas.delete(1.0, END)
        p = ''
        for i in range(currentnode.rownum):
            p += str(i + 1) + '\n'
        p += add_pointer(currentnode.rownum + 1, 5) + '\n'
        for i in range(currentnode.rownum + 1, len(txt.get("1.0", END).splitlines())):
            p += str(i + 1) + '\n'
        pointer_canvas.insert(END, p[:-1])
        if mode == 1:
            scheme_simple_display(scheme_canvas)
        elif mode == 2:
            scheme_struct_display(scheme_canvas, draw_file)
    else:
        # pointer_canvas.delete('pointer')
        reset(cc)


def open_file():  # открытие файла
    global rows
    global size
    txt.delete(1.0, END)  # очистка поля
    file = askopenfilename(filetypes=[("Text files", "*.txt")])  # выбор файла
    for i in fileinput.input(file, openhook=fileinput.hook_encoded("utf-8")):  # перенос содержимого файла в поле
        txt.insert(END, i)
    size = sum(1 for line in open(file, 'r'))  # подсчёт количества строк
    # rows = [line.rstrip('\n') for line in open(file, 'r', encoding='utf-8')]
    rows = txt.get("1.0", END).splitlines()  # получение массива строк
    print(file)
    # drawer_default_scheme()


def save_as_file():  # сохранить как
    file = asksaveasfile(mode='w', filetypes=[("Text files", "*.txt")], defaultextension=".txt")  # сохранить как и куда
    if file is None:  # asksaveasfile return `None` if dialog closed with "cancel".
        return
    print(file)
    text2save = str(txt.get(1.0, END))  # кидает в переменную всё из поля
    file.write(text2save)  # записывает
    file.close()  # закрывает файл


def open_arch() -> None:  # открыть архитектуру
    arch = askopenfilename(filetypes=[("Text files", "*.txt")])
    f = open(arch, 'r', encoding='utf-8')  # открытие файла
    L = NewLexer(split_symbols='<= =>')
    for row in f:  # перебор всех строк
        srow = L.parse(row)
        print(srow)
        match srow:
            case "регистр" | "register", inf:
                name, capacity = inf.split('(')
                capacity = int(capacity.split(')')[0])
                G.Elements[name] = Register(name, capacity)
            case "сумматор" | "adder", inf:
                name, capacity = inf.split('(')
                capacity = int(capacity.split(')')[0])
                G.Elements[name] = Adder(capacity, name)
            case "счётчик" | "counter", inf:
                if "(" in inf:
                    name, limit = inf.split('(')
                    limit = int(limit.split(')')[0])
                    G.Elements[name] = Counter(name, limit)
                else:
                    G.Elements[inf] = Counter(inf)
            case "триггер" | "trigger", inf:
                G.Elements[inf] = Trigger(inf)
            case eto, '<=', efrom:
                G.Connections.append(Connection(efrom, eto))
            case efrom, '=>', eto:
                G.Connections.append(Connection(efrom, eto))
            case _:
                if srow != '':
                    print("Неизвестный паттерн")
    f.close()
    #for connection in G.Connections:
    #    print(connection)


# настройки верхнего меню
mainmenu = Menu(root)
root.config(menu=mainmenu)
filemenu = Menu(mainmenu, tearoff=0)
schememenu = Menu(mainmenu, tearoff=0)
mainmenu.add_cascade(label="Файл", menu=filemenu)
filemenu.add_command(label="Открыть код", command=open_file)
filemenu.add_command(label="Выбрать архитектуру", command=open_arch)
# filemenu.add_command(label="Сохранить...", command=save_file)
filemenu.add_command(label="Сохранить код", command=save_as_file)
mainmenu.add_cascade(label="Схема", menu=schememenu)
schememenu.add_command(label="Структурная схема", command=create_scheme_struct)
schememenu.add_command(label="Упрощённая схема", command=create_scheme_simple)

# картинки кнопок
step_entry_btn_icon = PhotoImage(file='media/2.png')
step_detour_btn_icon = PhotoImage(file='media/3.png')
step_exit_btn_icon = PhotoImage(file='media/1.png')
reset_btn_icon = PhotoImage(file='media/4.png')
start_btn_icon = PhotoImage(file='media/5.png')

# размеры кнопок
step_entry_btn = Button(width="20", height="20", image=step_entry_btn_icon)
step_detour_btn = Button(width="20", height="20", image=step_detour_btn_icon)
step_exit_btn = Button(width="20", height="20", image=step_exit_btn_icon)
reset_btn = Button(width="20", height="20", image=reset_btn_icon)
start_btn = Button(width="20", height="20", image=start_btn_icon)

# функционал кнопок
# step_entry_btn .bind('<Button-1>', lambda e, f="Verdana": step(e, rows, cc))
step_entry_btn.bind('<Button-1>', step_bypass)
step_detour_btn.bind('<Button-1>', step_inside)
step_exit_btn.bind('<Button-1>', step_outside)
reset_btn.bind('<Button-1>', lambda e, f="Verdana": reset(cc))
start_btn.bind('<Button-1>', lambda e, f="Verdana": start())

# размещение кнопок
step_entry_btn.place_forget  # (x=20, y=7)
step_detour_btn.place_forget  # (x=60, y=7)
step_exit_btn.place_forget  # (x=100, y=7)
reset_btn.place_forget  # (x=170, y=7)
start_btn.place(x=20, y=7)

# конфигурация текстового поля
ROWHEIGHT = 18  # количество строк
mainframe = Frame(root)
scroll = Scrollbar(mainframe)
pointer_canvas = Text(mainframe, width=5, height=35, bg='white', spacing1=2, yscrollcommand=scroll.set)  # метка
txt = Text(mainframe, width=45, height=35, font="14", bg='white', yscrollcommand=scroll.set)  # текст поля


# pointer_canvas.create_line(0,ROWHEIGHT/2+2,10,ROWHEIGHT/2+2, arrow=LAST, tag='pointer')

def OnMouseWheel(event):  # привязывает одно событие к двум текстовым полям
    pointer_canvas.yview("scroll", event.delta, "units")
    txt.yview("scroll", event.delta, "units")
    return "break"


pointer_canvas.bind("<MouseWheel>", OnMouseWheel)
txt.bind("<MouseWheel>", OnMouseWheel)


def onScroll(*args):  # событие прокрутки
    pointer_canvas.yview(*args)
    txt.yview(*args)


scroll.config(command=onScroll)

pointer_canvas.pack(side=LEFT)
mainframe.pack(side=LEFT)
# txt.pack(side=LEFT, padx=0, pady=10)
txt.pack(side=LEFT)
scroll.pack(side=LEFT, fill=Y)
# txt.config(yscrollcommand=scroll.set)

root.mainloop()
