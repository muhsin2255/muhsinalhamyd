[app]

# الاسم الظاهر للتطبيق
title = MilkManager

# اسم الحزمة
package.name = milkmanager

# نطاق الحزمة (يفضل أن يكون نطاق مميز مثل اسم نطاقك بالعكس)
package.domain = org.muhsin

# المجلد الذي يحتوي الكود
source.dir = .

# أنواع الملفات التي يجب تضمينها داخل الـ APK
source.include_exts = py,png,jpg,kv,atlas,json,ttf

# المكتبات المطلوبة للتطبيق
requirements = python3,kivy,arabic-reshaper,python-bidi,pycryptodome,requests

# اتجاه الشاشة
orientation = portrait

# السماح بتشغيل التطبيق في وضع ملء الشاشة
fullscreen = 1

# صلاحيات التطبيق (مثلاً الاتصال بالإنترنت)
android.permissions = INTERNET

# إصدارات SDK المطلوبة
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_path =
android.sdk_path =

# إعدادات الأدوات والبناء
android.gradle_dependencies = com.android.support:appcompat-v7:28.0.0
android.build_tools_version = 33.0.2
android.compile_sdk = 33

# لون شاشة الإقلاع
android.extra_presplash_color = #FFFFFF

# تمكين دعم AndroidX
android.enable_androidx = True

# السماح بالنسخ الاحتياطي
android.allow_backup = True

# فلترة رسائل السجل
android.logcat_filters = *:S python:D

# إصدار التطبيق
version = 1.0

[buildozer]

# مستوى التفاصيل في السجل
log_level = 2

# السماح بالتشغيل كمستخدم root
warn_on_root = 1
