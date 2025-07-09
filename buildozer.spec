[app]
title = MilkApp
package.name = milkapp
package.domain = org.muhsin

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf

requirements = python3,kivy,arabic-reshaper,python-bidi

orientation = portrait
fullscreen = 1

android.api = 33
android.sdk = 33
android.ndk = 25b
android.minapi = 21
android.build_tools_version = 33.0.2

android.permissions = INTERNET
android.enable_androidx = True
android.allow_backup = True

# لتشغيل الخط العربي من fonts
presplash.filename = 
icon.filename =
