#include <WiFi.h>
#include <HTTPClient.h>
#include "DHT.h"

// WiFi credentials
const char *ssid = "MAHAKAL";
const char *password = "sateri456";

// Server and user configuration
const char *serverUrl = "https://1be56469-efc1-4d75-8a1a-ad3133b3084a-00-2tx68ed5s69to.sisko.replit.dev/predict/";
// const char *nodeName = "mumbai";

// https://1be56469-efc1-4d75-8a1a-ad3133b3084a-00-2tx68ed5s69to.sisko.replit.dev/predict/?NodeName=mumbai&MonsoonIntensity=3&TopographyDrainage=5&RiverManagement=1&ClimateChange=6&Siltation=6&DrainageSystems=9&CoastalVulnerability=5&Watersheds=6&DeterioratingInfrastructure=9&WetlandLoss=2

// Sensor pins
#define DHTPIN 15        // DHT11 sensor connected to pin 15
#define DHTTYPE DHT11    // Define the sensor type
#define rainSensorPin 32 // Digital pin: HIGH means rain, LOW means no rain
#define floatSensorPin 23 // Digital pin: HIGH means water max, LOW means water low
#define ultrasonicTrigPin 5 // Ultrasonic sensor trig pin
#define ultrasonicEchoPin 18 // Ultrasonic sensor echo pin
#define locationPin 34       // Analog pin for location sensor
#define flowSensorPin 35     // Flow sensor connected to pin 35
const int ledPin = 2;  


// DHT sensor instance
DHT dht(DHTPIN, DHTTYPE);

// Flow sensor variables
float calibrationFactor = 4.5;
volatile byte pulseCount;
float flowRate;
unsigned int flowMilliLitres;
unsigned long totalMilliLitres;
long currentMillis = 0;
long previousMillis = 0;
int interval = 1000;

// Function prototypes
void IRAM_ATTR pulseCounter();
void calculateParameters();
void makeGetRequest();
float getDistance();
void calculateFlowRate();

// Global variables for parameters
int monsoonIntensity;
int topographyDrainage;
int riverManagement;
int climateChange;
int siltation;
int drainageSystems;
int coastalVulnerability;
int watersheds;
int deterioratingInfrastructure;
int wetlandLoss;

String nodename;
float latitude, longitude;

int locationValue = 0;


void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(ledPin, OUTPUT);

  digitalWrite(ledPin, HIGH);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  delay(1000);
  digitalWrite(ledPin, LOW);


  // Initialize pins
  pinMode(rainSensorPin, INPUT);
  pinMode(flowSensorPin, INPUT_PULLUP);
  pinMode(floatSensorPin, INPUT_PULLUP);
  pinMode(ultrasonicTrigPin, OUTPUT);
  pinMode(ultrasonicEchoPin, INPUT);

  // Initialize flow sensor
  pulseCount = 0;
  flowRate = 0.0;
  flowMilliLitres = 0;
  totalMilliLitres = 0;
  attachInterrupt(digitalPinToInterrupt(flowSensorPin), pulseCounter, FALLING);
}

// Interrupt service routine for flow sensor
void IRAM_ATTR pulseCounter() {
  pulseCount++;
}

// Function to calculate flow rate
void calculateFlowRate() {
  currentMillis = millis();
  if (currentMillis - previousMillis > interval) {
    byte pulse1Sec = pulseCount;
    pulseCount = 0;

    // Calculate flow rate and volume
    flowRate = ((1000.0 / (millis() - previousMillis)) * pulse1Sec) / calibrationFactor;
    flowMilliLitres = (flowRate / 60) * 1000;
    totalMilliLitres += flowMilliLitres;

    previousMillis = millis();

    // Print flow sensor data
    Serial.print("Flow rate: ");
    Serial.print(flowRate);
    Serial.print(" L/min\t");
    Serial.print("Total volume: ");
    Serial.print(totalMilliLitres);
    Serial.println(" mL");
  }
}

// Function to calculate distance using ultrasonic sensor
float getDistance() {
  digitalWrite(ultrasonicTrigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(ultrasonicTrigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(ultrasonicTrigPin, LOW);

  long duration = pulseIn(ultrasonicEchoPin, HIGH);
  float distance = (duration * 0.034) / 2; // Convert to cm
  return distance;
}

void calculateParameters() {
  // Read sensor values
  float temperature = dht.readTemperature();  // In Celsius
  // temperature = random(24, 35); // Generates a random number

  float humidity = dht.readHumidity();       // Read humidity percentage
  int rainStatus = digitalRead(rainSensorPin); // HIGH = rain, LOW = no rain
  rainStatus = !rainStatus;
  int floatStatus = digitalRead(floatSensorPin); // HIGH = max water, LOW = low water
  floatStatus = !floatStatus;
  float riverLevel = getDistance(); // River level in cm
  locationValue = analogRead(locationPin); // Location sensor value

  // Check the range of locationValue and assign nodename and coordinates
  if (locationValue >= 0 && locationValue <= 485) {
    nodename = "Colaba";
    latitude = 18.9067;
    longitude = 72.8147;
  } 
  else if (locationValue >= 486 && locationValue <= 970) {
    nodename = "Fort";
    latitude = 18.9345;
    longitude = 72.8371;
  } 
  else if (locationValue >= 971 && locationValue <= 1455) {
    nodename = "MarineDrive";
    latitude = 18.9444;
    longitude = 72.8233;
  }
  else if (locationValue >= 1456 && locationValue <= 2415) {
    nodename = "Andheri";
    latitude = 19.1136;
    longitude = 72.8697;
  }
  else if (locationValue >= 2416 && locationValue <= 3000) {
    nodename = "Bandra";
    latitude = 19.0596;
    longitude = 72.8295;
  }
  else if (locationValue >= 3001 && locationValue <= 4095) {
    nodename = "Santacruz";
    latitude = 19.0843;
    longitude = 72.8360;
  }
  else {
    nodename = "Virar";  // Handle values outside the defined ranges
    latitude = 19.4564;
    longitude = 72.7925;
  }

  // Ensure valid sensor readings
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Calculate parameters
  monsoonIntensity = (rainStatus == HIGH) ? map(humidity, 50, 100, 5, 10) : 3;
  topographyDrainage = map(riverLevel, 0, 300, 1, 10);
  riverManagement = map(flowRate, 0, 20, 1, 10);
  climateChange = map(temperature, 25, 40, 5, 10);
  siltation = map(riverLevel, 0, 189, 3, 9);
  drainageSystems = 10 - map(flowRate, 0, 20, 1, 8);
  coastalVulnerability = (rainStatus == HIGH) ? 8 : 5;
  watersheds = map(riverLevel, 0, 189, 3, 9);
  deterioratingInfrastructure = (floatStatus == HIGH) ? 9 : 4;
  wetlandLoss = rainStatus ? map(humidity, 50, 100, 5, 8) : 2;

  // Print parameters
  Serial.println("Calculated Parameters:");
  Serial.print("Monsoon Intensity: "); Serial.println(monsoonIntensity);
  Serial.print("Topography Drainage: "); Serial.println(topographyDrainage);
  Serial.print("River Management: "); Serial.println(riverManagement);
  Serial.print("Climate Change: "); Serial.println(climateChange);
  Serial.print("Siltation: "); Serial.println(siltation);
  Serial.print("Drainage Systems: "); Serial.println(drainageSystems);
  Serial.print("Coastal Vulnerability: "); Serial.println(coastalVulnerability);
  Serial.print("Watersheds: "); Serial.println(watersheds);
  Serial.print("Deteriorating Infrastructure: "); Serial.println(deterioratingInfrastructure);
  Serial.print("Wetland Loss: "); Serial.println(wetlandLoss);

  Serial.println("-----------------------");

  Serial.print("temperature: "); Serial.println(temperature);
  Serial.print("humidity: "); Serial.println(humidity);
  Serial.print("rainStatus: "); Serial.println(rainStatus);
  Serial.print("flowRate: "); Serial.println(flowRate);
  Serial.print("floatStatus: "); Serial.println(floatStatus);
  Serial.print("riverLevel: "); Serial.println(riverLevel);
  Serial.println("");
  Serial.print("location Value: "); Serial.println(locationValue);
  Serial.print("nodename: "); Serial.println(nodename);

  Serial.println("-----------------------");
}
// NodeName=mumbai&MonsoonIntensity=3&TopographyDrainage=5&RiverManagement=1&ClimateChange=6&Siltation=6&DrainageSystems=9&CoastalVulnerability=5&Watersheds=6&DeterioratingInfrastructure=9&WetlandLoss=2
void makeGetRequest() {
  HTTPClient http;
  String url = String(serverUrl) +
               "?NodeName=" + nodename +
               "&Latitude=" + latitude +
               "&Longitude=" + longitude +
               "&MonsoonIntensity=" + monsoonIntensity +
               "&TopographyDrainage=" + topographyDrainage +
               "&RiverManagement=" + riverManagement +
               "&ClimateChange=" + climateChange +
               "&Siltation=" + siltation +
               "&DrainageSystems=" + drainageSystems +
               "&CoastalVulnerability=" + coastalVulnerability +
               "&Watersheds=" + watersheds +
               "&DeterioratingInfrastructure=" + deterioratingInfrastructure +
               "&WetlandLoss=" + wetlandLoss;

  Serial.println("Sending GET request to: " + url);
  http.begin(url);

  digitalWrite(ledPin, HIGH);delay(1000);digitalWrite(ledPin, LOW);delay(1000);
  digitalWrite(ledPin, HIGH);delay(1000);digitalWrite(ledPin, LOW);delay(1000);
  digitalWrite(ledPin, HIGH);delay(1000);digitalWrite(ledPin, LOW);delay(1000);


  int httpCode = http.GET();
  if (httpCode > 0) {
    Serial.printf("HTTP response code: %d\n", httpCode);
    String payload = http.getString();
    Serial.println("Server response: " + payload);
  } else {
    Serial.printf("HTTP request failed, error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();
}

void loop() {
  delay(2000);

  calculateFlowRate();
  calculateParameters();

  // Make API call every 20 seconds
  static long lastCallTime = millis();
  if (millis() - lastCallTime >= 20000) {
    makeGetRequest();
    lastCallTime = millis();
  }

  delay(1000);
}
