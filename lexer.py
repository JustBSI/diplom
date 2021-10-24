import re


class NewLexer:

    keywords: list
    keywords_first_letters: str

    def __init__(self, keywords: str = '', symbols: str = '') -> None:
        self.keywords = keywords.split()
        self.symbols  = symbols.split()
        self.symbols.sort(key=lambda x: len(x), reverse=True)
        print(self.symbols)
        self.keywords_fl = "".join(set([keyword[0] for keyword in self.keywords])) # first letters
        self.symbols_fl  = "".join(set([ symbol[0] for  symbol in self.symbols ])) # first letters

    def parse(self, row: str) -> list:
        row = row.split('//')[0] # чистка от строчных комментариев
        row = re.sub(" +", " ", row.strip()) # убираем сдвоенные, строенные и т.д. пробелы
        new_row = ''
        row_len = len(row)
        i = 0
        while i <len(row):
            if row[i] in self.symbols_fl:
                found = False
                for symbol in self.symbols:
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

        return new_row.strip().split()