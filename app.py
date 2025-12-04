from flask import Flask, render_template, request, jsonify
import uuid
from datetime import datetime
import requests, threading, time

app = Flask(__name__)

# -------------------------
#   GLOBAL ORDERS (NO DB)
# -------------------------
orders = {}

# -------------------------
#   KEEP-ALIVE FUNCTION
# -------------------------
def keep_alive():
    while True:
        try:
            requests.get("https://your-app.onrender.com/ping")
        except:
            pass
        time.sleep(25)  # Less than 50 sec Render timeout

threading.Thread(target=keep_alive, daemon=True).start()

@app.route("/ping")
def ping():
    return "OK", 200


# -------------------------
#   HELPER: TRACKING ID
# -------------------------
def generate_tid():
    return str(uuid.uuid4())[:8].upper()


# -------------------------
#   HOME
# -------------------------
@app.route("/")
def home():
    return "<h2>Car Wash Tracking System Running...</h2>"


# -------------------------
#   ADMIN PANEL
# -------------------------
@app.route("/admin")
def admin():
    return render_template("admin.html", orders=orders)


# -------------------------
#   CREATE NEW ORDER
# -------------------------
@app.route("/create", methods=["POST"])
def create_order():
    customer = request.form["customer"]
    car_no = request.form["car_no"]
    service = request.form["service"]

    tid = generate_tid()

    orders[tid] = {
        "customer": customer,
        "car": car_no,
        "service": service,
        "status": "Car Received",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    track_url = f"https://your-app.onrender.com/track/{tid}"

    return f"""
        <h3>Tracking Created Successfully ✔</h3>
        <p><b>Customer:</b> {customer}</p>
        <p><b>Car No:</b> {car_no}</p>
        <p><b>Service:</b> {service}</p>
        <hr>
        <p><b>Tracking Link:</b></p>
        <a href="{track_url}" target="_blank">{track_url}</a>
    """


# -------------------------
#   UPDATE STATUS (ADMIN)
# -------------------------
@app.route("/update/<tid>", methods=["POST"])
def update_order(tid):
    status = request.form["status"]
    orders[tid]["status"] = status
    orders[tid]["time"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    return "Updated Successfully!"


# -------------------------
#   CUSTOMER TRACK PAGE
# -------------------------
@app.route("/track/<tid>")
def track(tid):
    if tid not in orders:
        return "<h2>Invalid Tracking ID</h2>"

    return render_template("track.html", tid=tid, data=orders[tid])


# -------------------------
#   LIVE STATUS API
# -------------------------
@app.route("/live/<tid>")
def live(tid):
    return jsonify(orders[tid])


# -------------------------
#   START APP
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
