# Automation 2040 W C++ Firmware

C++ firmware for controlling the Pimoroni Automation 2040 W over USB serial.

## Prerequisites

1. **Pico SDK** - Clone into the parent directory:
   ```bash
   cd ..
   git clone https://github.com/raspberrypi/pico-sdk.git
   cd pico-sdk
   git submodule update --init
   ```

2. **Pimoroni Pico Libraries** - Clone into the parent directory:
   ```bash
   cd ..
   git clone https://github.com/pimoroni/pimoroni-pico.git
   ```

3. **Build tools**:
   ```bash
   # macOS
   brew install cmake arm-none-eabi-gcc

   # Ubuntu/Debian
   sudo apt install cmake gcc-arm-none-eabi libnewlib-arm-none-eabi build-essential
   ```

## Building

```bash
mkdir build
cd build
cmake ..
make -j4
```

This produces `automation2040w_usb.uf2` in the `build` directory.

## Flashing

1. Hold the **BOOTSEL** button on the Pico W
2. Connect USB cable
3. Release BOOTSEL - the Pico appears as a USB drive
4. Copy `automation2040w_usb.uf2` to the drive
5. The Pico will reboot and start running

## Directory Structure

Expected layout:
```
parent-folder/
├── pico-sdk/           # Raspberry Pi Pico SDK
├── pimoroni-pico/      # Pimoroni libraries
└── pico-automation-hat/
    └── firmware-cpp/   # This project
```

If your SDK/libraries are in different locations, set these CMake variables:
```bash
cmake -DPICO_SDK_PATH=/path/to/pico-sdk -DPIMORONI_PICO_PATH=/path/to/pimoroni-pico ..
```

## Protocol

Same as the Python firmware - see the main README for command reference.

The host Python library works unchanged with this firmware.

