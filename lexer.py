import re


class NewLexer:

    split_symbols: list
    non_split_symbols: str
    delete_symbols: str
    split_with_delete_symbols: str

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

        return new_row.strip().split()