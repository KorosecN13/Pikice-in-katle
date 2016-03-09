__author__ = 'KorosecN13'

# Pikice in skatle
from tkinter import *


class Vmesnik():

    def __init__(self, master):

        # Ozadje
        master.configure(background='pink')

        # Glavni meni
        menu = Menu(master)
        master.config(menu=menu)

        # File
        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)

        # Dodamo izbire v file_menu
        # file_menu.add_command(label="Nastavi velikost", command=self.nastavi_velikost)
        file_menu.add_command(label="Nova igra", command=self.nova_igra)
        file_menu.add_command(label="Izhod", command=master.destroy)

        # Velikost polja
        self.vrstice = 8
        self.stolpci = 8

        # Naredimo spremenljivke, ki hranijo vrednosti polj
        self.ime_igralec1 = StringVar(master, value='Igralec 1')
        self.ime_igralec2 = StringVar(master, value='Igralec 2')

        # Kaj moramo povedati programu
        polje_ime_igralec1 = Entry(master, width=10, textvariable=self.ime_igralec1)
        polje_ime_igralec2 = Entry(master, width=10, textvariable=self.ime_igralec2)

        # Umestimo jih na glavno okno
        polje_ime_igralec1.grid(row=1, column=0)
        polje_ime_igralec2.grid(row=1, column=1)

        # spremenljivke, ki stejejo trenutni rezultat igre
        self.stevec_igralec1 = IntVar(master, value=0)
        self.stevec_igralec2 = IntVar(master, value=0)

        # Oznake za stevce
        oznaka_ime_igralec1 = Label(master, textvariable=self.stevec_igralec1)
        oznaka_ime_igralec2 = Label(master, textvariable=self.stevec_igralec2)

        # Umestimo jih na glavno okno
        oznaka_ime_igralec1.grid(row=2, column=0)
        oznaka_ime_igralec2.grid(row=2, column=1)

        # Igralno polje
        self.polje = Canvas(master, width=450, height=450)
        self.polje.grid(columnspan=2, row=3, column=0)

        # prilagodi velikost vrstic in stolpcev, če spremenimo velikost okna
        for i in range(2):
            master.columnconfigure(i, weight=3)
        for i in range(4):
            master.rowconfigure(i, weight=3)

        for i in range(8):
            for j in range(8):
                self.polje.create_oval(50*(i+1)-5, 50*(j+1)-5, 50*(i+1)+5, 50*(j+1)+5)

        self.zacni_igro()

    # def nastavi_velikost(self):
    #    pass

    def nova_igra(self):
        pass

    def zacni_igro(self):
        self.polje.bind('<Button-1>', self.narisi_crto)

    def narisi_crto(self, event):
        """ narisi crto med ustrezna krogca na igralnem polju """
        x, y = event.x, event.y
        lok_x, lok_y = x % 50, y % 50
        if lok_x < 10 or lok_x > 40 or lok_y < 10 or lok_y > 40:
            if lok_y > lok_x:
                if lok_y > 50 - lok_x:
                    if y < 400 and 50 < x < 400:
                        self.polje.create_line(50*(x//50), 50*(y//50+1), 50*(x//50+1), 50*(y//50+1))
                else:
                    if x > 50 and 50 < y < 400:
                        self.polje.create_line(50*(x//50), 50*(y//50), 50*(x//50), 50*(y//50+1))
            else:
                if lok_y > 50 - lok_x:
                    if x < 400 and 50 < y < 400:
                        self.polje.create_line(50*(x//50+1), 50*(y//50), 50*(x//50+1), 50*(y//50+1))
                else:
                    if y > 50 and 50 < x < 400:
                        self.polje.create_line(50*(x//50), 50*(y//50), 50*(x//50+1), 50*(y//50))


root = Tk()
root.title('Pikice in Skatle')
aplikacija = Vmesnik(root)
root.mainloop()
