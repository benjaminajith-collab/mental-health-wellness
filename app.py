from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    error = None
    result = None
    level = None

    if request.method == "POST":
        try:
            sleep = int(request.form["sleep"])
            mood = int(request.form["mood"])
            screen = int(request.form["screen"])
            activity = int(request.form["activity"])

            # dummy logic
            result = (sleep + mood + activity - screen) / 3

            if result < 3:
                level = "High"
            elif result < 6:
                level = "Medium"
            else:
                level = "Low"

        except:
            error = "Invalid input!"

    return render_template("index.html", error=error, result=result, level=level)

if __name__ == "__main__":
    app.run(debug=True)
