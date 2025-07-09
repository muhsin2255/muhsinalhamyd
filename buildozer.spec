[app]

title = MilkManager
package.name = milkmanager
package.domain = org.kivy
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,ttf
version = 1.0
requirements = python3,kivy,arabic-reshaper,python-bidi,pycryptodome,requests
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.ndk_path = 
android.sdk_path = 
android.gradle_dependencies = com.android.support:appcompat-v7:28.0.0
android.compile_sdk = 33
android.build_tools_version = 33.0.2
android.extra_presplash_color = #FFFFFF
android.allow_backup = True
android.enable_androidx = True
android.logcat_filters = *:S python:D

[buildozer]

log_level = 2
warn_on_root = 1
