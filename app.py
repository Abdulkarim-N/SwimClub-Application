import data_utils
import convert_utils

from flask import Flask, session, render_template, request

app = Flask(__name__)
app.secret_key = "Chungas"

@app.get("/")
def index():
    return render_template(
        "index.html", #uses this template
        title="Welcome To the SwimClub", #changes the {title} to the given
        )

@app.get("/swims")
def display_swim_sessions():
    data= data_utils.get_swim_sessions()
    ## dates = [session[0].split(" ")[0] for session in data]  # SQLite3.
    dates = [str(session[0].date()) for session in data]  # MySQL/MariaDB.
    return render_template(
        "select.html",
        title="Select a swim session",
        url="/swimmers",
        select_id="chosen_date",
        data=dates,
    )



@app.post("/swimmers")
def display_swimmers():
    session["chosen_date"] = request.form["chosen_date"]
    data = data_utils.get_session_swimmers(session["chosen_date"])
    swimmers = [f"{x[0]}-{x[1]}" for x in data]
    return render_template( #uses the select template and fills the data with the following info
        "select.html",
        title="Select a swimmer",
        select_id="swimmer",
        url="/showevents",
        data=sorted(swimmers),
    )


@app.post("/showevents")
def display_swimmer_events():
    session["swimmer"],session["age"] = request.form["swimmer"].split("-")
    data = data_utils.get_swimmers_events(session["swimmer"],session["age"],session["chosen_date"])
    session["events"] = [f"{x[0]} {x[1]}" for x in data]
    return render_template(
        "select.html",
        title="Select an Event",
        url="/showbarchart",
        select_id="event",
        data=session["events"],
    )


@app.post("/showbarchart")
def show_bar_chart():
    distance,stroke = request.form["event"].split(" ")
    data = data_utils.get_swimmers_times(
        session["swimmer"],
        session["age"],
        distance,
        stroke,
        session["chosen_date"]
    )
    times = [time[0] for time in data]
    average_str,times_reversed,scaled = convert_utils.perform_conversions(times)
    worlds_time = convert_utils.get_worlds(distance,stroke)
    header = f"{session['swimmer']} (Under {session['age']}) {distance} {stroke} - {session['chosen_date']}"    
    return render_template(
        "chart.html",
        title=header,
        average=average_str,
        worlds=worlds_time,
        data=list(zip(times_reversed,scaled))
    )

if __name__ == "__main__":
    app.run(debug=True)