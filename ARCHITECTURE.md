# Architecture Comparison

## Web Interface: Gateway vs Automation-Firmware-WiFi

### Summary

**YES** - Both use the **same web interface** ([automation-firmware-wifi/index.html](automation-firmware-wifi/index.html))

The HTML file is self-contained with inline CSS and JavaScript, and uses the same REST API endpoints in both deployments.

---

## Deployment 1: USB Serial + Automation Gateway (Raspberry Pi)

```
┌─────────────────────────────────────────────────┐
│         Raspberry Pi 5 (Gateway)                │
│  ┌───────────────────────────────────────────┐  │
│  │  automation_service.py                    │  │
│  │  ├─ Flask HTTP Server (:8080)             │  │
│  │  │  ├─ Serves: automation-firmware-wifi/index.html   │  │
│  │  │  └─ REST API endpoints                 │  │
│  │  ├─ MQTT Client                           │  │
│  │  │  ├─ Publishes: automation/status       │  │
│  │  │  └─ Subscribes: automation/relay/+     │  │
│  │  └─ Serial Communication                  │  │
│  │     └─ Controls board over USB            │  │
│  └───────────────────────────────────────────┘  │
└──────────────────┬──────────────────────────────┘
                   │ USB Serial (115200 baud)
                   ↓
        ┌──────────────────────┐
        │ Automation 2040 W    │
        │ automation-firmware-serial      │
        │  - Text protocol     │
        │  - I/O control       │
        └──────────────────────┘
```

**Backend:** Flask (Python) on Raspberry Pi
**Web UI:** Same index.html
**MQTT:** Handled by Raspberry Pi
**Control:** USB serial commands

---

## Deployment 2: WiFi Standalone

```
┌────────────────────────────────────────┐
│   Automation 2040 W (automation-firmware-wifi)    │
│  ┌──────────────────────────────────┐  │
│  │  main.py                         │  │
│  │  ├─ HTTP Server (MicroPython)    │  │
│  │  │  ├─ Serves: index.html        │  │
│  │  │  └─ REST API endpoints        │  │
│  │  ├─ MQTT Client                  │  │
│  │  │  ├─ Publishes: automation/*   │  │
│  │  │  └─ Subscribes: automation/*  │  │
│  │  └─ Direct I/O Control           │  │
│  │     └─ Controls board locally    │  │
│  └──────────────────────────────────┘  │
│  WiFi Connected                        │
└────────────────────────────────────────┘
```

**Backend:** MicroPython HTTP server on Pico
**Web UI:** Same index.html (embedded in http_server.py)
**MQTT:** Handled by MicroPython
**Control:** Direct I/O access

---

## REST API Comparison

Both deployments provide identical API endpoints:

| Endpoint | Method | Description | Host | WiFi |
|----------|--------|-------------|------|------|
| `/` | GET | Web interface | ✅ | ✅ |
| `/api/health` | GET | Health check | ✅ | ❌* |
| `/api/status` | GET | Get I/O states | ✅ | ✅ |
| `/api/relay/:n` | POST | Control relay | ✅ | ✅ |
| `/api/output/:n` | POST | Control output | ✅ | ✅ |
| `/api/reset` | POST | Reset outputs | ✅ | ✅ |

*WiFi firmware doesn't have `/api/health` - the web UI only uses it for connection status

---

## Web Interface Features

The single [index.html](automation-firmware-wifi/index.html) file provides:

- **Real-time I/O display**
  - Relays (clickable to toggle)
  - Outputs (clickable to toggle)
  - Digital inputs (read-only)
  - Analog inputs (read-only)

- **Connection status**
  - Board connection (USB vs always connected)
  - MQTT connection status

- **Auto-refresh**
  - Updates every 1 second
  - Visual countdown timer

- **Control actions**
  - Toggle relays on/off
  - Toggle outputs on/off
  - Reset all outputs button

---

## Key Differences

### Host Deployment Advantages

1. **More reliable MQTT**
   - Better reconnection handling
   - More memory for queuing
   - systemd restart on crash

2. **Better logging**
   - journalctl integration
   - Structured logging
   - Log rotation

3. **Health monitoring**
   - `/api/health` endpoint
   - Uptime tracking
   - Error counting

4. **System integration**
   - systemd service
   - Auto-start on boot
   - Process management

5. **More powerful**
   - Flask (full Python web framework)
   - Better concurrent request handling
   - Can add more features easily

### WiFi Standalone Advantages

1. **Simpler deployment**
   - No gateway computer needed
   - Single device to manage
   - Lower total cost

2. **Lower latency**
   - Direct I/O access
   - No USB serial overhead
   - Faster response times

3. **Standalone operation**
   - Works without gateway
   - Portable
   - Self-contained

---

## When to Use Each

### Use USB Serial + Automation Gateway when:
- You need reliable MQTT integration
- You want centralized logging and monitoring
- You're deploying in production
- You already have a Raspberry Pi available
- You need advanced features (scheduling, database, etc.)

### Use WiFi Standalone when:
- You need a simple, standalone solution
- No gateway computer is available
- Cost is a primary concern
- The device needs to be portable
- Basic MQTT and web control is sufficient

---

## File Locations

### Shared Web Interface
- Source: [automation-firmware-wifi/index.html](automation-firmware-wifi/index.html)
- Used by: Both deployments
- Self-contained: All CSS and JavaScript inline

-### Automation Gateway Service
- Service: [automation-gateway/service/automation_service.py](automation-gateway/service/automation_service.py)
- Serves from: `automation-firmware-wifi/index.html` (absolute path)
- Port: 8080 (configurable)

### WiFi Firmware
- Service: [automation-firmware-wifi/http_server.py](automation-firmware-wifi/http_server.py)
- Embeds: HTML template in Python string
- Port: 80 (default HTTP)

---

## Summary

**Same user experience, different backends!**

The web interface is identical in both deployments. The choice between them depends on your infrastructure, reliability requirements, and whether you need a gateway computer.

Both architectures use the same automation board, same protocol, and same web UI - they just differ in where the intelligence lives (Raspberry Pi vs Pico W).
