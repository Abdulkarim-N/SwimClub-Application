import hfpy_utils
import swimclub
import statistics
import json


FOLDER = 'swimdata/'
CHARTS = 'charts/'
JSONDATA = 'records.json'

def read_swim_data(filename):
    with open(FOLDER + filename) as file:
        lines = file.readlines()

    swimmer,age,distance,stroke = filename.removesuffix('.txt').split('-')
    times = lines[0].strip().split(',')

    converts = []
    for t in times:
        if ':' in t:
            mins,rest = t.split(':')
            sec,hund = rest.split('.')
        else:
            mins = 0
            sec,hund = t.split('.')

        converts.append((int(mins)*60*100) + (int(sec)*100)+(int(hund)))

    average = statistics.mean(converts)
    mins_secs, hundreths = f"{(average/100):.2f}".split('.')
    mins_secs = int(mins_secs)
    minutes = mins_secs//60
    seconds = mins_secs-minutes*60

    average = f"{minutes}:{seconds:0>2}.{hundreths}"

    return swimmer,age,distance,stroke,times,average, converts


def produce_bar_chart(filename, location=CHARTS):

    (swimmer, age, distance, stroke, times , average, converts) = swimclub.read_swim_data(filename)
    title = (f"{swimmer} Under {age} {distance} {stroke}")

    with open("records.json") as jf:
        records = json.load(jf)
    
    COURSES = ("LC Men", "LC Women", "SC Men", "SC Women")
    times = []
    for course in COURSES:
        times.append(records[course][event_lookup(filename)])

    html = f"""<!DOCTYPE html>
    <html>
        <head>
            <title>{title}</title>
            <link rel="stylesheet" href="/static/webapp.css"/>
        </head>
        <body>
        <h2>{title}</h2>"""


    footer = f"""
            <p>Average time: {average} </p>
            <p>M: {times[0]} ({times[2]})<br/>W: {times[1]} ({times[3]})</p>
        </body>
    </html>
    """


    from_max = max(converts)

    svgs = ""

    times.reverse()
    converts.reverse()

    for n , t in enumerate(times):
        bar_width = hfpy_utils.convert2range(converts[n], 0, from_max, 0, 350)
        svgs= svgs + (f"""
                    <svg height="30" width="400">
                        <rect height="30" width="{bar_width}" style="fill:rgb(0,0,255);" />
                    </svg>{t}<br/>
            """)



    page = html + svgs + footer

    save_to = (f"{location}{filename.removesuffix('.txt')}.html")

    with open(save_to, 'w') as tf:
        print(page, file=tf)

    return save_to


def event_lookup(filename):

    conversions = {
    "Free":"freestyle",
    "Back":"backstroke",
    "Breast":"breaststroke",
    "Fly":"butterfly",
    "IM":"individual medley",
}
    *_, distance, stroke = filename.removesuffix(".txt").split("-")
    return f"{distance} {conversions[stroke]}"