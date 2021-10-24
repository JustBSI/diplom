import re

import globalvars as G  # отдельный файл с глобальными переменными


class Lexer:  # лексический анализ кода
    # типы слов в строках
    # объявление кортежа (каждому типу слов свой номер)
    ASSIG, ELEM, ADD, NUM, IF, ELSE, WHILE, EQU, MORE, LESS, NOT_EQU, MORE_EQU, LESS_EQU, ELEM_SLICE, RIGHT_SHIFT, LEFT_SHIFT, SUB = range(
        17)
    # типы операций и их обозначения
    symbols = {':=': ASSIG, '+': ADD, '-': SUB, '=': EQU, '>': MORE, '<': LESS, '!=': NOT_EQU, '>=': MORE_EQU,
               '<=': LESS_EQU, '>>': RIGHT_SHIFT, '<<': LEFT_SHIFT}
    # ключевые слова (циклы и условия)
    keywords = {'если': IF, 'иначе': ELSE, 'пока': WHILE}

    @classmethod  # метод класса, который вызывается без создания экземпляра класса
    def is_elem(cls, word):  # проверка, является ли кусок строки элементом
        w = word
        if w[0] == '-':
            w = w[1:]  # убираем минус
        if '[' in w:
            w = w.split('[')[0]
        return w in G.Elements.keys()  # проверка, есть ли элемент в словаре

    @classmethod
    def parse(self, row):  # анализирует строку и составляет лексический макет. РгА := РгА + 1 --> [1, 0, 1, 2, 3]
        string = row.split()
        result = []
        for word in string:
            if self.is_elem(word):  # если это элемент
                result.append(self.ELEM)  # то добавляем его в макет
            elif word.split('[')[0] in G.Elements.keys():  #
                result.append(self.ELEM_SLICE)
            elif word in self.keywords.keys():
                result.append(self.keywords[word])
            elif word in self.symbols.keys():
                result.append(self.symbols[word])
            # elif len(word.replace('0', '').replace('1', '')) == 0:
            elif len(re.sub(r"\d+", "", word, flags=re.UNICODE)) == 0:  # если найдено что-то кроме паттерна
                result.append(self.NUM)  # то это чисто
        return result  # возвращает макет строки