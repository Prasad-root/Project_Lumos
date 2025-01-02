#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClientSecure.h>
#include <ArduinoJson.h>

const char* ssid = "Nokia C1 Plus";
const char* password = "prasad2001";
const char* serverName = "https://lumos2025.eu.pythonanywhere.com/api/get_state";

const String nodeID = "adminNode";

String bulb1;
String bulb2;
String bulb3;
String bulb4;
String bulb5;

void setup() {
  Serial.begin(9600);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  // Pin Configuration
  pinMode(D0, OUTPUT);
  pinMode(D1, OUTPUT);
  pinMode(D2, OUTPUT);
  pinMode(D3, OUTPUT);
  pinMode(D4, OUTPUT);
}

void loop() {
  if (WiFi.status() == WL_CONNECTED) {
    WiFiClientSecure client;
    client.setInsecure();

    HTTPClient http;
    String url = String(serverName) + "?node_id=" + nodeID;

    //Serial.println("Requesting URL: " + url);
    http.begin(client, url);

    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String payload = http.getString();
      //Serial.println("Payload Received: " + payload);

      // Decode JSON response
      StaticJsonDocument<256> doc;
      DeserializationError error = deserializeJson(doc, payload);

      if (error) {
        Serial.print("JSON Parsing Error: ");
        Serial.println(error.c_str());
      } else {
        String bulb1 = doc["bulbs"]["bulb1"];
        String bulb2 = doc["bulbs"]["bulb2"];
        String bulb3 = doc["bulbs"]["bulb3"];
        String bulb4 = doc["bulbs"]["bulb4"];
        String bulb5 = doc["bulbs"]["bulb5"];

        digitalWrite(D0, bulb1 == "ON" ? HIGH : LOW);
        digitalWrite(D1, bulb2 == "ON" ? HIGH : LOW);
        digitalWrite(D2, bulb3 == "ON" ? HIGH : LOW);
        digitalWrite(D3, bulb4 == "ON" ? HIGH : LOW);
        digitalWrite(D4, bulb5 == "ON" ? HIGH : LOW);  
      }
    } else {
      Serial.print("Error in HTTP request: ");
      Serial.println(httpResponseCode);
    }

    http.end();
  } else {
    Serial.println("WiFi disconnected");
  }
  delay(1000);
}
