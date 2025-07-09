[app]
title = حساب كميات اللبن
package.name = milkaccountant
package.domain = org.muhsinlab
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 1.0
requirements = python3,kivy,arabic-reshaper,python-bidi
orientation = portrait
fullscreen = 1
android.permissions = INTERNET
android.minapi = 21
android.sdk = 33
android.build_tools_version = 33.0.2
android.ndk = 25b
android.gradle_dependencies = com.android.tools.build:gradle:7.2.1
android.target = android-33
android.private_storage = 1
android.allow_backup = 0

# تأكد من تضمين الخط العربي
include_patterns = fonts/*.ttf, fonts/OFL.txt

[buildozer]
log_level = 2
warn_on_root = 1
