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
#include "hardware/rtc.h" 
#include "pico/util/datetime.h" 
#include <string.h>
#include "pico/stdlib.h"
#include "lwip/apps/sntp.h"
// define pins 
#include <iostream>


#define BUZZER_PIN 20
#define POTEN_PIN 27 
#define BUTTON_PIN 18
#define LED_PIN 16
#define LIGHT_PIN 26
// main state machine -- do not delete 


#define NOTE_C4  262
#define NOTE_D4  294
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_G4  392
#define NOTE_A4  440
#define NOTE_AS4 466 
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_D5  587
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_G5  784
#define NOTE_A5  880

class MainSM: public StateMachine {
	SimpleState *root_state; 
public: 
	MainSM(SimpleState &root) : root_state(&root) {}
	void handler(Evt_t evt) {
		root_state-> handler(evt); 
	}
}; 

enum Events {
	EVT_BUTTON, 
	EVT_POTEN, 
	EVT_ALARM_TIMEOUT,
	EVT_ALARM_DONE, 
	EVT_TICK, 
	EVT_UPDATE_HOUR, 
	JUMP_PLAY,
	JUMP_TIME_SET,
	JUMP_ALARM_SET
};


volatile struct tm current_time = {
    .tm_sec = 0, 
    .tm_min = 0,  
    .tm_hour = 0, 
    .tm_mday = 1, 
    .tm_mon = 0,
    .tm_year = 124
};

volatile uint32_t alarm_cpt = 0; 
volatile int alarm_set = 0;
volatile int alarm_mode = 0; 
volatile uint32_t alarm_duration = 15;  
volatile uint32_t potent_val = 5;
int color_switch = 0; 
volatile int is_home = 0; 
volatile int menu_select = -1; 
volatile int menu_timer = 0;

volatile int is_play = 0;

int melody[] = { NOTE_D4, 0, NOTE_F4, NOTE_D4, 0, NOTE_D4, NOTE_G4, NOTE_D4 };
int durations[] = { 8, 8, 6, 16, 16, 16, 8, 8 };

int total_notes = sizeof(melody) / sizeof(int);

int shark_melody[] = {
    NOTE_D4, NOTE_E4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4,
    NOTE_D4, NOTE_E4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4,
    NOTE_D4, NOTE_E4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4, NOTE_G4,
    NOTE_G4, NOTE_G4, NOTE_F4
};

int shark_durations[] = {
    4, 4, 8, 8, 8, 8, 8, 8,
    4, 4, 8, 8, 8, 8, 8, 8,
    4, 4, 8, 8, 8, 8, 8, 8,
    4, 4, 2
};

int shark_len = sizeof(shark_melody) / sizeof(int);


CompositeState Root("Root");  
MainSM sm(Root); 
// task to update 
TaskHandle_t th_clock = NULL; 



//BUTTON SENSOR TAKS REACTS WHEN SOMEONE PRESSES THE BUTTON 
//
TaskHandle_t th_button = NULL; 

void gpio_callback(uint gpio, uint32_t events) {
	BaseType_t xHigherPriorityTaskWoken = pdFALSE; 
	// if rise event 
	if (events & GPIO_IRQ_EDGE_RISE) {
		//notify the task 
		vTaskNotifyGiveFromISR(th_button, &xHigherPriorityTaskWoken); 
	}
	//call sheduler if a higher priority tasj has been woken up 
	portYIELD_FROM_ISR(xHigherPriorityTaskWoken); 
}

void task_button(void *arg){
	while(1) {
		ulTaskNotifyTake(pdFALSE, portMAX_DELAY); //decrements notification value & wait forever
		vTaskDelay(pdMS_TO_TICKS(200));
		printf("button pressed!\n");
		sm.send(EVT_BUTTON); 
	}
}


// temperature 
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
void update_lcd(){

	lcd_clear(); 
	lcd_set_cursor(0,0); 
	char buff[32]; 

	if (menu_timer > 0) {
		lcd_print("Menu select :"); 
		lcd_set_cursor(1,0);
		const char* str = "";

		switch (menu_select) {
			case 0: 
				str = "^TIME_SET"; 
				break;
			case 1:
				str = "^ALARM_SET"; 
				break; 
			case 2 :
				str = "^PLAY"; 
				break; 
		} 
		for (int i = 0 ; i < strlen(str) ; i++){
			lcd_char(str[i]); 
			lcd_set_cursor(1,i+1); 
		}
		return; 
	}

	datetime_t time; 		
	sprintf(buff, "%02d:%02d:%02d", current_time.tm_hour, current_time.tm_min, current_time.tm_sec); 
	
	for (int i=0 ; i < strlen(buff) ; i++) {
		lcd_char(buff[i]); 
		lcd_set_cursor(0,i+1); 
	}

	float temp = read_onboard_temperature(TEMPERATURE_UNITS); 
	lcd_set_cursor(1,0); 
	sprintf(buff, "Temp : %.02f %c", temp, TEMPERATURE_UNITS); 
	for (int i=0 ; i < strlen(buff) ; i++) {
		lcd_char(buff[i]);
		lcd_set_cursor(1,i+1); 
	}
}

TaskHandle_t th_tick = NULL; 
void task_tick(void *arg) {
	while(1) {
		vTaskDelay(1000); 
		if (menu_timer > 0) {menu_timer--;}
		sm.send(EVT_TICK); 
	}
}


void wake_up(void *arg) {
	lcd_set_rgb(255,255,255); 
	lcd_clear();
	lcd_set_cursor(0,0); 
	lcd_print("In HOME"); 
	lcd_set_cursor(1,0); 
	const char* welcome = "Press Button"; 
	for (int i= 0; i< strlen(welcome) ; i++) {
		lcd_char(welcome[i]);
		lcd_set_cursor(1,i+1);
	}
}


void task_update_time(void* arg) {
	while (1) {
		current_time.tm_sec++;
		if(current_time.tm_sec >= 60){ current_time.tm_sec = 0; current_time.tm_min++; }
		if(current_time.tm_min >= 60){ current_time.tm_min = 0; current_time.tm_hour++; }
		if(current_time.tm_hour >= 24){ current_time.tm_hour = 0; }

		printf("It's: %02d:%02d:%02d\n", current_time.tm_hour, current_time.tm_min, current_time.tm_sec);
		vTaskDelay(pdMS_TO_TICKS(1000));
	}
} 

void task_time(void* arg) {

	char buff[16]; 
	int index = 0; 
	int h, m, s; 
	char sep_1, sep_2; 

	while (1) {
		if (std::cin >> h >> sep_1 >> m >> sep_2 >> s) {
			if (sep_1 == ':' && sep_2 == ':') {
				current_time.tm_hour = h; 
				current_time.tm_min = m; 
				current_time.tm_sec = s; 
				
				lcd_clear(); 
				lcd_set_cursor(0,0); 
				lcd_print("Fetched time :"); 
				lcd_set_cursor(1,0);
				buff[16]; 
				sprintf(buff, "%02d:%02d:%02d", h,m,s); 
				for (int i = 0 ; i < strlen(buff) ; i++) {
					lcd_char(buff[i]); 
					lcd_set_cursor(1,i+1);
				}
				vTaskDelay(2000); 
				sm.send(EVT_UPDATE_HOUR);

			}
		}
	}
}
// states

void task_alarm(void* arg) {
	uint32_t last_val = 0; 
	while (1) {
}
}

void task_cpt_alarm(void* arg) {
	while (1) {
		if (alarm_set) {
			if (alarm_cpt > 0) {
				alarm_cpt--; 
			} 
			if (alarm_cpt == 0) {
				alarm_set = 0; 
				sm.send(EVT_ALARM_TIMEOUT);
			}
		}
		
		if (alarm_mode) {
			if (alarm_duration > 0) {alarm_duration--;}
			if (alarm_duration == 0) {
				alarm_duration = 15; 
				alarm_mode = 0; 
				sm.send(EVT_ALARM_DONE); 
			}
		}

		vTaskDelay(pdMS_TO_TICKS(1000));
	}
}

void alarm_lcd() {
	char buff[32];
	lcd_clear();
	lcd_set_cursor(0,0); 
	lcd_print("SET ALARM MODE");
	lcd_set_cursor(1,0); 
	sprintf(buff,"For : %d secs", potent_val); 
	for (int i=0 ; i<strlen(buff) ; i++) {
		lcd_char(buff[i]);
		lcd_set_cursor(1,i+1); 
	}
}
TaskHandle_t th_buzzer = NULL; 
buzzer_t buzz; 

void task_buzzer(void *arg) {

	int index = 0;
	int index_shark = 0;
	int len = sizeof(melody) / sizeof(int); 
	int is_playing = 0; 

	while (1) {
		if (alarm_mode) {
			is_playing = 1; 
			int note = melody[index];
			int duration_ms = 1714 / durations[index];

			if (note == 0) buzzer_stop(&buzz);
			else buzzer_start(&buzz, note);
			
			vTaskDelay(pdMS_TO_TICKS(duration_ms));
			buzzer_stop(&buzz);
			vTaskDelay(pdMS_TO_TICKS(50)); 
			index++;
			
			if (index >= len){ index = 0;} 
    }
		if (is_play) {
			is_playing = 1;
			int note = shark_melody[index_shark];
			int duration_val = (shark_durations[index_shark] > 0) ? shark_durations[index_shark] : 8;
			int duration_ms = 1000 / duration_val;

			if (note == 0) buzzer_stop(&buzz);
			else buzzer_start(&buzz, note);

			vTaskDelay(pdMS_TO_TICKS(duration_ms));
			buzzer_stop(&buzz);
			vTaskDelay(pdMS_TO_TICKS(50));

			index_shark++;
			if (index_shark >= shark_len) { index_shark = 0; }
		}
		else {
			if (is_playing) {
				buzzer_stop(&buzz);
				index = 0;
				is_playing = 0;
			}
			vTaskDelay(pdMS_TO_TICKS(200));
		}
	}
} 

void task_potent(void* arg) {

	adc_select_input(1); 
	uint32_t start_val = adc_read();

	uint32_t last_alarm = 0; 
	uint32_t last_mode = start_val * 3 / 4096;
	int was_in_home = 0;
	while (1) {
		adc_select_input(1); 
		uint32_t pot_val = adc_read();

		if (is_home) {
			uint32_t mode = pot_val * 3 / 4096; 
			if (!was_in_home) {
				last_mode = mode;
				was_in_home = 1;
			}
			if (abs((int)mode - (int)last_mode) >= 1) {
					last_mode = mode; 
					menu_select = mode; 
					menu_timer = 4;
			}

		} else {
			was_in_home = 0; 
			uint32_t alarm = 5 + (pot_val * 56 / 4096); 

			if (abs((int)alarm - (int)last_alarm) >= 1) { 
				potent_val = alarm;
				last_alarm = alarm;
			}
		}

		vTaskDelay(pdMS_TO_TICKS(100));
	}
}

void on_entry_home() {
	alarm_mode = 0;
	is_play = 0; 
	is_home = 1;
	buzzer_stop(&buzz);
	menu_timer = 0;
}

void on_exit_home() {
	is_home = 0; 
}

void on_entry_play() {
	is_play = 1;
	lcd_clear(); 
	lcd_set_cursor(0,0); 
	lcd_print("PLAY MODE"); 
	lcd_set_cursor(1,0); 
	const char* str = "Playing Music";
	for (int i = 0 ; i < strlen(str) ; i++) {
		lcd_char(str[i]);
		lcd_set_cursor(1,i+1); 
	}
} 

SimpleState START("START"); 
SimpleState HOME("HOME", on_entry_home, on_exit_home); 
SimpleState TIME_SET("TIME_SET");
SimpleState ALARM_SET ("ALARM_SET"); 
SimpleState PLAY("PLAY", on_entry_play, empty_action);

SimpleState ALARM("ALARM");

int main() {
	stdio_init_all(); // init input output via usb
										//
	sleep_ms(5000); 
	timer_list_init(); 

	adc_init();
	adc_set_temp_sensor_enabled(true);

	rtc_init(); 

	// init LCD 
	lcd_init(i2c1, LCD_I2C_ADDRESS, LCD_RGB_ADDRESS); 
	lcd_set_cursor(0,0); 

	// init buzzer
	buzzer_init(&buzz, BUZZER_PIN); 

	// init button 
	gpio_init(BUTTON_PIN); 
	gpio_set_irq_enabled_with_callback(
			BUTTON_PIN,
			GPIO_IRQ_EDGE_RISE,
			true, 
			&gpio_callback
	); 

	adc_gpio_init(POTEN_PIN);

	gpio_init(LED_PIN);
  gpio_set_dir(LED_PIN, GPIO_OUT);

	// add them to root state
	Root.add_child(START); 
	Root.add_child(HOME);
	Root.add_child(TIME_SET);
	Root.add_child(ALARM_SET);
	Root.add_child(PLAY);
	Root.add_child(ALARM); 

	Root.set_initial(START);
		
	Transition StartStart(
			START, START,
			[](Evt_t e) {return e == EVT_TICK;}, 
			[]() {wake_up(nullptr);}
	);  

	Transition StartHome(
			START, HOME, 
			[](Evt_t e) {
				return e == EVT_BUTTON;			
			}, 
			[]() {}
	); 						

	Transition HomeHome(
		HOME, HOME, 
		[](Evt_t e) {return e == EVT_TICK;}, 
		[]() {
			update_lcd();
			buzzer_stop(&buzz); 
		} 
	);

	Transition HomeTimeSet {
		HOME, TIME_SET, 
		[](Evt_t e) {return (e == EVT_BUTTON && menu_select == 0 && menu_timer > 0);}, 
		[]() {
			lcd_clear(); 
			lcd_print("TIME SET MODE");
			lcd_set_cursor(1,0); 
			const char* str = "Waiting input..."; 
			for (int i =0 ; i<strlen(str) ; i++) {
				lcd_char(str[i]); 
				lcd_set_cursor(1,i+1);
			}
		} 
	};

	Transition HomeAlarmSet { 
		HOME, ALARM_SET, 
		[](Evt_t e) {return (e == EVT_BUTTON && menu_select == 1 && menu_timer > 0);},
		[]() {}
	}; 

	Transition HomePlay {
		HOME,PLAY, 
		[](Evt_t e) {return (e==EVT_BUTTON && menu_select == 2 && menu_timer > 0);},
		[]() {}
	}; 

	Transition HomeAlarme {
		HOME, ALARM, 
		[](Evt_t e) {return e==EVT_ALARM_TIMEOUT;},
		[]() {
			alarm_mode = 1;
			alarm_duration = 15;  
		}
	};

	Transition TimeSetHome {
		TIME_SET, HOME, 
		[](Evt_t e) {return e == EVT_UPDATE_HOUR;}, 
		[]() {}
	};


	Transition AlarmSetHome {
		ALARM_SET, HOME, 
		[](Evt_t e) {return e==EVT_BUTTON;},
		[]() {
			lcd_clear(); 
			lcd_print("Alarm Set !"); 
			lcd_set_cursor(1,0); 
			const char* str = "Waiting 2 secs"; 
			for (int i = 0 ; i < strlen(str) ; i++) {
				lcd_char(str[i]);
				lcd_set_cursor(1,i+1); 
			}
			vTaskDelay(pdMS_TO_TICKS(2000)); 
			alarm_set = 1;
			alarm_cpt = potent_val; 
		}
	}; 

	Transition AlarmSetAlarmSet {
		ALARM_SET, ALARM_SET,
		[](Evt_t e) { return (e == EVT_POTEN || e == EVT_TICK); },
		[]() { alarm_lcd(); }
    };


	Transition AlarmHome {
		ALARM, HOME, 
		[](Evt_t e){return (e==EVT_ALARM_DONE || e==EVT_BUTTON);}, 
		[]() {
			lcd_clear(); 
			lcd_set_rgb(255,255,255);
			lcd_print("Stopping Alarm"); 
			lcd_set_cursor(1,0); 
			const char* str = "Waiting 2 secs"; 
			for (int i = 0 ; i < strlen(str) ; i++) {
				lcd_char(str[i]); 
				lcd_set_cursor(1,i+1); 
			}
			vTaskDelay(pdMS_TO_TICKS(2000)); 
			alarm_mode = 0;
			gpio_put(LED_PIN,0); 
			color_switch = 0; 

		}
	} ;

	Transition AlarmAlarm {
		ALARM,ALARM, 
		[](Evt_t e) {return e==EVT_TICK;}, 
		[]() {
			lcd_clear();
			lcd_set_cursor(0,0);
			lcd_print("!! ALARM MODE !!");
			lcd_set_cursor(1,0);
			const char* str = "Button to quit";
			for (int i= 0; i < strlen(str) ; i++) {
				lcd_char(str[i]); 
				lcd_set_cursor(1,i+1);
			} 
			if (color_switch) {
					lcd_set_rgb(255, 0, 0);					
					gpio_put(LED_PIN, 1);
			} else {
					lcd_set_rgb(0, 0, 255);
					gpio_put(LED_PIN, 0);
			}
			color_switch = !color_switch;
		}
	};

	Transition PlayHome {
		PLAY,HOME,
		[](Evt_t e) {return e==EVT_BUTTON;},
		[]() {}
	};

	Transition PlayAlarm {
    PLAY, ALARM,
    [](Evt_t e) { return e == EVT_ALARM_TIMEOUT; },
    []() {
        is_play = 0;         
				alarm_mode = 1; 
				alarm_duration = 15;  
    }
};

	xTaskCreate(task_button, "button task", PICO_STACK_SIZE, NULL, 1, &th_button); 
	xTaskCreate(task_tick, "tick task", PICO_STACK_SIZE, NULL, 1, &th_tick); 
	xTaskCreate(task_buzzer, "buzzer_task", 4096, NULL, 1, &th_buzzer); 
	xTaskCreate(task_time, "time task", 4096, NULL,1,NULL);
	xTaskCreate(task_update_time, "task_update_time",  4096, NULL, 1, NULL);
	xTaskCreate(task_potent, "potent task", 4096, NULL, 1, NULL); 
	xTaskCreate(task_cpt_alarm, "cpt-alarm task", 4096, NULL, 1, NULL); 


	// FreeRTOS launching 
	vTaskStartScheduler(); 

	// computation should not read thoses lines
	while(1); // if main ends, raspberry ends too 
}


