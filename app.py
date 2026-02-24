from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

app = Flask(__name__)

# ---------- FUZZY SYSTEM SETUP ----------

sleep = ctrl.Antecedent(np.arange(0, 11, 1), "sleep")
mood_level = ctrl.Antecedent(np.arange(0, 11, 1), "mood_level")
screen_time = ctrl.Antecedent(np.arange(0, 11, 1), "screen_time")
physical_activity = ctrl.Antecedent(np.arange(0, 11, 1), "physical_activity")

stress = ctrl.Consequent(np.arange(0, 11, 1), "stress")

# Membership Functions
sleep["low"] = fuzz.trimf(sleep.universe, [0, 0, 4])
sleep["medium"] = fuzz.trimf(sleep.universe, [3, 5, 7])
sleep["high"] = fuzz.trimf(sleep.universe, [6, 10, 10])

mood_level["low"] = fuzz.trimf(mood_level.universe, [0, 0, 4])
mood_level["medium"] = fuzz.trimf(mood_level.universe, [3, 5, 7])
mood_level["high"] = fuzz.trimf(mood_level.universe, [6, 10, 10])

screen_time["low"] = fuzz.trimf(screen_time.universe, [0, 0, 4])
screen_time["medium"] = fuzz.trimf(screen_time.universe, [3, 5, 7])
screen_time["high"] = fuzz.trimf(screen_time.universe, [6, 10, 10])

physical_activity["low"] = fuzz.trimf(physical_activity.universe, [0, 0, 4])
physical_activity["medium"] = fuzz.trimf(physical_activity.universe, [3, 5, 7])
physical_activity["high"] = fuzz.trimf(physical_activity.universe, [6, 10, 10])

stress["low"] = fuzz.trimf(stress.universe, [0, 0, 4])
stress["medium"] = fuzz.trimf(stress.universe, [3, 5, 7])
stress["high"] = fuzz.trimf(stress.universe, [6, 10, 10])

# Rules
rules = [
    ctrl.Rule(sleep["low"] & screen_time["high"], stress["high"]),
    ctrl.Rule(sleep["low"] & mood_level["low"], stress["high"]),
    ctrl.Rule(sleep["medium"] & screen_time["medium"], stress["medium"]),
    ctrl.Rule(sleep["high"] & physical_activity["high"], stress["low"]),
    ctrl.Rule(mood_level["high"] & physical_activity["high"], stress["low"]),
    ctrl.Rule(sleep["medium"] & mood_level["medium"], stress["medium"]),
    ctrl.Rule(screen_time["high"] & physical_activity["low"], stress["high"]),
    ctrl.Rule(sleep["high"] & screen_time["low"], stress["low"]),
    ctrl.Rule(mood_level["low"] & physical_activity["medium"], stress["high"]),
    ctrl.Rule(sleep["low"] & screen_time["high"] & mood_level["low"], stress["high"])
]

stress_ctrl = ctrl.ControlSystem(rules)


# ---------- STRESS LEVEL FUNCTION ----------
def get_stress_level(val):
    if val <= 3:
        return "Low"
    elif val <= 6:
        return "Medium"
    else:
        return "High"


# ---------- ROUTE ----------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        sleep_val = float(request.form["sleep"])
        mood_val = float(request.form["mood"])
        screen_val = float(request.form["screen"])
        activity_val = float(request.form["activity"])

        sim = ctrl.ControlSystemSimulation(stress_ctrl)
        sim.input["sleep"] = sleep_val
        sim.input["mood_level"] = mood_val
        sim.input["screen_time"] = screen_val
        sim.input["physical_activity"] = activity_val

        sim.compute()
        result = round(sim.output["stress"], 2)
        level = get_stress_level(result)

        return render_template("index.html", result=result, level=level)

    return render_template("index.html")


import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)