__author__ = 'uporabnik'


class Clovek():
    def __init__(self, vmesnik, ime, stevec, barva):
        self.ime = ime
        self.stevec = stevec
        self.barva = barva
        self.vmesnik = vmesnik
        self.igra = None

    def igraj(self):
        """ caka, da igralec klikne na igralno polje """
        pass

    def prekini(self):
        pass

    def klik(self, x, y):
        """ povlece potezo, ce je ta veljavna """
        self.igra.povleci_potezo(x, y)


class Racunalnik():
    def __init__(self, vmesnik, ime, stevec, barva, algoritem):
        self.ime = ime
        self.stevec = stevec
        self.barva = barva
        self.algoritem = algoritem  # Algoritem, ki izračuna potezo
        self.vmesnik = vmesnik
        self.igra = None
        # self.mislec = None  # Vlakno (thread), ki razmišlja

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""
        pass

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem že izračunal potezo."""
        pass

    def prekini(self):
        """ To metodo kliče GUI, če je treba prekiniti razmišljanje. """
        pass

    def klik(self, x, y):
        """ racunalnik ignorira klike na igralnem polju """
        pass