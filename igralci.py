__author__ = 'uporabnik'
import threading


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
            target=lambda: self.algoritem.izracunaj_potezo(self.vmesnik.igra.kopija(), self.vmesnik))
        self.mislec.start()

    def preveri_potezo(self):
        """Vsakih 100ms preveri, ali je algoritem že izračunal potezo."""
        pass

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
        self.poteza = None
        self.kopija_vodoravne = None
        self.kopija_navpicne = None
        self.kopija_matrika_kvadratov = None

    ZMAGA = 100000
    NESKONCNO = ZMAGA + 1

    def prekini(self):
        """Metoda, ki jo pokliče GUI, če je treba nehati razmišljati, ker
           je uporabnik zaprl okno ali izbral novo igro."""
        self.prekinitev = True

    def izracunaj_potezo(self, igra, vmesnik):
        """Izračunaj potezo za trenutno stanje dane igre."""
        self.igra = igra
        self.prekinitev = False
        self.jaz = self.igra.na_potezi
        self.poteza = None
        (poteza, vrednost) = self.minimax(self.globina, True, None)
        self.jaz = None
        self.igra = None
        if not self.prekinitev:
            self.poteza = poteza
            vmesnik.igra.racunalnik_povleci_potezo(self.poteza)

    def minimax(self, globina, maksimiziramo, p):
        """Glavna metoda minimax."""
        if self.prekinitev:
            return None, 0
        if self.igra.konec_igre1():
            # Igre je konec, vrnemo njeno vrednost
            if self.igra.na_potezi == self.jaz:
                return None, Minimax.ZMAGA
            else:
                return None, -Minimax.ZMAGA
        else:
            # Igre ni konec
            if globina == 0:
                return None, self.vrednost_pozicije(p)
            else:
                # Naredimo eno stopnjo minimax
                if maksimiziramo:
                    # Maksimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = -Minimax.NESKONCNO
                    v_veljavne, n_veljavne = self.igra.veljavne_poteze()
                    for i, j in v_veljavne:
                        if globina != 1:
                            self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                        vrednost = self.minimax(globina-1, not maksimiziramo, ("vodoravno", i, j))[1]
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = "vodoravno", i, j
                    for i, j in n_veljavne:
                        if globina != 1:
                            self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                        vrednost = self.minimax(globina-1, not maksimiziramo, ("navpicno", i, j))[1]
                        self.igra.razveljavi()
                        if vrednost > vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = "navpicno", i, j
                else:
                    # Minimiziramo
                    najboljsa_poteza = None
                    vrednost_najboljse = Minimax.NESKONCNO
                    v_veljavne, n_veljavne = self.igra.veljavne_poteze()
                    for i, j in v_veljavne:
                        if globina != 1:
                            self.igra.navidezno_povleci_potezo(("vodoravno", i, j))
                        vrednost = self.minimax(globina-1, not maksimiziramo, ("vodoravno", i, j))[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = "vodoravno", i, j
                    for i, j in n_veljavne:
                        if globina != 1:
                            self.igra.navidezno_povleci_potezo(("navpicno", i, j))
                        vrednost = self.minimax(globina-1, not maksimiziramo, ("navpicno", i, j))[1]
                        self.igra.razveljavi()
                        if vrednost < vrednost_najboljse:
                            vrednost_najboljse = vrednost
                            najboljsa_poteza = "navpicno", i, j

                assert (najboljsa_poteza is not None), "minimax: izračunana poteza je None"
                return najboljsa_poteza, vrednost_najboljse

    def vrednost_pozicije(self, p):
        k, i, j = p
        vrednost = 0
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
            if i != 7:  # spodnji
                if self.igra.vodoravne[i+1][j]+self.igra.navpicne[i][j]+self.igra.navpicne[i][j+1] == 2:
                    self.kopiraj()
                    self.kopija_vodoravne[i][j] = True
                    self.kopija_matrika_kvadratov[i][j] += 1
                    if i != 0:
                        self.kopija_matrika_kvadratov[i-1][j] += 1
                    if vrednost < 1:
                        vrednost = min(vrednost, - self.dolzina_verige(k, i, j))
                elif self.igra.vodoravne[i+1][j]+self.igra.navpicne[i][j]+self.igra.navpicne[i][j+1] == 3:
                    self.kopiraj()
                    vrednost = max(vrednost, self.dolzina_verige(k, i, j))
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
            if j != 7:  # desni
                if self.igra.navpicne[i][j+1]+self.igra.vodoravne[i][j]+self.igra.vodoravne[i+1][j] == 2:
                    self.kopiraj()
                    self.kopija_navpicne[i][j] = True
                    self.kopija_matrika_kvadratov[i][j] += 1
                    if j != 0:
                        self.kopija_matrika_kvadratov[i][j-1] += 1
                    if vrednost < 1:
                        vrednost = min(vrednost, - self.dolzina_verige(k, i, j))
                elif self.igra.navpicne[i][j+1]+self.igra.vodoravne[i][j]+self.igra.vodoravne[i+1][j] == 3:
                    self.kopiraj()
                    vrednost = max(vrednost, self.dolzina_verige(k, i, j))
            self.igra.navidezno_povleci_potezo(("navpicno", i, j))
        return vrednost

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
