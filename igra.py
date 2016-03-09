__author__ = 'SusnikT12'

class Igra():
    def __init__(self, vmesnik):
        self.vodoravne = [[False for i in range(7)] for j in range(8)]
        self.navpicne = [[False for i in range(8)] for j in range(7)]
        self.vmesnik = vmesnik

    def doloci_crto(self, x, y):
        """ doloci crto, ki je najblizja koordinatam miske """
        lok_x, lok_y = x % 50, y % 50
        if lok_x < 10 or lok_x > 40 or lok_y < 10 or lok_y > 40:
            if lok_y > lok_x:
                if lok_y > 50 - lok_x:
                    if y < 400 and 50 < x < 400:
                        return ('vodoravno',y//50, x//50 - 1)
                else:
                    if x > 50 and 50 < y < 400:
                        return ('navpicno', y//50 - 1, x//50 - 1)
            else:
                if lok_y > 50 - lok_x:
                    if x < 400 and 50 < y < 400:
                        return ('navpicno',y//50 - 1,x//50 )
                else:
                    if y > 50 and 50 < x < 400:
                        return ('vodoravno',y//50 - 1, x//50 - 1)
        return False

    def veljavna_poteza(self, x, y):
        """ preveri ali je poteza veljavna - crta se ni narisana """
        doloci_crto = self.doloci_crto(x, y)
        if doloci_crto:
            k ,i, j = doloci_crto
            if k == "vodoravno":
                return not self.vodoravne[i][j]
            else:
                return not self.navpicne[i][j]


    def povleci_potezo(self, x, y):
        """ povleci poteza, ce je ta veljavna"""
        if self.veljavna_poteza(x, y):
            k ,i, j = self.doloci_crto(x, y)
            self.vmesnik.narisi_crto(k, i, j)
            if k == "vodoravno":
                self.vodoravne[i][j] = True
            else:
                self.navpicne[i][j]  = True

