"""
Configuration for Automation 2040 W WiFi Firmware
=================================================

Edit these settings or use the web interface at http://<device-ip>/
"""

# WiFi Settings
WIFI_SSID = "HoneyPie"
WIFI_PASSWORD = "RepaRetekMogyoro_742"

# MQTT Settings
MQTT_BROKER = "192.168.1.28"
MQTT_PORT = 1883
MQTT_TOPIC = "automation"
MQTT_CLIENT_ID = "automation2040w"

# Optional MQTT authentication (leave empty if not used)
MQTT_USER = ""
MQTT_PASSWORD = ""

# HTTP Server
HTTP_PORT = 80

# Update intervals (milliseconds)
MQTT_PUBLISH_INTERVAL = 1000  # How often to publish status
INPUT_POLL_INTERVAL = 100     # How often to check inputs for changes

