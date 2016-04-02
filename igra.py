__author__ = 'SusnikT12'
import time


class Igra():
    def __init__(self, vmesnik):
        self.vodoravne = [[False for i in range(7)] for j in range(8)]
        self.navpicne = [[False for i in range(8)] for j in range(7)]
        self.matrika_kvadratov = [[0 for i in range(7)]for j in range(7)]
        self.vmesnik = vmesnik
        self.na_potezi = None
        self.zgodovina = []
        self.konec = False

    def sprememba_igralca(self):
        """ spremeni igralca, ki je na potezi """
        if self.na_potezi == self.vmesnik.igralec1:
            self.na_potezi = self.vmesnik.igralec2
            self.vmesnik.napis.set("Na potezi je {0}.".format(self.vmesnik.igralec2.ime.get()))
        elif self.na_potezi == self.vmesnik.igralec2:
            self.na_potezi = self.vmesnik.igralec1
            self.vmesnik.napis.set("Na potezi je {0}.".format(self.vmesnik.igralec1.ime.get()))

    def doloci_crto(self, x, y):
        """ Doloci crto, ki je najblizja koordinatam miske.
        Ce igralec ni kliknil dovolj blizu kateri od crt, vrne False"""
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
        # nastavi barvo crte
        if self.na_potezi == self.vmesnik.igralec1:
            barva = self.vmesnik.igralec1.barva
        elif self.na_potezi == self.vmesnik.igralec2:
            barva = self.vmesnik.igralec2.barva
        # preveri, ce je poteza veljavna
        if self.veljavna_poteza(x, y):
            self.shrani_pozicijo()
            k, i, j = self.doloci_crto(x, y)
            self.vmesnik.narisi_crto(k, i, j, barva)
            # v matriki self.vodoravne/self.navpicne trenutno potezo nastavi na True in popravi matriko kvadratov
            if k == "vodoravno":
                self.vodoravne[i][j] = True
            else:
                self.navpicne[i][j] = True
            self.popravi_matriko_kvadratov(k, i, j)
            # ce je igralec zaprl kvadratek, ga pobarva
            p = self.poln_kvadratek(k, i, j)
            # ce igralec ni vec na potezi, spremeni igralca
            if p == 0:
                self.sprememba_igralca()
            # ce igre se ni konec, poklice metodo, ki odigra naslednjo potezo nasprotnika
            if not self.konec:
                if self.na_potezi == self.vmesnik.igralec1:
                    self.vmesnik.igralec1.igraj()
                elif self.na_potezi == self.vmesnik.igralec2:
                    self.vmesnik.igralec2.igraj()

    def racunalnik_povleci_potezo(self, poteza):
        """  povlece potezo, ki jo je izracunal racunalnik """
        k, i, j = poteza
        # nastavi barvo crte
        if self.na_potezi == self.vmesnik.igralec1:
            barva = self.vmesnik.igralec1.barva
        elif self.na_potezi == self.vmesnik.igralec2:
            barva = self.vmesnik.igralec2.barva
        self.shrani_pozicijo()
        self.vmesnik.narisi_crto(k, i, j, barva)
        # popravi matriki self.vodoravne/self.navpicne in self.matrika_kvadratov
        if k == "vodoravno":
            self.vodoravne[i][j] = True
        else:
            self.navpicne[i][j] = True
        self.popravi_matriko_kvadratov(k, i, j)
        # ce je igralec zaprl kvadratek, ga pobarva
        self.poln_kvadratek(k, i, j)

    def navidezno_povleci_potezo(self, p):
        """ navidezno povlece potezo pri minimaxu in vrne stevilo zaprtih kvadratov s to potezo """
        k, i, j = p
        self.shrani_navidezno_pozicijo()
        # popravi matriki self.vodoravne/self.navpicne in self.matrika_kvadratov
        if k == "vodoravno":
            self.vodoravne[i][j] = True
        else:
            self.navpicne[i][j] = True
        p = self.popravi_matriko_kvadratov(k, i, j)
        # ce je igralec zaprl kvadratek, popravi stevec (trenutni rezultat igre)
        if p:
            if self.na_potezi == self.jaz:
                self.jaz_stevec += p
            elif self.na_potezi == self.nasprotnik:
                self.nasprotnik_stevec += p
        # ce igralec ni zaprl kvadratka, je na potezi nasprotni igralec
        else:
            if self.na_potezi == self.jaz:
                self.na_potezi = self.nasprotnik
            elif self.na_potezi == self.nasprotnik:
                self.na_potezi = self.jaz
        return p

    def poln_kvadratek(self, k, i, j):
        """ Pogleda ali je zadnja poteza zaprla kaksen kvadratek.
        Ce se je kaksen kvadratek zaprl, vmesniku sporoci, naj ga pobarva in popravi stevec."""
        # nastavi barvo kvadratka
        if self.na_potezi == self.vmesnik.igralec1:
            barva = self.vmesnik.igralec1.barva
            stevec = self.vmesnik.igralec1.stevec
        else:
            barva = self.vmesnik.igralec2.barva
            stevec = self.vmesnik.igralec2.stevec
        p = 0  # preveri ali je kvadratek pobarvan (na koncu p>0) oz. ali je drugi igralec na potezi (na koncu p=0)
        if k == "vodoravno":
            if i != 0:  # zgornji
                if self.vodoravne[i-1][j]:
                    if self.navpicne[i-1][j]:
                        if self.navpicne[i-1][j+1]:
                            time.sleep(0.5)
                            self.vmesnik.pobarvaj_kvadratek(i, j+1, barva)
                            p = 1
                            stevec.set(stevec.get()+1)
            if i != 7:  # spodnji
                if self.vodoravne[i+1][j]:
                    if self.navpicne[i][j]:
                        if self.navpicne[i][j+1]:
                            time.sleep(0.5)
                            self.vmesnik.pobarvaj_kvadratek(i+1, j+1, barva)
                            p = 1
                            stevec.set(stevec.get()+1)
        else:
            if j != 0:  # levi
                if self.navpicne[i][j-1]:
                    if self.vodoravne[i][j-1]:
                        if self.vodoravne[i+1][j-1]:
                            time.sleep(0.5)
                            self.vmesnik.pobarvaj_kvadratek(i+1, j, barva)
                            p = 1
                            stevec.set(stevec.get()+1)
            if j != 7:  # desni
                if self.navpicne[i][j+1]:
                    if self.vodoravne[i][j]:
                        if self.vodoravne[i+1][j]:
                            time.sleep(0.5)
                            self.vmesnik.pobarvaj_kvadratek(i+1, j+1, barva)
                            p = 1
                            stevec.set(stevec.get()+1)
        if self.konec_igre():
            self.vmesnik.zmaga()
            self.konec = True
        else:
            return p

    def konec_igre(self):
        """ po vsaki potezi preveri ali je konec igre """
        return self.vmesnik.igralec1.stevec.get() + self.vmesnik.igralec2.stevec.get() == 49

    def konec_igre1(self):
        return all([all(self.vodoravne[i])for i in range(len(self.vodoravne))]) and \
               all([all(self.navpicne[i])for i in range(len(self.navpicne))])

    def kopija(self):
        """ vrni kopijo te igre """
        kopija = Igra(None)
        kopija.vodoravne = [self.vodoravne[i][:] for i in range(8)]
        kopija.navpicne = [self.navpicne[i][:] for i in range(7)]
        kopija.matrika_kvadratov = [self.matrika_kvadratov[i][:] for i in range(7)]
        kopija.na_potezi = self.na_potezi.ime.get()
        kopija.nasprotnik = self.nasprotnik().ime.get()
        kopija.jaz = kopija.na_potezi
        kopija.jaz_stevec = self.na_potezi.stevec.get()
        kopija.nasprotnik_stevec = self.nasprotnik().stevec.get()
        kopija.zgodovina = self.zgodovina
        return kopija

    def shrani_pozicijo(self):
        """Shrani trenutno pozicijo, da se bomo lahko kasneje vrnili vanjo
           z metodo razveljavi."""
        vodoravne = [self.vodoravne[i][:] for i in range(8)]
        navpicne = [self.navpicne[i][:] for i in range(7)]
        kvadrati = [self.matrika_kvadratov[i][:] for i in range(7)]
        self.zgodovina.append((vodoravne, navpicne, kvadrati, self.na_potezi, self.vmesnik.igralec1.stevec.get(), self.vmesnik.igralec2.stevec.get()))

    def shrani_navidezno_pozicijo(self):
        """Shrani trenutno pozicijo, ki smo jo dobili v postopku racunalnikovega racunanja pozicije,
        da se bomo lahko kasneje vrnili vanjo z metodo razveljavi."""
        vodoravne = [self.vodoravne[i][:] for i in range(8)]
        navpicne = [self.navpicne[i][:] for i in range(7)]
        kvadrati = [self.matrika_kvadratov[i][:] for i in range(7)]
        self.zgodovina.append((vodoravne, navpicne, kvadrati, self.na_potezi, self.jaz_stevec, self.nasprotnik_stevec))

    def razveljavi(self, k=1):
        """k-krat razveljavi potezo in se vrni v prejsnje stanje."""
        if k:
            for i in range(k-1):
                del self.zgodovina[-1]
            (self.vodoravne, self.navpicne, self.matrika_kvadratov, self.na_potezi, self.jaz_stevec, self.nasprotnik_stevec) = self.zgodovina.pop()

    def veljavne_poteze(self):
        """Vrni seznam veljavnih potez."""
        poteze = []
        for i in range(8):
            for j in range(7):
                if not self.vodoravne[i][j]:
                    poteze.append(("vodoravno", i, j))
        for i in range(7):
            for j in range(8):
                if not self.navpicne[i][j]:
                    poteze.append(("navpicno", i, j))
        return poteze

    def popravi_matriko_kvadratov(self, k, i, j):
        """ po vsaki potezi popravi matriko, kjer je shranjeno stevilo ze narisanih crt okoli vsakega kvadrata """
        p = 0
        if k == "vodoravno":
            if i != 0:  # zgornji
                self.matrika_kvadratov[i-1][j] += 1
                if self.matrika_kvadratov[i-1][j] == 4:
                    p += 1
            if i != 7:  # spodnji
                self.matrika_kvadratov[i][j] += 1
                if self.matrika_kvadratov[i][j] == 4:
                    p += 1
        else:
            if j != 0:  # levi
                self.matrika_kvadratov[i][j-1] += 1
                if self.matrika_kvadratov[i][j-1] == 4:
                    p += 1
            if j != 7:  # desni
                self.matrika_kvadratov[i][j] += 1
                if self.matrika_kvadratov[i][j] == 4:
                    p += 1
        return p

    def nasprotnik(self):
        """ vrne nasprotnika """
        if self.na_potezi == self.vmesnik.igralec1:
            return self.vmesnik.igralec2
        elif self.na_potezi == self.vmesnik.igralec2:
            return self.vmesnik.igralec1
