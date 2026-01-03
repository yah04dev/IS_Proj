import os
from flask import Flask, request, render_template
from datetime import datetime
import uuid  # ensures unique file names

app = Flask(__name__)

recording = False
current_filename = None

# Create a unique filename for every recording session
def get_filename():
    os.makedirs("data", exist_ok=True)  # save files in data folder
    # Use timestamp + random UUID to avoid collisions
    return os.path.join("data", datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + "_" + str(uuid.uuid4())[:8] + ".txt")

def write_to_file(filename, x, y, z, gx, gy, gz):
    with open(filename, 'a') as f:
        f.write(f"x: {x}, y: {y}, z: {z}, gx: {gx}, gy: {gy}, gz: {gz}\n")

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
