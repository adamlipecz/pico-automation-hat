"""
Minimal HTTP Server for Automation 2040 W
==========================================

Provides a settings web interface and REST API.
"""

import socket
import json

# HTML template for settings page
SETTINGS_PAGE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automation 2040 W</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; background: #0f1419; color: #e7e9ea; min-height: 100vh; padding: 20px; }
        .container { max-width: 600px; margin: 0 auto; }
        h1 { font-size: 24px; margin-bottom: 8px; color: #f97316; }
        .subtitle { color: #71767b; margin-bottom: 24px; }
        .status { display: inline-flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 20px; font-size: 14px; margin-bottom: 12px; margin-right: 8px; }
        .status.ok { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
        .status.err { background: rgba(239, 68, 68, 0.15); color: #ef4444; }
        .card { background: #1a1f26; border: 1px solid #2f3336; border-radius: 12px; padding: 20px; margin-bottom: 16px; }
        .card h2 { font-size: 16px; margin-bottom: 16px; color: #e7e9ea; }
        .row-label { font-size: 12px; color: #71767b; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
        .io-row { display: flex; gap: 12px; margin-bottom: 16px; }
        .io-row:last-child { margin-bottom: 0; }
        .io-item { flex: 1; background: #0f1419; border: 1px solid #2f3336; border-radius: 8px; padding: 12px; text-align: center; }
        .io-item.clickable { cursor: pointer; transition: all 0.15s; }
        .io-item.clickable:hover { border-color: #f97316; background: #1a1f26; }
        .io-item.clickable:active { transform: scale(0.97); }
        .io-label { font-size: 11px; color: #71767b; margin-bottom: 4px; }
        .io-value { font-size: 20px; font-weight: 700; }
        .io-value.on { color: #22c55e; }
        .io-value.off { color: #555; }
        .io-value.volt { color: #a855f7; }
        .field { margin-bottom: 16px; }
        label { display: block; font-size: 14px; color: #71767b; margin-bottom: 6px; }
        input { width: 100%%; padding: 10px 12px; background: #0f1419; border: 1px solid #2f3336; border-radius: 8px; color: #e7e9ea; font-size: 14px; }
        input:focus { outline: none; border-color: #f97316; }
        .row { display: flex; gap: 12px; }
        .row .field { flex: 1; }
        button { width: 100%%; padding: 12px; background: #f97316; color: white; border: none; border-radius: 8px; font-size: 16px; font-weight: 600; cursor: pointer; margin-top: 8px; }
        button:hover { background: #ea580c; }
        button.secondary { background: transparent; border: 1px solid #2f3336; color: #71767b; }
        .update-indicator { font-size: 11px; color: #71767b; text-align: right; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Automation 2040 W</h1>
        <p class="subtitle">Control Panel</p>
        
        <div class="status %s"><span>WiFi: %s</span></div>
        <div class="status %s"><span>MQTT: %s</span></div>
        
        <div class="card">
            <h2>I/O Status</h2>
            
            <div class="row-label">Relays</div>
            <div class="io-row" id="relays">%s</div>
            
            <div class="row-label">Outputs</div>
            <div class="io-row" id="outputs">%s</div>
            
            <div class="row-label">Digital Inputs</div>
            <div class="io-row" id="inputs">%s</div>
            
            <div class="row-label">Analog Inputs</div>
            <div class="io-row" id="adcs">%s</div>
            
            <div class="update-indicator">Auto-refresh: <span id="countdown">1</span>s</div>
        </div>
        
        <form method="POST" action="/api/config">
            <div class="card">
                <h2>WiFi Settings</h2>
                <div class="field">
                    <label>SSID</label>
                    <input type="text" name="wifi_ssid" value="%s">
                </div>
                <div class="field">
                    <label>Password</label>
                    <input type="password" name="wifi_password" placeholder="(unchanged)">
                </div>
            </div>
            
            <div class="card">
                <h2>MQTT Settings</h2>
                <div class="row">
                    <div class="field">
                        <label>Broker Address</label>
                        <input type="text" name="mqtt_broker" value="%s">
                    </div>
                    <div class="field" style="max-width: 100px;">
                        <label>Port</label>
                        <input type="number" name="mqtt_port" value="%s">
                    </div>
                </div>
                <div class="field">
                    <label>Topic Prefix</label>
                    <input type="text" name="mqtt_topic" value="%s">
                </div>
            </div>
            
            <button type="submit">Save Settings</button>
        </form>
        
        <button class="secondary" onclick="resetAll()" style="margin-top: 12px;">
            Reset All Outputs
        </button>
    </div>
    
    <script>
        function toggleRelay(n) {
            fetch('/api/relay/' + n + '/toggle', {method: 'POST'})
                .then(function() { refresh(); });
        }
        
        function toggleOutput(n) {
            fetch('/api/output/' + n + '/toggle', {method: 'POST'})
                .then(function() { refresh(); });
        }
        
        function resetAll() {
            fetch('/api/reset', {method: 'POST'}).then(function() { refresh(); });
        }
        
        function refresh() {
            fetch('/api/status').then(function(r) { return r.json(); }).then(function(data) {
                // Update relays
                for (var i = 0; i < data.relays.length; i++) {
                    var el = document.getElementById('relay-' + (i+1));
                    if (el) {
                        el.className = 'io-value ' + (data.relays[i] ? 'on' : 'off');
                        el.textContent = data.relays[i] ? 'ON' : 'OFF';
                    }
                }
                // Update outputs
                for (var i = 0; i < data.outputs.length; i++) {
                    var el = document.getElementById('output-' + (i+1));
                    if (el) {
                        var v = data.outputs[i];
                        el.className = 'io-value ' + (v > 0 ? 'on' : 'off');
                        el.textContent = v > 0 ? 'ON' : 'OFF';
                    }
                }
                // Update inputs
                for (var i = 0; i < data.inputs.length; i++) {
                    var el = document.getElementById('input-' + (i+1));
                    if (el) {
                        el.className = 'io-value ' + (data.inputs[i] ? 'on' : 'off');
                        el.textContent = data.inputs[i] ? 'HIGH' : 'LOW';
                    }
                }
                // Update ADCs
                for (var i = 0; i < data.adcs.length; i++) {
                    var el = document.getElementById('adc-' + (i+1));
                    if (el) {
                        el.textContent = data.adcs[i].toFixed(1) + 'V';
                    }
                }
            });
        }
        
        setInterval(refresh, 1000);
    </script>
</body>
</html>"""


def start_http_server(controller, port=80):
    """Start the HTTP server socket."""
    addr = socket.getaddrinfo('0.0.0.0', port)[0][-1]
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)
    s.setblocking(False)
    print(f"HTTP server on port {port}")
    return s


def handle_http_request(server_socket, controller):
    """Handle incoming HTTP requests (non-blocking)."""
    try:
        cl, addr = server_socket.accept()
    except OSError:
        return  # No connection waiting
    
    try:
        cl.settimeout(2.0)
        request = cl.recv(2048).decode()
        
        # Parse request
        lines = request.split('\r\n')
        if not lines or len(lines) < 1:
            cl.close()
            return
        
        # Parse first line
        first_line = lines[0].split(' ')
        if len(first_line) < 2:
            cl.close()
            return
        
        method, path = first_line[0], first_line[1]
        print(f"HTTP: {method} {path}")
        
        # Get body for POST requests
        body = ""
        if method == "POST":
            body_start = request.find('\r\n\r\n')
            if body_start > 0:
                body = request[body_start + 4:].strip()
            print(f"POST body: '{body}'")
        
        # Route request
        if path == "/" or path == "/index.html":
            response = handle_index(controller)
            content_type = "text/html"
        elif path == "/api/status":
            response = controller.get_status_json()
            content_type = "application/json"
        elif path == "/api/config" and method == "POST":
            response = handle_config_update(controller, body)
            content_type = "text/html"
        elif path == "/api/reset" and method == "POST":
            controller.reset()
            response = '{"status":"ok"}'
            content_type = "application/json"
        elif path.startswith("/api/relay/") and method == "POST":
            if path.endswith("/toggle"):
                response = handle_relay_toggle(controller, path)
            else:
                response = handle_relay_control(controller, path, body)
            content_type = "application/json"
        elif path.startswith("/api/output/") and method == "POST":
            if path.endswith("/toggle"):
                response = handle_output_toggle(controller, path)
            else:
                response = handle_output_control(controller, path, body)
            content_type = "application/json"
        elif path == "/favicon.ico":
            cl.send(b"HTTP/1.0 204 No Content\r\n\r\n")
            cl.close()
            return
        else:
            cl.send(b"HTTP/1.0 404 Not Found\r\n\r\nNot Found")
            cl.close()
            return
        
        # Send response in chunks (Pico can't send large data at once)
        data = response.encode()
        header = f"HTTP/1.0 200 OK\r\nContent-Type: {content_type}\r\nContent-Length: {len(data)}\r\n\r\n".encode()
        cl.send(header)
        
        # Send in 512-byte chunks
        for i in range(0, len(data), 512):
            cl.send(data[i:i+512])
        
    except Exception as e:
        import sys
        sys.print_exception(e)
    finally:
        try:
            cl.close()
        except:
            pass


def handle_index(controller):
    """Generate the settings page."""
    import config
    
    # Build relay items (clickable)
    relay_html = ""
    for i, state in enumerate(controller.relay_states):
        cls = "on" if state else "off"
        val = "ON" if state else "OFF"
        relay_html += '<div class="io-item clickable" onclick="toggleRelay(%d)"><div class="io-label">R%d</div><div class="io-value %s" id="relay-%d">%s</div></div>' % (i+1, i+1, cls, i+1, val)
    
    # Build output items (clickable)
    output_html = ""
    for i, value in enumerate(controller.output_values):
        is_on = value > 0
        cls = "on" if is_on else "off"
        val = "ON" if is_on else "OFF"
        output_html += '<div class="io-item clickable" onclick="toggleOutput(%d)"><div class="io-label">O%d</div><div class="io-value %s" id="output-%d">%s</div></div>' % (i+1, i+1, cls, i+1, val)
    
    # Build input items (read-only)
    input_html = ""
    for i in range(controller.board.NUM_INPUTS):
        state = controller.board.read_input(i)
        cls = "on" if state else "off"
        val = "HIGH" if state else "LOW"
        input_html += '<div class="io-item"><div class="io-label">I%d</div><div class="io-value %s" id="input-%d">%s</div></div>' % (i+1, cls, i+1, val)
    
    # Build ADC items (read-only)
    adc_html = ""
    for i in range(controller.board.NUM_ADCS):
        voltage = controller.board.read_adc(i)
        adc_html += '<div class="io-item"><div class="io-label">A%d</div><div class="io-value volt" id="adc-%d">%.1fV</div></div>' % (i+1, i+1, voltage)
    
    # WiFi status
    wifi_connected = controller.wlan.isconnected()
    wifi_status = controller.wlan.ifconfig()[0] if wifi_connected else "Disconnected"
    wifi_class = "ok" if wifi_connected else "err"
    
    # MQTT status
    mqtt_status = "Connected" if controller.mqtt_connected else "Disconnected"
    mqtt_class = "ok" if controller.mqtt_connected else "err"
    
    return SETTINGS_PAGE % (
        wifi_class, wifi_status,
        mqtt_class, mqtt_status,
        relay_html,
        output_html,
        input_html,
        adc_html,
        config.WIFI_SSID,
        config.MQTT_BROKER,
        config.MQTT_PORT,
        config.MQTT_TOPIC
    )


def handle_config_update(controller, body):
    """Handle config form submission."""
    import config
    
    # Parse form data
    params = {}
    for pair in body.split('&'):
        if '=' in pair:
            key, value = pair.split('=', 1)
            value = value.replace('+', ' ')
            value = value.replace('%2F', '/')
            value = value.replace('%3A', ':')
            value = value.replace('%40', '@')
            params[key] = value
    
    changed = False
    
    if 'wifi_ssid' in params and params['wifi_ssid']:
        config.WIFI_SSID = params['wifi_ssid']
        changed = True
    
    if 'wifi_password' in params and params['wifi_password']:
        config.WIFI_PASSWORD = params['wifi_password']
        changed = True
    
    if 'mqtt_broker' in params and params['mqtt_broker']:
        config.MQTT_BROKER = params['mqtt_broker']
        changed = True
    
    if 'mqtt_port' in params:
        try:
            config.MQTT_PORT = int(params['mqtt_port'])
            changed = True
        except:
            pass
    
    if 'mqtt_topic' in params and params['mqtt_topic']:
        config.MQTT_TOPIC = params['mqtt_topic']
        changed = True
    
    if changed:
        controller.save_config()
        return """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta http-equiv="refresh" content="3;url=/">
    <style>
        body { font-family: sans-serif; background: #0f1419; color: #e7e9ea; 
               display: flex; align-items: center; justify-content: center; 
               min-height: 100vh; text-align: center; }
        .msg { background: rgba(34, 197, 94, 0.15); color: #22c55e; 
               padding: 20px; border-radius: 12px; }
    </style>
</head>
<body>
    <div class="msg">
        <h2>Settings Saved!</h2>
        <p>Redirecting in 3 seconds...</p>
    </div>
</body>
</html>"""
    
    return handle_index(controller)


def handle_relay_toggle(controller, path):
    """Handle relay toggle API - simple toggle without body."""
    try:
        # Path is /api/relay/N/toggle
        parts = path.split('/')
        index = int(parts[3]) - 1
        
        if 0 <= index < controller.board.NUM_RELAYS:
            new_state = not controller.relay_states[index]
            controller.board.relay(index, new_state)
            controller.relay_states[index] = new_state
            print(f"Relay {index+1} toggled to {new_state}")
            return json.dumps({"status": "ok", "relay": index + 1, "state": new_state})
    except Exception as e:
        print(f"Relay toggle error: {e}")
    return json.dumps({"status": "error"})


def handle_output_toggle(controller, path):
    """Handle output toggle API - simple toggle without body."""
    try:
        # Path is /api/output/N/toggle
        parts = path.split('/')
        index = int(parts[3]) - 1
        
        if 0 <= index < controller.board.NUM_OUTPUTS:
            new_value = 0.0 if controller.output_values[index] > 0 else 1.0
            controller.board.output(index, new_value)
            controller.output_values[index] = new_value
            print(f"Output {index+1} toggled to {new_value}")
            return json.dumps({"status": "ok", "output": index + 1, "value": int(new_value * 100)})
    except Exception as e:
        print(f"Output toggle error: {e}")
    return json.dumps({"status": "error"})


def handle_relay_control(controller, path, body):
    """Handle relay control API with explicit state."""
    print(f"Relay API: path={path} body={body}")
    try:
        index = int(path.split('/')[-1]) - 1
        data = json.loads(body) if body else {}
        state = data.get('state', True)
        
        if 0 <= index < controller.board.NUM_RELAYS:
            controller.board.relay(index, state)
            controller.relay_states[index] = state
            print(f"Relay {index+1} set to {state}")
            return json.dumps({"status": "ok", "relay": index + 1, "state": state})
    except Exception as e:
        print(f"Relay error: {e}")
    return json.dumps({"status": "error"})


def handle_output_control(controller, path, body):
    """Handle output control API with explicit value."""
    print(f"Output API: path={path} body={body}")
    try:
        index = int(path.split('/')[-1]) - 1
        data = json.loads(body) if body else {}
        value = data.get('value', 100) / 100.0
        value = max(0.0, min(1.0, value))
        
        if 0 <= index < controller.board.NUM_OUTPUTS:
            controller.board.output(index, value)
            controller.output_values[index] = value
            print(f"Output {index+1} set to {value}")
            return json.dumps({"status": "ok", "output": index + 1, "value": int(value * 100)})
    except Exception as e:
        print(f"Output error: {e}")
    return json.dumps({"status": "error"})
