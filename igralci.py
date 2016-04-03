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
        """ To metodo kliče vmesnik, če je treba prekiniti razmišljanje.
        Človek jo lahko ignorira. """
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
        """ algoritmu ukaze naj razmisli poteze """
        self.mislec = threading.Thread(
            target=lambda: self.algoritem.izracunaj_potezo(self.vmesnik.igra.kopija()))
        self.mislec.start()
        # cez 100ms preveri ali je algoritem ze izracunal poteze
        self.vmesnik.polje.after(100, self.preveri_potezo)

    def preveri_potezo(self):
        """ Vsakih 100ms preveri, ali je algoritem ze izracunal poteze in jih odigra """
        seznam_potez = self.algoritem.poteze
        if seznam_potez is not None:
            # Algoritem je nasel poteze, povleci jih, ce ni bilo prekinitve
            while seznam_potez:
                self.vmesnik.igra.racunalnik_povleci_potezo(seznam_potez.pop())
                time.sleep(0.5)
            # Vzporedno vlakno ni več aktivno, zato ga "pozabimo"
            self.mislec = None
            self.igra.sprememba_igralca()
            # ce igre se ni konec, poklice metodo, ki odigra naslednjo potezo nasprotnika
            if not self.igra.konec:
                if self.igra.na_potezi == self.vmesnik.igralec1:
                    self.vmesnik.igralec1.igraj()
                if self.igra.na_potezi == self.vmesnik.igralec2:
                    self.vmesnik.igralec2.igraj()
        else:
            # Algoritem se ni nasel potez, preveri se enkrat cez 100ms
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
                # ce je igralec v polju pustil kaksen kvadrat s tremi ze odigranimi stranicami,
                # nasprotnik odigra poteze s katerimi napolni verigo, ki ji pripada ta kvadrat
                while sum([x.count(3) for x in self.igra.matrika_kvadratov]):
                    st_potez += len(self.najdi_verigo(self.najdi(3, self.igra.matrika_kvadratov)))
                vrednost_pozicije = self.vrednost_pozicije()
                # ker smo v procesu napolnjevanja verig oddigrali nekaj potez,
                # jih moramo zdaj se razveljaviti, da pridemo na prejsnje stanje
                self.igra.razveljavi(st_potez)
                return vrednost_pozicije, seznam_potez
            else:
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    seznam = []  # seznam hrani vse poteze, ki jih bo racunalnik po koncu racunanja odigral
                    potrebne_poteze, zapri_poteze, stevec_potez = self.potrebno_pregledati()
                    self.igra.razveljavi(stevec_potez)  # poteze, ki smo jih naredili med iskanjem potrebnih potez
                    # 'dobre' poteze damo na zacetek
                    for poteza in zapri_poteze:
                        potrebne_poteze.insert(0, potrebne_poteze.pop(potrebne_poteze.index(poteza)))
                    for k, i, j in potrebne_poteze:
                        p = self.igra.navidezno_povleci_potezo((k, i, j))
                        if p:
                            # ce je napolnil kaksen kvadratek, je igralec spet na vrsti
                            vrednost, s = self.minimax(globina, maksimiziramo, seznam_potez)
                        else:
                            # ce ni napolnil nobenega kvadratka, je na vrsti drugi igralec
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
                    potrebne_poteze, zapri_poteze, stevec_potez = self.potrebno_pregledati()
                    self.igra.razveljavi(stevec_potez)  # poteze, ki smo jih naredili med iskanjem potrebnih potez
                    # 'dobre' poteze damo na zacetek
                    for poteza in zapri_poteze:
                        potrebne_poteze.insert(0, potrebne_poteze.pop(potrebne_poteze.index(poteza)))
                    for k, i, j in potrebne_poteze:
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
                    # ce je globina enaka zacetni globini, smo dobili potezo, ki jo bo igralec odigral
                    seznam_potez = seznam + [najboljsa_poteza]
                return vrednost_najboljse, seznam_potez

    def vrednost_pozicije(self):
        """Ocena vrednosti pozicije: izracuna razliko med kvadrati trenutnega igralca in nasprotnika."""
        return self.igra.jaz_stevec - self.igra.nasprotnik_stevec

    def najdi(self, element, matrika):
        """ najde mesto prve pojavitve elementa v matriki """
        i, j = None, None
        for n, vrs in enumerate(matrika):
            if vrs.count(element):
                j = vrs.index(element)
                i = n
                break
        return i, j

    def najdi_vse(self, element, matrika):
        """ najde vsa mesta pojavitve elementa v matriki """
        kvadrati = []
        for n, vrs in enumerate(matrika):
            if vrs.count(element):
                j = vrs.index(element)
                i = n
                kvadrati += [(i, j)]
        return kvadrati

    def prazna_stranica(self, i, j):
        """ najde prazno stranico v kvadratu (i, j), ki ima 3 polne stranice """
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
            poteza = self.prazna_stranica(i, j)
            if not poteza:  # lahko se zgodi v ciklu
                break
            self.igra.navidezno_povleci_potezo(poteza)
            poteze += [poteza]
            if poteza[0] == "vodoravno":
                if (poteza[1] == i+1) and (i != 6):
                    i += 1
                elif (poteza[1] == i) and (i != 0):
                    i -= 1
            elif poteza[0] == "navpicno":
                if (poteza[2] == j+1) and (j != 6):
                    j += 1
                elif (poteza[2] == j) and (j != 0):
                    j -= 1
        return poteze

    def potrebno_pregledati(self):
        """ poisce poteze, ki jih je potrebno pregledati med iskanjem najboljse poteze """
        potrebne_poteze = []  # poteze, ki jih mora pregledati
        koristne_poteze = []  # poteze, ki so del verig, ki jih lahko igralec zapre
        nevtralne_poteze = []  # poteze s katerimi nobeden od igralcev ne bo mogel zapreti kvadratkov
        skodljive_poteze = []  # poteze, ki bodo nasprotniku odprle verige
        zapri_poteze = []  # poteze, ki jih bo algoritem najprej pregledal (s temi potezami bo zaprl kvadratke)
        stevec_potez = 0
        # v verigah, ki jih lahko v tem trenutku zacnemo zapirati, so potrebne poteze le prvi dve in zadnja
        while sum([x.count(3) for x in self.igra.matrika_kvadratov]):
            i, j = self.najdi(3, self.igra.matrika_kvadratov)
            zapri_poteze += [self.prazna_stranica(i, j)]
            poteze = self.najdi_verigo((i, j))
            # zadnja poteza nam ne sme v matriko dodati kaksen kvadrat vrednosti 2, zato kvadratu,
            # ki ima za stranico zadnjo potezo in ni del verige, zmanjsamo vrednost
            zadnja_poteza = poteze[-1]
            if zadnja_poteza[0] == "vodoravno":
                e, f = zadnja_poteza[1], zadnja_poteza[2]
                if e != 7:
                    if self.igra.matrika_kvadratov[e][f] != 4:
                        self.igra.matrika_kvadratov[e][f] -= 1
                if e != 0:
                    if self.igra.matrika_kvadratov[e-1][f] != 4:
                        self.igra.matrika_kvadratov[e-1][f] -= 1
            elif zadnja_poteza[0] == "navpicno":
                e, f = zadnja_poteza[1], zadnja_poteza[2]
                if f != 7:
                    if self.igra.matrika_kvadratov[e][f] != 4:
                        self.igra.matrika_kvadratov[e][f] -= 1
                if f != 0:
                    if self.igra.matrika_kvadratov[e][f-1] != 4:
                        self.igra.matrika_kvadratov[e][f-1] -= 1
            if len(poteze) > 3:
                koristne_poteze += poteze[:2]
                koristne_poteze += [poteze[-1]]
            else:
                koristne_poteze += poteze
            stevec_potez += len(poteze)
        # v verigah, ki jih se ne moremo zapirati, je potrebna le ena poteza
        while sum([x.count(2) for x in self.igra.matrika_kvadratov]):
            i, j = self.najdi(2, self.igra.matrika_kvadratov)
            k, e, f = self.prazna_stranica(i, j)
            self.igra.navidezno_povleci_potezo((k, e, f))
            stevec_potez += 1
            # poteza, ki smo jo pravkar odigrali, na verigo razdeli na dva dela - pogledati moramo oba
            ena_stran = self.najdi_verigo((i, j))
            stevec_potez += len(ena_stran)
            # zadnja poteza nam ne sme v matriko dodati kaksen kvadrat vrednosti 2, zato kvadratu,
            # ki ima za stranico zadnjo potezo in ni del verige, zmanjsamo vrednost
            zadnja_poteza = ena_stran[-1]
            if zadnja_poteza[0] == "vodoravno":
                n, m = zadnja_poteza[1], zadnja_poteza[2]
                if n != 7:
                    if self.igra.matrika_kvadratov[n][m] != 4:
                        self.igra.matrika_kvadratov[n][m] -= 1
                if n != 0:
                    if self.igra.matrika_kvadratov[n-1][m] != 4:
                        self.igra.matrika_kvadratov[n-1][m] -= 1
            elif zadnja_poteza[0] == "navpicno":
                n, m = zadnja_poteza[1], zadnja_poteza[2]
                if m != 7:
                    if self.igra.matrika_kvadratov[n][m] != 4:
                        self.igra.matrika_kvadratov[n][m] -= 1
                if m != 0:
                    if self.igra.matrika_kvadratov[n][m-1] != 4:
                        self.igra.matrika_kvadratov[n][m-1] -= 1
            druga_stran = []
            if k == "vodoravno":
                if (e == i+1) and (i != 6):
                    druga_stran = self.najdi_verigo((i+1, j))
                    # tudi tukaj moramo paziti, da ne dobimo dodatnega kvadrata vrednosti 2
                    if not druga_stran:
                        self.igra.matrika_kvadratov[i+1][j] -= 1
                elif (e == i) and (i != 0):
                    druga_stran = self.najdi_verigo((i-1, j))
                    if not druga_stran:
                        self.igra.matrika_kvadratov[i-1][j] -= 1
            elif k == "navpicno":
                if (f == j+1) and (j != 6):
                    druga_stran = self.najdi_verigo((i, j+1))
                    if not druga_stran:
                        self.igra.matrika_kvadratov[i][j+1] -= 1
                elif (f == j) and (j != 0):
                    druga_stran = self.najdi_verigo((i, j-1))
                    if not druga_stran:
                        self.igra.matrika_kvadratov[i][j-1] -= 1
            stevec_potez += len(druga_stran)
            skodljive_poteze += [(len(ena_stran)+len(druga_stran), (k, e, f))]
            if druga_stran:
                # zadnja poteza nam ne sme v matriko dodati kaksen kvadrat vrednosti 2, zato kvadratu,
                # ki ima za stranico zadnjo potezo in ni del verige, zmanjsamo vrednost
                zadnja_poteza = druga_stran[-1]
                if zadnja_poteza[0] == "vodoravno":
                    e, f = zadnja_poteza[1], zadnja_poteza[2]
                    if e != 7:
                        if self.igra.matrika_kvadratov[e][f] != 4:
                            self.igra.matrika_kvadratov[e][f] -= 1
                    if e != 0:
                        if self.igra.matrika_kvadratov[e-1][f] != 4:
                            self.igra.matrika_kvadratov[e-1][f] -= 1
                elif zadnja_poteza[0] == "navpicno":
                    e, f = zadnja_poteza[1], zadnja_poteza[2]
                    if f != 7:
                        if self.igra.matrika_kvadratov[e][f] != 4:
                            self.igra.matrika_kvadratov[e][f] -= 1
                    if f != 0:
                        if self.igra.matrika_kvadratov[e][f-1] != 4:
                            self.igra.matrika_kvadratov[e][f-1] -= 1
        # preveriti je potrebno se tiste poteze, ki niso del nobene verige
        for i in range(8):
            for j in range(7):
                if not self.igra.vodoravne[i][j]:
                    nevtralne_poteze.append(("vodoravno", i, j))
        for i in range(7):
            for j in range(8):
                if not self.igra.navpicne[i][j]:
                    nevtralne_poteze.append(("navpicno", i, j))
        random.shuffle(nevtralne_poteze)
        potrebne_poteze += koristne_poteze  # najprej bo algoritem pregledal koristne poteze,
        potrebne_poteze += nevtralne_poteze  # nato nevtralne,
        # na koncu pa se skodljive od tiste, ki je del najkrajse verige do tiste, ki je del najdaljse verige
        skodljive_poteze.sort(key=lambda x: x[0])
        for v, poteza in skodljive_poteze:
            potrebne_poteze += [poteza]
        return potrebne_poteze, zapri_poteze, stevec_potez


class AlfaBeta:

    def __init__(self, globina):
        self.globina = globina
        self.prekinitev = False
        self.igra = None
        self.jaz = None
        self.poteze = None

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
                st_potez = 0
                # ce je igralec v polju pustil kaksen kvadrat s tremi ze odigranimi stranicami,
                # nasprotnik odigra poteze s katerimi napolni verigo, ki ji pripada ta kvadrat
                while sum([x.count(3) for x in self.igra.matrika_kvadratov]):
                    st_potez += len(self.najdi_verigo(self.najdi(3, self.igra.matrika_kvadratov)))
                vrednost_pozicije = self.vrednost_pozicije()
                # ker smo v procesu napolnjevanja verig oddigrali nekaj potez,
                # jih moramo zdaj se razveljaviti, da pridemo na prejsnje stanje
                self.igra.razveljavi(st_potez)
                return vrednost_pozicije, seznam_potez
            else:
                # Naredimo eno stopnjo alfabeta
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    seznam = []  # seznam hrani vse poteze, ki jih bo racunalnik po koncu racunanja odigral
                    potrebne_poteze, zapri_poteze, stevec_potez = self.potrebno_pregledati()
                    self.igra.razveljavi(stevec_potez)  # poteze, ki smo jih naredili med iskanjem potrebnih potez
                    # 'dobre' poteze damo na zacetek
                    for poteza in zapri_poteze:
                        potrebne_poteze.insert(0, potrebne_poteze.pop(potrebne_poteze.index(poteza)))
                    for k, i, j in potrebne_poteze:
                        p = self.igra.navidezno_povleci_potezo((k, i, j))
                        if p:
                            # ce je napolnil kaksen kvadratek, je igralec spet na vrsti
                            vrednost, s = self.alfabeta(globina, alfa, beta, maksimiziramo, seznam_potez)
                        else:
                            # ce ni napolnil nobenega kvadratka, je na vrsti drugi igralec
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
                    potrebne_poteze, zapri_poteze, stevec_potez = self.potrebno_pregledati()
                    self.igra.razveljavi(stevec_potez)  # poteze, ki smo jih naredili med iskanjem potrebnih potez
                    # 'dobre' poteze damo na zacetek
                    for poteza in zapri_poteze:
                        potrebne_poteze.insert(0, potrebne_poteze.pop(potrebne_poteze.index(poteza)))
                    for k, i, j in potrebne_poteze:
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
                    # ce je globina enaka zacetni globini, smo dobili potezo, ki jo bo igralec odigral
                    seznam_potez = seznam + [najboljsa_poteza]
                return vrednost_najboljse, seznam_potez

    def vrednost_pozicije(self):
        """Ocena vrednosti pozicije: izracuna razliko med kvadrati trenutnega igralca in nasprotnika."""
        return self.igra.jaz_stevec - self.igra.nasprotnik_stevec

    def najdi(self, element, matrika):
        """ najde mesto prve pojavitve elementa v matriki """
        i, j = None, None
        for n, vrs in enumerate(matrika):
            if vrs.count(element):
                j = vrs.index(element)
                i = n
                break
        return i, j

    def najdi_vse(self, element, matrika):
        """ najde vsa mesta pojavitve elementa v matriki """
        kvadrati = []
        for n, vrs in enumerate(matrika):
            if vrs.count(element):
                j = vrs.index(element)
                i = n
                kvadrati += [(i, j)]
        return kvadrati

    def prazna_stranica(self, i, j):
        """ najde eno prazno stranico v kvadratu (i, j) """
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
            poteza = self.prazna_stranica(i, j)
            if not poteza:  # lahko se zgodi v ciklu
                break
            self.igra.navidezno_povleci_potezo(poteza)
            poteze += [poteza]
            if poteza[0] == "vodoravno":
                if (poteza[1] == i+1) and (i != 6):
                    i += 1
                elif (poteza[1] == i) and (i != 0):
                    i -= 1
            elif poteza[0] == "navpicno":
                if (poteza[2] == j+1) and (j != 6):
                    j += 1
                elif (poteza[2] == j) and (j != 0):
                    j -= 1
        return poteze

    def potrebno_pregledati(self):
        """ poisce poteze, ki jih je potrebno pregledati med iskanjem najboljse poteze """
        potrebne_poteze = []  # poteze, ki jih mora pregledati
        koristne_poteze = []  # poteze, ki so del verig, ki jih lahko igralec zapre
        nevtralne_poteze = []  # poteze s katerimi nobeden od igralcev ne bo mogel zapreti kvadratkov
        skodljive_poteze = []  # poteze, ki bodo nasprotniku odprle verige
        zapri_poteze = []  # poteze, ki jih bo algoritem najprej pregledal (s temi potezami bo zaprl kvadratke)
        stevec_potez = 0
        # v verigah, ki jih lahko v tem trenutku zacnemo zapirati, so potrebne poteze le prvi dve in zadnja
        while sum([x.count(3) for x in self.igra.matrika_kvadratov]):
            i, j = self.najdi(3, self.igra.matrika_kvadratov)
            zapri_poteze += [self.prazna_stranica(i, j)]
            poteze = self.najdi_verigo((i, j))
            # zadnja poteza nam ne sme v matriko dodati kaksen kvadrat vrednosti 2, zato kvadratu,
            # ki ima za stranico zadnjo potezo in ni del verige, zmanjsamo vrednost
            zadnja_poteza = poteze[-1]
            if zadnja_poteza[0] == "vodoravno":
                e, f = zadnja_poteza[1], zadnja_poteza[2]
                if e != 7:
                    if self.igra.matrika_kvadratov[e][f] != 4:
                        self.igra.matrika_kvadratov[e][f] -= 1
                if e != 0:
                    if self.igra.matrika_kvadratov[e-1][f] != 4:
                        self.igra.matrika_kvadratov[e-1][f] -= 1
            elif zadnja_poteza[0] == "navpicno":
                e, f = zadnja_poteza[1], zadnja_poteza[2]
                if f != 7:
                    if self.igra.matrika_kvadratov[e][f] != 4:
                        self.igra.matrika_kvadratov[e][f] -= 1
                if f != 0:
                    if self.igra.matrika_kvadratov[e][f-1] != 4:
                        self.igra.matrika_kvadratov[e][f-1] -= 1
            if len(poteze) > 3:
                koristne_poteze += poteze[:2]
                koristne_poteze += [poteze[-1]]
            else:
                koristne_poteze += poteze
            stevec_potez += len(poteze)
        # v verigah, ki jih se ne moremo zapirati, je potrebna le ena poteza
        while sum([x.count(2) for x in self.igra.matrika_kvadratov]):
            i, j = self.najdi(2, self.igra.matrika_kvadratov)
            k, e, f = self.prazna_stranica(i, j)
            self.igra.navidezno_povleci_potezo((k, e, f))
            stevec_potez += 1
            # poteza, ki smo jo pravkar odigrali, na verigo razdeli na dva dela - pogledati moramo oba
            ena_stran = self.najdi_verigo((i, j))
            stevec_potez += len(ena_stran)
            # zadnja poteza nam ne sme v matriko dodati kaksen kvadrat vrednosti 2, zato kvadratu,
            # ki ima za stranico zadnjo potezo in ni del verige, zmanjsamo vrednost
            zadnja_poteza = ena_stran[-1]
            if zadnja_poteza[0] == "vodoravno":
                n, m = zadnja_poteza[1], zadnja_poteza[2]
                if n != 7:
                    if self.igra.matrika_kvadratov[n][m] != 4:
                        self.igra.matrika_kvadratov[n][m] -= 1
                if n != 0:
                    if self.igra.matrika_kvadratov[n-1][m] != 4:
                        self.igra.matrika_kvadratov[n-1][m] -= 1
            elif zadnja_poteza[0] == "navpicno":
                n, m = zadnja_poteza[1], zadnja_poteza[2]
                if m != 7:
                    if self.igra.matrika_kvadratov[n][m] != 4:
                        self.igra.matrika_kvadratov[n][m] -= 1
                if m != 0:
                    if self.igra.matrika_kvadratov[n][m-1] != 4:
                        self.igra.matrika_kvadratov[n][m-1] -= 1
            druga_stran = []
            if k == "vodoravno":
                if (e == i+1) and (i != 6):
                    druga_stran = self.najdi_verigo((i+1, j))
                    # tudi tukaj moramo paziti, da ne dobimo dodatnega kvadrata vrednosti 2
                    if not druga_stran:
                        self.igra.matrika_kvadratov[i+1][j] -= 1
                elif (e == i) and (i != 0):
                    druga_stran = self.najdi_verigo((i-1, j))
                    if not druga_stran:
                        self.igra.matrika_kvadratov[i-1][j] -= 1
            elif k == "navpicno":
                if (f == j+1) and (j != 6):
                    druga_stran = self.najdi_verigo((i, j+1))
                    if not druga_stran:
                        self.igra.matrika_kvadratov[i][j+1] -= 1
                elif (f == j) and (j != 0):
                    druga_stran = self.najdi_verigo((i, j-1))
                    if not druga_stran:
                        self.igra.matrika_kvadratov[i][j-1] -= 1
            stevec_potez += len(druga_stran)
            skodljive_poteze += [(len(ena_stran)+len(druga_stran), (k, e, f))]
            if druga_stran:
                # zadnja poteza nam ne sme v matriko dodati kaksen kvadrat vrednosti 2, zato kvadratu,
                # ki ima za stranico zadnjo potezo in ni del verige, zmanjsamo vrednost
                zadnja_poteza = druga_stran[-1]
                if zadnja_poteza[0] == "vodoravno":
                    e, f = zadnja_poteza[1], zadnja_poteza[2]
                    if e != 7:
                        if self.igra.matrika_kvadratov[e][f] != 4:
                            self.igra.matrika_kvadratov[e][f] -= 1
                    if e != 0:
                        if self.igra.matrika_kvadratov[e-1][f] != 4:
                            self.igra.matrika_kvadratov[e-1][f] -= 1
                elif zadnja_poteza[0] == "navpicno":
                    e, f = zadnja_poteza[1], zadnja_poteza[2]
                    if f != 7:
                        if self.igra.matrika_kvadratov[e][f] != 4:
                            self.igra.matrika_kvadratov[e][f] -= 1
                    if f != 0:
                        if self.igra.matrika_kvadratov[e][f-1] != 4:
                            self.igra.matrika_kvadratov[e][f-1] -= 1
        # preveriti je potrebno se tiste poteze, ki niso del nobene verige
        for i in range(8):
            for j in range(7):
                if not self.igra.vodoravne[i][j]:
                    nevtralne_poteze.append(("vodoravno", i, j))
        for i in range(7):
            for j in range(8):
                if not self.igra.navpicne[i][j]:
                    nevtralne_poteze.append(("navpicno", i, j))
        random.shuffle(nevtralne_poteze)
        potrebne_poteze += koristne_poteze  # najprej bo algoritem pregledal koristne poteze,
        potrebne_poteze += nevtralne_poteze  # nato nevtralne,
        # na koncu pa se skodljive od tiste, ki je del najkrajse verige do tiste, ki je del najdaljse verige
        skodljive_poteze.sort(key=lambda x: x[0])  
        for v, poteza in skodljive_poteze:
            potrebne_poteze += [poteza]
        return potrebne_poteze, zapri_poteze, stevec_potez
