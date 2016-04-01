__author__ = 'SusnikT12'

import threading
import time
import random


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
        self.algoritem = algoritem  # Algoritem, ki izra�una potezo
        self.vmesnik = vmesnik
        self.igra = None
        self.mislec = None

    def igraj(self):
        """Igraj potezo, ki jo vrne algoritem."""
        self.mislec = threading.Thread(
            target=lambda: self.algoritem.izracunaj_potezo(self.vmesnik.igra.kopija()))
        self.mislec.start()
        self.vmesnik.polje.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem ze izracunal potezo."""
        seznam_potez = self.algoritem.poteze
        if seznam_potez is not None:
            # Algoritem je nasel potezo, povleci jo, ce ni bilo prekinitve
            while seznam_potez:
                self.vmesnik.igra.racunalnik_povleci_potezo(seznam_potez.pop())
                time.sleep(0.5)
            self.mislec = None
            self.igra.sprememba_igralca()
            if not self.igra.konec:
                if self.igra.na_potezi == self.vmesnik.igralec1:
                    self.vmesnik.igralec1.igraj()
                if self.igra.na_potezi == self.vmesnik.igralec2:
                    self.vmesnik.igralec2.igraj()
            # Vzporedno vlakno ni vec aktivno, zato ga "pozabimo"
        else:
            # Algoritem se ni nasel poteze, preveri se enkrat cez 100ms
            self.vmesnik.polje.after(100, self.preveri_potezo)

    def prekini(self):
        """ To metodo klice GUI, ce je treba prekiniti razmisljanje. """
        if self.mislec:
            self.algoritem.prekini()
            self.mislec.join()
            self.mislec = None

    def klik(self, x, y):
        """ racunalnik ignorira klike na igralnem polju """
        pass


class Minimax:

    def __init__(self, globina):
        self.globina = globina
        self.prekinitev = False
        self.igra = None
        self.jaz = None
        self.poteze = None
        self.kopija_vodoravne = None
        self.kopija_navpicne = None
        self.kopija_matrika_kvadratov = None

    ZMAGA = 100000
    NESKONCNO = ZMAGA + 1

    def prekini(self):
        """Metoda, ki jo poklice GUI, ce je treba nehati razmisljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izracunaj potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.poteze = None
        (vrednost, seznam_potez) = self.minimax(self.globina, True, [])
        self.igra = None
        if not self.prekinitev:
            self.poteze = seznam_potez

    def minimax(self, globina, maksimiziramo, seznam_potez):
        """Glavna metoda minimax."""
        if self.prekinitev:
            return 0, []
        if self.igra.jaz_stevec + self.igra.nasprotnik_stevec == 49:
            # Igre je konec, vrnemo njeno vrednost
            if self.igra.na_potezi == self.igra.jaz:
                return Minimax.ZMAGA, seznam_potez
            else:
                return -Minimax.ZMAGA, seznam_potez
        else:
            # Igre ni konec
            if globina == 0:
                st_potez = 0
                while sum([x.count(3) for x in self.igra.matrika_kvadratov]):
                    st_potez += self.napolni_verigo(self.najdi(3, self.igra.matrika_kvadratov))
                vrednost_pozicije = self.vrednost_pozicije()
                for i in range(st_potez):
                    self.igra.razveljavi()
                return vrednost_pozicije, seznam_potez
            else:
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    seznam = []
                    veljavne = self.igra.veljavne_poteze()
                    random.shuffle(veljavne)
                    for k, i, j in veljavne:
                        p = self.igra.navidezno_povleci_potezo((k, i, j))
                        if p:
                            vrednost, s = self.minimax(globina, maksimiziramo, seznam_potez)
                        else:
                            vrednost, s = self.minimax(globina-1, not maksimiziramo, seznam_potez)
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = (k, i, j)
                            seznam = s
                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = Minimax.NESKONCNO
                    seznam = []
                    veljavne = self.igra.veljavne_poteze()
                    random.shuffle(veljavne)
                    for k, i, j in veljavne:
                        p = self.igra.navidezno_povleci_potezo((k, i, j))
                        if p:
                            vrednost, s = self.minimax(globina, maksimiziramo, seznam_potez)
                        else:
                            vrednost, s = self.minimax(globina-1, not maksimiziramo, seznam_potez)
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = k, i, j
                assert (najboljsa_poteza is not None), "minimax: izracunana poteza je None"
                if globina == self.globina:
                    seznam_potez = seznam + [najboljsa_poteza]
                return vrednost_najboljse, seznam_potez

    def vrednost_pozicije(self):
        return self.igra.jaz_stevec - self.igra.nasprotnik_stevec

    def napolni_verigo(self, index):
        """ napolni odprto verigo, ki ji pripada kvadratek (i, j) """
        i, j = index
        st_potez = 0
        while self.kopija_matrika_kvadratov[i][j] == 3:
            st_potez += 1
            if not self.kopija_vodoravne[i][j]:
                self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                if i != 0:
                    i -= 1
            elif not self.igra.vodoravne[i+1][j]:
                self.igra.navidezno_povleci_potezo(("vodoravno", i+1, j))
                if i != 6:
                    i += 1
            elif not self.igra.navpicne[i][j]:
                self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                if j != 0:
                    j -= 1
            elif not self.igra.navpicne[i][j+1]:
                self.igra.navidezno_povleci_potezo(("navpicno", i, j+1))
                if j != 6:
                    j += 1
        return st_potez

    def najdi(self, element, seznam):
        i, j = None, None
        for n, vrs in enumerate(seznam):
            if seznam[n].count(element):
                j = seznam[n].index(element)
                i = n
                break
        return i, j


class AlfaBeta:

    def __init__(self, globina):
        self.globina = globina
        self.prekinitev = False
        self.igra = None
        self.jaz = None
        self.poteze = None
        self.kopija_vodoravne = None
        self.kopija_navpicne = None
        self.kopija_matrika_kvadratov = None

    ZMAGA = 100000
    NESKONCNO = ZMAGA + 1

    def prekini(self):
        """Metoda, ki jo poklice GUI, ce je treba nehati razmisljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izracunaj potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.poteze = None
        (vrednost, seznam_potez) = self.alfabeta(self.globina, -Minimax.NESKONCNO, Minimax.NESKONCNO, True, [])
        self.igra = None
        if not self.prekinitev:
            self.poteze = seznam_potez

    def alfabeta(self, globina, alfa, beta, maksimiziramo, seznam_potez):
        """Glavna metoda alfabeta."""
        if self.prekinitev:
            return 0, []
        if self.igra.jaz_stevec + self.igra.nasprotnik_stevec == 49:
            # Igre je konec, vrnemo njeno vrednost
            if self.igra.na_potezi == self.igra.jaz:
                return Minimax.ZMAGA, seznam_potez
            else:
                return -Minimax.ZMAGA, seznam_potez
        else:
            # Igre ni konec
            if globina == 0:
                a = [self.igra.matrika_kvadratov[i][:] for i in range(7)]
                st_potez = 0
                while sum([x.count(3) for x in self.igra.matrika_kvadratov]):
                    st_potez += self.napolni_verigo(self.najdi(3, self.igra.matrika_kvadratov))
                vrednost_pozicije = self.vrednost_pozicije()
                for i in range(st_potez):
                    self.igra.razveljavi()
                return vrednost_pozicije, seznam_potez
            else:
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    seznam = []
                    veljavne = self.igra.veljavne_poteze()
                    random.shuffle(veljavne)
                    nepotrebne_poteze = []
                    if sum([x.count(3) for x in self.igra.matrika_kvadratov]):
                        kvadrati = self.najdi_vse(3, self.igra.matrika_kvadratov)
                        for i, j in kvadrati:
                            veljavne.insert(0, veljavne.pop(veljavne.index(self.prazna_stranica(i, j))))
                            poteze = self.najdi_verigo((i, j))
                            if len(poteze) > 2:
                                nepotrebne_poteze += poteze[1:-1]
                    for poteza in set(nepotrebne_poteze):
                        del veljavne[veljavne.index(poteza)]
                    for k, i, j in veljavne:
                        p = self.igra.navidezno_povleci_potezo((k, i, j))
                        if p:
                            vrednost, s = self.alfabeta(globina, alfa, beta, maksimiziramo, seznam_potez)
                        else:
                            vrednost, s = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, seznam_potez)
                        self.igra.razveljavi()
                        alfa = max(alfa, vrednost)
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = (k, i, j)
                            seznam = s
                        if beta <= alfa:
                            break
                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = Minimax.NESKONCNO
                    veljavne = self.igra.veljavne_poteze()
                    random.shuffle(veljavne)
                    nepotrebne_poteze = []
                    if sum([x.count(3) for x in self.igra.matrika_kvadratov]):
                        kvadrati = self.najdi_vse(3, self.igra.matrika_kvadratov)
                        for i, j in kvadrati:
                            veljavne.insert(0, veljavne.pop(veljavne.index(self.prazna_stranica(i, j))))
                            poteze = self.najdi_verigo((i, j))
                            if len(poteze) > 2:
                                nepotrebne_poteze += poteze[1:-1]
                    for poteza in set(nepotrebne_poteze):
                        del veljavne[veljavne.index(poteza)]
                    for k, i, j in veljavne:
                        p = self.igra.navidezno_povleci_potezo((k, i, j))
                        if p:
                            vrednost, s = self.alfabeta(globina, alfa, beta, maksimiziramo, seznam_potez)
                        else:
                            vrednost, s = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, seznam_potez)
                        self.igra.razveljavi()
                        beta = min(beta, vrednost)
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = k, i, j
                        if beta <= alfa:
                            break
                assert (najboljsa_poteza is not None), "alfabeta: izracunana poteza je None"
                if globina == self.globina:
                    seznam_potez = seznam + [najboljsa_poteza]
                return vrednost_najboljse, seznam_potez

    def vrednost_pozicije(self):
        return self.igra.jaz_stevec - self.igra.nasprotnik_stevec

    def napolni_verigo(self, index):
        """ napolni odprto verigo, ki ji pripada kvadratek (i, j) """
        i, j = index
        st_potez = 0
        while self.igra.matrika_kvadratov[i][j] == 3:
            st_potez += 1
            if not self.igra.vodoravne[i][j]:
                self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                if i != 0:
                    i -= 1
            elif not self.igra.vodoravne[i+1][j]:
                self.igra.navidezno_povleci_potezo(("vodoravno", i+1, j))
                if i != 6:
                    i += 1
            elif not self.igra.navpicne[i][j]:
                self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                if j != 0:
                    j -= 1
            elif not self.igra.navpicne[i][j+1]:
                self.igra.navidezno_povleci_potezo(("navpicno", i, j+1))
                if j != 6:
                    j += 1
        return st_potez

    def najdi(self, element, seznam):
        i, j = None, None
        for n, vrs in enumerate(seznam):
            if seznam[n].count(element):
                j = seznam[n].index(element)
                i = n
                break
        return i, j

    def najdi_vse(self, element, seznam):
        i, j = None, None
        kvadrati = []
        for n, vrs in enumerate(seznam):
            if seznam[n].count(element):
                j = seznam[n].index(element)
                i = n
                kvadrati += [(i, j)]
        return kvadrati

    def prazna_stranica(self, i, j):
        if not self.igra.vodoravne[i][j]:
            return "vodoravno", i, j
        elif not self.igra.vodoravne[i+1][j]:
            return "vodoravno", i+1, j
        elif not self.igra.navpicne[i][j]:
            return "navpicno", i, j
        elif not self.igra.navpicne[i][j+1]:
            return "navpicno", i, j+1

    def najdi_verigo(self, index):
        """ najde poteze s katerimi napolnimo odprto verigo, ki ji pripada kvadratek (i, j) """
        i, j = index
        poteze = []
        while self.igra.matrika_kvadratov[i][j] == 3:
            if not self.igra.vodoravne[i][j]:
                self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                poteze += [("vodoravno", i, j)]
                if i != 0:
                    i -= 1
            elif not self.igra.vodoravne[i+1][j]:
                self.igra.navidezno_povleci_potezo(("vodoravno", i+1, j))
                poteze += [("vodoravno", i+1, j)]
                if i != 6:
                    i += 1
            elif not self.igra.navpicne[i][j]:
                self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                poteze += [("navpicno", i, j)]
                if j != 0:
                    j -= 1
            elif not self.igra.navpicne[i][j+1]:
                self.igra.navidezno_povleci_potezo(("navpicno", i, j+1))
                poteze += [("navpicno", i, j+1)]
                if j != 6:
                    j += 1
        for i in range(len(poteze)):
            self.igra.razveljavi()
        return poteze