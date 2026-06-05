# Fitness Planner

Web aplikacija za planiranje treninga i praćenje prehrane izrađena u Python Flask frameworku koristeći PonyORM i SQLite bazu podataka.

## Opis projekta

Fitness Planner omogućuje korisniku izradu fitness planova koji uključuju:

- broj treninga tjedno
- opis vježbi
- planirano trajanje treninga
- dnevni kalorijski cilj
- dnevne makronutrijente (proteini, masti i ugljikohidrati)

Korisnik zatim svakodnevno vodi dnevnik prehrane i treninga te može pratiti svoj napredak kroz statistike i vizualizacije podataka.

Projekt koristi vlastiti web servis izrađen u Flask-u te SQLite bazu podataka za pohranu podataka.

---

# Funkcionalnosti

## Planovi treninga

- Kreiranje novih fitness planova
- Uređivanje postojećih planova
- Brisanje planova
- Aktivacija jednog aktivnog plana
- Prikaz svih planova

## Dnevni unosi

- Dodavanje dnevnih unosa
- Evidencija kalorija i makronutrijenata
- Evidencija obavljenih treninga
- Evidencija tjelesne težine
- Praćenje trajanja treninga

## Statistike i analitika

- Ukupan broj dana praćenja
- Trenutna i početna težina
- Promjena težine kroz vrijeme
- Uspješnost treninga
- Uspješnost kalorijskog cilja
- Prosječan unos kalorija
- Prosječan unos proteina
- Ukupno vrijeme treninga
- Tjedni napredak korisnika
- Graf kretanja težine
- Graf unosa kalorija

---

# Tehnologije

- Python
- Flask
- PonyORM
- SQLite
- HTML
- CSS
- Bootstrap 5
- Chart.js
- Docker

---

# Struktura baze podataka

## Tablica: plan

| Atribut | Opis |
|---|---|
| id | Primarni ključ |
| naziv | Naziv plana |
| broj_vjezba | Broj treninga tjedno |
| opis_vjezba | Opis vježbi |
| trajanje | Planirano trajanje treninga |
| kalorije | Dnevni kalorijski cilj |
| proteini | Dnevni unos proteina |
| masti | Dnevni unos masti |
| ugljikohidrati | Dnevni unos ugljikohidrata |
| aktivno | Označava aktivni plan |

## Tablica: dnevnik

| Atribut | Opis |
|---|---|
| id | Primarni ključ |
| plan | Povezani plan |
| datum | Datum unosa |
| kalorije | Unesene kalorije |
| proteini | Uneseni proteini |
| masti | Unesene masti |
| ugljikohidrati | Uneseni ugljikohidrati |
| vjezba_obavljena | Je li trening odrađen |
| opis_vjezbe | Opis treninga |
| trajanje_vjezbe | Trajanje treninga |
| tezina | Tjelesna težina |

---

# Pokretanje aplikacije lokalno

## 1. Kloniranje repozitorija

```bash
git clone https://github.com/USERNAME/fitness-planner.git
cd fitness-planner
```

## 2. Kreiranje virtualnog okruženja
Windows

```bash
python -m venv venv
venv\Scripts\activate
```

Linux / MacOS

```bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Instalacija potrebnih paketa

```bash
pip install flask pony
```

## 4. Pokretanje aplikacije

```bash
python app.py
```

Aplikacija će biti dostupna na:

```
http://127.0.0.1:5000
```

Docker pokretanje

```bash
docker build -t fitness-planner .
docker run -p 5000:5000 fitness-planner
```