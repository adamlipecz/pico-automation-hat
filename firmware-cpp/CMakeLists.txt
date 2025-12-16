cmake_minimum_required(VERSION 3.13)

# Include the Pico SDK
set(PICO_SDK_PATH ${CMAKE_CURRENT_LIST_DIR}/../pico-sdk CACHE PATH "Path to the Pico SDK")
set(PIMORONI_PICO_PATH ${CMAKE_CURRENT_LIST_DIR}/../pimoroni-pico CACHE PATH "Path to Pimoroni Pico libraries")

# Include the Pico SDK import
include(${PICO_SDK_PATH}/external/pico_sdk_import.cmake)
include(${PIMORONI_PICO_PATH}/pimoroni_pico_import.cmake)

project(automation2040w_usb C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

# Initialize the Pico SDK
pico_sdk_init()

# Add the executable
add_executable(${PROJECT_NAME}
    src/main.cpp
)

# Include directories
target_include_directories(${PROJECT_NAME} PRIVATE
    ${CMAKE_CURRENT_LIST_DIR}/src
)

# Link libraries
target_link_libraries(${PROJECT_NAME}
    pico_stdlib
    pico_stdio_usb
    hardware_adc
    hardware_pwm
    hardware_gpio
    automation2040w  # Pimoroni library
)

# Enable USB output, disable UART output
pico_enable_stdio_usb(${PROJECT_NAME} 1)
pico_enable_stdio_uart(${PROJECT_NAME} 0)

# Create UF2 output file
pico_add_extra_outputs(${PROJECT_NAME})

