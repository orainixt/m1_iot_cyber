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

project(pico_project C CXX ASM) 
set(PICO_CXX_ENABLE_EXCEPTIONS 1)
pico_sdk_init()	

add_executable(pico_project
	pico_project.cpp
) 

pico_set_program_name(pico_project "pico_project")
pico_set_program_version(pico_project "0.1")
pico_enable_stdio_uart(pico_project 0)
pico_enable_stdio_usb(pico_project 1)

add_subdirectory(lib/sc_minilib) 
add_subdirectory(lib/pico_buzzer) 
add_subdirectory(lib/pico_lcd) 


target_link_libraries(pico_project
        pico_stdlib)
	
# Add the standard include files to the build
target_include_directories(pico_project PRIVATE
  ${CMAKE_CURRENT_LIST_DIR}
  ${CMAKE_CURRENT_LIST_DIR}/.. # for our common lwipopts or any other standard includes, if required
)

# Add the FreeRTOS library 
target_link_libraries(pico_project
	hardware_timer
	hardware_adc            # for ADC based sensors
	hardware_i2c            # for the LCD
	sc_minilib
	pico_lcd
	pico_buzzer
	FreeRTOS-Kernel-Heap4
	pico_cyw43_arch_lwip_threadsafe_background
	hardware_rtc 
	pico_lwip_sntp         	
	pico_lwip_core
)

# Here you can add additional libraries
# target_link_libraries(example_sc_minilib ...)

pico_add_extra_outputs(pico_project)




