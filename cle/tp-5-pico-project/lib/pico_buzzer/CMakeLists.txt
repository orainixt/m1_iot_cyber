add_library(pico_buzzer
	buzzer.c
)

target_include_directories(pico_buzzer PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})

# pull in common dependencies
target_link_libraries(pico_buzzer
	hardware_adc
	hardware_pwm)

