- [Introduction](#org58eb4e3)
  - [Hardware/Software platform](#orgc0f0f80)
  - [Seeed studio tutorials](#org3e63a1a)
- [Project](#orgb1f4936)
  - [List of sensors and actuators used in the project](#orgced489e)
  - [Description](#org532ce74)
  - [Development](#org6b32659)



<a id="org58eb4e3"></a>

# Introduction


<a id="orgc0f0f80"></a>

## Hardware/Software platform

The following exercises will be done on a Arduino Uno platform. To program the platform, you need to use one of the two IDEs :

-   The Arduino IDE (which is already available on the machines in A11)

-   [Platform IO](https://docs.platformio.org/en/latest//what-is-platformio.html), which is available as a plugin of VSCode. Please follow the instruction on the web site to install it on the machines of A11.


<a id="org3e63a1a"></a>

## Seeed studio tutorials

The sensors and actuators that we will use are part of the Seeed Studio [Grove Arduino Starter Kit](https://www.seeedstudio.com/Grove-Starter-Kit-for-Arduino-p-1855.html).

You can find some video lectures on how to use the Seeed Studio Shield and the kit :

-   <https://www.youtube.com/watch?v=GfgSyCZMb_g&ab_channel=CreateLabzStore>

Here are the Starter Kit examples that you can download and try on the board.

-   <https://github.com/Seeed-Studio/Sketchbook_Starter_Kit_for_Arduino>


<a id="orgb1f4936"></a>

# Project


<a id="orgced489e"></a>

## List of sensors and actuators used in the project

-   The button;
-   the buzzer;
-   the display;
-   the light sensor;
-   the step motor;
-   the temperature sensor;
-   the potentiometer.


<a id="org532ce74"></a>

## Description

The objective of this student project is to develop a prototype of a small gadget for Christmas with an Arduino board.

The application changes from one mode to the other depending on the status of the button and of other sensors, according to the following state machine:

![img](application-sm.png)

The events are the following:

-   The `button` event corresponds to a button press;
-   The `tick_up` event corresponds to turning the potentiometer to the right for one tick;
-   The `tick_dw` event corresponds to turning the potentiometer to the left for one tick.
-   The `light_off` event corresponds to the light sensor not detecting enough light (you will need to set a threshold for the detected light).
-   The `light_on` is when the light is sensor detects enough light.

The states are the following:

1.  In state `Time` the display shows the number of seconds since the device has been reset on the display.

2.  In state `Temp`, the display shows on the display the value of the temperature sensor (in Celsius degrees).

3.  In state `Christmas` :
    -   the buzzer starts to play a Christmas tune (for example, Jingle Bells);
    -   the display shows the Christmas date: `25:12`.

4.  State `Light` has two substates:
    -   state `Bright` turns the backlight of the display on, and shows the string "Merry Christmas"
    
    -   state `Dark` turns the backlight of the display off, and shows the string "Happy new year".

While playing the music in the Christmas mode, the music should stop immediately as soon as the state machine exits the state. When entering the state again later, the music continue from where it were interrupted.

The value of the potentiometer should be discretized between `0-9`. When the user turns the potentiometer from one value to the next one, the buzzer should play a short "click" sound. For example, if the current value is a 4, and the user turns the potentiometer clockwise to reach value 5, then the buzzer plays a short "click" and triggers the `tick_up` event. If the counter decreases (ex. from 7 to 6) then the buzzer plays a click sound, and the `tick_dw` event is triggered. Additionally, the step motor turns anticlockwise when the counter decreases and clockwise when the counter increases.


<a id="org6b32659"></a>

## Development

Develop the application using Arduino. Use techniques similar to the one used for code-generation from StateCharts to properly organize your code. Pay attention, the memory is **very limited**.