[app]
title = Milk Accountant
package.name = milk_accountant
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0.0
requirements = python3,kivy,requests,pycryptodomex,arabic_reshaper,python-bidi
orientation = portrait
icon.filename = %(source.dir)s/nykd.png
android.api = 34
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE