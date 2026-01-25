# Control-Access (ESP32 + MicroPython)

Multi-factor access control system built with an **ESP32** and **MicroPython**.  
The project combines **fingerprint (AS608)**, **RFID (RC522)**, and **PIN keypad (4×4)** authentication, and logs every access event in a **local database (XAMPP + MySQL/MariaDB)**.

This repository documents the full workflow: **prototype assembly → sensor integration → database + PHP pages → access logging → final system demo videos**.

> Goal: provide a secure and traceable access system where each entry is linked to a user, an authentication method, and a timestamp.

---

## What this system can do

- Authenticate users using **fingerprint**, **RFID**, or **PIN**
- Show system status on an **OLED display (I2C)**
- Control a **relay** to simulate a door lock/unlock action
- Register users and store access logs in a **local web database**
- Keep the code **modular**, so it is easy to extend (new sensors, new rules, etc.)

## System Build and Physical Prototype

This section presents the main stages of the project, from the physical assembly of the system to the access logging in the database.

---

### 1. Physical Assembly of the System

![Physical prototype – ESP32 access control system](images/prototipo.png)

The first stage of the project was the physical assembly of the access control system.  
All components were mounted together to simulate a real access terminal.

The prototype includes:
- ESP32 as the main microcontroller
- 4×4 matrix keypad for PIN authentication
- AS608 fingerprint sensor
- RC522 RFID reader
- OLED display for user feedback
- LEDs and relay to indicate access status

This setup allows a clear interaction between the user and the system.

---

### 2. System in Operation

![Access control system operating with keypad, fingerprint and RFID](images/funcional.png)

Once the hardware was assembled, the system was programmed using **MicroPython**.

During normal operation, the user can authenticate using:
- A fingerprint
- An RFID card
- A 4-digit PIN code entered via the keypad

The OLED display shows messages such as *“Enter PIN”*, *“Access granted”*, or *“Access denied”*, while LEDs provide immediate visual feedback.

---

### 3. Access Logging and Database Records

![Access records stored in XAMPP database](images/XAMMP.png)

Every access attempt is sent to a **local server using XAMPP** and stored in a database.

Each record contains:
- User identifier
- Authentication method (fingerprint, RFID, or PIN)
- Date and time of access

This ensures full traceability of system usage and allows monitoring through a web interface.

## Authentication Flow (Internal Logic)

This section summarizes how the system processes an access attempt from start to finish.

1. **User input**  
   The user interacts with the system using one of the available methods:
   - PIN code via keypad  
   - Fingerprint via biometric sensor  
   - RFID card via reader  

2. **Data acquisition**  
   The ESP32 detects the active authentication method and captures the corresponding data
   (PIN value, fingerprint ID, or RFID UID).

3. **Verification**  
   The captured data is sent to a local server through an HTTP request.  
   The server checks the database to verify whether the credentials match a registered user.

4. **Decision and response**  
   - If the credentials are valid, access is granted.  
   - If no match is found, access is denied.  

   The ESP32 then activates the relay, updates the LEDs, and shows the result on the OLED display.

5. **Event logging**  
   Each attempt is stored in the database with the user identifier, authentication method,
   and timestamp, ensuring full traceability of system activity.



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

This video presents a complete demonstration of the access control system in operation.  
It shows the physical prototype, the different authentication methods (fingerprint, RFID, and PIN),
and how the system responds in real time to each access attempt.

▶️ [Watch the Project Video](https://youtu.be/PbTgEAiEI7A)

---

## Database Explanation Video

This video explains how the local database is structured and how access events are stored.
It includes the user registration interface, the access log table, and the communication
between the ESP32 and the server using XAMPP.

▶️ [Watch the Database Video](https://youtu.be/VDUhq6uBhqI)



