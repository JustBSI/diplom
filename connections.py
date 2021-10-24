


class Connection:

    # связанные элементы: from => to или to <= from
    efrom: str
    eto: str

    # выравнивание при неравной размерности элементов.
    efrom_align: str = 'right'
    eto_align: str = 'right'

    efrom_is_slice: bool
    eto_is_slice: bool

    efrom_slice: tuple
    eto_slice: tuple

    def __init__(self, efrom: str, eto: str):
        self.efrom = efrom
        self.eto = eto

    def __repr__(self):
        return f'{self.eto} <= {self.efrom}'

