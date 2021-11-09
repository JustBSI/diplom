import re
import globalvars as G  # отдельный файл с глобальными переменными

if G.MODE == G.NEW:

    class Lexer:

        split_symbols: list
        non_split_symbols: list
        delete_symbols: list
        split_with_delete_symbols: list

        def __init__(self,
                     split_symbols:             str = '',
                     non_split_symbols:         str = '',
                     delete_symbols:            str = '',
                     split_with_delete_symbols: str = ''
                     ) -> None:

            self.split_symbols = split_symbols.split()
            self.split_symbols.sort(key=lambda x: len(x), reverse=True)

            self.non_split_symbols = non_split_symbols.split()
            self.non_split_symbols.sort(key=lambda x: len(x), reverse=True)

            self.delete_symbols = delete_symbols.split()
            self.delete_symbols.sort(key=lambda x: len(x), reverse=True)

            self.split_with_delete_symbols = split_with_delete_symbols.split()
            self.split_with_delete_symbols.sort(key=lambda x: len(x), reverse=True)

            self.split_symbols_fl = "".join(set([symbol[0] for symbol in self.split_symbols]))  # first letters

            print("new")

        def parse(self, row: str) -> list:
            row = row.split('//')[0]  # чистка от строчных комментариев
            for symbol in self.split_with_delete_symbols:
                row = row.strip().replace(symbol, " ")
            row = re.sub(" +", " ", row.strip())  # убираем сдвоенные, строенные и т.д. пробелы
            for symbol in self.non_split_symbols:
                row = row.strip().replace(" "+symbol, symbol)
            for symbol in self.delete_symbols:
                row = row.strip().replace(symbol, "")
            new_row = ''
            row_len = len(row)
            i = 0
            while i < len(row):
                if row[i] in self.split_symbols_fl:
                    found = False
                    for symbol in self.split_symbols:
                        symbol_len = len(symbol)
                        if i+symbol_len <= row_len:
                            if row[i:i+symbol_len] == symbol:
                                if new_row[-1] != ' ':
                                    new_row += ' '
                                new_row += symbol + ' '
                                i += symbol_len
                                found = True
                                break
                    if not found:
                        i += 1
                elif row[i] == ' ':
                    if row[i-1] != ' ':
                        new_row += ' '
                    i += 1
                else:
                    new_row += row[i]
                    i += 1
            result = new_row.strip().split()
            if len(result) == 1:
                result = result[0]
            return result


elif G.MODE == G.OLD:

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

