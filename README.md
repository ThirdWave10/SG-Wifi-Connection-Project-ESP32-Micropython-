# ESP32 Wi-Fi Initialization Module

## Overview

This project is an ESP32-based Wi-Fi initialization and configuration module designed to simplify connecting the device to a Wi-Fi network.

It supports two modes:  
- **Station (STA) mode:** Connects to an existing Wi-Fi network using credentials provided by the user.  
- **Access Point (AP) mode:** If connection to Wi-Fi fails, the ESP32 starts a Wi-Fi access point with a web interface to scan available networks and let the user input SSID and password.

---

## Features

- Scans nearby Wi-Fi networks and displays SSIDs, signal strength, channels, and security type.
- Hosts a simple web server for Wi-Fi configuration via a user-friendly web page.
- Stores Wi-Fi credentials in a JSON file on the ESP32's filesystem (`settings.json`).
- Attempts to connect up to 3 times before falling back to AP mode for reconfiguration.
- Unique hardware ID generation for device identification.
- Supports connection retry logic and device reset after configuration update.

---

## Technology

- **Platform:** ESP32 microcontroller  
- **Language:** MicroPython  
- **Modules used:** `network`, `socket`, `json`, `machine`, `time`, `ubinascii`  
- **Web interface:** Simple HTML form generated dynamically to display scanned Wi-Fi networks and accept user input.

---

## Usage

1. Deploy the MicroPython script to your ESP32 device.  
2. On boot, the script attempts to connect to stored Wi-Fi credentials.  
3. If connection fails, ESP32 creates an Access Point with SSID `snake-<IP>_<HWID>`.  
4. Connect to the AP via Wi-Fi and open the IP address in a browser to access the web configuration page.  
5. Select the Wi-Fi network and enter the password via the web interface.  
6. Credentials are saved, device resets, and attempts connection again.

---

## File Structure

- `main.py` (or your main script name): The primary MicroPython script to run on ESP32.  
- `settings.json`: JSON file storing Wi-Fi SSID and password (created after first configuration).  

---

## Installation and Deployment

1. Flash MicroPython firmware on your ESP32.  
2. Upload the project files (`main.py` and any dependencies) using tools such as `ampy`, `rshell`, or `Thonny`.  
3. Reset the device and monitor the serial output for Wi-Fi status.  

---

## Notes

- The AP IP, subnet mask, and DNS are hardcoded — modify in the script as needed.  
- The web server runs on port 80 and uses non-blocking sockets for handling requests.  
- Passwords and other sensitive data are stored locally on the device; ensure physical security of the ESP32.  
- The code includes a mapping for URL encoded characters to decode POST data correctly.

---

## Contact And Author

For questions, contact:  
**Luke Reilly** (Student Developer, Age 14)
Email: l.j.reilly1010@gmail.com

---

## Acknowledgments

- Part contributor: Anyplace7926
- ESP32 MicroPython community and documentation  
- Inspiration from various IoT and Wi-Fi setup projects

---
