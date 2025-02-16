import fastf1
import os
from flask import Flask, request, jsonify, render_template
import numpy as np
import matplotlib.pyplot as plt
import fastf1.plotting
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import LeakyReLU
from tensorflow.keras.losses import MeanSquaredError

# ✅ Fix Matplotlib GUI Issues
import matplotlib
matplotlib.use('Agg')

app = Flask(__name__)

# Enable FastF1 Cache
fastf1.Cache.enable_cache("E:/python codes/cache")

# ✅ Ensure Static Folder Exists
STATIC_FOLDER = "static"
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

@app.route('/')
def index():
    """Render the frontend page."""
    return render_template("index.html")

### ✅ Fixed Lap Time Distribution API
@app.route('/lapdistribution', methods=['GET'])
def get_lap_distribution():
    year = request.args.get('year', type=int)
    race = request.args.get('race', type=str)
    session_type = request.args.get('session', type=str)
    driver = request.args.get('driver', type=str)

    try:
        # ✅ Load session
        session = fastf1.get_session(year, race, session_type)
        session.load()

        # ✅ Find driver (handle both abbreviations & numbers)
        driver_match = [
            drv for drv in session.drivers 
            if drv == driver or session.get_driver(drv)['Abbreviation'] == driver
        ]
        
        if not driver_match:
            return jsonify({"error": f"Driver '{driver}' not found in session."}), 404
        
        driver_id = driver_match[0]
        driver_laps = session.laps.pick_driver(driver_id)

        # ✅ FIX: Check if LapTime data is available before proceeding
        if driver_laps.empty or driver_laps['LapTime'].isnull().all():
            return jsonify({"error": f"No valid lap time data available for driver {driver}."}), 404

        # ✅ Generate Histogram
        fig, ax = plt.subplots()
        ax.hist(driver_laps['LapTime'].dt.total_seconds(), bins=15, color='blue', edgecolor='black')

        ax.set_xlabel("Lap Time (seconds)")
        ax.set_ylabel("Frequency")
        ax.set_title(f"Lap Time Distribution - {driver}")

        img_path = os.path.join(STATIC_FOLDER, "lap_distribution.png")
        plt.savefig(img_path)
        plt.close()

        return jsonify({"image_url": f"/{img_path}"})

    except Exception as e:
        print(f"❌ Lap Distribution Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
