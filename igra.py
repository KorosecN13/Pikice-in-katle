__author__ = 'SusnikT12'


class Igra():
    def __init__(self, vmesnik):
        self.vodoravne = [[False for i in range(7)] for j in range(8)]
        self.navpicne = [[False for i in range(8)] for j in range(7)]
        self.vmesnik = vmesnik
        self.na_potezi = None

    def sprememba_igralca(self):
        if self.na_potezi == self.vmesnik.igralec1:
            self.na_potezi = self.vmesnik.igralec2
        elif self.na_potezi == self.vmesnik.igralec2:
            self.na_potezi = self.vmesnik.igralec1

    def doloci_crto(self, x, y):
        """ doloci crto, ki je najblizja koordinatam miske """
        lok_x, lok_y = x % 50, y % 50
        if lok_x < 10 or lok_x > 40 or lok_y < 10 or lok_y > 40:
            if lok_y > lok_x:
                if lok_y > 50 - lok_x:
                    if y < 400 and 50 < x < 400:
                        return 'vodoravno', y//50, x//50 - 1
                else:
                    if x > 50 and 50 < y < 400:
                        return 'navpicno', y//50 - 1, x//50 - 1
            else:
                if lok_y > 50 - lok_x:
                    if x < 400 and 50 < y < 400:
                        return 'navpicno', y//50 - 1, x//50
                else:
                    if y > 50 and 50 < x < 400:
                        return 'vodoravno', y//50 - 1, x//50 - 1
        return False

    def veljavna_poteza(self, x, y):
        """ preveri ali je poteza veljavna - crta se ni narisana """
        doloci_crto = self.doloci_crto(x, y)
        if doloci_crto:
            k, i, j = doloci_crto
            if k == "vodoravno":
                return not self.vodoravne[i][j]
            else:
                return not self.navpicne[i][j]

    def povleci_potezo(self, x, y):
        """ povleci potezo, ce je ta veljavna """
        if self.na_potezi == self.vmesnik.igralec1:
            barva = self.vmesnik.igralec1.barva
        elif self.na_potezi == self.vmesnik.igralec2:
            barva = self.vmesnik.igralec2.barva
        if self.veljavna_poteza(x, y):
            k, i, j = self.doloci_crto(x, y)
            self.vmesnik.narisi_crto(k, i, j, barva)
            if k == "vodoravno":
                self.vodoravne[i][j] = True
            else:
                self.navpicne[i][j] = True
            self.poln_kvadratek(k, i, j)

    def poln_kvadratek(self, k, i, j):
        """ pogleda ali je zadnja poteza zaprla kaksen kvadratek """
        if self.na_potezi == self.vmesnik.igralec1:
            barva = self.vmesnik.igralec1.barva
            stevec = self.vmesnik.igralec1.stevec
        else:
            barva = self.vmesnik.igralec2.barva
            stevec = self.vmesnik.igralec2.stevec
        p = 0  # preveri ali je kvadratek pobarvan oz. ali je drugi igralec na potezi
        if k == "vodoravno":
            if i != 0:  # zgornji
                if self.vodoravne[i-1][j]:
                    if self.navpicne[i-1][j]:
                        if self.navpicne[i-1][j+1]:
                            self.vmesnik.pobarvaj_kvadratek(i, j+1, barva)
                            p = 1
                            stevec.set(stevec.get()+1)
            if i != 7:  # spodnji
                if self.vodoravne[i+1][j]:
                    if self.navpicne[i][j]:
                        if self.navpicne[i][j+1]:
                            self.vmesnik.pobarvaj_kvadratek(i+1, j+1, barva)
                            p = 1
                            stevec.set(stevec.get()+1)
        else:
            if j != 0:  # levi
                if self.navpicne[i][j-1]:
                    if self.vodoravne[i][j-1]:
                        if self.vodoravne[i+1][j-1]:
                            self.vmesnik.pobarvaj_kvadratek(i+1, j, barva)
                            p = 1
                            stevec.set(stevec.get()+1)
            if j != 7:  # desni
                if self.navpicne[i][j+1]:
                    if self.vodoravne[i][j]:
                        if self.vodoravne[i+1][j]:
                            self.vmesnik.pobarvaj_kvadratek(i+1, j+1, barva)
                            p = 1
                            stevec.set(stevec.get()+1)
        if self.konec_igre():
            self.vmesnik.zmaga()
        if p == 0:
            self.sprememba_igralca()
        if self.na_potezi == self.vmesnik.igralec1:
            self.vmesnik.igralec1.igraj()
        if self.na_potezi == self.vmesnik.igralec2:
            self.vmesnik.igralec2.igraj()

    def konec_igre(self):
        """ po vsaki potezi preveri ali je konec igre """
        return self.vmesnik.igralec1.stevec.get() + self.vmesnik.igralec2.stevec.get() == 49

#    def konec_igre(self):
#        return all([all(self.vodoravne[i])for i in len(self.vodoravne)]) and \
#               all([all(self.navpicne[i])for i in len(self.navpicne)])