# Contributing to Pico Automation Hat

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- VSCode (recommended) or any text editor

### Initial Setup

1. Clone the repository:
   ```bash
   git clone <repo-url>
   cd pico-automation-hat
   ```

2. Install uv (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies:
   ```bash
   make install
   ```

4. Open in VSCode:
   ```bash
   code .
   ```

   VSCode will prompt to install recommended extensions (Ruff, Python, Pylance).

## Development Workflow

### Code Formatting and Linting

The project uses **Ruff** for both linting and formatting:

```bash
# Format code
make format

# Lint code
make lint

# Check formatting without making changes
make check
```

**VSCode users:** Ruff runs automatically on save!

### Project Structure

```
pico-automation-hat/
├── firmware-serial/      # USB serial firmware for the board
├── firmware-wifi/        # WiFi firmware for standalone operation
├── host/                 # Raspberry Pi host service
│   ├── automation2040w.py          # Serial communication library
│   ├── automation_service.py       # Main service (MQTT/HTTP)
│   └── examples/                   # Usage examples
├── pyproject.toml        # Project metadata and tool config
└── Makefile              # Development commands
```

### Making Changes

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** using your preferred editor

3. **Format and lint:**
   ```bash
   make format
   make lint
   ```

4. **Test your changes:**
   - For host service: Test on Raspberry Pi or use examples
   - For firmware: Deploy to board and test functionality

5. **Commit your changes:**
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

6. **Push and create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Coding Standards

### Python Style

- **Line length:** 100 characters (enforced by Ruff)
- **Indentation:** 4 spaces (no tabs)
- **Imports:** Automatically organized by Ruff
- **Docstrings:** Google style for functions and classes

Example:
```python
def control_relay(relay_num: int, state: bool) -> None:
    """
    Control a relay on the Automation 2040 W.

    Args:
        relay_num: Relay number (1-3)
        state: True to turn on, False to turn off

    Raises:
        ValueError: If relay_num is out of range
    """
    if not 1 <= relay_num <= 3:
        raise ValueError(f"Relay number must be 1-3, got {relay_num}")
    # Implementation...
```

### MicroPython Firmware

- Keep compatible with MicroPython constraints
- Minimize memory usage
- Use clear variable names
- Comment non-obvious logic

### Commit Messages

Use clear, descriptive commit messages:

```
Add MQTT reconnection logic to host service

- Implement exponential backoff for reconnections
- Add health check endpoint
- Update documentation
```

## Testing

### Manual Testing

1. **Host Service:**
   ```bash
   cd host
   source .venv/bin/activate
   python3 automation_service.py
   ```

2. **Serial Firmware:**
   ```bash
   cd firmware-serial
   ./deploy.sh
   # Test with: mpremote repl
   ```

3. **WiFi Firmware:**
   ```bash
   cd firmware-wifi
   ./deploy.sh
   # Check web interface at board IP
   ```

### Integration Testing

Test the full stack:
1. Deploy serial firmware to board
2. Deploy host service to Raspberry Pi
3. Verify MQTT messages
4. Test REST API endpoints
5. Check web interface

## Documentation

When adding features:

1. Update [README.md](README.md) if user-facing
2. Update [SETUP.md](SETUP.md) if affects deployment
3. Add docstrings to all public functions
4. Comment complex logic

## VSCode Tips

### Keyboard Shortcuts

- **Format Document:** `Shift+Alt+F` (or save)
- **Organize Imports:** `Shift+Alt+O`
- **Run Task:** `Cmd+Shift+P` → "Tasks: Run Task"

### Available Tasks

Access via `Cmd+Shift+P` → "Tasks: Run Task":

- Lint with Ruff
- Format with Ruff
- Install Dependencies
- Deploy Host Service
- Deploy Serial Firmware
- Deploy WiFi Firmware

### Extensions

Install recommended extensions when prompted:
- **Ruff** - Linting and formatting
- **Python** - Language support
- **Pylance** - IntelliSense

## Common Issues

### "ModuleNotFoundError" when running scripts

Make sure you're in the virtual environment:
```bash
cd host
source .venv/bin/activate
```

Or use the VSCode integrated terminal (automatically activates).

### Ruff not working in VSCode

1. Check Ruff extension is installed
2. Reload VSCode window: `Cmd+Shift+P` → "Developer: Reload Window"
3. Check output panel: View → Output → Select "Ruff"

### Permission denied on serial port (Linux)

Add yourself to dialout group:
```bash
sudo usermod -a -G dialout $USER
# Log out and back in
```

## Release Process

1. Update version in `pyproject.toml`
2. Update `VERSION` in firmware files
3. Update CHANGELOG.md
4. Create git tag: `git tag v1.0.0`
5. Push tags: `git push --tags`

## Questions?

- Check [SETUP.md](SETUP.md) for deployment questions
- Check [README.md](README.md) for usage questions
- Open an issue for bugs or feature requests

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
