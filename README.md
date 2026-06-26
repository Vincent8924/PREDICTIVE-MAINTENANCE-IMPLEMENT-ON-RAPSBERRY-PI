# IoT-Based Predictive Maintenance of Machines Powered with AI and ML Algorithms

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware: Raspberry Pi 5](https://img.shields.io/badge/Hardware-Raspberry%20Pi%205-C51A4A?logo=Raspberry-Pi)](https://www.raspberrypi.com/products/raspberry-pi-5/)
[![Hardware: ESP32](https://img.shields.io/badge/Hardware-ESP32-E7352C?logo=espressif)](https://www.espressif.com/en/products/socs/esp32)

**Author:** Vincent Tay Yong Jun  
**Institution:** Multimedia University (Faculty of Information Science & Technology)  

## 📖 Overview
This repository contains the deployment codebase for a decentralized 5C Edge-IIoT predictive maintenance framework. The system is engineered to monitor rotary machinery in real-time, leveraging an unsupervised deep learning architecture to detect mechanical anomalies without relying on costly cloud-computing infrastructure or scarce labeled fault data. 

The core of this system utilizes a **Lite-Hybrid-AE (1D-CNN + LSTM Autoencoder)** optimized via INT8 post-training quantization. It is deployed on a resource-constrained Raspberry Pi 5 edge gateway, ensuring sub-millisecond inference latency (0.88ms average) and minimal CPU load (0.44% average).

## ✨ Key Features
* **Unsupervised Anomaly Detection:** Utilizes a Lite-Hybrid-AE model trained exclusively on nominal, healthy mechanical baseline data to map spatial-temporal degradation patterns. 
* **Aggressive Dimensionality Reduction:** The ESP32 sensor node captures univariate (X-axis) mechanical vibration data strictly through an MPU6050 sensor. The system is designed to acquire vibration data only, intentionally excluding temperature tracking to minimize transmission payload and preserve local wireless bandwidth.
* **Dynamic Calibration Engine:** Implements a software-defined Three-Sigma (3σ) algorithm that autonomously calibrates the anomaly threshold during the first 50 epochs of operation, dynamically adapting to non-stationary environmental noise. 
* **Edge Data Persistence & Visualization:** Features a zero-configuration SQLite database paired with a localized Streamlit dashboard for real-time visualization of machine health, peak frequencies (via FFT), and edge-hardware telemetry. 
* **Resilient State Auto-Recovery:** Employs a state persistence protocol (JSON memory recovery) to lock in dynamic thresholds, ensuring immediate accuracy recovery following unexpected power cycles. 

## 🏗️ System Architecture (5C Framework)
1.  **Connection Layer:** An ESP32 microcontroller paired with an MPU6050 IMU operating at a deterministic 200Hz sampling rate. 
2.  **Conversion Layer:** MQTT message broker facilitating lightweight, asynchronous data propagation. 
3.  **Cyber Layer:** Dual-track diagnostics on the Raspberry Pi 5 running the TensorFlow Lite model and parallel Fast Fourier Transform (FFT) extraction. 
4.  **Cognition Layer:** Local SQLite persistent logging and a color-coded Streamlit Human-Computer Interaction (HCI) dashboard. 
5.  **Configuration Layer:** Autonomous feedback loops powered by the Dynamic Calibration Engine. 

## 🛠️ Hardware Requirements
* **Edge Gateway:** Raspberry Pi 5 Model B
* **Sensor Node:** ESP32 Microcontroller
* **Sensor:** MPU6050 Inertial Measurement Unit (IMU)

*Note: The MPU6050 interfaces with the ESP32 via the I2C serial communication protocol (SDA to GPIO 1, SCL to GPIO 2)*.

## 💻 Tech Stack
* **Machine Learning/AI:** TensorFlow Lite, Keras, Numpy
* **Embedded Development:** C++, Arduino IDE (ESP32 Firmware)
* **Backend & Processing:** Python, Paho-MQTT, SciPy (FFT)
* **Database & UI:** SQLite, Streamlit, Pandas

## 🚀 Setup & Installation 

### 1. Edge Gateway (Raspberry Pi 5)
1. Clone the repository to your Raspberry Pi.
2. Install the required Python dependencies:
   ```bash
   pip install tflite-runtime paho-mqtt streamlit pandas numpy psutil
   ```

### 2. Initialize the MQTT broker and start the AI gateway:
    python pi_gateway_ai.py

### 3. Start the data logger to populate the SQLite database on PC:
    python data_logger.py

### 4. Sensor Node (ESP32)
1. Open ESP32_Sender.ino in the Arduino IDE.
2. Update the ssid, password, and mqtt_server variables with your local network credentials.
3. Flash the firmware to the ESP32 board.

### 5. Streamlit Dashboard
1. Launch the interactive Human-Computer Interaction (HCI) UI:
    ```bash 
    streamlit run app.py
    ```
2. The dashboard will track live vibrations, MSE vs. threshold limits, and hardware thermals locally.

## 🎥 Demonstration
    A short demonstration of the system operating on a physical air conditioning compressor can be viewed here: https://youtu.be/lzvHtOjECMs.