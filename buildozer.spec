[app]
title = Milk Accountant
package.name = milk_accountant
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0.0
requirements = python3==3.9,kivy==2.3.0,requests==2.31.0,pycryptodomex==3.19.0,arabic_reshaper==3.0.0,python-bidi==0.4.2
orientation = portrait
icon.filename = %(source.dir)s/nykd.png
android.api = 34
android.minapi = 21
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.allow_backup = true
