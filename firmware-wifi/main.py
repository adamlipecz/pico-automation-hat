"""
Automation 2040 W WiFi Firmware
===============================

Features:
- WiFi auto-connect
- MQTT client for IoT integration
- HTTP settings interface
- USB serial still works for debugging

MQTT Topics:
- automation/status      - JSON with all I/O states (published periodically)
- automation/relay/N     - Set relay N (1-3): "ON" or "OFF"
- automation/output/N    - Set output N (1-3): 0-100
- automation/command     - General commands: "RESET", "STATUS"

HTTP Endpoints:
- GET  /           - Settings page
- GET  /api/status - JSON status
- POST /api/config - Update settings
"""

import json
import time
import network
import machine
from machine import Pin

# Import Pimoroni automation library
from automation import Automation2040W, SWITCH_A, SWITCH_B

# Try to import config, use defaults if not found
try:
    import config
except ImportError:
    # Create default config
    class config:
        WIFI_SSID = "HoneyPie"
        WIFI_PASSWORD = "RepaRetekMogyoro_742"
        MQTT_BROKER = "192.168.1.28"
        MQTT_PORT = 1883
        MQTT_TOPIC = "automation"
        MQTT_CLIENT_ID = "automation2040w"
        MQTT_USER = ""
        MQTT_PASSWORD = ""
        HTTP_PORT = 80
        MQTT_PUBLISH_INTERVAL = 1000
        INPUT_POLL_INTERVAL = 100

# Try to import MQTT library
try:
    from umqtt.simple import MQTTClient
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("Warning: umqtt not available, MQTT disabled")

VERSION = "1.0.0"


class AutomationController:
    """Main controller with WiFi, MQTT, and HTTP support."""
    
    def __init__(self):
        self.board = Automation2040W()
        self.wlan = network.WLAN(network.STA_IF)
        self.mqtt = None
        self.mqtt_connected = False
        
        # State tracking
        self.relay_states = [False] * self.board.NUM_RELAYS
        self.output_values = [0.0] * self.board.NUM_OUTPUTS
        self.last_inputs = [False] * self.board.NUM_INPUTS
        
        # Timing
        self.last_mqtt_publish = 0
        self.last_input_poll = 0
        self.last_mqtt_retry = 0
        
        # Load saved config if exists
        self.load_config()
    
    def load_config(self):
        """Load config from file if it exists."""
        try:
            with open('config.json', 'r') as f:
                saved = json.load(f)
                config.WIFI_SSID = saved.get('wifi_ssid', config.WIFI_SSID)
                config.WIFI_PASSWORD = saved.get('wifi_password', config.WIFI_PASSWORD)
                config.MQTT_BROKER = saved.get('mqtt_broker', config.MQTT_BROKER)
                config.MQTT_PORT = saved.get('mqtt_port', config.MQTT_PORT)
                config.MQTT_TOPIC = saved.get('mqtt_topic', config.MQTT_TOPIC)
                print("Loaded saved config")
        except:
            pass
    
    def save_config(self):
        """Save current config to file."""
        try:
            with open('config.json', 'w') as f:
                json.dump({
                    'wifi_ssid': config.WIFI_SSID,
                    'wifi_password': config.WIFI_PASSWORD,
                    'mqtt_broker': config.MQTT_BROKER,
                    'mqtt_port': config.MQTT_PORT,
                    'mqtt_topic': config.MQTT_TOPIC,
                }, f)
            print("Config saved")
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def connect_wifi(self):
        """Connect to WiFi network."""
        print(f"Connecting to WiFi: {config.WIFI_SSID}")
        self.board.switch_led(SWITCH_A, 50)  # LED A = connecting
        
        self.wlan.active(True)
        self.wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
        
        # Wait for connection (max 20 seconds)
        for i in range(40):
            if self.wlan.isconnected():
                break
            time.sleep(0.5)
            # Blink LED
            self.board.switch_led(SWITCH_A, 50 if i % 2 == 0 else 0)
        
        if self.wlan.isconnected():
            ip = self.wlan.ifconfig()[0]
            print(f"Connected! IP: {ip}")
            self.board.switch_led(SWITCH_A, 100)  # LED A = connected
            return True
        else:
            print("WiFi connection failed")
            self.board.switch_led(SWITCH_A, 0)
            return False
    
    def reconnect_mqtt(self):
        """Disconnect and reconnect to MQTT with current config."""
        if self.mqtt:
            try:
                self.mqtt.disconnect()
            except:
                pass
            self.mqtt = None
        self.mqtt_connected = False
        return self.connect_mqtt()
    
    def connect_mqtt(self):
        """Connect to MQTT broker."""
        if not MQTT_AVAILABLE:
            return False
        
        print(f"Connecting to MQTT: {config.MQTT_BROKER}:{config.MQTT_PORT}")
        self.board.switch_led(SWITCH_B, 50)  # LED B = connecting
        
        try:
            self.mqtt = MQTTClient(
                config.MQTT_CLIENT_ID,
                config.MQTT_BROKER,
                port=config.MQTT_PORT,
                user=config.MQTT_USER if config.MQTT_USER else None,
                password=config.MQTT_PASSWORD if config.MQTT_PASSWORD else None
            )
            self.mqtt.set_callback(self.mqtt_callback)
            self.mqtt.connect()
            
            # Subscribe to command topics
            topic_base = config.MQTT_TOPIC
            self.mqtt.subscribe(f"{topic_base}/relay/+")
            self.mqtt.subscribe(f"{topic_base}/output/+")
            self.mqtt.subscribe(f"{topic_base}/command")
            
            print("MQTT connected!")
            self.board.switch_led(SWITCH_B, 100)  # LED B = connected
            self.mqtt_connected = True
            return True
            
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            self.board.switch_led(SWITCH_B, 0)
            self.mqtt_connected = False
            return False
    
    def mqtt_callback(self, topic, msg):
        """Handle incoming MQTT messages."""
        topic = topic.decode()
        msg = msg.decode().upper().strip()
        topic_base = config.MQTT_TOPIC
        
        print(f"MQTT: {topic} = {msg}")
        
        try:
            if topic.startswith(f"{topic_base}/relay/"):
                # Relay control: automation/relay/1 = ON
                index = int(topic.split('/')[-1]) - 1
                if 0 <= index < self.board.NUM_RELAYS:
                    state = msg in ("ON", "1", "TRUE")
                    self.board.relay(index, state)
                    self.relay_states[index] = state
                    
            elif topic.startswith(f"{topic_base}/output/"):
                # Output control: automation/output/1 = 50
                index = int(topic.split('/')[-1]) - 1
                if 0 <= index < self.board.NUM_OUTPUTS:
                    if msg in ("ON", "TRUE"):
                        value = 1.0
                    elif msg in ("OFF", "FALSE"):
                        value = 0.0
                    else:
                        value = float(msg) / 100.0
                    value = max(0.0, min(1.0, value))
                    self.board.output(index, value)
                    self.output_values[index] = value
                    
            elif topic == f"{topic_base}/command":
                if msg == "RESET":
                    self.reset()
                elif msg == "STATUS":
                    self.publish_status()
                    
        except Exception as e:
            print(f"Error handling MQTT message: {e}")
    
    def publish_status(self):
        """Publish current status to MQTT."""
        if not self.mqtt_connected:
            return
        
        try:
            status = {
                "relays": self.relay_states,
                "outputs": [int(v * 100) for v in self.output_values],
                "inputs": [self.board.read_input(i) for i in range(self.board.NUM_INPUTS)],
                "adcs": [round(self.board.read_adc(i), 3) for i in range(self.board.NUM_ADCS)],
                "ip": self.wlan.ifconfig()[0] if self.wlan.isconnected() else None
            }
            
            self.mqtt.publish(
                f"{config.MQTT_TOPIC}/status",
                json.dumps(status)
            )
        except Exception as e:
            print(f"MQTT publish failed: {e}")
            self.mqtt_connected = False
    
    def check_input_changes(self):
        """Check for input changes and publish them."""
        for i in range(self.board.NUM_INPUTS):
            current = self.board.read_input(i)
            if current != self.last_inputs[i]:
                self.last_inputs[i] = current
                if self.mqtt_connected:
                    try:
                        self.mqtt.publish(
                            f"{config.MQTT_TOPIC}/input/{i+1}",
                            "HIGH" if current else "LOW"
                        )
                    except:
                        pass
    
    def reset(self):
        """Reset all outputs to safe state."""
        for i in range(self.board.NUM_RELAYS):
            self.board.relay(i, False)
            self.relay_states[i] = False
        for i in range(self.board.NUM_OUTPUTS):
            self.board.output(i, 0.0)
            self.output_values[i] = 0.0
    
    def get_status_json(self):
        """Get current status as JSON string."""
        return json.dumps({
            "version": VERSION,
            "wifi_connected": self.wlan.isconnected(),
            "mqtt_connected": self.mqtt_connected,
            "ip": self.wlan.ifconfig()[0] if self.wlan.isconnected() else None,
            "relays": self.relay_states,
            "outputs": [int(v * 100) for v in self.output_values],
            "inputs": [self.board.read_input(i) for i in range(self.board.NUM_INPUTS)],
            "adcs": [round(self.board.read_adc(i), 3) for i in range(self.board.NUM_ADCS)],
            "config": {
                "wifi_ssid": config.WIFI_SSID,
                "mqtt_broker": config.MQTT_BROKER,
                "mqtt_port": config.MQTT_PORT,
                "mqtt_topic": config.MQTT_TOPIC
            }
        })
    
    def run(self):
        """Main loop."""
        print(f"Automation 2040 W WiFi v{VERSION}")
        
        # Connect to WiFi
        if not self.connect_wifi():
            print("Running in offline mode")
        
        # Connect to MQTT
        if self.wlan.isconnected():
            self.connect_mqtt()
        
        # Start HTTP server
        from http_server import start_http_server
        http_socket = start_http_server(self, config.HTTP_PORT)
        
        print("Ready!")
        if self.wlan.isconnected():
            print(f"Web interface: http://{self.wlan.ifconfig()[0]}/")
        
        # Main loop
        while True:
            now = time.ticks_ms()
            
            # Check MQTT messages
            if self.mqtt_connected:
                try:
                    self.mqtt.check_msg()
                except:
                    self.mqtt_connected = False
            
            # Auto-reconnect MQTT every 15 seconds if disconnected
            if not self.mqtt_connected and self.wlan.isconnected():
                if time.ticks_diff(now, self.last_mqtt_retry) >= 15000:
                    self.last_mqtt_retry = now
                    print("MQTT disconnected, attempting reconnect...")
                    self.connect_mqtt()
            
            # Periodic MQTT status publish
            if time.ticks_diff(now, self.last_mqtt_publish) >= config.MQTT_PUBLISH_INTERVAL:
                self.last_mqtt_publish = now
                self.publish_status()
            
            # Check input changes
            if time.ticks_diff(now, self.last_input_poll) >= config.INPUT_POLL_INTERVAL:
                self.last_input_poll = now
                self.check_input_changes()
            
            # Handle HTTP requests (non-blocking)
            from http_server import handle_http_request
            handle_http_request(http_socket, self)
            
            # Small delay to prevent tight loop
            time.sleep_ms(10)


# Entry point
if __name__ == "__main__":
    controller = AutomationController()
    controller.run()

