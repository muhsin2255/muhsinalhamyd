[app]
title = نظام إدارة الكميات
package.name = milkaccountant
package.domain = com.muhsin
version = 1.0.0
source.dir = .
source.main = main.py

requirements = 
    python3,
    kivy==2.3.0,
    arabic-reshaper,
    python-bidi,
    pycryptodomex,
    requests,
    certifi

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 34
android.arch = armeabi-v7a

android.permissions = 
    INTERNET,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE

orientation = portrait
fullscreen = 0
log_level = 2

[buildozer]
log_level = 2
