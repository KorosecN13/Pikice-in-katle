#Vsebinski načrt

##Razredi

###Razred Vmesnik

Razred v katerem je definiran grafični vmesnik. Ima naslednje metode:
* zacni_igro(self, igralec1, igralec2): nastavi začetno stanje igre, shrani igralca
* polje_klik(self, event): kaj se zgodi ob kliku na igralno polje
* narisi_crto(self, k, i, j, barva): nariše črto ustrezne barve med ustreznima točkama na polju
* pobarvaj_kvadratek(self, j, i, barva): pobarva kvadratek na igralnem polju
* zmaga(self): izpiše kdo je zmagal

### Razred Igra

Objekt tega razreda shranjuje trenutno stanje igre. Ima naslednje metode:
* sprememba_igralca(self): zamenja igralca, ki je na potezi
* doloci_crto(self, x, y): določi črto, ki ustreza danima koordinatama na polju
* veljavna_poteza(self, x, y): preveri, ali je poteza veljavna
* povleci_potezo(self, x, y): vmesniku sporoči katero črto naj nariše in kakšne barve mora biti
* poln_kvadratek(self, k, i, j): pogleda, ali se je zaprl kateri od kvadratkov in vmeniku sporoči kateri kvadratrek naj pobarva
* konec_igre(self): po odigrani potezi pogleda ali je konec igre

### Igralci
Vsak igralec ima atribut ime, stevec in barva.

#### Razred Clovek
Igralec je človek. Ima naslednje metode:
* igraj(self): ne naredi ničesar, čaka, da bo igralec kliknil na polje
* klik(self, x, y): ob kliku igralca na polje, odigra potezo

#### Razred Racunalnik
Igralec je računalnik. Ima naslednje metode:
* igraj(self): 
* preveri_potezo(self):
* prekini(self):
* klik(self, x, y): ko je na vrsti računalnik, ignorira klikanje
