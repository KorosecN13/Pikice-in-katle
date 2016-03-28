__author__ = 'KorosecN13'

# Pikice in skatle
from tkinter import *
from igra import Igra
from igralci import Clovek
from igralci import Racunalnik
from igralci import Minimax


class Vmesnik():

    TAG_FIGURE = 'figure'

    def __init__(self, master):

        # Ozadje
        master.configure(background='gold3')

        # Glavni meni
        menu = Menu(master)
        master.config(menu=menu)

        # Ustvarimo menija
        nova_igra_menu = Menu(menu)
        zapri_menu = Menu(menu)

        # Ustvarimo orodno vrstico
        menu.add_cascade(label="Nova igra", menu=nova_igra_menu)
        menu.add_cascade(label="Izhod", menu=zapri_menu)

        # Dodamo izbire v nova_igra_menu
        nova_igra_menu.add_command(label="človek : človek",
                                   command=lambda: self.zacni_igro(Clovek(self, self.ime_igralec1, self.stevec_igralec1,
                                                                          self.barva1),
                                                                   Clovek(self, self.ime_igralec2, self.stevec_igralec2,
                                                                          self.barva2)))
        nova_igra_menu.add_command(label="človek : računalnik",
                                   command=lambda: self.zacni_igro(Clovek(self, self.ime_igralec1, self.stevec_igralec1,
                                                                          self.barva1),
                                                                   Racunalnik(self, self.ime_igralec1,
                                                                              self.stevec_igralec2, self.barva2, Minimax(2))))
        nova_igra_menu.add_command(label="računalnik : človek",
                                   command=lambda: self.zacni_igro(Racunalnik(self, self.ime_igralec1,
                                                                              self.stevec_igralec1, self.barva1, Minimax(2)),
                                                                   Clovek(self, self.ime_igralec2, self.stevec_igralec2,
                                                                          self.barva2)))
        nova_igra_menu.add_command(label="računalnik : računalnik",
                                   command=lambda: self.zacni_igro(Racunalnik(self, self.ime_igralec1,
                                                                              self.stevec_igralec1, self.barva1, Minimax(2)),
                                                                   Racunalnik(self, self.ime_igralec2,
                                                                              self.stevec_igralec2, self.barva2, Minimax(2))))

        # Dodamo izbiro v zapri_menu
        zapri_menu.add_command(label="Izhod", command=master.destroy)

        # Velikost polja
        self.vrstice = 8
        self.stolpci = 8

        # Igralno polje
        self.polje = Canvas(master, width=450, height=450)
        self.polje.grid(columnspan=2, row=3, column=0)

        # prilagodi velikost vrstic in stolpcev, če spremenimo velikost okna
        for i in range(2):
            master.columnconfigure(i, weight=3)
        for i in range(4):
            master.rowconfigure(i, weight=3)

        # v polje narisemo pike
        for i in range(8):
            for j in range(8):
                self.polje.create_oval(50*(i+1)-5, 50*(j+1)-5, 50*(i+1)+5, 50*(j+1)+5, fill='gold4', width=0)

        # spremenljivke, ki dolocajo barvi igralcev
        self.barva1 = 'light blue'
        self.barva2 = 'orange'

        # Naredimo spremenljivke, ki hranijo ime igralcev
        self.ime_igralec1 = StringVar(master, value='Igralec 1')
        self.ime_igralec2 = StringVar(master, value='Igralec 2')

        # Kaj moramo povedati programu
        polje_ime_igralec1 = Entry(master, width=15, textvariable=self.ime_igralec1, background=self.barva1)
        polje_ime_igralec2 = Entry(master, width=15, textvariable=self.ime_igralec2, background=self.barva2)

        # Umestimo jih na glavno okno
        polje_ime_igralec1.grid(row=1, column=0)
        polje_ime_igralec2.grid(row=1, column=1)

        # Spremenljivke, ki štejejo trenutni rezultat igre
        self.stevec_igralec1 = IntVar(master, value=0)
        self.stevec_igralec2 = IntVar(master, value=0)

        # Oznake za stevce
        oznaka_stevec_igralec1 = Label(master, textvariable=self.stevec_igralec1, background=self.barva1)
        oznaka_stevec_igralec2 = Label(master, textvariable=self.stevec_igralec2, background=self.barva2)

        # Umestimo jih na glavno okno
        oznaka_stevec_igralec1.grid(row=2, column=0)
        oznaka_stevec_igralec2.grid(row=2, column=1)

        # objekta, ki predstavljata igralca
        self.igralec1 = None
        self.igralec2 = None

        # objekt, ki predstavlja igro
        self.igra = None

        # kaj se zgodi ob kliku na igralno polje
        self.polje.bind('<Button-1>', self.polje_klik)

        # zacnemo igro proti racunalniku
        self.zacni_igro(Clovek(self, self.ime_igralec1, self.stevec_igralec1, self.barva1),
                        Racunalnik(self, self.ime_igralec1, self.stevec_igralec2, self.barva2, Minimax(2)))

    def zacni_igro(self, igralec1, igralec2):
        """ nastavi stanje igra na zacetek """
        if type(igralec1) == Racunalnik:
            if type(igralec2) == Racunalnik:
                self.ime_igralec2.set("Racunalnik 2")
                self.ime_igralec1.set("Racunalnik 1")
            else:
                self.ime_igralec1.set("Racunalnik")
                if self.ime_igralec2.get() in ("Racunalnik", "Racunalnik 2"):
                    self.ime_igralec2.set("Igralec 2")
        elif type(igralec2) == Racunalnik:
            self.ime_igralec2.set("Racunalnik")
            if self.ime_igralec1.get() in ("Racunalnik", "Racunalnik 1"):
                self.ime_igralec1.set("Igralec 1")
        else:
            if self.ime_igralec1.get() in ("Racunalnik", "Racunalnik 1"):
                self.ime_igralec1.set("Igralec 1")
            if self.ime_igralec2.get() in ("Racunalnik", "Racunalnik 2"):
                self.ime_igralec2.set("Igralec 2")
        # Pobrišemo vse figure s polja
        self.polje.delete(Vmesnik.TAG_FIGURE)
        # Ustvarimo novo igro
        self.igra = Igra(self)
        # Shranimo igralce
        self.igralec1 = igralec1
        self.igralec2 = igralec2
        igralec1.igra = self.igra
        igralec2.igra = self.igra
        # nastavimo stevce na 0
        self.stevec_igralec1.set(0)
        self.stevec_igralec2.set(0)
        self.igra.na_potezi = self.igralec1
        self.igralec1.igraj()

    def polje_klik(self, event):
        """ poklice ustrezno fukcijo klik - za cloveka ali racunalnik """
        x, y = event.x, event.y
        if self.igra.na_potezi == self.igralec1:
            self.igralec1.klik(x, y)
        if self.igra.na_potezi == self.igralec2:
            self.igralec2.klik(x, y)
        else:
            pass

    def narisi_crto(self, k, i, j, barva):
        """ narisi crto med ustrezna krogca na igralnem polju """
        if k == 'vodoravno':
            self.polje.create_line(50*(j+1)+5, 50*(i+1), 50*(j+2)-5, 50*(i+1),
                                   fill=barva, width=3, tag=Vmesnik.TAG_FIGURE)
        else:
            self.polje.create_line(50*(j+1), 50*(i+1)+5, 50*(j+1), 50*(i+2)-5,
                                   fill=barva, width=3, tag=Vmesnik.TAG_FIGURE)

    def pobarvaj_kvadratek(self, j, i, barva):
        """ pobarva zaprt kvadratek na igralnem polju """
        self.polje.create_rectangle(50*i+5, 50*j+5, 50*i+45, 50*j+45, fill=barva, width=0, tag=Vmesnik.TAG_FIGURE)

    def zmaga(self):
        """ izpise kdo je zmagovalec """
        if self.igralec1.stevec.get() > self.igralec2.stevec.get():
            zmagovalec = self.igralec1.ime.get()
        else:
            zmagovalec = self.igralec2.ime.get()
        self.polje.create_rectangle(100, 150, 350, 300, fill='green yellow', tag=Vmesnik.TAG_FIGURE)
        self.polje.itemconfig(self.polje.create_text(225, 200, font=("Purisa", 20), tag=Vmesnik.TAG_FIGURE),
                              text='Zmagal je')
        self.polje.itemconfig(self.polje.create_text(225, 250, font=("Purisa", 20), tag=Vmesnik.TAG_FIGURE),
                              text='{0}'.format(zmagovalec))


root = Tk()
root.title('Pikice in Skatle')
aplikacija = Vmesnik(root)
root.mainloop()
