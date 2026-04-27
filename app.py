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

class Dnevnik(db.Entity):
    id = PrimaryKey(int, auto=True)
    plan = Optional(Plan)
    datum = Required(str)
    kalorije = Required(int)
    proteini = Required(int)
    masti = Required(int)
    ugljikohidrati = Required(int)
    vjezba_obavljena = Required(bool)
    opis_vjezbe = Required(str)
    trajanje_vjezbe = Required(int)
    tezina = Required(float)

db.bind(provider='sqlite', filename='database.sqlite', create_db=True)
db.generate_mapping(create_tables=True)

@app.route("/")
@db_session
def index():
    plans = select(p for p in Plan)[:]
    return render_template("index.html", plans=plans)

@app.route("/add-plan", methods=["GET","POST"])
@db_session
def add_plan():
    if request.method == "POST":
        Plan(
            naziv=request.form["naziv"],
            broj_vjezba=int(request.form["broj"]),
            opis_vjezba=request.form["opis"],
            trajanje=int(request.form["trajanje"]),
            kalorije=int(request.form["kalorije"]),
            proteini=int(request.form["proteini"]),
            masti=int(request.form["masti"]),
            ugljikohidrati=int(request.form["uh"])
        )
        return redirect("/")
    return render_template("add_plan.html")

if __name__ == "__main__":
    app.run(debug=True)