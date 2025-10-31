# Control-Access
Multi-factor access control system using ESP32 and MicroPython. Includes fingerprint (AS608), RFID (RC522), and keypad authentication, with OLED display and relay control. Logs access events and supports modular expansion.

# Access Control System – ESP32 + MicroPython

This project implements a multi-factor access control system using an ESP32 microcontroller programmed with MicroPython. It combines **fingerprint recognition**, **RFID scanning**, and **keypad-based PIN entry** to manage secure access control.

## Features

- Fingerprint authentication (AS608 sensor)
- RFID card reading (RC522 module)
- PIN code input via 4x4 matrix keypad
- OLED display for real-time user guidance
- Relay module to simulate door lock/unlock
- Access event logging with authentication method and timestamp
- Modular and readable MicroPython code

---

## Components Used

| Component            | Description                         |
|----------------------|-------------------------------------|
| ESP32                | Main microcontroller (Wi-Fi capable)|
| AS608 Fingerprint    | Biometric sensor                    |
| RC522 RFID Module    | Reads MIFARE cards and tags         |
| 4x4 Keypad           | PIN code entry                      |
| OLED Display (I2C)   | User interface                      |
| Breadboard & Wires   | For connections                     |

---

## File Structure

- `/main.py`               – Main execution file for the access control system
- `/oled.py`               – Helper functions for OLED display messages
- `/ssd1306.py`            – OLED display driver library (I2C protocol)
- `/keypad_utp.py`         – Matrix keypad handler for PIN entry
- `/enroll_rfid.py`        – Script to enroll new RFID cards or key fobs
- `/mfrc522.py`            – RFID reader driver library (MFRC522 module)
- `/enroll_fingerprint.py` – Script to enroll new fingerprints using the AS608 sensor
- `/fingerprint.py`        – Fingerprint sensor driver library (AS608)
- `/urequests.py`          – Lightweight HTTP client for MicroPython (GET, POST, etc.)
- `/enroll_lib.py`         – Fingerprint enrollment logic with feedback and OLED support
- `/api_queue.py`          – Handles access event logging, with retry queue for offline buffering

## Project Overview Video

[Watch the Project Video](https://youtu.be/PbTgEAiEI7A)

## Database Explanation Video

[Watch the Database Video](https://youtu.be/VDUhq6uBhqI)




