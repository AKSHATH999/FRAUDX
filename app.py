from flask import Flask, render_template, request, redirect, session
import sqlite3
import joblib
import numpy as np

app = Flask(__name__)
app.secret_key = "fraudx_secret_key"

# Load ML Model
model = joblib.load('trained_model/fraud_model.pkl')

# DB CONNECTION
def get_db_connection():
    conn = sqlite3.connect("fraudx.db")
    conn.row_factory = sqlite3.Row
    return conn

# HOME
@app.route('/')
def home():
    return render_template('index.html')

# REGISTER
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except Exception as e:
            return f"Error: {e}"

    return render_template("register.html")

# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")

# DASHBOARD
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result='SAFE'")
    safe = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result='FRAUD'")
    fraud = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        user=session["user"],
        total=total,
        safe=safe,
        fraud=fraud
    )

# DETECT FRAUD
@app.route("/detect", methods=["GET", "POST"])
def detect():

    prediction = None

    if request.method == "POST":

        try:
            time = float(request.form["time"])
            amount = float(request.form["amount"])

            v_features = [0] * 28
            features = np.array([time] + v_features + [amount]).reshape(1, -1)

            result = model.predict(features)[0]
            prediction = "FRAUD" if result == 1 else "SAFE"

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO predictions (amount, time, prediction_result) VALUES (?, ?, ?)",
                (amount, time, prediction)
            )

            conn.commit()
            conn.close()

        except Exception as e:
            prediction = f"Error: {e}"

    return render_template("detect.html", prediction=prediction)

# HISTORY
@app.route("/history")
def history():

    if "user" not in session:
        return redirect("/login")

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
    data = cursor.fetchall()

    conn.close()

    return render_template("history.html", data=data)

# STATS API
@app.route("/stats")
def stats():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result='SAFE'")
    safe = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result='FRAUD'")
    fraud = cursor.fetchone()[0]

    conn.close()

    return {
        "total": total,
        "safe": safe,
        "fraud": fraud
    }

# LOGOUT
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# RUN APP
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)