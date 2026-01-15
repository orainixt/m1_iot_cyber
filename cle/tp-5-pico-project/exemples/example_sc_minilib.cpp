#include "FreeRTOS.h"
#include "pico/cyw43_arch.h" // this line is for WiFi
#include "sm_defs.h"
#include "timeout.h"
#include "state_chart.hpp"
#include "task.h"
#include "i2c_scan.h"
#include "lcd.h"
#include "buzzer.h"
#include "hardware/adc.h"
#include <string.h>
#include "pico/stdlib.h"

// the light sensor is connected to A0
#define LIGHT_ADC 0
// The LED is connected to D16
#define LED_PIN 16
// The button is connected to D18
#define BUTTON_PIN 18 
// The buzzer is connected to A1
#define BUZZ_PIN 27

/*
  The main state machine. This is always the same, do not change it. 
 */
class MainSM : public StateMachine {
    SimpleState *root_state;
public:
    MainSM(SimpleState &root) : root_state(&root) {}
    void handler(Evt_t evt) {
        root_state->handler(evt);
    }
};

// The list of possible events in the system
enum Events {EVT_PRESS, EVT_LIGHTLOW, EVT_LIGHTOK};

// the root state 
CompositeState Root("Root");
// The main state machine, takes the root state as parameter
MainSM sm(Root);

///////////////////////////////////////////////////////////////////
/// LIGHT SENSOR TASK
/// It reads the luminosity via the light sensor attached to A0
///////////////////////////////////////////////////////////////////
TaskHandle_t th_light = NULL;

uint16_t light_intensity = 0;

void task_light(void *arg){
    while (1){
        // every half a second
        vTaskDelay(500);
        // the light sensor is on A0
        adc_select_input(LIGHT_ADC);
        // reads the value 
        uint16_t adc = adc_read();
        printf("Value of light sensor is : %u\n", adc);
        light_intensity = adc;

        if (light_intensity < 1000 ) { sm.send(EVT_LIGHTLOW); }
        else { sm.send(EVT_LIGHTOK); }
    }
}


///////////////////////////////////////////////////////////////////
/// BUTTON SENSOR TASK
/// It reacts when someone presses the button 
///////////////////////////////////////////////////////////////////

// handle of the task to wake up in the interrupt
TaskHandle_t th_button = NULL;


// Interrupt handler routine
void gpio_callback(uint gpio, uint32_t events)
{
    BaseType_t xHigherPriorityTaskWoken = pdFALSE; // Has a higher priority task been woken ?

    // if a RISE event 
    if (events & GPIO_IRQ_EDGE_RISE) { 
        // notify the task 
        vTaskNotifyGiveFromISR( th_button, &xHigherPriorityTaskWoken );
    }
    // call the scheduler if a higher priority task has been woken up
    portYIELD_FROM_ISR( xHigherPriorityTaskWoken );
}

void task_button(void *arg)
{
    while(1) {
        ulTaskNotifyTake(pdFALSE,        // Decrements the notification value
                         portMAX_DELAY); // waits forever 
        printf("Button pressed !!!\n");
        sm.send(EVT_PRESS);
    }
}


///////////////////////////////////////////////////////////////////
///  ON BOARD TEMPERATURE SENSOR
///////////////////////////////////////////////////////////////////
#define TEMPERATURE_UNITS 'C'

float read_onboard_temperature(const char unit)
{
    /* 12-bit conversion, assume max value == ADC_VREF == 3.3 V */
    const float conversionFactor = 3.3f / (1 << 12);

    adc_select_input(4); // the onboard sensor is on ADC 4
    float adc = (float)adc_read() * conversionFactor;
    float tempC = 27.0f - (adc - 0.706f) / 0.001721f;

    if (unit == 'C') {
        return tempC;
    } else if (unit == 'F') {
        return tempC * 9 / 5 + 32;
    }

    return -1.0f;
}

// handle of the temperature task 
TaskHandle_t th_temp = NULL;

void task_temp(void *arg)
{
    while (1){
        // every 4 s
        vTaskDelay(4000);
        // reads the temperature
        float temperature = read_onboard_temperature(TEMPERATURE_UNITS);
        printf("Onboard temperature = %.02f %c\n", temperature, TEMPERATURE_UNITS);
    }
}



///////////////////////////////////////////////////////////////////
/// BLINK LED
///////////////////////////////////////////////////////////////////
TaskHandle_t th_led = NULL;
void task_led(void *arg){
    while (1){
        // waits 500 ms
        vTaskDelay(500);
        // turn led on
        gpio_put(LED_PIN, true);
        // waits 500 ms
        vTaskDelay(500);
        // turn led off
        gpio_put(LED_PIN, false);
    }
}


///////////////////////////////////////////////////////////////////
/// PLAY ARPEGE A minor
///////////////////////////////////////////////////////////////////
TaskHandle_t th_buzzer = NULL;

buzzer_t buzz;

void task_buzzer(void *arg)
{
    while (1){
        buzzer_stop(&buzz);
        buzzer_start(&buzz, 440); // Play A4

        vTaskDelay(250);

        buzzer_stop(&buzz);
        buzzer_start(&buzz, 523); // Play C5

        vTaskDelay(250);

        buzzer_stop(&buzz);
        buzzer_start(&buzz, 659); // Play E5

        vTaskDelay(250);

        buzzer_stop(&buzz);
        buzzer_start(&buzz, 523); // Play C5

        vTaskDelay(250);
    }
}


// This function sets the background light of the LCD to green,
// then prints a string on the LCD ans on the USB/Serial device
void lcd_green()
{
    lcd_set_rgb(24,246,56);
    lcd_clear();
    lcd_print("Light is OK\n");
    printf("Setting light\n");
}



//////////////////////////////////////////////////////////////
/// MAIN
/// Here we declare the statechart structure using the SC_MINILIB
/// then we create the FreeRTOS tasks, and finally we start
/// the scheduler before going to sleep
//////////////////////////////////////////////////////////////
int main()
{
    // Init input/output via usb
    stdio_init_all();

    // This initializes the timer for the SC_MINILIB
    timer_list_init();
    
    // initializes adc
    adc_init();

    // The LCD is connected to I2C1 
    lcd_init(i2c1, LCD_I2C_ADDRESS, LCD_RGB_ADDRESS);
		lcd_set_cursor(0,0);

    // Initialize The LED
    gpio_init(LED_PIN);
    gpio_set_dir(LED_PIN, GPIO_OUT);

    // Initialize the button
    gpio_init(BUTTON_PIN);
    gpio_set_irq_enabled_with_callback(BUTTON_PIN,
                                       GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL,
                                       true, &gpio_callback);

    // Initialize the buzzer
    buzzer_init(&buzz, BUZZ_PIN); // connected to A1
    
    // From now on, we create the state machine using sc_minilib

    // A simple State 
    SimpleState Off("OFF");
    // A composite state
    CompositeState On("ON");
    // The are both contained in Root, and the initial state is Off. 
    Root.add_child(Off);
    Root.add_child(On);
    Root.set_initial(Off);

    // The On state contains two more states
    // A simple state
    SimpleState Red("RED");
    // A simple state. Here I specify lcd_green as an entry function,
    // it will be executed every time the state is entered
    // the exit action does nothin (empty_action)
    SimpleState Green("GREEN", lcd_green, empty_action);
    // they ara all part of On, and Red is the inital state
    On.add_child(Red);
    On.add_child(Green);
    On.set_initial(Red);
    
    // Now I speficy all transitions The first transition goes from
    // Off to On The third parameter is a boolean guard. In the
    // following example, it is expressed as a lambda function, that
    // is a function with no name that is created on the fly.
    // 
    // A lambda function is C++ has the following syntax
    // [<capture>](<parameter list>) { <function body> }
    // - <capture> is the list of external local variables I want to use in the function, in this case nothing 
    // - <parameter list> is the list of parameters of the function. In this case, the event
    // - <function body> is the code of the function
    // Instead of a lambda, I can specify a regular function, as long as it is a function that
    // takes a Evt parameter (see later).
    // The guard function (third parameter) has to return a boolean, and implements the
    // guard expression. In this case, we check if the received event is "EVT_PRESS". 
    // 
    // The fourth parameter is another lambda function to express an
    // action. It must be a function with no parameter that returns a
    // void.
    Transition OffOn(Off, On,
                     [](Evt_t e) {
                         return e == EVT_PRESS;
                     },
                     []() {
                         printf("From Off to On\n");
                     }
        );
    
    // Same as before, from On to Off. 
    Transition OnOff(On, Off,
                     [](Evt_t e) {
                         return e == EVT_PRESS;
                     },
                     []() {
                         printf("From On to Off\n");
                     }
        );

    // From Red to Green, I specify the action as the lcd_green function.
    Transition RedGreen(Red, Green,
                        [](Evt_t e) {
                            return e == EVT_LIGHTOK;
                        },
                        lcd_green
        );

    // From Green to Red, I specify the action as a lambda function with a global variable. 
    // In this case, the function prints on screen the value of light intensity. 
    Transition GreenRed(Green, Red,
                        [](Evt_t e) {
                            return e == EVT_LIGHTLOW;
                        },
                        []() {
                            lcd_set_rgb(255,0,0);
                            lcd_clear();
                            lcd_print("Light is DARK\n");
                            char str[30];
                            sprintf(str, "%u", light_intensity);
                            lcd_print(str);
                            printf("Unsetting light\n");
                        }
        );    
    
    xTaskCreate(task_light,  "light task",  PICO_STACK_SIZE, NULL , 1, &th_light);
    //xTaskCreate(task_buzzer, "buzzer task", PICO_STACK_SIZE, NULL , 1, &th_buzzer);
    xTaskCreate(task_button, "button task", PICO_STACK_SIZE, NULL , 1, &th_button);
    xTaskCreate(task_led,    "led task",    PICO_STACK_SIZE, NULL , 1, &th_led);
    xTaskCreate(task_temp,   "temp task",   PICO_STACK_SIZE, NULL , 1, &th_temp);
    
    vTaskStartScheduler();

    while(1);

}

