#!/usr/bin/env python3
"""
Automation 2040 W Host Service
===============================

System service that:
- Communicates with Automation 2040 W over USB serial
- Provides MQTT integration with auto-reconnect
- Hosts web interface from firmware-wifi
- Provides REST API for health monitoring
- Handles disconnects gracefully

Author: Generated for Pimoroni Automation 2040 W
License: MIT
"""

import json
import logging
import signal
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Add parent directory to path for lib imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import paho.mqtt.client as mqtt
from lib.automation2040w import Automation2040W
from lib.automation2040w import ConnectionError as BoardConnectionError
from flask import Flask, jsonify, request, send_from_directory

# Configuration
CONFIG_FILE = Path(__file__).parent / "config.json"
DEFAULT_CONFIG = {
    "serial": {
        "port": None,  # Auto-detect
        "baudrate": 115200,
        "reconnect_interval": 5,
    },
    "mqtt": {
        "broker": "192.168.1.1",
        "port": 1883,
        "topic_prefix": "automation",
        "client_id": "automation2040w-host",
        "username": "",
        "password": "",
        "publish_interval": 1,
        "reconnect_interval": 15,
    },
    "http": {"host": "0.0.0.0", "port": 8080},
    "logging": {"level": "INFO", "file": "/var/log/automation-service.log"},
}


class AutomationService:
    """Main service class coordinating board control, MQTT, and HTTP."""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize the service."""
        self.config = self.load_config(config_path or CONFIG_FILE)
        self.setup_logging()

        self.logger = logging.getLogger(__name__)
        self.running = False

        # Components
        self.board: Optional[Automation2040W] = None
        self.mqtt_client: Optional[mqtt.Client] = None

        # Setup Flask
        self.flask_app = Flask(__name__)

        # State tracking
        self.board_connected = False
        self.mqtt_connected = False
        self.last_status: dict[str, Any] = {}
        self.error_count = 0
        self.start_time = datetime.now()

        # Threads
        self.board_thread: Optional[threading.Thread] = None
        self.mqtt_thread: Optional[threading.Thread] = None

        # Setup Flask routes
        self.setup_flask_routes()

        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

    def load_config(self, config_path: Path) -> dict[str, Any]:
        """Load configuration from file or create default."""
        if config_path.exists():
            try:
                with open(config_path) as f:
                    loaded = json.load(f)
                # Merge with defaults
                config = DEFAULT_CONFIG.copy()
                for section, values in loaded.items():
                    if section in config:
                        config[section].update(values)
                    else:
                        config[section] = values
                return config
            except Exception as e:
                print(f"Error loading config: {e}, using defaults")

        # Save default config
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)

        return DEFAULT_CONFIG.copy()

    def setup_logging(self):
        """Setup logging configuration."""
        log_config = self.config["logging"]
        level = getattr(logging, log_config["level"].upper(), logging.INFO)

        # Create formatter
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # File handler
        try:
            log_file = Path(log_config["file"])
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
        except Exception as e:
            print(f"Could not setup file logging: {e}")
            file_handler = None

        # Setup root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        root_logger.addHandler(console_handler)
        if file_handler:
            root_logger.addHandler(file_handler)

    def setup_flask_routes(self):
        """Setup Flask HTTP routes."""
        app = self.flask_app

        @app.route("/")
        def index():
            """Serve main web interface."""
            static_dir = Path(__file__).parent.parent / "static"
            return send_from_directory(static_dir, "index.html")

        @app.route("/api/health")
        def health():
            """Health check endpoint."""
            uptime = (datetime.now() - self.start_time).total_seconds()
            mqtt_config = self.config["mqtt"]
            return jsonify(
                {
                    "status": "healthy" if self.running else "stopped",
                    "uptime_seconds": uptime,
                    "board_connected": self.board_connected,
                    "mqtt_connected": self.mqtt_connected,
                    "mqtt_broker": f"{mqtt_config['broker']}:{mqtt_config['port']}",
                    "mqtt_topic_prefix": mqtt_config["topic_prefix"],
                    "error_count": self.error_count,
                    "last_update": datetime.now().isoformat(),
                }
            )

        @app.route("/api/status")
        def status():
            """Get current board status."""
            if not self.board_connected:
                return jsonify({"error": "Board not connected"}), 503

            return jsonify(self.last_status)

        @app.route("/api/relay/<int:relay_num>", methods=["POST"])
        def control_relay(relay_num):
            """Control relay."""
            if not self.board_connected:
                self.logger.warning(f"API: Relay {relay_num} control rejected - board not connected")
                return jsonify({"error": "Board not connected"}), 503

            data = request.get_json() or {}
            state = data.get("state", True)

            try:
                self.logger.info(f"API: Setting relay {relay_num} to {state}")
                self.board.relay(relay_num, state)
                return jsonify({"status": "ok", "relay": relay_num, "state": state})
            except Exception as e:
                self.logger.error(f"Relay control error: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route("/api/output/<int:output_num>", methods=["POST"])
        def control_output(output_num):
            """Control output."""
            if not self.board_connected:
                self.logger.warning(f"API: Output {output_num} control rejected - board not connected")
                return jsonify({"error": "Board not connected"}), 503

            data = request.get_json() or {}
            value = data.get("value", 100)

            try:
                self.logger.info(f"API: Setting output {output_num} to {value}%")
                self.board.output(output_num, value)
                return jsonify({"status": "ok", "output": output_num, "value": value})
            except Exception as e:
                self.logger.error(f"Output control error: {e}")
                return jsonify({"error": str(e)}), 500

        @app.route("/api/reset", methods=["POST"])
        def reset():
            """Reset all outputs."""
            if not self.board_connected:
                self.logger.warning("API: Reset rejected - board not connected")
                return jsonify({"error": "Board not connected"}), 503

            try:
                self.logger.info("API: Resetting all outputs")
                self.board.reset()
                return jsonify({"status": "ok"})
            except Exception as e:
                self.logger.error(f"Reset error: {e}")
                return jsonify({"error": str(e)}), 500

    def connect_board(self):
        """Connect to the Automation 2040 W board."""
        serial_config = self.config["serial"]

        try:
            self.logger.info("Connecting to board...")
            self.board = Automation2040W(
                port=serial_config["port"], baudrate=serial_config["baudrate"]
            )
            self.board_connected = True
            self.logger.info(
                f"Connected to board on {self.board.port}, firmware: {self.board.version}"
            )
            return True
        except BoardConnectionError as e:
            self.logger.error(f"Board connection failed: {e}")
            self.board_connected = False
            return False

    def disconnect_board(self):
        """Disconnect from board."""
        if self.board:
            try:
                self.logger.info("Disconnecting from board...")
                self.board.disconnect()
                self.logger.info("Board disconnected")
            except Exception as e:
                self.logger.warning(f"Error during board disconnect: {e}")
            self.board = None
        self.board_connected = False

    def board_worker(self):
        """Board communication worker thread."""
        reconnect_interval = self.config["serial"]["reconnect_interval"]
        self.logger.info("Board worker thread started")

        while self.running:
            if not self.board_connected:
                self.logger.debug("Board not connected, attempting connection...")
                if self.connect_board():
                    # Setup MQTT after successful board connection
                    if not self.mqtt_connected:
                        self.logger.debug("Board connected, setting up MQTT...")
                        self.setup_mqtt()
                else:
                    self.logger.debug(f"Connection failed, retrying in {reconnect_interval}s")
                    time.sleep(reconnect_interval)
                    continue

            try:
                # Read board status
                status = self.board.status()
                self.last_status = status
                self.logger.debug(f"Board status: inputs={status.get('inputs', [])}, relays={status.get('relays', [])}")

                # Publish to MQTT if connected
                if self.mqtt_connected:
                    self.publish_status(status)
                    self.logger.debug("Status published to MQTT")

            except Exception as e:
                self.logger.error(f"Board communication error: {e}")
                self.error_count += 1
                self.logger.warning(f"Total errors: {self.error_count}, disconnecting board...")
                self.disconnect_board()
                time.sleep(reconnect_interval)
                continue

            # Wait before next poll
            time.sleep(self.config["mqtt"]["publish_interval"])

    def setup_mqtt(self):
        """Setup MQTT client and connect."""
        mqtt_config = self.config["mqtt"]

        try:
            self.mqtt_client = mqtt.Client(client_id=mqtt_config["client_id"])

            # Set username/password if provided
            if mqtt_config["username"]:
                self.mqtt_client.username_pw_set(mqtt_config["username"], mqtt_config["password"])

            # Setup callbacks
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_disconnect = self.on_mqtt_disconnect
            self.mqtt_client.on_message = self.on_mqtt_message

            # Connect
            self.logger.info(
                f"Connecting to MQTT broker {mqtt_config['broker']}:{mqtt_config['port']}"
            )
            self.mqtt_client.connect(mqtt_config["broker"], mqtt_config["port"], 60)

            # Start MQTT loop in separate thread
            self.mqtt_client.loop_start()

        except Exception as e:
            self.logger.error(f"MQTT setup failed: {e}")
            self.mqtt_connected = False

    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connection callback."""
        if rc == 0:
            self.logger.info("Connected to MQTT broker")
            self.mqtt_connected = True

            # Subscribe to command topics
            topic_prefix = self.config["mqtt"]["topic_prefix"]
            client.subscribe(f"{topic_prefix}/relay/+")
            client.subscribe(f"{topic_prefix}/output/+")
            client.subscribe(f"{topic_prefix}/command")

            self.logger.info(f"Subscribed to {topic_prefix}/*")
        else:
            self.logger.error(f"MQTT connection failed with code {rc}")
            self.mqtt_connected = False

    def on_mqtt_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback."""
        self.logger.warning(f"Disconnected from MQTT broker (rc={rc})")
        self.mqtt_connected = False

    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback."""
        try:
            topic = msg.topic
            payload = msg.payload.decode().strip().upper()
            topic_prefix = self.config["mqtt"]["topic_prefix"]

            self.logger.debug(f"MQTT: {topic} = {payload}")

            if not self.board_connected:
                self.logger.warning("Received MQTT command but board not connected")
                return

            # Relay control
            if topic.startswith(f"{topic_prefix}/relay/"):
                relay_num = int(topic.split("/")[-1])
                state = payload in ("ON", "1", "TRUE")
                self.board.relay(relay_num, state)
                self.logger.info(f"MQTT: Set relay {relay_num} to {state}")

            # Output control
            elif topic.startswith(f"{topic_prefix}/output/"):
                output_num = int(topic.split("/")[-1])
                if payload in ("ON", "TRUE"):
                    value = 100
                elif payload in ("OFF", "FALSE"):
                    value = 0
                else:
                    value = int(payload)
                self.board.output(output_num, value)
                self.logger.info(f"MQTT: Set output {output_num} to {value}")

            # Commands
            elif topic == f"{topic_prefix}/command":
                if payload == "RESET":
                    self.board.reset()
                    self.logger.info("MQTT: Reset command executed")
                elif payload == "STATUS":
                    status = self.board.status()
                    self.publish_status(status)
                    self.logger.info("MQTT: Status command executed")

        except Exception as e:
            self.logger.error(f"Error handling MQTT message: {e}")

    def publish_status(self, status: dict[str, Any]):
        """Publish status to MQTT."""
        if not self.mqtt_connected or not self.mqtt_client:
            self.logger.debug("MQTT not connected, skipping publish")
            return

        try:
            topic = f"{self.config['mqtt']['topic_prefix']}/status"
            self.mqtt_client.publish(topic, json.dumps(status))
        except Exception as e:
            self.logger.error(f"MQTT publish error: {e}")

    def run_flask(self):
        """Run Flask web server."""
        http_config = self.config["http"]
        self.logger.info(f"Starting HTTP server on {http_config['host']}:{http_config['port']}")

        # Disable Flask's default logger in production
        log = logging.getLogger("werkzeug")
        log.setLevel(logging.WARNING)

        self.flask_app.run(
            host=http_config["host"], port=http_config["port"], debug=False, threaded=True
        )

    def start(self):
        """Start the service."""
        self.logger.info("=" * 60)
        self.logger.info("Starting Automation 2040 W Host Service")
        self.logger.info("=" * 60)
        self.logger.info(f"Serial port: {self.config['serial']['port'] or 'auto-detect'}")
        self.logger.info(f"MQTT broker: {self.config['mqtt']['broker']}:{self.config['mqtt']['port']}")
        self.logger.info(f"HTTP server: {self.config['http']['host']}:{self.config['http']['port']}")
        self.logger.info("=" * 60)
        self.running = True

        # Start board worker thread
        self.logger.info("Starting board worker thread...")
        self.board_thread = threading.Thread(target=self.board_worker, daemon=True)
        self.board_thread.start()

        # Run Flask in main thread (blocks)
        self.run_flask()

    def stop(self):
        """Stop the service."""
        self.logger.info("=" * 60)
        self.logger.info("Stopping Automation Service")
        self.logger.info("=" * 60)
        self.running = False

        # Stop MQTT
        if self.mqtt_client:
            self.logger.info("Stopping MQTT client...")
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
            self.logger.info("MQTT client stopped")

        # Disconnect board
        self.disconnect_board()

        # Wait for threads
        if self.board_thread and self.board_thread.is_alive():
            self.logger.info("Waiting for board thread to stop...")
            self.board_thread.join(timeout=5)
            self.logger.info("Board thread stopped")

        self.logger.info("Service stopped successfully")

    def signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        self.logger.info(f"Received signal {signum}")
        self.stop()
        sys.exit(0)


def main():
    """Main entry point."""
    service = AutomationService()
    service.start()


if __name__ == "__main__":
    main()
