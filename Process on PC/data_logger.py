"""
=============================================================================
Edge-Fog Data Logger (ULTIMATE EDITION)
Role: Subscribes to the Raspberry Pi's massive JSON payload and permanently 
      stores all metrics into SQLite for Streamlit Visualization.
Author: Vincent Tay Yong Jun
=============================================================================
"""

import paho.mqtt.client as mqtt
import sqlite3
import json

# Initialize SQLite Database with the Ultimate Schema
conn = sqlite3.connect('vibration_data.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS logs_ultimate
             (timestamp DATETIME, status TEXT, mse REAL, threshold REAL, 
              latency REAL, peak_freq REAL, cpu REAL, ram REAL, temp REAL, raw_waveform TEXT)''')
conn.commit()

# Ensure this matches your Raspberry Pi's actual IP address!
RASPBERRY_PI_IP = "172.27.176.176" 

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        # Extract nested structures
        status = data['status']
        ai = data['ai_metrics']
        phys = data['physical_metrics']
        health = data['edge_health']
        
        waveform_str = json.dumps(data.get('raw_waveform', []))
        
        # Insert all 9 metrics into the database
        c.execute("""INSERT INTO logs_ultimate VALUES 
                     (datetime('now','localtime'), ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                  (status, ai['mse'], ai['threshold'], ai['latency_ms'], 
                   phys['peak_frequency_hz'], health['cpu_usage_percent'], 
                   health['ram_usage_percent'], health['pi_temperature_c'], waveform_str))
        conn.commit()
        
        print(f"✅ DB Saved | Status: {status} | MSE: {ai['mse']:.4f} | Peak Freq: {phys['peak_frequency_hz']}Hz")
        
    except Exception as e:
        print(f"[ERROR] Database Insertion Failed: {e}")

if __name__ == "__main__":
    client = mqtt.Client()
    client.on_message = on_message
    client.connect(RASPBERRY_PI_IP, 1883, 60)
    client.subscribe("dashboard/results")
    print("\n✅ Ultimate Data Logger Active. Waiting for Edge metrics...\n")
    client.loop_forever()