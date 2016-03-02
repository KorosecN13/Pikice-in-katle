__author__ = 'KorosecN13'

# Pikice in skatle
from tkinter import *

class Vmesnik():

    def __init__(self, master):

        self.master = master

        ''' Ozadje'''
        master.configure(background='pink')

        ''' Glavni meni'''
        menu = Menu(master)
        master.config(menu=menu)

        ''' File'''
        file_menu = Menu(menu)
        menu.add_cascade(label="File", menu=file_menu)

        ''' Dodamo izbire v file_menu '''
        #file_menu.add_command(label="Nastavi velikost", command=self.nastavi_velikost)
        file_menu.add_command(label="Nova igra", command=self.nova_igra)
        file_menu.add_command(label="Izhod", command=master.destroy)

        '''Velikost polja'''
        self.vrstice = 8
        self.stolpci = 8

        ''' Naredimo spremenljivke, ki hranijo vrednosti polj '''
        self.ime_igralec1 = StringVar(master, value = 'Igralec 1')
        self.ime_igralec2 = StringVar(master, value = 'Igralec 2')


        ''' Kaj moramo povedati programu '''
        polje_ime_igralec1 = Entry(master, width = 10, textvariable = self.ime_igralec1)
        polje_ime_igralec2 = Entry(master, width = 10, textvariable = self.ime_igralec2)

        ''' Umestimo jih na glavno okno'''
        polje_ime_igralec1.grid(row = 1, column = 0)
        polje_ime_igralec2.grid(row = 1, column = 1)

        self.stevec_igralec1 = IntVar(master, value = 0)
        self.stevec_igralec2 = IntVar(master, value = 0)

        ''' Oznake'''
        oznaka_ime_igralec1 = Label(master, textvariable = self.stevec_igralec1)
        oznaka_ime_igralec2 = Label(master, textvariable = self.stevec_igralec2)



        ''' Umestimo jih na glavno okno'''
        oznaka_ime_igralec1.grid(row = 2, column = 0)
        oznaka_ime_igralec2.grid(row = 2, column = 1)

        '''Igralno polje'''
        polje = Canvas(master, width = 450, height = 450)
        polje.grid(columnspan = 2, row = 3, column = 0)

        for i in range(2):
            master.columnconfigure(i, weight = 3)
        for i in range(4):
            master.rowconfigure(i, weight = 3)

        for i in range(8):
            for j in range(8):
                polje.create_oval(50*(i+1)-5, 50*(j+1)-5, 50*(i+1)+5, 50*(j+1)+5)

    def nastavi_velikost(self):
        pass

    def nova_igra(self):
        pass

master = Tk()
master.title('Pikice in Skatle')
aplikacija = Vmesnik(master)
master.mainloop()
