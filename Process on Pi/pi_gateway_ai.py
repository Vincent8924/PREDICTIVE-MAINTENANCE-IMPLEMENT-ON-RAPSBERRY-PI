"""
=============================================================================
Edge AI Predictive Maintenance Gateway (ULTIMATE EDITION)
Device: Raspberry Pi 4
Features: 
  - Lite-Hybrid-AE AI Inference
  - Dynamic Calibration & State Persistence
  - Edge Hardware Health Monitoring (CPU, RAM, Temp)
  - Physical Signal Explainability (Peak Frequency)
Author: Vincent Tay Yong Jun
=============================================================================
"""

import os
import time
import json
import numpy as np
import psutil
import paho.mqtt.client as mqtt

try:
    import tflite_runtime.interpreter as tflite
    print("[SYSTEM] Edge optimization active: Using tflite_runtime.")
except ImportError:
    import tensorflow.lite as tflite
    print("[SYSTEM] Using standard TensorFlow Lite engine.")

# =========================================================================
# 1. SYSTEM CONFIGURATION
# =========================================================================
MODEL_PATH = "Lite_Hybrid_AE_Edge.tflite"
MQTT_BROKER = "localhost"  
TOPIC_SUBSCRIBE_RAW = "sensor/raw"
TOPIC_PUBLISH_RESULT = "dashboard/results"
MEMORY_FILE = "machine_threshold_memory.json"

# Assume MPU6050 sampling rate is ~200Hz for Frequency Calculation
SAMPLING_RATE_HZ = 200  

CALIBRATION_ROUNDS = 50
calibration_mse_list = []
dynamic_threshold = 0.0
buffer_x = []
current_round = 0
is_calibrated = False

SYSTEM_START_TIME = time.time()

# Restore Persistent Memory
if os.path.exists(MEMORY_FILE):
    try:
        with open(MEMORY_FILE, 'r') as f:
            dynamic_threshold = float(json.load(f)['threshold'])
            is_calibrated = True
            print(f"\n🧠 [STATE RESTORED] Locked Threshold: {dynamic_threshold:.4f}\n")
    except Exception as e:
        print(f"[WARNING] Memory failed. Recalibrating. Error: {e}")

# =========================================================================
# 2. HELPER FUNCTIONS
# =========================================================================
print(f"[SYSTEM] Loading AI Engine: {MODEL_PATH}")
interpreter = tflite.Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def process_signal(raw_data):
    """ Applies FFT to transform Time Domain to Frequency Domain. """
    signal = np.array(raw_data, dtype=np.float32)
    signal = signal - np.mean(signal)  
    fft_vals = np.abs(np.fft.rfft(signal))
    features = fft_vals[1:513].astype(np.float32)
    return features.reshape(1, 512, 1)

def get_pi_temperature():
    """ Extracts physical CPU temperature from Raspberry Pi sensors. """
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            return float(f.read()) / 1000.0
    except:
        return 0.0 # Fallback if run on Windows/Mac

# =========================================================================
# 3. CORE PIPELINE & MQTT
# =========================================================================
def on_connect(client, userdata, flags, rc):
    client.subscribe(TOPIC_SUBSCRIBE_RAW)
    print(f"[MQTT] Connected. Listening on {TOPIC_SUBSCRIBE_RAW}...")

def on_message(client, userdata, msg):
    global buffer_x, current_round, dynamic_threshold, calibration_mse_list, is_calibrated
    
    try:
        payload = json.loads(msg.payload.decode())
        buffer_x.append(payload['x'])
        
        # Trigger when 1024 points are accumulated
        if len(buffer_x) >= 1024:
            input_data = process_signal(buffer_x)
            
            # 1. Edge AI Inference & Latency
            t0 = time.time()
            interpreter.set_tensor(input_details[0]['index'], input_data)
            interpreter.invoke()
            reconstructed = interpreter.get_tensor(output_details[0]['index'])
            latency_ms = (time.time() - t0) * 1000
            
            # 2. Mathematical Evaluation (MSE)
            mse = float(np.mean(np.square(input_data - reconstructed)))
            
            # 3. Physical Explainability (Peak Frequency)
            peak_freq_idx = int(np.argmax(input_data[0, :, 0]))
            peak_freq_hz = peak_freq_idx * (SAMPLING_RATE_HZ / 1024)
            
            machine_status = "INITIALIZING"
            
            # --- PHASE A: CALIBRATION ---
            if not is_calibrated:
                current_round += 1
                calibration_mse_list.append(mse)
                machine_status = f"CALIBRATING {current_round}/{CALIBRATION_ROUNDS}"
                print(f"[{machine_status}] MSE: {mse:.4f}")
                
                if current_round == CALIBRATION_ROUNDS:
                    dynamic_threshold = float(np.mean(calibration_mse_list)) + (3 * float(np.std(calibration_mse_list)))
                    is_calibrated = True
                    with open(MEMORY_FILE, 'w') as f:
                        json.dump({'threshold': dynamic_threshold}, f)
                    print(f"\n✅ [CALIBRATION COMPLETE] Threshold = {dynamic_threshold:.4f}\n")
                    
            # --- PHASE B: MONITORING ---
            else:
                machine_status = "ANOMALY" if mse > dynamic_threshold else "NORMAL"
                log_color = "🔴" if machine_status == "ANOMALY" else "🟢"
                print(f"{log_color} [{machine_status}] MSE: {mse:.4f} | Latency: {latency_ms:.1f}ms | Peak Freq: {peak_freq_hz:.1f}Hz")
                
            # --- PHASE C: COMPILE ULTIMATE PAYLOAD ---
            result_payload = {
                "status": machine_status,
                "ai_metrics": {
                    "mse": round(mse, 4),
                    "threshold": round(dynamic_threshold, 4),
                    "latency_ms": round(latency_ms, 2)
                },
                "physical_metrics": {
                    "peak_frequency_hz": round(peak_freq_hz, 2),
                    "gateway_uptime_sec": int(time.time() - SYSTEM_START_TIME)
                },
                "edge_health": {
                    "cpu_usage_percent": psutil.cpu_percent(),
                    "ram_usage_percent": psutil.virtual_memory().percent,
                    "pi_temperature_c": round(get_pi_temperature(), 1)
                },
                "raw_waveform": buffer_x
            }
            
            # Dispatch to PC
            client.publish(TOPIC_PUBLISH_RESULT, json.dumps(result_payload))
            buffer_x = [] # Reset buffer

    except Exception as e:
        print(f"[ERROR] Stream failed: {e}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("   LITE-HYBRID-AE EDGE GATEWAY (ULTIMATE EDITION)   ")
    print("="*60 + "\n")
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, 1883, 60)
    client.loop_forever()