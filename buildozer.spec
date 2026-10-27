[app]
# (str) Title of your application
title = Bluetooth Chat Terminal

# (str) Package name
package.name = bt_chat_terminal

# (str) Package domain (needed for android packaging)
package.domain = org.example

# (str) Source code directory
source.dir = .

# (list) Source files to include (let Kivy catch everything)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 1.0.0

# (list) Application requirements
# Pin stable dependencies to avoid pulling experimental Python 3.14/3.15 assets
requirements = python3==3.11.11,kivy==2.3.0

# (str) Supported orientation (one of landscape, portrait or all)
orientation = portrait

# ----------------------------------------------
# Android specific configuration profiles
# ----------------------------------------------

# (bool) Indicate if the application should be fullscreen
fullscreen = 1

# (list) Permissions required for hardware communication
android.permissions = BLUETOOTH, BLUETOOTH_ADMIN, BLUETOOTH_CONNECT, BLUETOOTH_SCAN

# (int) Target Android API (Keep at 33 for maximum hardware compatibility)
android.api = 33

# (int) Minimum API your APK requires to launch
android.minapi = 24

# (str) Android NDK version to request (Standard for stable builds)
android.ndk = 25b

# (str) Android Build Tools Version
# CRITICAL FIX: Explicitly pins version 33.0.0 to prevent it from auto-downloading broken v37.0.0
android.build_tools_version = 33.0.0

# (bool) Use skip-update hooks where possible to avoid dependency drifts
android.skip_update = False

# (bool) Accept SDK licenses automatically during execution loops
android.accept_sdk_license = True

# (str) Format output variant
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
# (int) Log level (1 = error only, 2 = debugging data modules)
log_level = 2

# (int) Display warning markers if configurations seem unstable
warn_on_root = 1
