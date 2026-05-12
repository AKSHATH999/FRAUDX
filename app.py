from flask import Flask, render_template, request, redirect, session
import mysql.connector
import joblib
import numpy as np

app = Flask(__name__)
app.secret_key = "fraudx_secret_key"

# Load Trained ML Model
model = joblib.load('trained_model/fraud_model.pkl')

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Aksh13@30",
        database="fraudx"
    )

# HOME PAGE
@app.route('/')
def home():
    return render_template('index.html')

# REGISTER PAGE
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            values = (username, password)

            cursor.execute(query, values)

            conn.commit()

            cursor.close()
            conn.close()

            return redirect("/login")

        except Exception as e:
            return f"Error: {e}"

    return render_template("register.html")

# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE username=%s AND password=%s"
        values = (username, password)

        cursor.execute(query, values)

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

    # total transactions
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]

    # safe transactions
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result LIKE '%SAFE%'")
    safe = cursor.fetchone()[0]

    # fraud transactions
    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result LIKE '%FRAUD%'")
    fraud = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        user=session["user"],
        total=total,
        safe=safe,
        fraud=fraud
    )

# FRAUD DETECTION
@app.route("/detect", methods=["GET", "POST"])
def detect():
    print("METHOD:", request.method)
    print("FORM DATA:", request.form)

    prediction = None

    if request.method == "POST":

        try:
            print("DETECT ROUTE HIT")

            time = float(request.form["time"])
            amount = float(request.form["amount"])

            v_features = [0] * 28
            features = np.array([time] + v_features + [amount]).reshape(1, -1)

            result = model.predict(features)[0]

            prediction = "FRAUD" if result == 1 else "SAFE"

            print("PREDICTION:", prediction)

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute(
                "INSERT INTO predictions (prediction_result, amount, time) VALUES (%s, %s, %s)",
                (prediction, amount, time)
            )

            conn.commit()
            conn.close()

            print("INSERT DONE")

        except Exception as e:
            print("ERROR:", e)
            prediction = f"Error: {e}"

    return render_template("detect.html", prediction=prediction)
#TRANSACTION HISTORY
@app.route("/history")
def history():

    # safety check (user must be logged in)
    if "user" not in session:
        return redirect("/login")

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM predictions ORDER BY id DESC")
        data = cursor.fetchall()

        conn.close()

        return render_template("history.html", data=data)

    except Exception as e:
        return f"Error: {e}"
#STATS
@app.route("/stats")
def stats():

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM predictions")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result='SAFE'")
    safe = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM predictions WHERE prediction_result LIKE '%FRAUD%'")
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

# RUN FLASK
if __name__ == "__main__":
    app.run(debug=True)