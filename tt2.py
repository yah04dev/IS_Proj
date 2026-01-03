import os
from flask import Flask, request, render_template,redirect,url_for
from datetime import datetime
import uuid  # ensures unique file names
import re
import numpy as np
import joblib
app = Flask(__name__)

recording = False
current_filename = None

# Create a unique filename for every recording session
def get_filename():
    os.makedirs("data", exist_ok=True)  # save files in data folder
    # Use timestamp + random UUID to avoid collisions
    return os.path.join("data","test.txt")

def write_to_file(filename, x, y, z, gx, gy, gz):
    with open(filename, 'a') as f:
        f.write(f"x: {x}, y: {y}, z: {z}, gx: {gx}, gy: {gy}, gz: {gz}\n")
def extract_features(path):
    rows = []

    with open(path, "r") as f:
        for line in f:
            nums = re.findall(r'-?\d+\.?\d*', line)
            if len(nums) == 6:
                rows.append([float(n) for n in nums])

    if len(rows) < 5:
        raise ValueError("File too short")

    data = np.array(rows)

    feat = []
    for i in range(6):
        a = data[:, i]
        feat += [a.mean(), a.std(), a.min(), a.max(), np.var(a)]

    return feat

@app.route('/')
def index():






    return render_template('index.html')


@app.route('/toggle', methods=['POST'])
def toggle_recording():
    global recording, current_filename
    action = request.form.get("action")

    if action == "start":
        recording = True
        current_filename = get_filename()  # NEW FILE FOR THIS SESSION
        print(f"[INFO] Recording started → {current_filename}")
        return f"Recording started → {current_filename}"

    elif action == "stop":
        recording = False
        print(f"[INFO] Recording stopped → {current_filename}")
        current_filename = None
        return "Recording stopped"

    else:
        return "Invalid action", 400


@app.route("/resault")
def resault():
        model = joblib.load("handwriting_svm.pkl")
        file = os.path.join("data", "test.txt")
 
        features = extract_features(file)

        pred = model.predict([features])[0]

        print("GOOD writing" if pred == 1 else "BAD writing")
        if pred == 1:
           file = os.path.join("data", "test.txt")


           if os.path.exists(file):
             os.remove(file)
             print("File deleted")
           else:
             print("File not found")
           return redirect(url_for("good"))
        else:
           file = os.path.join("data", "test.txt")


           if os.path.exists(file):
             os.remove(file)
             print("File deleted")
           else:
             print("File not found")
           return redirect(url_for("bad"))

@app.route("/good")
def good():
    return render_template("good.html")

@app.route("/bad")
def bad():
    return render_template("bad.html")
@app.route('/data', methods=['GET'])
def receive_data():
  
    global recording, current_filename

    if not recording or current_filename is None:
        return "Not recording", 200

    x = request.args.get('x')
    y = request.args.get('y')
    z = request.args.get('z')
    gx = request.args.get('gx')
    gy = request.args.get('gy')
    gz = request.args.get('gz')

    write_to_file(current_filename, x, y, z, gx, gy, gz)
    return "OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
