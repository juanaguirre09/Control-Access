# Control-Access
Multi-factor access control system using ESP32 and MicroPython. Includes fingerprint (AS608), RFID (RC522), and keypad authentication, with OLED display and relay control. Logs access events and supports modular expansion.

# 🔐 Access Control System – ESP32 + MicroPython

This project implements a multi-factor access control system using an ESP32 microcontroller programmed with MicroPython. It combines **fingerprint recognition**, **RFID scanning**, and **keypad-based PIN entry** to manage secure access control.

## 🚀 Features

- 🔎 Fingerprint authentication (AS608 sensor)
- 📶 RFID card reading (RC522 module)
- 🔢 PIN code input via 4x4 matrix keypad
- 📺 OLED display for real-time user guidance
- 🔒 Relay module to simulate door lock/unlock
- 📝 Access event logging with authentication method and timestamp
- 🧩 Modular and readable MicroPython code

---

## 🛠️ Components Used

| Component            | Description                         |
|----------------------|-------------------------------------|
| ESP32                | Main microcontroller (Wi-Fi capable)|
| AS608 Fingerprint    | Biometric sensor                    |
| RC522 RFID Module    | Reads MIFARE cards and tags         |
| 4x4 Keypad           | PIN code entry                      |
| OLED Display (I2C)   | User interface                      |
| Relay Module         | Controls electric lock or actuator  |
| Breadboard & Wires   | For connections                     |

---

## ⚙️ System Architecture

