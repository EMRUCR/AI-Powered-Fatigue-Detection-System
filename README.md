# AI-Powered Fatigue Detection System

A real-time fatigue detection system that tracks the driver's eyes through a camera and produces visual, audible, and LED-based warnings when prolonged eye closure is detected.

The computer vision and alarm logic run in Python. An ESP32 controls a WS2812B LED strip according to commands received from Python through serial communication.

## Features

- Real-time face and eye tracking with MediaPipe Face Mesh
- Eye Aspect Ratio calculation for eye-closure detection
- Three-stage LED warning system
- Audible alarm when prolonged eye closure is detected
- Blinking warning image on the camera feed during the alarm
- Final desktop warning after three fatigue detections
- Smooth LED color transitions controlled by an ESP32

## System Behavior

| Eye state | Duration | System response |
| --- | ---: | --- |
| Eyes open | — | LED strip remains blue |
| Eyes closed | Less than 2 seconds | No warning |
| Eyes closed | 2–4 seconds | LED strip transitions from blue to orange |
| Eyes closed | 4 seconds or longer | LED strip flashes red, the audible alarm starts, and the warning image blinks |
| Eyes reopened after an alarm | 2 seconds | Alarm stops and the LED strip returns to blue |
| Fatigue detected for the third time | — | A final rest warning is displayed and the program closes |

The default Eye Aspect Ratio threshold is `0.21`.

## How It Works

MediaPipe Face Mesh detects six landmarks around each eye. The system calculates the Eye Aspect Ratio with the following formula:

```text
EAR = (vertical distance 1 + vertical distance 2) / (2 × horizontal distance)
```

The average EAR of both eyes is compared with the configured threshold. Python measures how long the eyes remain closed and sends the relevant command to the ESP32:

```text
Python                      ESP32
OPENING                  -> startup brightness animation
NORMAL                   -> solid blue
NORMAL_TO_ORANGE         -> blue to orange transition
ORANGE_TO_RED            -> flashing red warning
ORANGE_TO_NORMAL         -> orange to blue transition
RED_TO_NORMAL            -> return to blue after the alarm
```

Serial communication runs at `115200` baud.

## Project Structure

```text
AI-Powered-Fatigue-Detection-System/
├── C++ (ESP32)/
│   ├── src/
│   │   └── main.cpp
│   └── platformio.ini
├── Python/
│   ├── main.py
│   ├── requirements.txt
│   ├── warning.mp3
│   └── warning.png
└── README.md
```

## Requirements

### Hardware

- ESP32 development board
- WS2812B LED strip with 144 LEDs
- External 5 V power supply suitable for the LED strip
- USB cable for the ESP32
- Camera
- Computer with a speaker
- Jumper wires

### LED Connections

| WS2812B connection | Connect to |
| --- | --- |
| `DIN` | ESP32 GPIO `18` |
| `5V` | External 5 V power supply positive output |
| `GND` | External power supply ground and ESP32 ground |

Do not power the 144-LED strip directly from the ESP32 or the computer's USB port. The ESP32 and the external power supply must share a common ground.

### Software

- Python 3.10
- Visual Studio Code
- PlatformIO
- Arduino framework for ESP32
- FastLED

Python dependencies:

```txt
opencv-python==4.13.0.92
mediapipe==0.10.14
pygame==2.6.1
pyserial==3.5
```

`time`, `math`, and `tkinter` are provided by Python and are not included in `requirements.txt`.

## Installation

### 1. Upload the ESP32 Code

Open the `C++ (ESP32)` folder as a PlatformIO project.

The included `platformio.ini` configuration uses:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino
monitor_speed = 115200
upload_port = COM3

lib_deps =
    fastled/FastLED
```

If the ESP32 uses another serial port, change `upload_port` before uploading the code.

Upload `src/main.cpp` to the ESP32. Close PlatformIO Serial Monitor after the upload so that Python can access the serial port.

### 2. Install the Python Dependencies

Open a terminal in the `Python` folder:

```bash
pip install -r requirements.txt
```

### 3. Configure the Serial Port

The Python code uses `COM3` by default:

```python
esp32 = serial.Serial(
    port="COM3",
    baudrate=115200,
    timeout=1
)
```

Change `COM3` in `main.py` if the ESP32 appears on another port.

### 4. Run the System

Make sure the following files are in the same folder:

```text
main.py
warning.mp3
warning.png
requirements.txt
```

Run the program from the `Python` folder:

```bash
python main.py
```

Press `q` while the camera window is active to close the program.

## Main Configuration Values

The detection behavior can be adjusted through these values in `main.py`:

```python
EAR_THRESHOLD = 0.21
CLOSED_TIME_LIMIT = 4
ALARM_DELAY_AFTER_OPEN = 2
max_warning_count = 3
```

The red LED blinking speed is controlled in `main.cpp`:

```cpp
const unsigned long RED_BLINK_INTERVAL = 460;
```

The LED strip configuration is:

```cpp
#define LED_PIN 18
#define NUM_LEDS 144
```

## Troubleshooting

### Serial Port Access Error

- Confirm that the ESP32 port matches the port set in `main.py`
- Close PlatformIO Serial Monitor and other applications using the same port
- Disconnect and reconnect the ESP32 if the port is not listed

### Camera Does Not Open

- Confirm that a camera is connected and not being used by another application
- Change `cv2.VideoCapture(0)` to the correct camera index if multiple cameras are connected

### Warning Image or Sound Does Not Load

- Run the command from the `Python` folder
- Confirm that `warning.png` and `warning.mp3` are next to `main.py`

### LED Strip Does Not Respond

- Confirm that the data wire is connected to GPIO `18`
- Confirm that the ESP32 and LED power supply share a common ground
- Confirm that the baud rate is `115200` in both Python and the ESP32 code
- Check the direction of the LED strip and connect GPIO `18` to its `DIN` side

## Technologies

- Python
- C++
- OpenCV
- MediaPipe
- Pygame
- PySerial
- ESP32
- FastLED
- WS2812B
