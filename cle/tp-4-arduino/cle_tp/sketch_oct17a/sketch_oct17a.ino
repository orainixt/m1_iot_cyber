#include "rgb_lcd.h"
#include <Wire.h>

enum State {
  TIME,
  TEMP,
  CHRISTMAS,
  LIGHT
};

enum Event {
  EVENT_NONE,
  button,
  tick_up,
  tick_dw,
  light_off,
  light_on
};

rgb_lcd lcd;

int buttonPin = 4; 
int buzzerPin = 3; 
int potPin = A3; 
int tempPin = A1;
int relayPin =  6;
int pinLight = A0; 
int pinLed = 7; 


State currentState = LIGHT;
unsigned long startTime;
int potValue = 0;
int prevPotValue = 0;
bool isLightOn = true;
bool isPlaying = false; 
float resistance;
float temperature;
float lastTemperature; 
unsigned long seconds;
int B = 3975;
unsigned long temps;
int noteIndex=0;
unsigned long lastNoteTime = 0;
int lastPotValue; 
int lastRoundedPotValue; 
char notes[] = "ccggaagffeeddc ";
int beats[] = {1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 4};
int tempo = 300;
int threshold = 60;


void setup() {
  temps = millis();
  lcd.begin(16, 2);
  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(tempPin, INPUT);
  pinMode(buzzerPin, OUTPUT);
  pinMode(relayPin, OUTPUT);

  lastPotValue = analogRead(potPin); 
  lastRoundedPotValue =map(lastPotValue, 0, 1023, 0, 9);
 }

void playTone(int tone, int duration) {
  for (long i = 0; i < duration * 1000L; i += tone * 2) {
    digitalWrite(buzzerPin, HIGH);
    delayMicroseconds(tone);
    digitalWrite(buzzerPin, LOW);
    delayMicroseconds(tone);
  }
}

void playNote(char note, int duration) {
  char names[] = {'c', 'd', 'e', 'f', 'g', 'a', 'b', 'C'};
  int tones[] = {1915, 1700, 1519, 1432, 1275, 1136, 1014, 956};
  for (int i = 0; i < 8; i++) {
    if (names[i] == note) {
      playTone(tones[i], duration);
    }
  }
}

// affiche Merry christmas avec un ecran allume light mode
void affichageMerry() {
    lcd.clear();
    lcd.print("Merry Christmas!");

    int colors[][3] = {
        {255, 0, 0},    // rouge
        {0, 255, 0},    // vert
        {0, 0, 255},    // bleu
        {255, 255, 0},  // jaune
        {0, 255, 255},  // cyan
        {255, 0, 255},  // magenta
        {255, 255, 255} // blanc
    };

    int numColors = sizeof(colors) / sizeof(colors[0]);

    for (int i = 0; i < numColors; i++) {
        lcd.setRGB(colors[i][0], colors[i][1], colors[i][2]);
        delay(300);
    }
}

// afficheHappy new year avec un ecran eteint dark mode
void affichageHappy(){
    lcd.clear();
    lcd.setRGB(0, 0, 0);
    lcd.print("Happy New Year");
}




void executeChristmas() {

  int length = 15;
  lcd.clear();
  lcd.print("25:12");
  unsigned long currentTime = millis();
  if (currentTime - lastNoteTime >= (unsigned long)(beats[noteIndex] * tempo)) {
    if (notes[noteIndex] != ' ') {
      playNote(notes[noteIndex], beats[noteIndex] * tempo);
    }
    noteIndex++;
    if (noteIndex >= length) noteIndex = 0;

    lastNoteTime = currentTime;
  }
}

void afficherLight() {
  lcd.clear();
  lcd.print("Light is ");
  lcd.print(isLightOn ? "ON" : "OFF");
}

void afficherTemperature() {
  int val = analogRead(tempPin);
  resistance = (float)(1023 - val) * 10000 / val;
  temperature = 1 / (log(resistance / 10000) / B + 1 / 298.15) - 273.15;  
  lcd.clear();
  lcd.print("Temp: ");
  lcd.print(temperature);
  lcd.print("C");
  }

void afficherTemps() {
  seconds = (millis()-temps)/1000;
  lcd.clear();
  lcd.print("Time: ");
  lcd.print(seconds);
  lcd.print(" s");
}

Event readEvent() {
  
  static bool lastButtonState = HIGH; // bouton relâché au départ
  
  bool buttonState = digitalRead(buttonPin);
  int potValue = analogRead(potPin); 
  int roundedPotValue = map(potValue, 0, 1023, 0, 9);
  
  Event e = EVENT_NONE;
  
  if (buttonState == LOW && lastButtonState == HIGH) {
    e = button;
  }

  if (roundedPotValue > lastRoundedPotValue){
    e = tick_up;
  } 
  if (roundedPotValue < lastRoundedPotValue){
    e = tick_dw;
  } 

  lastRoundedPotValue = roundedPotValue; 
  lastButtonState = buttonState; 

  return e; 
} 


void handleState(Event event){

  if (event == tick_up){
    lcd.setCursor(0,1);
    lcd.print("event : tick_up");
    digitalWrite(relayPin, HIGH);
    delay(100) ;
    digitalWrite(relayPin, LOW);
    delay(1000);
  }
  if (event == tick_dw) {
    lcd.setCursor(0,1);
    lcd.print("event : tick_dw");
    digitalWrite(relayPin, HIGH);
    delay(100) ;
    digitalWrite(relayPin, LOW);
    delay(1000);
  }

  
  switch (currentState) {
    case (TIME):
      if (event == button) {
        currentState = TEMP;
      } 
      lcd.setRGB(255,255,255);
      afficherTemps();
      break; 
    
    case (TEMP) :
      if (event == button) {
        currentState = CHRISTMAS;
      }
      afficherTemperature();
      break;
    
    case (CHRISTMAS) :
      if (event == button) {
        currentState = LIGHT;
      }
      executeChristmas();
      break;
    case (LIGHT): {
      if (event == button) {
        lcd.setRGB(255,255,255);
        currentState=TIME;
        temps = millis();
      }
      int sensorVal = analogRead(pinLight);
      if (sensorVal > threshold) {
        lcd.setRGB(255,255,255);
        affichageMerry(); 
      } else {
        affichageHappy();
      }
    }
    
  }
}

void loop(){
  Event event = readEvent(); 
  handleState(event); 
  delay(100);
}

// ESSAIS 


// #include <Wire.h>
// #include "rgb_lcd.h"

// rgb_lcd lcd;

// int temppin = A0;
// int buttonPin = 2;      // Broche du bouton
// int state = 0;          // 0 = Time, 1 = Temp
// bool lastButtonState = HIGH;

// void setup() {
//   lcd.begin(16, 2);
//   pinMode(buttonPin, INPUT_PULLUP);  // Active résistance interne
// }

// void loop() {
//   bool buttonState = digitalRead(buttonPin);

//   // Détection d’un appui (changement d’état)
//   if (buttonState == LOW && lastButtonState == HIGH) {
//     state = (state + 1) % 2;  // alterne entre 0 et 1
//     delay(200);               // anti-rebond
//   }
//   lastButtonState = buttonState;

//   lcd.clear();
//   if (state == 0) {
//     unsigned long seconds = millis() / 1000;
//     lcd.print("Time: ");
//     lcd.print(seconds);
//   } else if (state == 1) {
//     int sensorvalue = analogRead(temppin);
//     float resistance = (float)(1023 - sensorvalue) * 10000 / sensorvalue;
//     float temp = 1 / (log(resistance / 10000.0) / 3975.0 + 1 / 298.15) - 273.15;
//     lcd.print("Temp mode");
//     lcd.print(temp);

    
//   }

//   delay(500);
// }

// #include <Wire.h>
// #include "rgb_lcd.h"

// rgb_lcd lcd;
// int rotaryPin = A1;
// int lightPin = A2;

// void setup() {
//   lcd.begin(16, 2);
//   Serial.begin(9600);
// }

// void loop() {
//   int value = analogRead(rotaryPin);
//   int level = map(value, 0, 1023, 0, 9);
//   int lightval = analogRead(lightPin);
//   lcd.clear();
//   lcd.print("Level: ");
//   lcd.print(level);
//   lcd.print("Light: ");
//   lcd.print(lightval);


//   delay(300);
// }
// const int pinLight = A2;
// const int pinLed   = 7;

// int thresholdvalue=400;                 //the threshold to turn on or off the LED

// void setup()
// {
//     pinMode(pinLed, OUTPUT);             //set the LED on Digital 12 as an OUTPUT
// }

// void loop()
// {
//     int sensorValue = analogRead(pinLight);    //the light sensor is attached to analog 0
//     if(sensorValue<thresholdvalue)
//     {
//         digitalWrite(pinLed, HIGH);
//     }
//     else
//     {
//         digitalWrite(pinLed, LOW);
//     }
// }

/*
const int pinSound = A3;               // pin of Sound Sensor
const int pinLed   = 7;                // pin of LED

int thresholdValue = 500;                 // the threshold to turn on or off the LED

void setup()
{
    pinMode(pinLed, OUTPUT);            //set the LED on Digital 12 as an OUTPUT
}

void loop()
{
    int sensorValue = analogRead(pinSound);   //read the sensorValue on Analog 0
    if(sensorValue>thresholdValue)
    digitalWrite(pinLed,HIGH);
    delay(200);
    digitalWrite(pinLed,LOW);
}
*/
// const int buttonPin = 2;     // the button is attached to digital pin 3
// const int relayPin =  4;     // the relay is attached to digital pin 7
// int buttonState = 0;

// void setup()
// {
//     pinMode(relayPin, OUTPUT);
//     pinMode(buttonPin, INPUT);
// }

// void loop()
// {
//     // read the state of the button:
//     buttonState = digitalRead(buttonPin);
    
//     if (buttonState == 1)   
//     {
    
//         digitalWrite(relayPin, HIGH);
//     }
//     else   
//     {
          
//         digitalWrite(relayPin, LOW);
//     }
//     delay(10);
// }

// Changer la couleur de l'ecran

// #include <Wire.h>
// #include "rgb_lcd.h"

// rgb_lcd lcd;

// char dtaUart[15];
// char dtaLen = 0;

// void setup() 
// {
//     Serial.begin(115200);
//     // set up the LCD's number of columns and rows:
//     lcd.begin(16, 2);
//     // Print a message to the LCD.
//     lcd.print("set cllor");
// }

// void loop() 
// {

//     if(dtaLen == 11)
//     {
//         int r = (dtaUart[0]-'0')*100 + (dtaUart[1]-'0')*10 + (dtaUart[2]-'0');
//         int g = (dtaUart[4]-'0')*100 + (dtaUart[5]-'0')*10 + (dtaUart[6]-'0');
//         int b = (dtaUart[8]-'0')*100 + (dtaUart[9]-'0')*10 + (dtaUart[10]-'0');

        
//         dtaLen = 0;
        
//         lcd.setRGB(r, g, b);

//         Serial.println("get data");
        
//         Serial.println(r);
//         Serial.println(g);
//         Serial.println(b);
//         Serial.println();

//     }
// }

// void serialEvent()
// {
//     while(Serial.available())
//     {
//         dtaUart[dtaLen++] = Serial.read();
//     }
// }

// capteur de mouv genre si on touche le capteur la led s'allume 
// const int touchPin = 5;   // broche digitale
// const int ledPin = 7;     // LED pour visualiser

// void setup() {
//   pinMode(touchPin, INPUT);
//   pinMode(ledPin, OUTPUT);
//   Serial.begin(9600);
// }
 
// void loop() {
//   int state = digitalRead(touchPin);

//   if (state == HIGH) {  // doigt détecté
//     digitalWrite(ledPin, HIGH);
//     Serial.println("Touched!");
//   } else {
//     digitalWrite(ledPin, LOW);
//   }

//   delay(50);
// }
/*
rgb_lcd lcd;

void setup(){
  
  lcd.begin(16,2);

}

void loop() {

  int time = minus 
}
 */
// mode fade
// #include <Wire.h>
// #include "rgb_lcd.h"

// rgb_lcd lcd;

// void setup() 
// {
//     // set up the LCD's number of columns and rows:
//     lcd.begin(16, 2);
//     // Print a message to the LCD.
//     lcd.print("fade demo");

// }

// void breath(unsigned char color)
// {

//     for(int i=0; i<255; i++)
//     {
//         lcd.setPWM(color, i);
//         delay(5);
//     }

//     delay(500);
//     for(int i=254; i>=0; i--)
//     {
//         lcd.setPWM(color, i);
//         delay(5);
//     }

//     delay(500);
// }

// void loop() 
// {
//     breath(REG_RED);
//     breath(REG_GREEN);
//     breath(REG_BLUE);
// }

///////////////////////////
//------ affcihe soit le temps soit la temperature en fonction du boutton (changement de mode)
//////////////////////////
// #include <Wire.h>
// #include "rgb_lcd.h"

// rgb_lcd lcd;
// int tempPin = A1;
// int buttonPin = 2;

// float temperature;
// int B = 3975;
// float resistance;

// bool lastButt = HIGH;
// int state = 0;
// void setup() {
//   pinMode(buttonPin,INPUT);
//   Serial.begin(9600);
//   pinMode(tempPin,INPUT);
//   lcd.begin(16,2);
// }

// void affichage(){
  
//   int val = analogRead(tempPin);                               // get analog value
//   resistance=(float)(1023-val)*10000/val;                      // get resistance
//   temperature=1/(log(resistance/10000)/B+1/298.15)-273.15;

//   unsigned long seconds = millis() / 1000;
//   if (state == 0){
//     lcd.clear();
//     lcd.print("time: ");
//     lcd.print(seconds);
//   }
//   else {
//     lcd.clear();
//     lcd.print("Temp: ");
//     lcd.print(temperature);
//   }
// }

// void loop() {
//   bool buttsta = digitalRead(buttonPin);
//   if (buttsta == LOW && lastButt == HIGH) {
//     state = !state;   
//     delay(200);       
//   }
//   lastButt = buttsta; 
//   affichage();

//   delay(300);

// }


/* Melody
 * (cleft) 2005 D. Cuartielles for K3
 *
 * This example uses a piezo speaker to play melodies.  It sends
 * a square wave of the appropriate frequency to the piezo, generating
 * the corresponding tone.
 *
 * The calculation of the tones is made following the mathematical
 * operation:
 *
 *       timeHigh = period / 2 = 1 / (2 * toneFrequency)
 *
 * where the different tones are described as in the table:
 *
 * note  frequency  period  timeHigh
 * c          261 Hz          3830  1915
 * d          294 Hz          3400  1700
 * e          329 Hz          3038  1519
 * f          349 Hz          2864  1432
 * g          392 Hz          2550  1275
 * a          440 Hz          2272  1136
 * b          493 Hz          2028 1014
 * C         523 Hz         1912  956
 *
 * http://www.arduino.cc/en/Tutorial/Melody
 */


///////////////////
// ------- tourner le moteur ---------
///////////////////
// int rotaryAnalog = A1;
// int moteurPin = 4;

// int lastValue = 0;  // valeur précédente

// void setup(){
//   pinMode(rotaryAnalog, INPUT);
//   pinMode(moteurPin, OUTPUT);
//   Serial.begin(9600);
// }

// void loop() {
//   int value = analogRead(rotaryAnalog);
  
//   if(value > lastValue + 5){   // on met une petite tolérance pour éviter les petits sauts
//     // tourne moteur dans un sens
//     digitalWrite(moteurPin, HIGH);  
//     Serial.println("Tick Up -> moteur tourne dans un sens");
//   }
//   else if(value < lastValue - 5){
//     // tourne moteur dans l'autre sens
//     digitalWrite(moteurPin, LOW);   
//     Serial.println("Tick Down -> moteur tourne dans l'autre sens");
//   }
  
//   lastValue = value;
//   delay(50);  // petit délai pour stabiliser la lecture
// }


// #include <Wire.h>
// #include "rgb_lcd.h"

// rgb_lcd lcd;

// int speakerPin = 3;
// int lightPin = A0;
// int seuil = 100;
// int pinButton = 4;
// int tempPin = A1;

// float temperature;
// int B = 3975;
// float resistance;

// bool lastButtonState = HIGH;
// int mode = 0;
// int state = 0;

// int length = 15;
// char notes[] = "ccggaagffeeddc ";
// int beats[] = {1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 4};
// int tempo = 300;

// void playTone(int tone, int duration) {
//   for (long i = 0; i < duration * 1000L; i += tone * 2) {
//     digitalWrite(speakerPin, HIGH);
//     delayMicroseconds(tone);
//     digitalWrite(speakerPin, LOW);
//     delayMicroseconds(tone);
//   }
// }

// void playNote(char note, int duration) {
//   char names[] = {'c', 'd', 'e', 'f', 'g', 'a', 'b', 'C'};
//   int tones[] = {1915, 1700, 1519, 1432, 1275, 1136, 1014, 956};
//   for (int i = 0; i < 8; i++) {
//     if (names[i] == note) {
//       playTone(tones[i], duration);
//     }
//   }
// }

// void setup() {
//   lcd.begin(16, 2);
//   pinMode(speakerPin, OUTPUT);
//   pinMode(lightPin, OUTPUT);
//   pinMode(pinButton, INPUT);
//   pinMode(tempPin, INPUT);
//   Serial.begin(9600);
// }

// void affichage() {
//   int val = analogRead(tempPin);
//   resistance = (float)(1023 - val) * 10000 / val;
//   temperature = 1 / (log(resistance / 10000) / B + 1 / 298.15) - 273.15;

//   unsigned long seconds = millis() / 1000;
//   if (state == 0) {
//     lcd.clear();
//     lcd.print("time: ");
//     lcd.print(seconds);
//   } else {
//     lcd.clear();
//     lcd.print("Temp: ");
//     lcd.print(temperature);
//   }
// }

// bool compareLightMode() {
//   int sensorValue = analogRead(lightPin);
//   Serial.println(sensorValue);
//   if (sensorValue > seuil) {
//     return false;
//   } else {
//     return true;
//   }
// }

// void loop() {
//   bool buttonState = digitalRead(pinButton);
//   if (buttonState == LOW && lastButtonState == HIGH) {
//     mode = !mode;
//     delay(300);
//   }
//   lastButtonState = buttonState;

//   lcd.clear();

//   if (mode == 0) {
//     lcd.setRGB(0, 0, 255);
//     affichage();
//   } else {
//     lcd.setRGB(255, 0, 0);
//     lcd.setCursor(0, 0);
//     lcd.print("Happy New Year");
//   }

//   delay(500);
// }
/*
int potPin = A2;
int ledPin = 2;

void setup() {
  pinMode(ledPin, OUTPUT);
  Serial.begin(9600);
}

void loop() {
  int potValue = analogRead(potPin); 
  int level = map(potValue, 0, 1023, 0, 9);

  Serial.println(level);

  if (level > 4) { 
    digitalWrite(ledPin, HIGH);
  } else {
    digitalWrite(ledPin, LOW);
  }

  delay(200);
}

*/





// #include <Wire.h>
// #include "rgb_lcd.h"

// rgb_lcd lcd;
// int speakerPin = 3;
// int tempPin = A1;
// int buttonPin = 4;
// float temperature;
// int length = 15;
// int B = 3975;
// float resistance;
// unsigned long seconds;
// unsigned long temps;
// bool lastButtonState = HIGH;
// char notes[] = "ccggaagffeeddc ";
// int beats[] = {1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 4};
// int tempo = 300;
// int mode = 0;
// int noteIndex=0;
// unsigned long lastNoteTime = 0;  // pour savoir quand jouer la prochaine note
// bool notePlaying = false;

// void setup() {
//   temps = millis();
//   lcd.begin(16, 2);
//   pinMode(buttonPin, INPUT);
//   pinMode(tempPin, INPUT);
//   pinMode(speakerPin, OUTPUT);
//   Serial.begin(9600);

// }


// void playTone(int tone, int duration) {
//   for (long i = 0; i < duration * 1000L; i += tone * 2) {
//     digitalWrite(speakerPin, HIGH);
//     delayMicroseconds(tone);
//     digitalWrite(speakerPin, LOW);
//     delayMicroseconds(tone);
//   }
// }

// void playNote(char note, int duration) {
//   char names[] = {'c', 'd', 'e', 'f', 'g', 'a', 'b', 'C'};
//   int tones[] = {1915, 1700, 1519, 1432, 1275, 1136, 1014, 956};
//   for (int i = 0; i < 8; i++) {
//     if (names[i] == note) {
//       playTone(tones[i], duration);
//     }
//   }
// }
// void afficherTemperature() {
//   int val = analogRead(tempPin);
//   resistance = (float)(1023 - val) * 10000 / val;  
//   temperature = 1 / (log(resistance / 10000) / B + 1 / 298.15) - 273.15;

//   lcd.clear();
//   lcd.print("Temp: ");
//   lcd.print(temperature, 1);
//   lcd.print(" C");
// }

// void afficherTemps() {
//   seconds = (millis()-temps)/1000;
//   lcd.clear();
//   lcd.print("Time: ");
//   lcd.print(seconds);
//   lcd.print(" s");
// }

// void loop() {
//   bool buttonState = digitalRead(buttonPin);

//   if (buttonState == LOW && lastButtonState == HIGH) {
//     mode = (mode+1) % 3;
//     if (mode ==1){
//       temps= millis();
//     }
//     delay(300);
    
//   }
//   lastButtonState = buttonState;

//   if (mode == 0) {
//     afficherTemperature();
//   } 
//   else if (mode ==1){
//     afficherTemps();
//   }
//   else if (mode == 2) {
//     unsigned long currentTime = millis();

//     if (currentTime - lastNoteTime >= (unsigned long)(beats[noteIndex] * tempo)) {
//       lcd.clear();
//       lcd.print("25:12");


//       if (notes[noteIndex] != ' ') {
//         playNote(notes[noteIndex], beats[noteIndex] * tempo);
//       }

//       noteIndex++;
//       if (noteIndex >= length) noteIndex = 0;

//       lastNoteTime = currentTime;
//     }
//   }
//   else if (mode == 3){
//     //     lcd.setRGB(255, 0, 0);
// //     lcd.setCursor(0, 0);
// //     lcd.print("Happy New Year");
//   }
//   delay(50);
// }



/*
#include <Wire.h>
#include "rgb_lcd.h"

rgb_lcd lcd;
int rotaryPin = A3;
int relayPin =  6;
pinMode(relayPin, OUTPUT);
void setup() {
  lcd.begin(16, 2);
  pinMode(relayPin, OUTPUT);
}

void clickPotentiometer()
  int value = analogRead(rotaryPin);
  int level = map(value, 0, 1023, 0, 9);
  
  if (level>4){
    digitalWrite(relayPin, HIGH);
  }
  else {
    digitalWrite(relayPin, LOW);

  }
  lcd.clear();
  lcd.print("Level: ");
  lcd.print(level);
  delay(300);
}
*/
