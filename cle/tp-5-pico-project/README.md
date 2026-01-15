# Pico Project -- Lucas Sauvage

This is the repo for the CLE project of Lucas Sauvage 

## UML 

![UML](./XLJHQjim57tNLrpwqBI3bAGlWuw4UektXZLsi9N1o8Bnx0iHiMKZoMt3kW_eT_N79bjsgvYcyzELxhtdddkEyBLKiL1LdX75L8Pm0YT49h6EFev6SCzIjILontWPYpY7lE15iXL5Zg14XMJBKWJCIxM756KYMAbOmGaPm70uXF45p9wVliwzEPtx7ipS49wVg4F3Eak8dgmGGke4b83-cWYkmFr18ph_yXs6KxYFTnXLvTbvLtxZBrpuqzG.pdf)

## Project 

### States

It was asked to create a StateMachine using a Raspberry Pico.
5 states were asked : 

    - HOME : Print time since pico start or time if it was fetch
    - TIME_SET : Wait the python script to synchronize time 
    - ALARM_SET : Set an alarm for 5-60 sec
    - ALARM : Automatically switched to at alarm timeout
    - PLAY : Play a music

### Events

    - EVT_BUTTON : Whenever button is pressed
	EVT_POTEN : Whenever potent is turned
	EVT_ALARM_TIMEOUT : When alarm reachs 0second 
	EVT_ALARM_DONE : When the alarm is done 
	EVT_TICK : Every 1 second
	EVT_UPDATE_HOUR : When the Pico fetchs the hour (via python script) 
	JUMP_PLAY : Used by the menu to jump to Play
	JUMP_TIME_SET : Used by the menu to jump to TimeSet 
	JUMP_ALARM_SET : Used by the menu to jump to AlarmSet
 
However, there is a bug whenever states are switch while buzzer is buzzing (and therefore not stopped). 
If it happens, you should unplug the Pico, it won't go off.

### Tasks 

task_bouton : Waits an input button 
task_tick : Sends TICK event every second 
task_buzzer : Handle audio 
task_time : Waits for the python script to fetch time 
task_update_time : Increments the structure used for Hour 
task_potent : Used to get potent value 
task_cpt_alarm : Used to handle alarm cpt // Send EVT_ALARM_TIMEOUT and EVT_ALARM_DONE

### Interrupt routine 

There's only one interrupt routine, and it's `gpio_callback`. 
It's used to send and handle button events. 

### Problems encountered 

There's a problem with the buzzer as I said above.
I created the main problem, because even if I saw that hour was fetched through python script (which I had to do in the end), I tried for a couple of days to use the cyw43_arch.h header which fetch time through internet.
Even if the connection was up (detected by my personal hotspot) it always returns an error. 
Furthermore, I add a problem with the potentiometre, because `adc_select_input` was running for both temperature and menu_select. 
