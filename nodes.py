import globalvars as G  # отдельный файл с глобальными переменными
from oldlexer import *


class Node:  # управление узлами. Узлом является абстрактная модель,
    # представляющая исполняемую инструкцию и возможные переходы к другим инструкциям.
    # типы узлов
    types = ['ACT', 'IF', 'ELSE', 'WHILE']
    ACT, IF, ELSE, WHILE = range(4)

    def __init__(self, row=None, out=None, rownum=None):  # функция инициализации узла.
        if row:
            self.row = row  # рассматриваемая сырая строка из кода: РгА := РгА + 1
            self.pattern = Lexer.parse(
                row)  # передаём паттерну полученную пропарсенную лексером строку: [1, 0, 1, 2, 3]
            if Lexer.IF in self.pattern:  # если паттерн содержит 4 (IF), то значит строка содержит условие
                self.type = Node.IF  # присваиваем этому узлу тип if
            elif Lexer.ELSE in self.pattern:
                self.type = Node.ELSE
            elif Lexer.WHILE in self.pattern:
                self.type = Node.WHILE
            else:
                self.type = Node.ACT  # если это не условия и не цикл, то это операция
        if out:
            self.out = out  # ссылка на выход на верхний уровень
        if rownum:
            self.rownum = rownum  # номер рассматриваемой строки, нужен для маркера

    @staticmethod  # метод класса без ссылки на метод класа или сам класс
    def parse(rows, out=None, bias=0):  # парсит строки по узлам и уровням (bias -- это смещение маркера)

        current = Node()
        first = current
        i = 0  # счётчик для маркера
        while i < len(rows):  # перебор по строкам кода
            if not rows[i].strip():  # если строка пустая
                i += 1  # сдвигаем маркер
            elif rows[i][0:4] != "    ":  # если нет сдвига, значит это всё ещё тот же уровень
                current.next = Node(rows[i], out, bias + i)  # создаём ссылку на следующий узел
                current = current.next  # переходим на него
                current.rownum = bias + i  # высчитывание глобальной строки
                i += 1  # сдвигаем маркер
            else:  # если находим сдвиг (таб)
                inside_rows = []  # строку закидываем в массив внутренних строк
                while i < len(rows) and rows[i][0:4] == "    ":  # пока сдвиг есть
                    inside_rows.append(rows[i][4:])  # добавлять строки в массив уровня
                    i += 1  # сдвигаем маркер
                current.inside = Node.parse(inside_rows, current,
                                            i - len(inside_rows) + bias)  # ссылка на первый узел внутреннего уровня

        return first.next  # возвращает текущий узел

    def step(self):  # шаг с обходом
        if self.type == Node.ACT:  # если узел -- это действие
            self.execute  # выполнять
            return self.find_next()  # ищет следующий узел
        elif self.type == Node.IF:  # если узел -- это гА' + РгБ'условие
            if self.execute:  # проверка выполнения условия (true или false)
                self.inside.execute_all()  # выполняет все узлы уровня
                if hasattr(self, "next"):  # проверка есть ли у узла ссылка на следующий
                    if self.next.type == Node.ELSE:  # если тип следующего узла "если"
                        return self.next.find_next()  # ищем следующий следующего
                    else:
                        return self.next  # возвращает ссылку на следующий узел
                else:
                    return self.find_out()  # возвращает ссылку на узел внешнего уровня
            else:  # если условие не выполняется
                if hasattr(self, "next"):  # проверка есть ли у узла ссылка на следующий
                    if self.next.type == Node.ELSE:  # если тип следующего узла "если"
                        self.next.inside.execute_all()  # выполняет все узлы уровня
                        return self.next.find_next()  # возвращает ссылку на следующий узел следующего узла
                    else:
                        return self.next  # возвращает ссылку на следующий узел
                else:
                    return self.find_out()  # возвращает ссылку на узел внешнего уровня
        elif self.type == Node.WHILE:  # если узел -- это "пока"
            while self.execute:  # пока выполняется уловие
                self.inside.execute_all()  # выполнит все узлы уровня
            return self.find_next()  # возвращает ссылку на слдующий уровень
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None

    def step_inside(self):  # шаг с заходом
        if self.type == Node.ACT:  # если узел -- это действие
            self.execute  # выполнить
            return self.find_next()  # вернуть ссылку на следующий
        elif self.type == Node.IF:  # если узел -- условие
            if self.execute:  # если выполняется условие
                return self.inside  # ссылка на первый узел тела цикла
            else:  # если условие не выполняется
                if hasattr(self, "next"):  # если у узла есть ссылка на следующий
                    if self.next.type == Node.ELSE:  # если следующий узел -- это else
                        return self.next.inside  # ссылка на тело else
                    else:  # если это не else
                        return self.next  # ссылка на следующий узел
                else:  # если ссылки на следующий узел нет
                    return self.find_out()  # ссылка на внешний уровень
        elif self.type == Node.WHILE:  # если узел -- while
            if self.execute:  # если выполняется условие
                return self.inside  # ссылка на первый узел тела цикла
            else:  # если условие не выполняется
                return self.find_next()  # вернуть ссылку на следующий
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[self.type])
            return None

    def step_outside(self):  # шаг с выходом
        last = self.execute_all()  # довыполняем всё до внешнего уровня
        current = last.find_out()  # ссылка на узел где окажемся после выполения тела
        if current.type == Node.WHILE and last.out is current:  # чтобы не проскочить возможный следущий while
            while current.execute:  # пока выполняется условие
                current.inside.execute_all()  # выполняем тело
            return current.find_next()  # ссылка на следующий узел внешнего уровня
        else:  # если это не while
            return current  # ссылка на узел, в который попали

    def find_next(self):  # ищет ссылку на следующий узгА' + РгБ'ел
        if hasattr(self, "next"):  # если есть ссылка на следующий узел
            return self.next  # ссылка на следующий узел
        else:  # если ссылки на следующий нет
            return self.find_out()  # ссылка на внешний узел

    def find_out(self):  # ищет ссылку на внешний узел
        if hasattr(self, "out"):  # если есть ссылка на внешний узел
            if self.out.type == Node.WHILE:  # и если этот узел -- while
                return self.out  # ссылка на тело while
            elif self.out.type == Node.IF:  # если этот узел -- if
                if hasattr(self.out, "next"):  # если у внешнего есть ссылка на следующий
                    if self.out.next.type == Node.ELSE:  # и если это else
                        if hasattr(self.out.next, "next"):  # если есть узел за else
                            return self.out.next.next  # ссылка на следущий за else узел
                        else:  # если за else на этом уровне ничего нет
                            return self.out.next.find_out()  # ссылка на внешний уровень
                    else:  # если это не else
                        return self.out.next  # ссылка на вншний узел
                else:  # если за if ничего нет
                    return self.out.find_out()  # ссылка на внешний узел
            elif self.out.type == Node.ELSE:  # если это else
                if hasattr(self.out, "next"):  # и если у него есть ссылка на следующий
                    return self.out.next  # ссылка на него
                else:  # если следующего нет
                    return self.out.find_out()  # ссылка на внешний
            else:
                print("Ошибка: недопустимый тип узла -- " + Node.types[self.out.type])
                return None
        else:  # если внешнего узла нет
            return None

    def display(self, indent=0):  # функция для отображения макета кода в консоли (для отладки)
        ans = ''
        try:
            print(str(self.rownum) + ' ' + '| ' * indent + Node.types[self.type] + ' ' + self.row + ' ' + str(
                self.pattern) + ' ' + str(hasattr(self, "next")))
        # print(str(self.rownum))
        except Exception as e:
            # print(e)
            print('strange node')
        if hasattr(self, "inside"):
            self.inside.display(indent + 1)
        if hasattr(self, "next"):
            self.next.display(indent)

    @staticmethod
    def pure_name(word):  # выцепляет название элемента из слова
        res = word.strip()  # делит по пробелам
        if res[0] == '-':  # отбрасывает минус
            res = res[1:]
        if '[' in res:  # отбрасывает скобки
            res = res.split('[')[0]
        return res  # возвращаем имя элемента

    @staticmethod
    def pure_slice(word):  # функция получает диапазон среза из кода (если есть)
        if '[' in word:
            return word.split('[')[1].split(']')[0].strip()
        return None

    @staticmethod
    def set_elem(elem, val):  # установка значения элемента
        if '[' in elem:  # если срез
            G.Elements[Node.pure_name(elem)].set(val, Node.pure_slice(elem))
        else:  # если просто значение
            G.Elements[Node.pure_name(elem)].set(val)

    @staticmethod
    def get_elem(elem):  # получает значение элемента
        if '[' in elem:  # если срез
            return G.Elements[Node.pure_name(elem)].get(slice=Node.pure_slice(elem), inv=elem[0] == '-')
        else:  # если просто значение
            return G.Elements[Node.pure_name(elem)].get(inv=elem[0] == '-')

    # исполнение
    @property
    def execute(self):  # функция выполнения
        c = self.row.split()  # сплитит строку, с которой работаем
        p = self.pattern  # закидываем паттерн для сравнения
        if p[1] == 0:  # если это инструкция присвоения :=
            if p[0] == 1:  # если слева элемент
                if len(p) == 3:  # проверка на правильность операции (РгА := 1)
                    if p[2] == 3:  # если справа значение
                        Node.set_elem(c[0], c[2])  # присваивает значение переменной
                    elif p[2] == 1:  # если справа элемент
                        Node.set_elem(c[0], Node.get_elem(c[2]))  # присваивает переменной значение другой переменной
                elif len(p) == 5:  # если строка вида РгА := РгБ + 1
                    if p[3] == 2:  # если это сложение
                        if p[2] == 1:  # если первый операнд элемент
                            if p[4] == 1:  # если второй операнд элемент
                                G.Elements[c[0]].set(G.Elements['СМ'].add(G.Elements[c[2]].data, G.Elements[c[4]].data, 0)[
                                                   0])  # присвоить элементу сумму значений операндов
                            elif p[4] == 3:  # если второй операнд это значение
                                if type(G.Elements[c[2]]).__name__ == 'Counter':  # если второй операнд счётчик
                                    G.Elements[c[2]].count += int(c[4])  # увеличить счётчик на значение
                    elif p[3] == 14:  # если сдвиг вправо
                        if type(G.Elements[c[2]]).__name__ == 'Register':  # если слева регистр
                            new_data = [0] + G.Elements[c[2]].data[:-1]  # формируется новое значение
                            for i in range(len(new_data)):  # записываем результат в регистр
                                G.Elements[c[0]].data[i] = new_data[i]
                    elif p[3] == 15:  # если сдвиг влево
                        if type(G.Elements[c[2]]).__name__ == 'Register':  # если слева регистр
                            new_data = G.Elements[c[2]].data[1:]  # формируется новое значение
                            new_data.append(0)  # дописываем в правово края ноль
                            for i in range(len(new_data)):  # записываем результат в регистр
                                G.Elements[c[0]].data[i] = new_data[i]
                    elif p[3] == 16:  # если вычитание
                        if type(G.Elements[c[2]]).__name__ == 'Counter':  # если второй операнд счётчик
                            G.Elements[c[2]].count -= int(c[4])  # уменьшить счётчик на значение
                elif len(p) == 7:  # если прибавляется единица (РгА := РгА + РгБ + 1)
                    # print(G.Elements[c[2]]).data
                    G.Elements[c[0]].set(G.Elements['СМ'].add(G.Elements[c[2]].data, G.Elements[c[4]].data, 1)[0])
        elif p[0] == Lexer.IF:  # если строка содержит условие
            return self.condition()  # вернуть результат
        elif p[0] == Lexer.WHILE:  # если строка содержит цикл
            return self.condition()  # вернуть результат
        # else:
        # print('nothing was done')

    def execute_all(self):  # выполнение всего уровня
        current = self
        while hasattr(current, "next"):  # пока у текущего есть ссылка на следующий
            if current.type == Node.ACT:  # и если текущий -- это действие
                current.execute  # выполнить
                current = current.next  # взять ссылку на следующий
            elif current.type == Node.IF:  # если текущий -- if
                if current.execute:  # и если выполняется условие
                    current.inside.execute_all()  # выполнить тело if
                    if current.next.type == Node.ELSE:  # если следующий -- это else
                        if hasattr(current.next, "next"):  # если у него есть тело
                            current = current.next.next  # выход на внешний уровень
                    else:  # если else нет
                        current = current.next  # следующий узел
                else:  # если условие не выполняется
                    current = current.next  # переход на следующий узел
                    if current.type == Node.ELSE:  # если это else
                        current.inside.execute_all()  # выполнить тело else
                        if hasattr(current, "next"):  # если после него есть узел
                            current = current.next  # взять ссылку на следующий
            elif current.type == Node.WHILE:  # если это while
                while current.execute:  # пока выполняется условие
                    current.inside.execute_all()  # выполнить тело
                current = current.next  # взять ссылку на следующий
            else:
                print("Ошибка: недопустимый тип узла -- " + Node.types[current.type])
        if current.type == Node.ACT:  # если это действие
            current.execute  # выполнить
        elif current.type == Node.IF:  # если это условие
            if current.execute:  # если условие выполняется
                current.inside.execute_all()  # выполнить тело
        elif current.type == Node.WHILE:  # если это while
            while current.execute:  # пока выполняется условие
                current.inside.execute_all()  # выполнить тело
        else:
            print("Ошибка: недопустимый тип узла -- " + Node.types[current.type])
        return current

    def get_pattern_value(self, num, c):  # получает значение элемента по паттерну
        if self.pattern[num] == Lexer.ELEM:  # если слева элемент
            if '[' in c[num]:  # если есть указатель на конкретный разряд
                return G.Elements[c[num].split('[')[0]].value(c[num].split('[')[1].split(']')[0].strip())  # вернуть значение
            else:  # если указателя нет
                return G.Elements[c[num]].value()  # вернуть значение
        elif self.pattern[num] == Lexer.ELEM_SLICE:  # если это срез элемента
            v = c[num].split('[')  # диапазон
            return G.Elements[v[0]].slice_value(v[1][:-1].strip())  # берем срез
        elif self.pattern[num] == Lexer.NUM:  # если это число
            return int(c[num])  # вернуть это число

    def condition(self) -> bool:  # функция сравнения
        c = self.row.split()  # строка, с которой работаем
        op1 = self.get_pattern_value(1, c)  # значение первого операнда
        op2 = self.get_pattern_value(3, c)  # значение второго операнда
        # print(op1 == op2)
        if c[2] == '=':
            c[2] = '=='
        try:
            return eval(str(op1) + c[2] + str(op2))
        except Exception:
            print(Exception)
            return False