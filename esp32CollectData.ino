// ESP32_Sender.ino
#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>

const char* ssid = "Vincent";
const char* password = "vincenttay";
const char* mqtt_server = "192.168.137.133"; 

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  Wire.begin(1, 2);
  Wire.setClock(100000);
  
  // 唤醒 MPU6050
  Wire.beginTransmission(0x68); Wire.write(0x6B); Wire.write(0); Wire.endTransmission();
  
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) { client.connect("ESP32_Fan"); }
  client.loop();

  Wire.beginTransmission(0x68); Wire.write(0x3B); Wire.endTransmission(false);
  Wire.requestFrom(0x68, 6, true);
  if (Wire.available() >= 6) {
    int16_t ax = Wire.read() << 8 | Wire.read();
    float x = ax / 16384.0; 
    
    String payload = "{\"x\":" + String(x, 3) + "}";
    client.publish("sensor/raw", payload.c_str());
  }
  delay(5);
}