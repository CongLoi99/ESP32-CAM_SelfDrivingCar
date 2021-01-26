
#include <WiFi.h>
#include <PubSubClient.h>

#define MQTT_SERVER "Broker host"
#define MQTT_USERNAME "username"
#define MQTT_PASSWORD "password"

#define MQTT_topic_pub "topic public"
#define MQTT_topic_sub "topic subscribe"

const char ssid[] = "Wifi ID";
const char password[] = "Wifi password";

WiFiClient net;
PubSubClient client(net);

// Motor A
int motor1Pin1 = 27; 
int motor1Pin2 = 26; 
int enable1PinA = 14; 

// Motor B
int motor1Pin3 = 25; 
int motor1Pin4 = 33; 
int enable1PinB = 32; 

// Setting PWM properties
const int freq = 30000;
const int pwmChannelA = 0;
const int pwmChannelB = 0;
const int resolution = 8;
int dutyCycle = 155;

void setup_wifi() {
    delay(10);
    //kết nối wifi network
    Serial.println();
    Serial.print("Connecting to ");
    Serial.println(ssid);
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    randomSeed(micros());
    Serial.println("");
    Serial.println("WiFi connected");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
}

//thực hiện kết nối lại
void reconnect() {
  // chờ tói khi kết nối
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("Client",MQTT_USERNAME,MQTT_PASSWORD)) {
      Serial.println("connected");
      //khí kết nối gửi thông báo
      client.publish(MQTT_topic_pub,"hello world");
      // nhận lại thông tin
      client.subscribe(MQTT_topic_sub);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void callback(char* topic, byte *payload, unsigned int length) {
    Serial.println("-------new message from broker-----");
    Serial.print("channel:");
    Serial.println(topic);
    Serial.print("data:");  
    String reseivedStr = "";
    for (int i = 0; i < length; i++) {
    reseivedStr = (char)payload[i];
  }
    Serial.print(reseivedStr);
    if (reseivedStr.equals("F"))  Forward();
    if (reseivedStr.equals("R"))   right();
    if (reseivedStr.equals("L"))   left();
    if (reseivedStr.equals("S"))   Stop();
    Serial.println();
}

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(MQTT_SERVER, 1883);
  client.setCallback(callback);

  // sets the pins as outputs:
  pinMode(motor1Pin1, OUTPUT);
  pinMode(motor1Pin2, OUTPUT);
  pinMode(enable1PinA, OUTPUT);

  pinMode(motor1Pin3, OUTPUT);
  pinMode(motor1Pin4, OUTPUT);
  pinMode(enable1PinB, OUTPUT);
  
  // configure LED PWM functionalitites
  ledcSetup(pwmChannelA, freq, resolution);
  ledcSetup(pwmChannelB, freq, resolution);
  
  // attach the channel to the GPIO to be controlled
  ledcAttachPin(enable1PinA, pwmChannelA);
  ledcAttachPin(enable1PinB, pwmChannelB);
}

void loop() {
  //kiểm tra kết nối
  if(!client.connected()){
    reconnect();
  }
  client.loop();
 }

void Stop(){
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor1Pin3, LOW);
  digitalWrite(motor1Pin4, LOW);
}

void Forward(){
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor1Pin3, HIGH);
  digitalWrite(motor1Pin4, LOW);
  ledcWrite(pwmChannelA, dutyCycle);
  ledcWrite(pwmChannelB, dutyCycle);    
}

void left(){
  digitalWrite(motor1Pin1, HIGH);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor1Pin3, LOW);
  digitalWrite(motor1Pin4, LOW);
  ledcWrite(pwmChannelA, dutyCycle);
  ledcWrite(pwmChannelB, dutyCycle);   
}

void right(){
  digitalWrite(motor1Pin1, LOW);
  digitalWrite(motor1Pin2, LOW);
  digitalWrite(motor1Pin3, HIGH);
  digitalWrite(motor1Pin4, LOW);
  ledcWrite(pwmChannelA, dutyCycle);
  ledcWrite(pwmChannelB, dutyCycle);    
}
