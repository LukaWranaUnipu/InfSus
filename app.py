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


@app.route("/")
@db_session
def index():

    aktivni_plan = select(p for p in Plan if p.aktivno).first()

    entries = list(select(e for e in Dnevnik).order_by(Dnevnik.datum))

    total_days = len(entries)

    avg_weight = (
        round(sum(e.tezina for e in entries) / total_days, 2) if total_days else 0
    )

    latest_weight = entries[-1].tezina if entries else 0

    start_weight = entries[0].tezina if entries else 0

    weight_change = round(latest_weight - start_weight, 2) if total_days > 1 else 0

    trainings_done = sum(1 for e in entries if e.vjezba_obavljena)

    training_success_rate = (
        round((trainings_done / total_days) * 100, 1) if total_days else 0
    )

    avg_calories = (
        round(sum(e.kalorije for e in entries) / total_days) if total_days else 0
    )

    avg_protein = (
        round(sum(e.proteini for e in entries) / total_days) if total_days else 0
    )

    total_training_minutes = sum(e.trajanje_vjezbe for e in entries)

    calorie_goal_success = 0

    if aktivni_plan and total_days:

        successful_days = sum(1 for e in entries if e.kalorije <= aktivni_plan.kalorije)

        calorie_goal_success = round((successful_days / total_days) * 100, 1)

    
    return render_template(
        "index.html",
        aktivni_plan=aktivni_plan,
        total_days=total_days,
        avg_weight=avg_weight,
        latest_weight=latest_weight,
        start_weight=start_weight,
        weight_change=weight_change,
        trainings_done=trainings_done,
        training_success_rate=training_success_rate,
        avg_calories=avg_calories,
        avg_protein=avg_protein,
        total_training_minutes=total_training_minutes,
        calorie_goal_success=calorie_goal_success,
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
