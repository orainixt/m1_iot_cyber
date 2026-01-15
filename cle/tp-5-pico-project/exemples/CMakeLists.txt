cmake_minimum_required(VERSION 3.13)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

set(PICO_SDK_PATH "/home/annick/cle/pico-sdk")
set(FREERTOS_KERNEL_PATH "/home/annick/cle/FreeRTOS-Kernel")

set(PICO_BOARD pico_w CACHE STRING "Board type")

include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)
include(${FREERTOS_KERNEL_PATH}/portable/ThirdParty/GCC/RP2040/FreeRTOS_Kernel_import.cmake)

if (PICO_SDK_VERSION_STRING VERSION_LESS "1.4.0")
  message(FATAL_ERROR "Raspberry Pi Pico SDK version 1.4.0 (or later) required. Your version is ${PICO_SDK_VERSION_STRING}")
endif()

set(FREERTOS "True")


## PROJECT 
project(example_sc_minilib C CXX ASM)
set(PICO_CXX_ENABLE_EXCEPTIONS 1)
pico_sdk_init()	

add_executable(example_sc_minilib
	example_sc_minilib.cpp)

pico_set_program_name(example_sc_minilib "example_sc_minilib")
pico_set_program_version(example_sc_minilib "0.1")
pico_enable_stdio_uart(example_sc_minilib 0)
pico_enable_stdio_usb(example_sc_minilib 1)

add_subdirectory(lib/sc_minilib) 
add_subdirectory(lib/pico_buzzer) 
add_subdirectory(lib/pico_lcd) 


target_link_libraries(example_sc_minilib
        pico_stdlib)

# Add the standard include files to the build
target_include_directories(example_sc_minilib PRIVATE
  ${CMAKE_CURRENT_LIST_DIR}
  ${CMAKE_CURRENT_LIST_DIR}/.. # for our common lwipopts or any other standard includes, if required
)

# Add the FreeRTOS library 
target_link_libraries(example_sc_minilib
	hardware_timer
	hardware_adc            # for ADC based sensors
	hardware_i2c            # for the LCD
	sc_minilib
	pico_lcd
	pico_buzzer
	FreeRTOS-Kernel-Heap4
)

# Here you can add additional libraries
# target_link_libraries(example_sc_minilib ...)

pico_add_extra_outputs(example_sc_minilib)


