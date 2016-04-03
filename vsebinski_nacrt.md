#Vsebinski načrt

## Opis delovanja aplikacije

V glavnem oknu aplikacije dva igralca igrata Pikice in škatle. Vsak od igralcev je lahko človek ali računalnik. Človek svoje poteze vnaša tako, da z miško klikne na črto, ki jo želi povleči.

Aplikacija je v enem od treh stanj:


1. Začetek - uporabnik izbere eno od štirih možnostih igranja:
   * človek - človek
   * človek - računalnik
   * računalnik - človek
   * računalnik - računalnik
2. Igra - med igro so v oknu naslednji podatki:
  * imena obeh igralcev
  * kdo je trenutno na potezi
  * število pobarvanih kvadratkov
3. Konec igre - prikazuje napis, kdo je zmagovalec.

Prehodi med stanji:

* Prehod iz začetka v igro: sproži ga uporabnik, ko izbere način igranja
* Prehod iz igre v konec igre: sproži ga uporabniški vmesnik, ko ugotovi, da je igre konec
* Prehod iz konca igre v začetek igre: uporabnik ponovno izbere kombinacijo igralcev

## Struktura programa

Program je implementiran v Pythonu 3 in je sestavljen iz treh delov:

1. **Grafični vmesnik:** uporablja knjižnico [tkinter](http://infohost.nmt.edu/tcc/help/pubs/tkinter/web/index.html).

2. **Igra:** računalnik bo izbiral svoje poteze z algoritmoma [minimax](https://cs.stanford.edu/people/eroberts/courses/soco/projects/1998-99/game-theory/Minimax.html) in [alfa-beta rezanje](https://en.wikipedia.org/wiki/Alpha–beta_pruning).

3. **Igralci:** uporablja knjižnice [threading](https://docs.python.org/2/library/threading.html), [time](https://docs.python.org/2/library/time.html) in [random](https://docs.python.org/2/library/random.html)

## Razredi

### Razred `Vmesnik`
To je razred, v katerem je definiran grafični vmesnik. Ima naslednje metode:
* `zacni_igro(self, igralec1, igralec2)`: nastavi začetno stanje igre, shrani igralca
* `zapri_okno(self, master)`: zapre okno in ustavi razmišljanje igralcev
* `polje_klik(self, event)`: pove, kaj se zgodi ob kliku na igralno polje
* `narisi_crto(self, k, i, j, barva)`: nariše črto ustrezne barve med ustreznima točkama na polju
* `pobarvaj_kvadratek(self, j, i, barva)`: pobarva kvadratek na igralnem polju
* `prekini_igralce(self)`: sporoči igralcem, da morajo nehati razmišljati
* `zmaga(self)`: izpiše kdo je zmagal

### Razred `Igra`

Objekt tega razreda shranjuje trenutno stanje igre. Ima naslednje metode:
* `sprememba_igralca(self)`: zamenja igralca, ki je na potezi
* `doloci_crto(self, x, y)`: določi črto, ki ustreza danima koordinatama na polju
* `veljavna_poteza(self, x, y)`: preveri, ali je poteza veljavna
* `povleci_potezo(self, x, y)`: vmesniku sporoči, katero črto naj nariše in kakšne barve mora biti
* `racunalnik_povleci_potezo(self, poteza)`: povleče potezo, ki jo je izračunal računalnik
* navidezno_povleci_potezo(self, p): navidezno povlece potezo pri minimaxu in vrne stevilo zaprtih kvadratov s to potezo
* poln_kvadratek(self, k, i, j): pogleda, ali se je zaprl kateri od kvadratkov in vmeniku sporoči kateri kvadratrek naj pobarva
* konec_igre(self): po odigrani potezi pogleda ali je konec igre

#### Metode, namenjene računalnikovemu razmišljanju
* `kopija(self)`: vrne kopijo te igre 
* `shrani_pozicijo(self)`: shrani trenutno pozicijo, da se bomo lahko kasneje vrnili vanjo z metodo razveljavi
* `shrani_navidezno_pozicijo(self)`: shrani trenutno pozicijo, ki smo jo dobili v postopku računalnikovega računanja pozicije 
* `razveljavi(self, k=1)`: k-krat razveljavi potezo in se vrni v prejsnje stanje
* `popravi_matriko_kvadratov(self, k, i, j)`: po vsaki potezi popravi matriko, kjer je shranjeno število že narisanih črt okoli vsakega kvadrata
* `nasprotnik(self)`: vrne nasprotnika

### Razred `Clovek`
Igralec je ta, ki igra. 
Atributi: ime, števec in barva.
Igralec je človek. Ima naslednje metode:
* `igraj(self)`: ne naredi ničesar, čaka, da bo igralec kliknil na polje
* `prekini(self)`: to metodo kliče vmesnik, če je treba prekiniti razmišljanje, človek jo lahko ignorira
* `klik(self, x, y)`: ob kliku igralca na polje, odigra potezo

### Razred `Racunalnik`
Igralec je računalnik.
Atributi: ime, števec in barva.
Ima naslednje metode
* `igraj(self)`: algoritmu ukaže, naj razmisli poteze
* `preveri_potezo(self)`: vsakih 100ms preveri, ali je algoritem že izračunal poteze in jih odigra
* `prekini(self)`: to metodo klice GUI, če je treba prekiniti razmisljanje
* `klik(self, x, y)`: ko je na vrsti računalnik, ignorira klikanje

### Razred `Minimax`
* `prekini(self)`: metoda, ki jo poklice GUI, če je treba nehati razmisljati, ker je uporabnik zaprl okno ali izbral novo igro
* `izracunaj_potezo(self, igra)`: izračuna potezo za trenutno stanje igre
* `minimax(self, globina, maksimiziramo, seznam_potez)`: glavna metoda minimax, več o njej si lahko preberete
[tukaj](https://cs.stanford.edu/people/eroberts/courses/soco/projects/1998-99/game-theory/Minimax.html)
* `vrednost_pozicije(self)`: ocena vrednosti pozicije: izračuna razliko med kvadrati trenutnega igralca in nasprotnika
* `najdi(self, element, matrika)`: najde mesto prve pojavitve elementa v matriki 
* `najdi_vse(self, element, matrika)`: najde vsa mesta pojavitve elementa v matriki
* `prazna_stranica(self, i, j)`: najde prazno stranico v kvadratu (i, j), ki ima 3 polne stranice
* `najdi_verigo(self, index)`: najde poteze s katerimi napolnimo odprto verigo, ki ji pripada kvadratek (i, j)
* `potrebno_pregledati(self)`: poišče poteze, ki jih je potrebno pregledati med iskanjem najboljše poteze


### Razred `Alfabeta`
Metode so enake kot pri razredu Minimax, razlika je le v glavni metodi in dodatni funkciji, ki sta opisani spodaj.
* `alfabeta(self, globina, alfa, beta, maksimiziramo, seznam_potez)`: glavna metoda alfabeta, o kateri si več lahko preberete [tukaj](https://www.ocf.berkeley.edu/~yosenl/extras/alphabeta/alphabeta.html)
