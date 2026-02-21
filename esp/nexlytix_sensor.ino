#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <DHT.h>

// change these
#define SSID      "YOUR_WIFI"
#define PASS      "YOUR_PASS"
#define BROKER    "192.168.1.100"
#define DEVICE_ID "VemCore-01"

#define DHT_PIN   4
#define VIB_PIN   34     // analog vibration sensor
#define INTERVAL  5000

DHT dht(DHT_PIN, DHT22);
WiFiClient net;
PubSubClient mqtt(net);

uint32_t seq = 0;
uint32_t lastSend = 0;
char topic[96];


void setup() {
  Serial.begin(115200);
  dht.begin();

  WiFi.begin(SSID, PASS);
  Serial.print("wifi");
  while (WiFi.status() != WL_CONNECTED) { delay(400); Serial.print("."); }
  Serial.println(" ok");

  mqtt.setServer(BROKER, 1883);
  snprintf(topic, sizeof(topic), "nexlytix/nexlytix/%s/telemetry", DEVICE_ID);
}

void reconnect() {
  while (!mqtt.connected()) {
    Serial.print("mqtt...");
    if (mqtt.connect(DEVICE_ID)) { Serial.println("ok"); }
    else { Serial.printf("fail rc=%d\n", mqtt.state()); delay(3000); }
  }
}

const char* statusFor(float t, float h, float v) {
  if (t > 55 || h > 85 || v > 1.8) return "error";
  if (t > 45 || h > 75 || v > 1.2) return "warn";
  return "ok";
}

void loop() {
  if (!mqtt.connected()) reconnect();
  mqtt.loop();

  if (millis() - lastSend < INTERVAL) return;
  lastSend = millis();

  float t = dht.readTemperature();
  float h = dht.readHumidity();
  float v = analogRead(VIB_PIN) / 4095.0 * 2.0;

  if (isnan(t) || isnan(h)) { Serial.println("dht err"); return; }

  StaticJsonDocument<256> doc;
  doc["device_id"] = DEVICE_ID;
  doc["ts"]        = "";
  doc["seq"]       = ++seq;
  doc["status"]    = statusFor(t, h, v);
  doc["sig"]       = "";

  auto s              = doc.createNestedObject("sensors");
  s["temp_c"]         = round(t * 100) / 100.0;
  s["humidity_pct"]   = round(h * 100) / 100.0;
  s["vibration_rms"]  = round(v * 1000) / 1000.0;

  char buf[256];
  serializeJson(doc, buf);
  mqtt.publish(topic, buf);

  Serial.printf("[%lu] t=%.1fC h=%.0f%% v=%.3f %s\n", seq, t, h, v, statusFor(t,h,v));
}
