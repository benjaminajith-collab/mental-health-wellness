from flask import Flask, render_template, request
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib
matplotlib.use('Agg')
import os

app = Flask(__name__)

# ---------- FUZZY SYSTEM SETUP ----------

sleep = ctrl.Antecedent(np.arange(0, 11, 1), "sleep")
mood_level = ctrl.Antecedent(np.arange(0, 11, 1), "mood_level")
screen_time = ctrl.Antecedent(np.arange(0, 11, 1), "screen_time")
physical_activity = ctrl.Antecedent(np.arange(0, 11, 1), "physical_activity")

stress = ctrl.Consequent(np.arange(0, 11, 1), "stress")

# ---------- FIXED MEMBERSHIP FUNCTIONS (NO DEAD ZONES) ----------

sleep["low"] = fuzz.trimf(sleep.universe, [0, 0, 5])
sleep["medium"] = fuzz.trimf(sleep.universe, [1, 5, 9])
sleep["high"] = fuzz.trimf(sleep.universe, [5, 10, 10])

mood_level["low"] = fuzz.trimf(mood_level.universe, [0, 0, 5])
mood_level["medium"] = fuzz.trimf(mood_level.universe, [1, 5, 9])
mood_level["high"] = fuzz.trimf(mood_level.universe, [5, 10, 10])

screen_time["low"] = fuzz.trimf(screen_time.universe, [0, 0, 5])
screen_time["medium"] = fuzz.trimf(screen_time.universe, [1, 5, 9])
screen_time["high"] = fuzz.trimf(screen_time.universe, [5, 10, 10])

physical_activity["low"] = fuzz.trimf(physical_activity.universe, [0, 0, 5])
physical_activity["medium"] = fuzz.trimf(physical_activity.universe, [1, 5, 9])
physical_activity["high"] = fuzz.trimf(physical_activity.universe, [5, 10, 10])

stress["low"] = fuzz.trimf(stress.universe, [0, 0, 5])
stress["medium"] = fuzz.trimf(stress.universe, [1, 5, 9])
stress["high"] = fuzz.trimf(stress.universe, [5, 10, 10])

# ---------- RULES (COVER ALL CASES) ----------

rules = [
    # HIGH STRESS
    ctrl.Rule(sleep["low"] & screen_time["high"], stress["high"]),
    ctrl.Rule(sleep["low"] & mood_level["low"], stress["high"]),
    ctrl.Rule(screen_time["high"] & physical_activity["low"], stress["high"]),

    # MEDIUM STRESS
    ctrl.Rule(sleep["medium"] & screen_time["medium"], stress["medium"]),
    ctrl.Rule(sleep["medium"] & mood_level["medium"], stress["medium"]),
    ctrl.Rule(sleep["low"] & screen_time["low"], stress["medium"]),  # 🔥 covers your error case

    # LOW STRESS
    ctrl.Rule(sleep["high"] & physical_activity["high"], stress["low"]),
    ctrl.Rule(mood_level["high"] & physical_activity["high"], stress["low"]),
    ctrl.Rule(sleep["high"] & screen_time["low"], stress["low"]),

    # EXTRA COVERAGE
    ctrl.Rule(mood_level["low"] & physical_activity["medium"], stress["high"]),
    ctrl.Rule(sleep["medium"], stress["medium"])  # light fallback (not dominating)
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
        try:
            sleep_val = float(request.form.get("sleep"))
            mood_val = float(request.form.get("mood"))
            screen_val = float(request.form.get("screen"))
            activity_val = float(request.form.get("activity"))

            if any(val > 10 for val in [sleep_val, mood_val, screen_val, activity_val]):
                return render_template("index.html", error="Values must be ≤ 10")

            if any(val < 0 for val in [sleep_val, mood_val, screen_val, activity_val]):
                return render_template("index.html", error="Values must be ≥ 0")

            sim = ctrl.ControlSystemSimulation(stress_ctrl)

            sim.input["sleep"] = sleep_val
            sim.input["mood_level"] = mood_val
            sim.input["screen_time"] = screen_val
            sim.input["physical_activity"] = activity_val

            sim.compute()

            result = round(sim.output["stress"], 2)
            level = get_stress_level(result)

            return render_template("index.html", result=result, level=level)

        except Exception as e:
            print("ERROR:", e)
            return render_template("index.html", error=f"Error: {str(e)}")

    return render_template("index.html")

# ---------- RUN ----------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
