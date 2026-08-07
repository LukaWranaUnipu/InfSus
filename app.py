from flask import Flask, render_template, request, redirect
from pony.orm import *
from datetime import date

app = Flask(__name__)
db = Database()


class Plan(db.Entity):
    id = PrimaryKey(int, auto=True)
    naziv = Required(str)
    broj_vjezba = Required(int)
    opis_vjezba = Required(str)
    trajanje = Required(int)
    kalorije = Required(int)
    proteini = Required(int)
    masti = Required(int)
    ugljikohidrati = Required(int)
    aktivno = Required(bool, default=False)
    dnevnici = Set("Dnevnik")


class Dnevnik(db.Entity):
    id = PrimaryKey(int, auto=True)
    plan = Optional(Plan)
    datum = Required(str)
    kalorije = Required(int)
    proteini = Required(int)
    masti = Required(int)
    ugljikohidrati = Required(int)
    vjezba_obavljena = Required(bool)
    opis_vjezbe = Optional(str)
    trajanje_vjezbe = Optional(int)
    tezina = Required(float)


db.bind(provider="sqlite", filename="database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)


def unosi_za_plan(entries, plan):
    if not plan:
        return []

    return [e for e in entries if e.plan == plan]


def tjedni_trening_uspjesnost(entries, plan):
    if not plan or not entries:
        return 0

    planirani_treninzi = max(plan.broj_vjezba, 0)

    if planirani_treninzi == 0:
        return 0

    tjedni = {}

    for entry in entries:
        datum = date.fromisoformat(entry.datum)
        godina, tjedan, _ = datum.isocalendar()
        tjedni.setdefault((godina, tjedan), 0)

        if entry.vjezba_obavljena:
            tjedni[(godina, tjedan)] += 1

    uspjesni_tjedni = sum(
        1 for broj_treninga in tjedni.values() if broj_treninga >= planirani_treninzi
    )

    return round((uspjesni_tjedni / len(tjedni)) * 100, 1)


def trening_cilj_uspjesnost(broj_treninga, plan):
    if not plan or plan.broj_vjezba <= 0:
        return 0

    return round(min((broj_treninga / plan.broj_vjezba) * 100, 100), 1)


@app.route("/")
@db_session
def index():

    aktivni_plan = select(p for p in Plan if p.aktivno).first()

    entries = list(select(e for e in Dnevnik).order_by(Dnevnik.datum))
    plan_entries = unosi_za_plan(entries, aktivni_plan)

    ukupni_dani = len(entries)

    prosjecna_tezina = (
        round(sum(e.tezina for e in entries) / ukupni_dani, 2) if ukupni_dani else 0
    )

    trenutna_tezina = entries[-1].tezina if entries else 0

    pocetna_tezina = entries[0].tezina if entries else 0

    promijena_tezine = round(trenutna_tezina - pocetna_tezina, 2) if ukupni_dani > 1 else 0

    trening_obavljen = sum(1 for e in entries if e.vjezba_obavljena)

    stopa_uspjesnosti_treninga = tjedni_trening_uspjesnost(
        plan_entries,
        aktivni_plan,
    )

    prosjecne_kalorije = (
        round(sum(e.kalorije for e in entries) / ukupni_dani) if ukupni_dani else 0
    )

    prosjecni_proteini = (
        round(sum(e.proteini for e in entries) / ukupni_dani) if ukupni_dani else 0
    )

    ukupne_minute_treninga = sum(e.trajanje_vjezbe or 0 for e in entries)

    usjpjesnost_kalorijskog_cilja = 0

    if aktivni_plan and plan_entries:

        successful_days = sum(
            1 for e in plan_entries if e.kalorije <= aktivni_plan.kalorije
        )

        usjpjesnost_kalorijskog_cilja = round(
            (successful_days / len(plan_entries)) * 100, 1
        )

    zadnjih_7 = plan_entries[-7:] if len(plan_entries) >= 7 else []

    tjedni_treninzi = sum(1 for e in zadnjih_7 if e.vjezba_obavljena)

    tjedni_kalorijski_uspjeh = 0

    if aktivni_plan and zadnjih_7:

        uspjesni_dani = sum(
            1 for e in zadnjih_7 if e.kalorije <= aktivni_plan.kalorije
        )

        tjedni_kalorijski_uspjeh = round(
            (uspjesni_dani / len(zadnjih_7)) * 100
        )

    tjedni_trening_uspjeh = trening_cilj_uspjesnost(
        tjedni_treninzi,
        aktivni_plan,
    ) if zadnjih_7 else 0


    uspjesna_dijeta = tjedni_kalorijski_uspjeh >= 70
    uspjesni_treninzi = bool(
        aktivni_plan and zadnjih_7 and tjedni_treninzi >= aktivni_plan.broj_vjezba
    )

    tezine = [e.tezina for e in entries]
    datumi = [e.datum for e in entries]

    kalorije_data = [e.kalorije for e in entries]

    
    return render_template(
        "index.html",
        aktivni_plan=aktivni_plan,
        ukupni_dani=ukupni_dani,
        prosjecna_tezina=prosjecna_tezina,
        trenutna_tezina=trenutna_tezina,
        pocetna_tezina=pocetna_tezina,
        promijena_tezine=promijena_tezine,
        trening_obavljen=trening_obavljen,
        stopa_uspjesnosti_treninga=stopa_uspjesnosti_treninga,
        prosjecne_kalorije=prosjecne_kalorije,
        prosjecni_proteini=prosjecni_proteini,
        ukupne_minute_treninga=ukupne_minute_treninga,
        usjpjesnost_kalorijskog_cilja=usjpjesnost_kalorijskog_cilja,
        tjedni_kalorijski_uspjeh=tjedni_kalorijski_uspjeh,
        tjedni_trening_uspjeh=tjedni_trening_uspjeh,
        tjedni_treninzi=tjedni_treninzi,
        uspjesna_dijeta=uspjesna_dijeta,
        uspjesni_treninzi=uspjesni_treninzi,
        broj_tjednih_unosa=len(zadnjih_7),
        tezine=tezine,
        datumi=datumi,
        kalorije_data=kalorije_data,
    )


@app.route("/planovi")
@db_session
def planovi():
    aktivni_plan = select(p for p in Plan if p.aktivno).first()

    ostali_planovi = select(p for p in Plan if not p.aktivno)[:]

    plans = []

    if aktivni_plan:
        plans.append(aktivni_plan)

    plans.extend(ostali_planovi)

    return render_template("planovi.html", plans=plans)


@app.route("/aktiviraj/<int:id>")
@db_session
def aktiviraj(id):
    for p in Plan.select():
        p.aktivno = False

    plan = Plan[id]
    plan.aktivno = True

    return redirect("/planovi")


@app.route("/dodaj_plan", methods=["GET", "POST"])
@db_session
def dodaj_plan():
    if request.method == "POST":
        postoji_plan = Plan.select().count() > 0

        Plan(
            naziv=request.form["naziv"],
            broj_vjezba=int(request.form["broj"]),
            opis_vjezba=request.form["opis"],
            trajanje=int(request.form["trajanje"]),
            kalorije=int(request.form["kalorije"]),
            proteini=int(request.form["proteini"]),
            masti=int(request.form["masti"]),
            ugljikohidrati=int(request.form["uh"]),
            aktivno=not postoji_plan,
        )
        return redirect("/planovi")
    return render_template("dodaj_plan.html")


@app.route("/uredi-plan/<int:id>", methods=["GET", "POST"])
@db_session
def uredi_plan(id):

    plan = Plan[id]

    if request.method == "POST":

        plan.naziv = request.form["naziv"]
        plan.broj_vjezba = int(request.form["broj"])
        plan.opis_vjezba = request.form["opis"]
        plan.trajanje = int(request.form["trajanje"])
        plan.kalorije = int(request.form["kalorije"])
        plan.proteini = int(request.form["proteini"])
        plan.masti = int(request.form["masti"])
        plan.ugljikohidrati = int(request.form["uh"])

        return redirect("/planovi")

    return render_template("uredi_plan.html", plan=plan)


@app.route("/obrisi-plan/<int:id>")
@db_session
def obrisi_plan(id):

    plan = Plan[id]

    je_aktivan = plan.aktivno

    delete(p for p in Dnevnik if p.plan == plan)

    plan.delete()

    if je_aktivan:

        prvi = select(p for p in Plan).first()

        if prvi:
            prvi.aktivno = True

    return redirect("/planovi")


@app.route("/dodaj_unos", methods=["GET", "POST"])
@db_session
def dodaj_unos():

    aktivni_plan = select(p for p in Plan if p.aktivno).first()

    if aktivni_plan and request.method == "POST":
        Dnevnik(
            plan=aktivni_plan,
            datum=str(date.today()),
            kalorije=int(request.form["kalorije"]),
            proteini=int(request.form["proteini"]),
            masti=int(request.form["masti"]),
            ugljikohidrati=int(request.form["uh"]),
            vjezba_obavljena=request.form.get("vjezba") == "on",
            opis_vjezbe=request.form.get("opis", ""),
            trajanje_vjezbe=int(request.form.get("trajanje") or 0),
            tezina=float(request.form["tezina"]),
        )

        return redirect("/dodaj_unos")

    entries = select(e for e in Dnevnik).order_by(desc(Dnevnik.id))[:]

    return render_template("dodaj_unos.html", plan=aktivni_plan, entries=entries)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
