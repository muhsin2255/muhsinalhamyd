[app]
title = Milk Accountant
package.name = milk_accountant
package.domain = org.shadow
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,txt
version = 1.0.1
requirements = python3==3.9,kivy==2.3.0,requests==2.31.0,pycryptodomex==3.19.0,arabic_reshaper==3.0.0,python-bidi==0.4.2,numpy
orientation = portrait
icon.filename = %(source.dir)s/nykd.png
android.api = 34
android.minapi = 21
android.ndk_path = $ANDROID_NDK_HOME
android.sdk_path = $ANDROID_SDK_ROOT
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, ACCESS_NETWORK_STATE
android.allow_backup = false
android.wakelock = false
p4a.branch = develop
