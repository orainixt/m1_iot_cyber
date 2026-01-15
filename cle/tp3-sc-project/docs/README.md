---
author: Giuseppe Lipari
title: |
  Master Mention Informatique  
  Conceptions des Logiciels Embarqués  
  TP 3 - Statechart Project
---

# Instructions

In this project we will use sismic to design and simulate a statechart.

<https://sismic.readthedocs.io/en/latest/>

# Air conditioner

In this project you have to specify, simulate and test the control
system of an air conditioner.

## Specification

The AC operates in a room of a house with an external environment. The
*current temperature* is the room internal temperature; the *external
temperature* is the temperature of the external environment.

![](room-image.jpeg)

When the AC is turned off, the room temperature naturally evolves with
time so that the current room temperature eventually becomes equal to
the external temperature according to an exponential decay process. The
user of the AC would like to change this so to achieve a *desired
temperature*.

The AC can be operated in two ways: "Automatic" and "Manual". It has
three modes of operations: "Cooling", "Pause" and "Heating". The
interface consists of four buttons: an "On/Off" button, a "Next" button,
a "Plus" and a "Minus" buttons.

![](gui.png)

When the Air Conditioner is turned on, it starts in "Manual" mode and
"Pause" state. By pressing the "Next" button, the AC cycles between
"Pause -\> Heating -\> Cooling -\> Pause". When "Cooling", the ac will send a
"negative" power to the room so to cool it down; when in "Pause", the AC
does not send any power to the room; when in "Heating", the AC sends a
"positive" power to the room so to warm it up.

If the user presses the "Plus" or the "Minus" button, the system
switches to "Automatic" mode. In this operation mode, the user can
increase and decrease the *desired temperature* with buttons "Plus" and
"Minus".

When the system enters for the first time into the "Automatic" operation
mode, the desired temperature is set equal to the *current temperature*.
Then,

- If the desired temperature is greater than the current temperature by
  more than 1 degree, the air conditioner goes in "Heating mode".
- If the desired temperature is lower than the current temperature by
  more than 1 degree, the air conditioner goes in "Cooling mode".
- Otherwise it goes into the "Pause" mode.

To switch back to manual mode, the user presses "Next" again.

The system remembers the last configuration: if the system was in
"Manual/Heating" mode before switching to "Automatic", it goes back to
"Manual/Heating" when pressing the "Next" button. At the same time, the
system remembers the last desired temperature when switching to
"Automatic" after the first time.

The user can switch the AC off by pressing the On/Off button. Also, the
AC switches off automatically after 30 seconds without any user
interaction.

When on, the display shows the Operating mode ("Cooling", "Pause" or
"Heating", and "Automatic" or "Manual"). If in automatic mode, it also
shows the desired temperature. The display is updated after every change
of state. When off, the display does not show anything.

When the current temperature in the room goes above 40 degrees, the AC
raises an alarm; if the temperature stays above 40 degrees for more than
5 seconds, the AC goes off. The alarm can be simulated by simply
printing an appropriate message on the terminal.

### Event parameters

In Sismic, events can carry parameters.

See for example the code in this section of the Sismic documentation :
<https://sismic.readthedocs.io/en/latest/concurrent.html#communicating-statecharts>

Look at the example, and observe the line

``` example
- event: button_0_pushed
         action: send('floorSelected', floor= 0)
```

When the event "button_0_pushed" is triggered, the action consist in
triggering a second event "floorSelected" with parameter "floor=0".
Then, in a second state machine called elevator (see here:
<https://github.com/AlexandreDecan/sismic/blob/master/docs/examples/elevator/elevator.yaml>)
the state "floorSelecting" has a transition triggered by the event
"floorSelected", and the corresponding action is :

``` example
- name: floorSelecting
        transitions:
          - target: floorSelecting
            event: floorSelected
            action: destination = event.floor
```

that is: the variable "destination" takes the value "floor" carried by
the event "floorSelected".

### Assignment

1.  Write the YAML statechart, and generate the graphical UML diagram.

2.  Use the ACGui.py python script to simulate the system. Modify it so
    that the operation mode and the desired temperature are shown in the
    interface.

3.  Suppose the external temperature is 20 degrees and does not change.
    Write the shortest sequence of events to go from Off into
    Automatic/Heating. Test that your StateChart correctly implements
    it.

4.  Write a complete sequence of tests to check that the AC works as
    expected. As a minimum you should test the following behaviours:

    - All states are reachable with the correct sequence of events;

    - The AC correctly switches to Heating, Pause, Cooling when in
      Automatic mode, depending on the relative values of the current
      and desired temperature;

    - The AC raises an alarm if the current room temperature goes above
      40 degrees, and then goes off after 5 seconds if the temperature
      is still above 40 degrees.

    - The AC remembers the last desired temperature when it enters
      automatic mode for the second time;

    - The AC remembers the last operating state when it switches to
      "Manual".

5.  Check the following properties by using appropriate contracts:

    - If the StateChart is in Automatic/Heating mode, then it must be
      true that `currTemp<desTemp-1`
    - If the StateChart is in Automatic/Cooling mode, then
      `currTemp>desTemp+1`
    - If the StateChart is in Automatic/Pause mode, then
      `destemp-1<=currTemp<=desTemp+1`

### Answers

- StateCharts in YAML (with contracts)
- A set of Python scripts to test the system
- The shortest sequence of events (point 3).
