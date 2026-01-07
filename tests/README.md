# Tests Directory

This directory contains all test files for the InkFrame project, organized by purpose and type.

## Directory Structure

```
tests/
├── README.md                           # This file
├── test_simulation.py                 # Simulation mode tests (works on any system)
├── test_display.py                    # Display component tests
├── test_photo_manager.py              # Photo manager unit tests
├── test_full_display.py               # End-to-end display tests
├── test_color_pipeline.py             # Color processing pipeline tests
├── test_display_colors.py             # Display color rendering tests
├── test_our_display.py                # Custom display logic tests
├── test_display_direct.py             # Direct display driver tests
├── test_save_canvas.py                # Canvas saving tests
├── test_weather_api.py                # Weather API integration tests
├── hardware/                          # Hardware diagnostic and testing scripts
│   ├── simple_test.py                # GPIO and SPI basic test
│   ├── basic_test.py                 # Minimal display initialization test
│   ├── official_test.py              # Waveshare official test adaptation
│   ├── check_model.py                # Display model compatibility checker
│   ├── lgpio_test.py                 # lgpio library test
│   ├── lgpio_reset_test.py           # GPIO reset test
│   └── pin_check.py                  # GPIO interface availability checker
└── color/                             # Color display specific tests
    ├── color_test.py                 # ACeP 7-color display test
    └── color_display_test.py         # 7.3 inch ACeP 7-color e-ink display test
```

## Test Categories

### Simulation Tests (`test_simulation.py`)

**Purpose**: Test application functionality without requiring hardware.

**When to Use**:
- Development on non-Raspberry Pi systems
- Testing logic changes without needing display hardware
- Continuous integration environments

**How to Run**:
```bash
python tests/test_simulation.py
```

### Unit Tests

These tests verify individual components in isolation:

- `test_display.py` - Display driver functionality
- `test_photo_manager.py` - Photo management logic
- `test_weather_api.py` - Weather data retrieval
- `test_color_pipeline.py` - Image color processing
- `test_save_canvas.py` - Canvas rendering and saving

**When to Use**:
- When making changes to specific components
- For automated testing pipelines
- To verify individual modules work correctly

**How to Run**:
```bash
python tests/test_display.py
python tests/test_photo_manager.py
# ... etc
```

### Integration Tests

These tests verify components work together:

- `test_full_display.py` - Complete display cycle
- `test_display_colors.py` - Color rendering pipeline
- `test_our_display.py` - Custom display integration
- `test_display_direct.py` - Direct driver integration

**When to Use**:
- After making cross-component changes
- Before deploying to production
- To verify end-to-end functionality

**How to Run**:
```bash
python tests/test_full_display.py
# ... etc
```

### Hardware Tests (`tests/hardware/`)

These scripts diagnose and test hardware connectivity:

#### `simple_test.py`
**Purpose**: Test basic GPIO and SPI communication without initializing display.

**When to Use**:
- First step in hardware troubleshooting
- Verifying physical connections
- Checking GPIO pin configuration

**How to Run**:
```bash
python tests/hardware/simple_test.py
```

#### `basic_test.py`
**Purpose**: Minimal test for display initialization and clearing.

**When to Use**:
- After GPIO/SPI tests pass
- Testing display power and initialization
- Verifying basic display functionality

**How to Run**:
```bash
python tests/hardware/basic_test.py
```

#### `check_model.py`
**Purpose**: Automatically determine which Waveshare display model works with your hardware.

**When to Use**:
- Setting up a new display
- When display doesn't work with configured model
- After hardware changes

**How to Run**:
```bash
python tests/hardware/check_model.py
```

#### `official_test.py`
**Purpose**: Adapted from Waveshare's official test scripts.

**When to Use**:
- Verifying Waveshare library installation
- Comparing with official examples
- Comprehensive hardware verification

**How to Run**:
```bash
python tests/hardware/official_test.py
```

#### `lgpio_test.py` & `lgpio_reset_test.py`
**Purpose**: Test lgpio library and GPIO reset functionality.

**When to Use**:
- When RPi.GPIO library is not available
- Testing alternative GPIO libraries
- GPIO state reset after crashes

**How to Run**:
```bash
python tests/hardware/lgpio_test.py
python tests/hardware/lgpio_reset_test.py

python tests/hardware/pin_check.py
```

### Color Display Tests (`tests/color/`)

These tests are specific to ACeP 7-color displays:

- `color_test.py` - Full color display test with all 7 colors
- `color_display_test.py` - 7.3 inch ACeP 7-color e-ink display test

**When to Use**:
- Testing ACeP 7-color displays
- Verifying color rendering
- Color calibration

**How to Run**:
```bash
python tests/color/color_test.py
```

## Hardware Testing Sequence

When troubleshooting display issues on Raspberry Pi, follow this sequence:

1. **GPIO/SPI Test**
   ```bash
   python tests/hardware/simple_test.py
   ```

2. **Display Model Check**
   ```bash
   python tests/hardware/check_model.py
   ```

3. **Basic Display Test**
   ```bash
   python tests/hardware/basic_test.py
   ```

4. **Official Test**
   ```bash
   python tests/hardware/official_test.py
   ```

5. **Full Integration Test**
   ```bash
   python tests/test_full_display.py
   ```

If any step fails, consult `troubleshooting.md` in the project root.

## Running All Tests

To run all tests (excluding hardware tests that require a Raspberry Pi):

```bash
# Run all simulation and unit tests
python tests/test_simulation.py
python tests/test_display.py
python tests/test_photo_manager.py
python tests/test_color_pipeline.py
python tests/test_weather_api.py
python tests/test_save_canvas.py

# Run hardware tests (requires RPi)
python tests/hardware/simple_test.py
python tests/hardware/basic_test.py
python tests/hardware/check_model.py
python tests/hardware/official_test.py
python tests/hardware/lgpio_test.py
python tests/hardware/lgpio_reset_test.py
python tests/hardware/pin_check.py

# Run integration tests
python tests/test_full_display.py
python tests/test_display_colors.py
```

## Testing on Non-Raspberry Pi Systems

When developing on a system without the e-ink display hardware:

1. Use simulation mode for most testing:
   ```bash
   python tests/test_simulation.py
   ```

2. Test logic and algorithms:
   ```bash
   python tests/test_photo_manager.py
   python tests/test_color_pipeline.py
   ```

3. Test web interface:
   ```bash
   python run.py --web-only
   ```

4. Check available GPIO interfaces:
   ```bash
   python tests/hardware/pin_check.py
   ```

## Writing New Tests

When adding new functionality, follow these guidelines:

1. **Unit Tests**: Create focused tests for individual functions/classes
2. **Integration Tests**: Test interactions between components
3. **Hardware Tests**: Add diagnostic scripts for new hardware features
4. **Simulation**: Ensure all tests can run in simulation mode when possible

Test files should:
- Be named starting with `test_`
- Include clear docstrings explaining their purpose
- Have proper error handling and logging
- Be runnable independently

## Test Coverage Goals

- Unit tests for all critical logic
- Integration tests for major workflows
- Hardware tests for all supported display models
- Simulation mode support for all tests

## Notes

- Hardware tests require a Raspberry Pi with the e-ink display connected
- Always test in simulation mode first before running on hardware
- Some tests may take several minutes to complete (e-ink displays are slow)
- Clear the display between tests to avoid ghosting artifacts