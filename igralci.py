__author__ = 'uporabnik'
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
        self.algoritem = algoritem  # Algoritem, ki izračuna potezo
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
        """Vsakih 100ms preveri, ali je algoritem že izračunal potezo."""
        seznam_potez = self.algoritem.poteze
        if seznam_potez is not None:
            # Algoritem je našel potezo, povleci jo, če ni bilo prekinitve
            while seznam_potez:
                self.vmesnik.igra.racunalnik_povleci_potezo(seznam_potez.pop())
                time.sleep(0.5)
            self.mislec = None
            self.igra.sprememba_igralca()
            if self.igra.na_potezi == self.vmesnik.igralec1:
                self.vmesnik.igralec1.igraj()
            if self.igra.na_potezi == self.vmesnik.igralec2:
                self.vmesnik.igralec2.igraj()
            # Vzporedno vlakno ni več aktivno, zato ga "pozabimo"
        else:
            # Algoritem še ni našel poteze, preveri še enkrat čez 100ms
            self.vmesnik.polje.after(100, self.preveri_potezo)

    def prekini(self):
        """ To metodo kliče GUI, če je treba prekiniti razmišljanje. """
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
        """Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izračunaj potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_potezi
        self.poteze = None
        (poteza, vrednost, seznam_potez) = self.minimax(self.globina, True, None, [])
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            self.poteze = seznam_potez

    def minimax(self, globina, maksimiziramo, p, seznam_potez):
        """Glavna metoda minimax."""
        if self.prekinitev:
            return None, 0
        if self.igra.konec_igre1():
            # Igre je konec, vrnemo njeno vrednost
            if self.igra.na_potezi == self.jaz:
                return None, Minimax.ZMAGA, seznam_potez
            else:
                return None, -Minimax.ZMAGA, seznam_potez
        else:
            # Igre ni konec
            if globina == 0:
                vrednost_pozicije, kopija = self.vrednost_pozicije(p)
                if vrednost_pozicije > 0:
                    self.igra.zgodovina.append((kopija[0], kopija[1], kopija[2], self.igra.na_potezi))
                    vrednost_pozicije += self.minimax(1, not maksimiziramo, None, seznam_potez)[1]
                    self.igra.razveljavi()
                return None, vrednost_pozicije, seznam_potez
            else:
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza_n = None
                    najboljsa_poteza_v = None
                    vrednost_najboljse_v = -Minimax.NESKONCNO
                    vrednost_najboljse_n = -Minimax.NESKONCNO
                    seznam_v = []
                    seznam_n = []
                    v_veljavne, n_veljavne = self.igra.veljavne_poteze()
                    random.shuffle(v_veljavne)
                    random.shuffle(n_veljavne)
                    for i, j in v_veljavne:
                        if globina != 1:
                            p = self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                            if p:
                                poteza, v, s = self.minimax(globina, maksimiziramo, ("vodoravno", i, j), seznam_potez)
                                vrednost = v + p
                            else:
                                poteza, v, s = self.minimax(globina-1, not maksimiziramo, ("vodoravno", i, j), seznam_potez)
                                vrednost = v
                        else:
                            poteza, v, s = self.minimax(globina-1, not maksimiziramo, ("vodoravno", i, j), seznam_potez)
                            vrednost = v
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse_v:
                            vrednost_najboljse_v = vrednost
                            najboljsa_poteza_v = ("vodoravno", i, j)
                            seznam_v = s
                    for i, j in n_veljavne:
                        if globina != 1:
                            p = self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                            if p:
                                poteza, v, s = self.minimax(globina, maksimiziramo, ("navpicno", i, j), seznam_potez)
                                vrednost = v + p
                            else:
                                poteza, v, s = self.minimax(globina-1, not maksimiziramo, ("navpicno", i, j), seznam_potez)
                                vrednost = v
                        else:
                            poteza, v, s = self.minimax(globina-1, not maksimiziramo, ("navpicno", i, j), seznam_potez)
                            vrednost = v
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse_n:
                            vrednost_najboljse_n = vrednost
                            najboljsa_poteza_n = ("navpicno", i, j)
                            seznam_n = s
                    if vrednost_najboljse_v == vrednost_najboljse_n:
                        vrednost_najboljse, najboljsa_poteza, seznam = \
                            random.choice([(vrednost_najboljse_v, najboljsa_poteza_v, seznam_v), (vrednost_najboljse_n, najboljsa_poteza_n, seznam_n)])
                    else:
                        if vrednost_najboljse_v > vrednost_najboljse_n:
                            vrednost_najboljse, najboljsa_poteza, seznam = vrednost_najboljse_v, najboljsa_poteza_v, seznam_v
                        else:
                            vrednost_najboljse, najboljsa_poteza, seznam = vrednost_najboljse_n, najboljsa_poteza_n, seznam_n
                else:
                    # Minimiziramo
                    najboljsa_poteza_v = None
                    najboljsa_poteza_n = None
                    vrednost_najboljse_v = Minimax.NESKONCNO
                    vrednost_najboljse_n = Minimax.NESKONCNO
                    v_veljavne, n_veljavne = self.igra.veljavne_poteze()
                    random.shuffle(v_veljavne)
                    random.shuffle(n_veljavne)
                    for i, j in v_veljavne:
                        if globina != 1:
                            p = self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                            if p:
                                vrednost = - self.minimax(globina, maksimiziramo, ("vodoravno", i, j), seznam_potez)[1] - p
                            else:
                                vrednost = - self.minimax(globina-1, not maksimiziramo, ("vodoravno", i, j), seznam_potez)[1]
                        else:
                            vrednost = - self.minimax(globina-1, not maksimiziramo, ("vodoravno", i, j), seznam_potez)[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse_v:
                            vrednost_najboljse_v = vrednost
                            najboljsa_poteza_v = "vodoravno", i, j
                    for i, j in n_veljavne:
                        if globina != 1:
                            p = self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                            if p:
                                vrednost = - self.minimax(globina, maksimiziramo, ("navpicno", i, j), seznam_potez)[1] - p
                            else:
                                vrednost = - self.minimax(globina-1, not maksimiziramo, ("navpicno", i, j), seznam_potez)[1]
                        else:
                            vrednost = - self.minimax(globina-1, not maksimiziramo, ("navpicno", i, j), seznam_potez)[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse_n:
                            vrednost_najboljse_n = vrednost
                            najboljsa_poteza_n = ("navpicno", i, j)
                    if vrednost_najboljse_v == vrednost_najboljse_n:
                        vrednost_najboljse, najboljsa_poteza = \
                            random.choice([(vrednost_najboljse_v, najboljsa_poteza_v), (vrednost_najboljse_n, najboljsa_poteza_n)])
                    else:
                        if vrednost_najboljse_v < vrednost_najboljse_n:
                            vrednost_najboljse, najboljsa_poteza = vrednost_najboljse_v, najboljsa_poteza_v
                        else:
                            vrednost_najboljse, najboljsa_poteza = vrednost_najboljse_n, najboljsa_poteza_n
                assert (najboljsa_poteza is not None), "minimax: izračunana poteza je None"
                if globina == self.globina:
                    seznam_potez = seznam + [najboljsa_poteza]
                return najboljsa_poteza, vrednost_najboljse, seznam_potez

    def vrednost_pozicije(self, p):
        k, i, j = p
        vrednost = 0
        kopija = []
        if k == "vodoravno":
            if i != 0:  # zgornji
                if self.igra.vodoravne[i-1][j]+self.igra.navpicne[i-1][j]+self.igra.navpicne[i-1][j+1] == 2:
                    self.kopiraj()
                    self.kopija_vodoravne[i][j] = True
                    self.kopija_matrika_kvadratov[i-1][j] += 1
                    if i != 7:
                        self.kopija_matrika_kvadratov[i][j] += 1
                    vrednost = - self.dolzina_verige(k, i, j)
                elif self.igra.vodoravne[i-1][j]+self.igra.navpicne[i-1][j]+self.igra.navpicne[i-1][j+1] == 3:
                    self.kopiraj()
                    vrednost = self.dolzina_verige(k, i, j)
                kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
            if i != 7:  # spodnji
                if self.igra.vodoravne[i+1][j]+self.igra.navpicne[i][j]+self.igra.navpicne[i][j+1] == 2:
                    self.kopiraj()
                    self.kopija_vodoravne[i][j] = True
                    self.kopija_matrika_kvadratov[i][j] += 1
                    if i != 0:
                        self.kopija_matrika_kvadratov[i-1][j] += 1
                    d = self.dolzina_verige(k, i, j)
                    if (vrednost < 1) and (-d < vrednost):
                        vrednost = - d
                        kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
                elif self.igra.vodoravne[i+1][j]+self.igra.navpicne[i][j]+self.igra.navpicne[i][j+1] == 3:
                    self.kopiraj()
                    d = self.dolzina_verige(k, i, j)
                    if d > vrednost:
                        vrednost = d
                        kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
            self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
        elif k == "navpicno":
            if j != 0:  # levi
                if self.igra.navpicne[i][j-1]+self.igra.vodoravne[i][j-1]+self.igra.vodoravne[i+1][j-1] == 2:
                    self.kopiraj()
                    self.kopija_navpicne[i][j] = True
                    self.kopija_matrika_kvadratov[i][j-1] += 1
                    if j != 7:
                        self.kopija_matrika_kvadratov[i][j] += 1
                    vrednost = - self.dolzina_verige(k, i, j)
                elif self.igra.navpicne[i][j-1]+self.igra.vodoravne[i][j-1]+self.igra.vodoravne[i+1][j-1] == 3:
                    self.kopiraj()
                    vrednost = self.dolzina_verige(k, i, j)
                kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
            if j != 7:  # desni
                if self.igra.navpicne[i][j+1]+self.igra.vodoravne[i][j]+self.igra.vodoravne[i+1][j] == 2:
                    self.kopiraj()
                    self.kopija_navpicne[i][j] = True
                    self.kopija_matrika_kvadratov[i][j] += 1
                    if j != 0:
                        self.kopija_matrika_kvadratov[i][j-1] += 1
                    d = self.dolzina_verige(k, i, j)
                    if (vrednost < 1) and (- d < vrednost):
                        vrednost = - d
                        kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
                elif self.igra.navpicne[i][j+1]+self.igra.vodoravne[i][j]+self.igra.vodoravne[i+1][j] == 3:
                    self.kopiraj()
                    d = self.dolzina_verige(k, i, j)
                    if d > vrednost:
                        vrednost = d
                        kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
            self.igra.navidezno_povleci_potezo(("navpicno", i, j))
        return vrednost, kopija

    def kopiraj(self):
        self.kopija_vodoravne = [self.igra.vodoravne[i][:] for i in range(8)]
        self.kopija_navpicne = [self.igra.navpicne[i][:] for i in range(7)]
        self.kopija_matrika_kvadratov = [self.igra.matrika_kvadratov[i][:] for i in range(7)]

    def dolzina_verige(self, k, i, j):
        """ izracuna dolzino verige, ki jo lahko naslednji igralec pobarva, ce naredimo dano
        potezo """
        dolzina = 0
        e, f = i, j
        # vodoravna poteza
        if k == "vodoravno":
            if i != 0:  # zgornji
                while self.kopija_matrika_kvadratov[e-1][f] == 3:
                    dolzina += 1
                    if not self.kopija_vodoravne[e-1][f]:
                        self.kopija_vodoravne[e-1][f] = True
                        self.kopija_matrika_kvadratov[e-1][f] = 4
                        if e == 1:
                            break
                        self.kopija_matrika_kvadratov[e-2][f] += 1
                        if self.kopija_matrika_kvadratov[e-2][f] == 4:
                            dolzina += 1
                            break
                        e -= 1
                    elif not self.kopija_vodoravne[e][f]:
                        self.kopija_vodoravne[e][f] = True
                        self.kopija_matrika_kvadratov[e-1][f] = 4
                        if e == 7:
                            break
                        self.kopija_matrika_kvadratov[e][f] += 1
                        if self.kopija_matrika_kvadratov[e][f] == 4:
                            dolzina += 1
                            break
                        e += 1
                    elif not self.kopija_navpicne[e-1][f]:
                        self.kopija_navpicne[e-1][f] = True
                        self.kopija_matrika_kvadratov[e-1][f] = 4
                        if f == 0:
                            break
                        self.kopija_matrika_kvadratov[e-1][f-1] += 1
                        if self.kopija_matrika_kvadratov[e-1][f-1] == 4:
                            dolzina += 1
                            break
                        f -= 1
                    elif not self.kopija_navpicne[e-1][f+1]:
                        self.kopija_navpicne[e-1][f+1] = True
                        self.kopija_matrika_kvadratov[e-1][f] = 4
                        if f == 6:
                            break
                        self.kopija_matrika_kvadratov[e-1][f+1] += 1
                        if self.kopija_matrika_kvadratov[e-1][f+1] == 4:
                            dolzina += 1
                            break
                        f += 1
            if i != 7:  # spodnji
                e, f = i, j
                while self.kopija_matrika_kvadratov[e][f] == 3:
                    dolzina += 1
                    if not self.kopija_vodoravne[e][f]:
                        self.kopija_vodoravne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if e == 0:
                            break
                        self.kopija_matrika_kvadratov[e-1][f] += 1
                        if self.kopija_matrika_kvadratov[e-1][f] == 4:
                            dolzina += 1
                            break
                        e -= 1
                    elif not self.kopija_vodoravne[e+1][f]:
                        self.kopija_vodoravne[e+1][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if e == 6:
                            break
                        self.kopija_matrika_kvadratov[e+1][f] += 1
                        if self.kopija_matrika_kvadratov[e+1][f] == 4:
                            dolzina += 1
                            break
                        e += 1
                    elif not self.kopija_navpicne[e][f]:
                        self.kopija_navpicne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if f == 0:
                            break
                        self.kopija_matrika_kvadratov[e][f-1] += 1
                        if self.kopija_matrika_kvadratov[e][f-1] == 4:
                            dolzina += 1
                            break
                        f -= 1
                    elif not self.kopija_navpicne[e][f+1]:
                        self.kopija_navpicne[e][f+1] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if f == 6:
                            break
                        self.kopija_matrika_kvadratov[e][f+1] += 1
                        if self.kopija_matrika_kvadratov[e][f+1] == 4:
                            dolzina += 1
                            break
                        f += 1
        # navpicna poteza
        if k == "navpicno":
            if j != 0:  # levi
                while self.kopija_matrika_kvadratov[e][f-1] == 3:
                    dolzina += 1
                    if not self.kopija_navpicne[e][f-1]:
                        self.kopija_navpicne[e][f-1] = True
                        self.kopija_matrika_kvadratov[e][f-1] = 4
                        if f == 1:
                            break
                        self.kopija_matrika_kvadratov[e][f-2] += 1
                        if self.kopija_matrika_kvadratov[e][f-2] == 4:
                            dolzina += 1
                            break
                        f -= 1
                    elif not self.kopija_navpicne[e][f]:
                        self.kopija_navpicne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f-1] = 4
                        if f == 7:
                            break
                        self.kopija_matrika_kvadratov[e][f] += 1
                        if self.kopija_matrika_kvadratov[e][f] == 4:
                            dolzina += 1
                            break
                        f += 1
                    elif not self.kopija_vodoravne[e][f-1]:
                        self.kopija_vodoravne[e][f-1] = True
                        self.kopija_matrika_kvadratov[e][f-1] = 4
                        if e == 0:
                            break
                        self.kopija_matrika_kvadratov[e-1][f-1] += 1
                        if self.kopija_matrika_kvadratov[e-1][f-1] == 4:
                            dolzina += 1
                            break
                        e -= 1
                    elif not self.kopija_vodoravne[e+1][f-1]:
                        self.kopija_vodoravne[e+1][f-1] = True
                        self.kopija_matrika_kvadratov[e][f-1] = 4
                        if e == 6:
                            break
                        self.kopija_matrika_kvadratov[e+1][f-1] += 1
                        if self.kopija_matrika_kvadratov[e+1][f-1] == 4:
                            dolzina += 1
                            break
                        e += 1
            if j != 7:  # desni
                e, f = i, j
                while self.kopija_matrika_kvadratov[e][f] == 3:
                    dolzina += 1
                    if not self.kopija_navpicne[e][f+1]:
                        self.kopija_navpicne[e][f+1] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if f == 6:
                            break
                        self.kopija_matrika_kvadratov[e][f+1] += 1
                        if self.kopija_matrika_kvadratov[e][f+1] == 4:
                            dolzina += 1
                            break
                        f += 1
                    elif not self.kopija_navpicne[e][f]:
                        self.kopija_navpicne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if f == 0:
                            break
                        self.kopija_matrika_kvadratov[e][f-1] += 1
                        if self.kopija_matrika_kvadratov[e][f-1] == 4:
                            dolzina += 1
                            break
                        f -= 1
                    elif not self.kopija_vodoravne[e][f]:
                        self.kopija_vodoravne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if e == 0:
                            break
                        self.kopija_matrika_kvadratov[e-1][f] += 1
                        if self.kopija_matrika_kvadratov[e-1][f] == 4:
                            dolzina += 1
                            break
                        e -= 1
                    elif not self.kopija_vodoravne[e+1][f]:
                        self.kopija_vodoravne[e+1][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if e == 6:
                            break
                        self.kopija_matrika_kvadratov[e+1][f] += 1
                        if self.kopija_matrika_kvadratov[e+1][f] == 4:
                            dolzina += 1
                            break
                        e += 1
        return dolzina


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
        """Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True

    def izracunaj_potezo(self, igra):
        """Izračunaj potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_potezi
        self.poteze = None
        (poteza, vrednost, seznam_potez) = self.alfabeta(self.globina, -Minimax.NESKONCNO, Minimax.NESKONCNO, True, None, [])
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            self.poteze = seznam_potez

    def alfabeta(self, globina, alfa, beta,  maksimiziramo, p, seznam_potez):
        """Glavna metoda minimax."""
        if self.prekinitev:
            return None, 0
        if self.igra.konec_igre1():
            # Igre je konec, vrnemo njeno vrednost
            if self.igra.na_potezi == self.jaz:
                return None, Minimax.ZMAGA, seznam_potez
            else:
                return None, -Minimax.ZMAGA, seznam_potez
        else:
            # Igre ni konec
            if globina == 0:
                vrednost_pozicije, kopija = self.vrednost_pozicije(p)
                if vrednost_pozicije:
                    self.igra.vodoravne, self.igra.navpicne = kopija[0], kopija[1]
                    self.igra.matrika_kvadratov = kopija[2]
                    if vrednost_pozicije > 0:
                        vrednost_pozicije += self.alfabeta(1, alfa-vrednost_pozicije, beta-vrednost_pozicije, True, None, seznam_potez)[1]
                    vrednost_pozicije -= sum([x.count(3) for x in self.igra.matrika_kvadratov])
                else:
                    vrednost_pozicije -= sum([x.count(3) for x in self.igra.matrika_kvadratov])
                if maksimiziramo:
                    vrednost_pozicije = - vrednost_pozicije
                return None, vrednost_pozicije, seznam_potez
            else:
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza_n = None
                    najboljsa_poteza_v = None
                    vrednost_najboljse_v = -Minimax.NESKONCNO
                    vrednost_najboljse_n = -Minimax.NESKONCNO
                    seznam_v = []
                    seznam_n = []
                    v_veljavne, n_veljavne = self.igra.veljavne_poteze()
                    # random.shuffle(v_veljavne)
                    # random.shuffle(n_veljavne)
                    for i, j in v_veljavne:
                        if globina != 1:
                            p = self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                            if p:
                                poteza, v, s = self.alfabeta(globina, alfa-p, beta-p, maksimiziramo, ("vodoravno", i, j), seznam_potez)
                                vrednost = v + p
                            else:
                                poteza, v, s = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, ("vodoravno", i, j), seznam_potez)
                                vrednost = v
                        else:
                            poteza, v, s = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, ("vodoravno", i, j), seznam_potez)
                            vrednost = v
                        self.igra.razveljavi()
                        alfa = max(alfa, vrednost)
                        if vrednost > vrednost_najboljse_v:
                            vrednost_najboljse_v = vrednost
                            najboljsa_poteza_v = ("vodoravno", i, j)
                            seznam_v = s
                        if beta <= alfa:
                            break
                    for i, j in n_veljavne:
                        if globina != 1:
                            p = self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                            if p:
                                poteza, v, s = self.alfabeta(globina, alfa-p, beta-p, maksimiziramo, ("navpicno", i, j), seznam_potez)
                                vrednost = v + p
                            else:
                                poteza, v, s = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, ("navpicno", i, j), seznam_potez)
                                vrednost = v
                        else:
                            poteza, v, s = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, ("navpicno", i, j), seznam_potez)
                            vrednost = v
                        self.igra.razveljavi()
                        alfa = max(alfa, vrednost)
                        if vrednost > vrednost_najboljse_n:
                            vrednost_najboljse_n = vrednost
                            najboljsa_poteza_n = ("navpicno", i, j)
                            seznam_n = s
                        if beta <= alfa:
                            break
                    if vrednost_najboljse_v == vrednost_najboljse_n:
                        vrednost_najboljse, najboljsa_poteza, seznam = \
                            random.choice([(vrednost_najboljse_v, najboljsa_poteza_v, seznam_v), (vrednost_najboljse_n, najboljsa_poteza_n, seznam_n)])
                    else:
                        if vrednost_najboljse_v > vrednost_najboljse_n:
                            vrednost_najboljse, najboljsa_poteza, seznam = vrednost_najboljse_v, najboljsa_poteza_v, seznam_v
                        else:
                            vrednost_najboljse, najboljsa_poteza, seznam = vrednost_najboljse_n, najboljsa_poteza_n, seznam_n
                else:
                    # Minimiziramo
                    najboljsa_poteza_v = None
                    najboljsa_poteza_n = None
                    vrednost_najboljse_v = Minimax.NESKONCNO
                    vrednost_najboljse_n = Minimax.NESKONCNO
                    v_veljavne, n_veljavne = self.igra.veljavne_poteze()
                    # random.shuffle(v_veljavne)
                    # random.shuffle(n_veljavne)
                    for i, j in v_veljavne:
                        if globina != 1:
                            p = self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                            if p:
                                vrednost = self.alfabeta(globina, alfa-p, beta-p, maksimiziramo, ("vodoravno", i, j), seznam_potez)[1] - p
                            else:
                                vrednost = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, ("vodoravno", i, j), seznam_potez)[1]
                        else:
                            vrednost = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, ("vodoravno", i, j), seznam_potez)[1]
                        self.igra.razveljavi()
                        beta = min(beta, vrednost)
                        if vrednost < vrednost_najboljse_v:
                            vrednost_najboljse_v = vrednost
                            najboljsa_poteza_v = "vodoravno", i, j
                        if beta <= alfa:
                            break
                    for i, j in n_veljavne:
                        if globina != 1:
                            p = self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                            if p:
                                vrednost = self.alfabeta(globina, alfa-p, beta-p, maksimiziramo, ("navpicno", i, j), seznam_potez)[1] - p
                            else:
                                vrednost = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, ("navpicno", i, j), seznam_potez)[1]
                        else:
                            vrednost = self.alfabeta(globina-1, alfa, beta, not maksimiziramo, ("navpicno", i, j), seznam_potez)[1]
                        self.igra.razveljavi()
                        beta = min(beta, vrednost)
                        if vrednost < vrednost_najboljse_n:
                            vrednost_najboljse_n = vrednost
                            najboljsa_poteza_n = ("navpicno", i, j)
                        if beta <= alfa:
                            break
                    if vrednost_najboljse_v == vrednost_najboljse_n:
                        vrednost_najboljse, najboljsa_poteza = \
                            random.choice([(vrednost_najboljse_v, najboljsa_poteza_v), (vrednost_najboljse_n, najboljsa_poteza_n)])
                    else:
                        if vrednost_najboljse_v < vrednost_najboljse_n:
                            vrednost_najboljse, najboljsa_poteza = vrednost_najboljse_v, najboljsa_poteza_v
                        else:
                            vrednost_najboljse, najboljsa_poteza = vrednost_najboljse_n, najboljsa_poteza_n
                assert (najboljsa_poteza is not None), "minimax: izračunana poteza je None"
                if globina == self.globina:
                    seznam_potez = seznam + [najboljsa_poteza]
                return najboljsa_poteza, vrednost_najboljse, seznam_potez

    def vrednost_pozicije(self, p):
        k, i, j = p
        vrednost = 0
        kopija = []
        if k == "vodoravno":
            if i != 0:  # zgornji
                if self.igra.vodoravne[i-1][j]+self.igra.navpicne[i-1][j]+self.igra.navpicne[i-1][j+1] == 2:
                    self.kopiraj()
                    self.kopija_vodoravne[i][j] = True
                    self.kopija_matrika_kvadratov[i-1][j] += 1
                    if i != 7:
                        self.kopija_matrika_kvadratov[i][j] += 1
                    vrednost = - self.dolzina_verige(k, i, j)
                elif self.igra.vodoravne[i-1][j]+self.igra.navpicne[i-1][j]+self.igra.navpicne[i-1][j+1] == 3:
                    self.kopiraj()
                    vrednost = self.dolzina_verige(k, i, j)
                kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
            if i != 7:  # spodnji
                if self.igra.vodoravne[i+1][j]+self.igra.navpicne[i][j]+self.igra.navpicne[i][j+1] == 2:
                    self.kopiraj()
                    self.kopija_vodoravne[i][j] = True
                    self.kopija_matrika_kvadratov[i][j] += 1
                    if i != 0:
                        self.kopija_matrika_kvadratov[i-1][j] += 1
                    d = self.dolzina_verige(k, i, j)
                    if (vrednost < 1) and (-d < vrednost):
                        vrednost = - d
                        kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
                elif self.igra.vodoravne[i+1][j]+self.igra.navpicne[i][j]+self.igra.navpicne[i][j+1] == 3:
                    self.kopiraj()
                    d = self.dolzina_verige(k, i, j)
                    if d > vrednost:
                        vrednost = d
                        kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
            self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
        elif k == "navpicno":
            if j != 0:  # levi
                if self.igra.navpicne[i][j-1]+self.igra.vodoravne[i][j-1]+self.igra.vodoravne[i+1][j-1] == 2:
                    self.kopiraj()
                    self.kopija_navpicne[i][j] = True
                    self.kopija_matrika_kvadratov[i][j-1] += 1
                    if j != 7:
                        self.kopija_matrika_kvadratov[i][j] += 1
                    vrednost = - self.dolzina_verige(k, i, j)
                elif self.igra.navpicne[i][j-1]+self.igra.vodoravne[i][j-1]+self.igra.vodoravne[i+1][j-1] == 3:
                    self.kopiraj()
                    vrednost = self.dolzina_verige(k, i, j)
                kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
            if j != 7:  # desni
                if self.igra.navpicne[i][j+1]+self.igra.vodoravne[i][j]+self.igra.vodoravne[i+1][j] == 2:
                    self.kopiraj()
                    self.kopija_navpicne[i][j] = True
                    self.kopija_matrika_kvadratov[i][j] += 1
                    if j != 0:
                        self.kopija_matrika_kvadratov[i][j-1] += 1
                    d = self.dolzina_verige(k, i, j)
                    if (vrednost < 1) and (- d < vrednost):
                        vrednost = - d
                        kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
                elif self.igra.navpicne[i][j+1]+self.igra.vodoravne[i][j]+self.igra.vodoravne[i+1][j] == 3:
                    self.kopiraj()
                    d = self.dolzina_verige(k, i, j)
                    if d > vrednost:
                        vrednost = d
                        kopija = [self.kopija_vodoravne, self.kopija_navpicne, self.kopija_matrika_kvadratov]
            self.igra.navidezno_povleci_potezo(("navpicno", i, j))
        return vrednost, kopija

    def kopiraj(self):
        self.kopija_vodoravne = [self.igra.vodoravne[i][:] for i in range(8)]
        self.kopija_navpicne = [self.igra.navpicne[i][:] for i in range(7)]
        self.kopija_matrika_kvadratov = [self.igra.matrika_kvadratov[i][:] for i in range(7)]

    def dolzina_verige(self, k, i, j):
        """ izracuna dolzino verige, ki jo lahko naslednji igralec pobarva, ce naredimo dano
        potezo """
        dolzina = 0
        e, f = i, j
        # vodoravna poteza
        if k == "vodoravno":
            if i != 0:  # zgornji
                while self.kopija_matrika_kvadratov[e-1][f] == 3:
                    dolzina += 1
                    if not self.kopija_vodoravne[e-1][f]:
                        self.kopija_vodoravne[e-1][f] = True
                        self.kopija_matrika_kvadratov[e-1][f] = 4
                        if e == 1:
                            break
                        self.kopija_matrika_kvadratov[e-2][f] += 1
                        if self.kopija_matrika_kvadratov[e-2][f] == 4:
                            dolzina += 1
                            break
                        e -= 1
                    elif not self.kopija_vodoravne[e][f]:
                        self.kopija_vodoravne[e][f] = True
                        self.kopija_matrika_kvadratov[e-1][f] = 4
                        if e == 7:
                            break
                        self.kopija_matrika_kvadratov[e][f] += 1
                        if self.kopija_matrika_kvadratov[e][f] == 4:
                            dolzina += 1
                            break
                        e += 1
                    elif not self.kopija_navpicne[e-1][f]:
                        self.kopija_navpicne[e-1][f] = True
                        self.kopija_matrika_kvadratov[e-1][f] = 4
                        if f == 0:
                            break
                        self.kopija_matrika_kvadratov[e-1][f-1] += 1
                        if self.kopija_matrika_kvadratov[e-1][f-1] == 4:
                            dolzina += 1
                            break
                        f -= 1
                    elif not self.kopija_navpicne[e-1][f+1]:
                        self.kopija_navpicne[e-1][f+1] = True
                        self.kopija_matrika_kvadratov[e-1][f] = 4
                        if f == 6:
                            break
                        self.kopija_matrika_kvadratov[e-1][f+1] += 1
                        if self.kopija_matrika_kvadratov[e-1][f+1] == 4:
                            dolzina += 1
                            break
                        f += 1
            if i != 7:  # spodnji
                e, f = i, j
                while self.kopija_matrika_kvadratov[e][f] == 3:
                    dolzina += 1
                    if not self.kopija_vodoravne[e][f]:
                        self.kopija_vodoravne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if e == 0:
                            break
                        self.kopija_matrika_kvadratov[e-1][f] += 1
                        if self.kopija_matrika_kvadratov[e-1][f] == 4:
                            dolzina += 1
                            break
                        e -= 1
                    elif not self.kopija_vodoravne[e+1][f]:
                        self.kopija_vodoravne[e+1][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if e == 6:
                            break
                        self.kopija_matrika_kvadratov[e+1][f] += 1
                        if self.kopija_matrika_kvadratov[e+1][f] == 4:
                            dolzina += 1
                            break
                        e += 1
                    elif not self.kopija_navpicne[e][f]:
                        self.kopija_navpicne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if f == 0:
                            break
                        self.kopija_matrika_kvadratov[e][f-1] += 1
                        if self.kopija_matrika_kvadratov[e][f-1] == 4:
                            dolzina += 1
                            break
                        f -= 1
                    elif not self.kopija_navpicne[e][f+1]:
                        self.kopija_navpicne[e][f+1] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if f == 6:
                            break
                        self.kopija_matrika_kvadratov[e][f+1] += 1
                        if self.kopija_matrika_kvadratov[e][f+1] == 4:
                            dolzina += 1
                            break
                        f += 1
        # navpicna poteza
        if k == "navpicno":
            if j != 0:  # levi
                while self.kopija_matrika_kvadratov[e][f-1] == 3:
                    dolzina += 1
                    if not self.kopija_navpicne[e][f-1]:
                        self.kopija_navpicne[e][f-1] = True
                        self.kopija_matrika_kvadratov[e][f-1] = 4
                        if f == 1:
                            break
                        self.kopija_matrika_kvadratov[e][f-2] += 1
                        if self.kopija_matrika_kvadratov[e][f-2] == 4:
                            dolzina += 1
                            break
                        f -= 1
                    elif not self.kopija_navpicne[e][f]:
                        self.kopija_navpicne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f-1] = 4
                        if f == 7:
                            break
                        self.kopija_matrika_kvadratov[e][f] += 1
                        if self.kopija_matrika_kvadratov[e][f] == 4:
                            dolzina += 1
                            break
                        f += 1
                    elif not self.kopija_vodoravne[e][f-1]:
                        self.kopija_vodoravne[e][f-1] = True
                        self.kopija_matrika_kvadratov[e][f-1] = 4
                        if e == 0:
                            break
                        self.kopija_matrika_kvadratov[e-1][f-1] += 1
                        if self.kopija_matrika_kvadratov[e-1][f-1] == 4:
                            dolzina += 1
                            break
                        e -= 1
                    elif not self.kopija_vodoravne[e+1][f-1]:
                        self.kopija_vodoravne[e+1][f-1] = True
                        self.kopija_matrika_kvadratov[e][f-1] = 4
                        if e == 6:
                            break
                        self.kopija_matrika_kvadratov[e+1][f-1] += 1
                        if self.kopija_matrika_kvadratov[e+1][f-1] == 4:
                            dolzina += 1
                            break
                        e += 1
            if j != 7:  # desni
                e, f = i, j
                while self.kopija_matrika_kvadratov[e][f] == 3:
                    dolzina += 1
                    if not self.kopija_navpicne[e][f+1]:
                        self.kopija_navpicne[e][f+1] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if f == 6:
                            break
                        self.kopija_matrika_kvadratov[e][f+1] += 1
                        if self.kopija_matrika_kvadratov[e][f+1] == 4:
                            dolzina += 1
                            break
                        f += 1
                    elif not self.kopija_navpicne[e][f]:
                        self.kopija_navpicne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if f == 0:
                            break
                        self.kopija_matrika_kvadratov[e][f-1] += 1
                        if self.kopija_matrika_kvadratov[e][f-1] == 4:
                            dolzina += 1
                            break
                        f -= 1
                    elif not self.kopija_vodoravne[e][f]:
                        self.kopija_vodoravne[e][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if e == 0:
                            break
                        self.kopija_matrika_kvadratov[e-1][f] += 1
                        if self.kopija_matrika_kvadratov[e-1][f] == 4:
                            dolzina += 1
                            break
                        e -= 1
                    elif not self.kopija_vodoravne[e+1][f]:
                        self.kopija_vodoravne[e+1][f] = True
                        self.kopija_matrika_kvadratov[e][f] = 4
                        if e == 6:
                            break
                        self.kopija_matrika_kvadratov[e+1][f] += 1
                        if self.kopija_matrika_kvadratov[e+1][f] == 4:
                            dolzina += 1
                            break
                        e += 1
        return dolzina
