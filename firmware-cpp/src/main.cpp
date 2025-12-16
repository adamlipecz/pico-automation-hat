/**
 * Automation 2040 W USB Control Firmware (C++)
 * =============================================
 *
 * A simple text-based command protocol for controlling the Pimoroni Automation 2040 W
 * over USB serial (CDC ACM).
 *
 * Protocol Design:
 * - Commands are newline-terminated ASCII strings
 * - Responses always start with OK, ERR, or the requested data
 * - Query commands end with '?'
 * - Human-readable and easy to debug with any serial terminal
 *
 * Commands:
 * ---------
 * RELAY <n> <ON|OFF>      Set relay n (1-3) on or off
 * RELAY <n>?              Query relay n state
 * OUTPUT <n> <value>      Set output n (1-3), value 0-100 (PWM %) or ON/OFF
 * OUTPUT <n>?             Query output n state
 * INPUT <n>?              Query digital input n (1-4)
 * ADC <n>?                Query ADC n (1-3) voltage
 * LED <A|B> <value>       Set button LED brightness (0-100)
 * BUTTON <A|B>?           Query button state
 * STATUS                  Get all I/O states as JSON
 * RESET                   Reset all outputs to safe state
 * VERSION                 Get firmware version
 * HELP                    Show available commands
 *
 * Author: Generated for Pimoroni Automation 2040 W
 * License: MIT
 */

#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include "pico/stdlib.h"
#include "automation2040w.hpp"

using namespace automation;

// Firmware version
static const char* VERSION = "1.0.0";

// Command buffer
static char cmd_buffer[256];
static int cmd_pos = 0;

// Board instance
static Automation2040W board;

// Relay states (board doesn't provide read-back, so we track them)
static bool relay_states[Automation2040W::NUM_RELAYS] = {false};
static float output_values[Automation2040W::NUM_OUTPUTS] = {0.0f};

// Forward declarations
void process_command(const char* cmd);
void cmd_relay(const char* args);
void cmd_output(const char* args);
void cmd_input(const char* args);
void cmd_adc(const char* args);
void cmd_led(const char* args);
void cmd_button(const char* args);
void cmd_status();
void cmd_reset();
void cmd_help();

/**
 * Convert string to uppercase in place
 */
void str_toupper(char* str) {
    while (*str) {
        *str = toupper((unsigned char)*str);
        str++;
    }
}

/**
 * Skip whitespace and return pointer to next non-space character
 */
const char* skip_whitespace(const char* str) {
    while (*str && isspace((unsigned char)*str)) {
        str++;
    }
    return str;
}

/**
 * Parse an integer from string, return pointer to next character after number
 */
const char* parse_int(const char* str, int* value) {
    *value = 0;
    while (*str && isdigit((unsigned char)*str)) {
        *value = *value * 10 + (*str - '0');
        str++;
    }
    return str;
}

/**
 * Check if string starts with prefix (case-insensitive after uppercase)
 */
bool starts_with(const char* str, const char* prefix) {
    return strncmp(str, prefix, strlen(prefix)) == 0;
}

/**
 * Process a single character of input
 */
void process_char(char c) {
    if (c == '\n' || c == '\r') {
        if (cmd_pos > 0) {
            cmd_buffer[cmd_pos] = '\0';
            process_command(cmd_buffer);
            cmd_pos = 0;
        }
    } else if (cmd_pos < (int)sizeof(cmd_buffer) - 1) {
        cmd_buffer[cmd_pos++] = c;
    }
}

/**
 * Process a complete command
 */
void process_command(const char* cmd) {
    // Make a mutable copy and convert to uppercase
    char buf[256];
    strncpy(buf, cmd, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';
    str_toupper(buf);

    const char* p = skip_whitespace(buf);

    // Skip empty lines and comments
    if (*p == '\0' || *p == '#') {
        return;
    }

    if (starts_with(p, "RELAY")) {
        cmd_relay(p + 5);
    } else if (starts_with(p, "OUTPUT")) {
        cmd_output(p + 6);
    } else if (starts_with(p, "INPUT")) {
        cmd_input(p + 5);
    } else if (starts_with(p, "ADC")) {
        cmd_adc(p + 3);
    } else if (starts_with(p, "LED")) {
        cmd_led(p + 3);
    } else if (starts_with(p, "BUTTON")) {
        cmd_button(p + 6);
    } else if (starts_with(p, "STATUS")) {
        cmd_status();
    } else if (starts_with(p, "RESET")) {
        cmd_reset();
    } else if (starts_with(p, "VERSION")) {
        printf("OK %s\n", VERSION);
    } else if (starts_with(p, "PING")) {
        printf("OK PONG\n");
    } else if (starts_with(p, "HELP")) {
        cmd_help();
    } else {
        printf("ERR Unknown command\n");
    }
}

/**
 * Handle RELAY command
 */
void cmd_relay(const char* args) {
    args = skip_whitespace(args);

    if (*args == '\0') {
        printf("ERR RELAY requires arguments\n");
        return;
    }

    int index;
    args = parse_int(args, &index);
    index--;  // Convert to 0-based

    if (index < 0 || index >= Automation2040W::NUM_RELAYS) {
        printf("ERR Relay index out of range (1-%d)\n", Automation2040W::NUM_RELAYS);
        return;
    }

    args = skip_whitespace(args);

    if (*args == '?') {
        // Query
        printf("OK %s\n", relay_states[index] ? "ON" : "OFF");
    } else if (starts_with(args, "ON") || starts_with(args, "1") || starts_with(args, "TRUE") || starts_with(args, "HIGH")) {
        board.relay(index, true);
        relay_states[index] = true;
        printf("OK\n");
    } else if (starts_with(args, "OFF") || starts_with(args, "0") || starts_with(args, "FALSE") || starts_with(args, "LOW")) {
        board.relay(index, false);
        relay_states[index] = false;
        printf("OK\n");
    } else {
        printf("ERR RELAY requires ON or OFF\n");
    }
}

/**
 * Handle OUTPUT command
 */
void cmd_output(const char* args) {
    args = skip_whitespace(args);

    if (*args == '\0') {
        printf("ERR OUTPUT requires arguments\n");
        return;
    }

    int index;
    args = parse_int(args, &index);
    index--;  // Convert to 0-based

    if (index < 0 || index >= Automation2040W::NUM_OUTPUTS) {
        printf("ERR Output index out of range (1-%d)\n", Automation2040W::NUM_OUTPUTS);
        return;
    }

    args = skip_whitespace(args);

    if (*args == '?') {
        // Query - return percentage
        printf("OK %d\n", (int)(output_values[index] * 100.0f));
    } else if (starts_with(args, "ON") || starts_with(args, "TRUE") || starts_with(args, "HIGH")) {
        board.output(index, 1.0f);
        output_values[index] = 1.0f;
        printf("OK\n");
    } else if (starts_with(args, "OFF") || starts_with(args, "FALSE") || starts_with(args, "LOW")) {
        board.output(index, 0.0f);
        output_values[index] = 0.0f;
        printf("OK\n");
    } else if (isdigit((unsigned char)*args)) {
        int percent;
        parse_int(args, &percent);
        if (percent < 0) percent = 0;
        if (percent > 100) percent = 100;
        float value = percent / 100.0f;
        board.output(index, value);
        output_values[index] = value;
        printf("OK\n");
    } else {
        printf("ERR OUTPUT requires value (0-100 or ON/OFF)\n");
    }
}

/**
 * Handle INPUT command
 */
void cmd_input(const char* args) {
    args = skip_whitespace(args);

    if (*args == '\0') {
        printf("ERR INPUT requires index\n");
        return;
    }

    int index;
    args = parse_int(args, &index);
    index--;  // Convert to 0-based

    if (index < 0 || index >= Automation2040W::NUM_INPUTS) {
        printf("ERR Input index out of range (1-%d)\n", Automation2040W::NUM_INPUTS);
        return;
    }

    bool value = board.read_input(index);
    printf("OK %s\n", value ? "HIGH" : "LOW");
}

/**
 * Handle ADC command
 */
void cmd_adc(const char* args) {
    args = skip_whitespace(args);

    if (*args == '\0') {
        printf("ERR ADC requires index\n");
        return;
    }

    int index;
    args = parse_int(args, &index);
    index--;  // Convert to 0-based

    if (index < 0 || index >= Automation2040W::NUM_ADCS) {
        printf("ERR ADC index out of range (1-%d)\n", Automation2040W::NUM_ADCS);
        return;
    }

    float voltage = board.read_adc(index);
    printf("OK %.3f\n", voltage);
}

/**
 * Handle LED command
 */
void cmd_led(const char* args) {
    args = skip_whitespace(args);

    if (*args == '\0') {
        printf("ERR LED requires button (A/B) and brightness\n");
        return;
    }

    int button = -1;
    if (*args == 'A') {
        button = Automation2040W::SWITCH_A;
    } else if (*args == 'B') {
        button = Automation2040W::SWITCH_B;
    } else {
        printf("ERR LED button must be A or B\n");
        return;
    }
    args++;

    args = skip_whitespace(args);

    if (*args == '\0' || !isdigit((unsigned char)*args)) {
        printf("ERR LED requires brightness (0-100)\n");
        return;
    }

    int brightness;
    parse_int(args, &brightness);
    if (brightness < 0) brightness = 0;
    if (brightness > 100) brightness = 100;

    board.switch_led(button, brightness);
    printf("OK\n");
}

/**
 * Handle BUTTON command
 */
void cmd_button(const char* args) {
    args = skip_whitespace(args);

    if (*args == '\0') {
        printf("ERR BUTTON requires button (A/B)\n");
        return;
    }

    int button = -1;
    if (*args == 'A') {
        button = Automation2040W::SWITCH_A;
    } else if (*args == 'B') {
        button = Automation2040W::SWITCH_B;
    } else {
        printf("ERR BUTTON must be A or B\n");
        return;
    }

    bool pressed = board.switch_pressed(button);
    printf("OK %s\n", pressed ? "PRESSED" : "RELEASED");
}

/**
 * Handle STATUS command - return all states as JSON
 */
void cmd_status() {
    printf("{\"relays\":[");
    for (int i = 0; i < Automation2040W::NUM_RELAYS; i++) {
        printf("%s%s", i > 0 ? "," : "", relay_states[i] ? "true" : "false");
    }
    printf("],\"outputs\":[");
    for (int i = 0; i < Automation2040W::NUM_OUTPUTS; i++) {
        printf("%s%.1f", i > 0 ? "," : "", output_values[i] * 100.0f);
    }
    printf("],\"inputs\":[");
    for (int i = 0; i < Automation2040W::NUM_INPUTS; i++) {
        printf("%s%s", i > 0 ? "," : "", board.read_input(i) ? "true" : "false");
    }
    printf("],\"adcs\":[");
    for (int i = 0; i < Automation2040W::NUM_ADCS; i++) {
        printf("%s%.3f", i > 0 ? "," : "", board.read_adc(i));
    }
    printf("],\"buttons\":{\"a\":%s,\"b\":%s}}\n",
           board.switch_pressed(Automation2040W::SWITCH_A) ? "true" : "false",
           board.switch_pressed(Automation2040W::SWITCH_B) ? "true" : "false");
}

/**
 * Handle RESET command
 */
void cmd_reset() {
    // Turn off all relays
    for (int i = 0; i < Automation2040W::NUM_RELAYS; i++) {
        board.relay(i, false);
        relay_states[i] = false;
    }
    // Turn off all outputs
    for (int i = 0; i < Automation2040W::NUM_OUTPUTS; i++) {
        board.output(i, 0.0f);
        output_values[i] = 0.0f;
    }
    // Turn off LEDs
    board.switch_led(Automation2040W::SWITCH_A, 0);
    board.switch_led(Automation2040W::SWITCH_B, 0);

    printf("OK\n");
}

/**
 * Handle HELP command
 */
void cmd_help() {
    printf("OK Commands:\n");
    printf("RELAY <n> <ON|OFF>   - Set relay (1-%d)\n", Automation2040W::NUM_RELAYS);
    printf("RELAY <n>?           - Query relay state\n");
    printf("OUTPUT <n> <0-100>   - Set output PWM %% (1-%d)\n", Automation2040W::NUM_OUTPUTS);
    printf("OUTPUT <n> <ON|OFF>  - Set output full on/off\n");
    printf("OUTPUT <n>?          - Query output state\n");
    printf("INPUT <n>?           - Query input (1-%d)\n", Automation2040W::NUM_INPUTS);
    printf("ADC <n>?             - Query ADC voltage (1-%d)\n", Automation2040W::NUM_ADCS);
    printf("LED <A|B> <0-100>    - Set button LED brightness\n");
    printf("BUTTON <A|B>?        - Query button state\n");
    printf("STATUS               - Get all states as JSON\n");
    printf("RESET                - Reset to safe state\n");
    printf("VERSION              - Show firmware version\n");
    printf("PING                 - Test connection\n");
}

/**
 * Main entry point
 */
int main() {
    // Initialize stdio (USB serial)
    stdio_init_all();

    // Initialize the board
    board.init();

    // Wait for USB connection
    while (!stdio_usb_connected()) {
        sleep_ms(100);
    }

    // Print startup banner
    printf("# Automation 2040 W Controller v%s (C++)\n", VERSION);
    printf("# Relays: %d, Outputs: %d, Inputs: %d, ADCs: %d\n",
           Automation2040W::NUM_RELAYS,
           Automation2040W::NUM_OUTPUTS,
           Automation2040W::NUM_INPUTS,
           Automation2040W::NUM_ADCS);
    printf("# Ready - type HELP for commands\n");

    // Main loop
    while (true) {
        int c = getchar_timeout_us(1000);  // 1ms timeout
        if (c != PICO_ERROR_TIMEOUT) {
            process_char((char)c);
        }
    }

    return 0;
}

