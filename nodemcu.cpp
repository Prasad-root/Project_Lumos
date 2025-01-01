#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>

const char* ssid = "Nokia C1 Plus";
const char* password = "prasad2001";
const char* serverName = "http://<FLASK_SERVER_IP>:5000/api/get_state";

const String nodeID = "adminNode"; 

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);
  pinMode(D5, OUTPUT);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(serverName) + "?node_id=" + nodeID;
    http.begin(url);

    int httpResponseCode = http.GET();
    if (httpResponseCode > 0) {
      String payload = http.getString();
      Serial.println(payload);

      // Parse JSON response (example code, use ArduinoJson for advanced parsing)
      if (payload.indexOf("\"bulb1\":\"ON\"") > 0) digitalWrite(D1, HIGH); else digitalWrite(D1, LOW);
      if (payload.indexOf("\"bulb2\":\"ON\"") > 0) digitalWrite(D2, HIGH); else digitalWrite(D2, LOW);
      if (payload.indexOf("\"bulb3\":\"ON\"") > 0) digitalWrite(D3, HIGH); else digitalWrite(D3, LOW);
      if (payload.indexOf("\"bulb4\":\"ON\"") > 0) digitalWrite(D4, HIGH); else digitalWrite(D4, LOW);
      if (payload.indexOf("\"bulb5\":\"ON\"") > 0) digitalWrite(D5, HIGH); else digitalWrite(D5, LOW);
    }
    http.end();
  }

  delay(1000);  // Check every second
} 