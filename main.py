from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import Color, Rectangle, RoundedRectangle, Line, Ellipse
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.properties import NumericProperty, StringProperty, ListProperty, BooleanProperty
from kivy.effects.scroll import ScrollEffect
import arabic_reshaper
from bidi.algorithm import get_display
import os
import json
import base64
from datetime import datetime, timedelta
import requests
import uuid
import hashlib
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import hmac
import time
import traceback
from urllib.request import urlretrieve

# ============= إعدادات الخط =============
FONT_URL = "https://drive.google.com/uc?export=download&id=1ltypDv74JZexde9x2sDzhA1irwbLxKne"
FONT_PATH = "/storage/emulated/0/accountant/ArabicFont.ttf"

def download_font():
    """تحميل الخط إذا لم يكن موجودًا"""
    if not os.path.exists(FONT_PATH):
        try:
            os.makedirs(os.path.dirname(FONT_PATH), exist_ok=True)
            urlretrieve(FONT_URL, FONT_PATH)
            print("تم تحميل الخط بنجاح")
            return True
        except Exception as e:
            print(f"فشل تحميل الخط: {e}")
            return False
    return True

# حاول تحميل الخط عند التشغيل
if download_font():
    try:
        LabelBase.register(name="ArabicFont", fn_regular=FONT_PATH)
        print("تم تسجيل الخط بنجاح")
    except Exception as e:
        print(f"فشل تسجيل الخط: {e}")

# === إعدادات التصميم ===
Window.clearcolor = (0.96, 0.96, 0.96, 1)
COLOR_PRIMARY = [0.2, 0.6, 0.8, 1]
COLOR_SECONDARY = [0.3, 0.7, 0.5, 1]
COLOR_DANGER = [0.9, 0.3, 0.3, 1]
COLOR_WARNING = [1, 0.6, 0.2, 1]
COLOR_LIGHT = [0.98, 0.98, 0.98, 1]
COLOR_DARK = [0.1, 0.1, 0.1, 1]
GRADIENT_BLUE = [(0.2, 0.5, 0.8, 1), (0.1, 0.3, 0.6, 1)]
GRADIENT_GREEN = [(0.3, 0.7, 0.5, 1), (0.1, 0.5, 0.3, 1)]
GRADIENT_RED = [(0.9, 0.3, 0.3, 1), (0.7, 0.1, 0.1, 1)]
GRADIENT_ORANGE = [(1, 0.6, 0.2, 1), (0.8, 0.4, 0.1, 1)]

# === مكونات التصميم المخصصة ===
class ModernButton(Button):
    """زر عصري مع تأثيرات متحركة وتدرج لوني"""
    button_color = ListProperty(COLOR_PRIMARY)
    ripple_color = ListProperty([1, 1, 1, 0.2])
    rounded = BooleanProperty(True)
    radius = ListProperty([dp(15)])
    font_name = StringProperty("ArabicFont")
    padding = ListProperty([dp(10), dp(5)])
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = [0, 0, 0, 0]
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # خلفية بيضاء مع حواف مستديرة
            Color(rgba=[1, 1, 1, 1])
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=self.radius
            )
            
            # زر داخلي أصغر مع حواف مستديرة
            inner_pos = [self.pos[0] + dp(2), self.pos[1] + dp(2)]
            inner_size = [self.size[0] - dp(4), self.size[1] - dp(4)]
            
            if self.rounded:
                Color(rgba=self.button_color)
                RoundedRectangle(
                    pos=inner_pos,
                    size=inner_size,
                    radius=[max(0, r - dp(2)) for r in self.radius]
                )
                
    def on_press(self):
        anim = Animation(button_color=[c * 0.8 for c in self.button_color], duration=0.1)
        anim += Animation(button_color=self.button_color, duration=0.1)
        anim.start(self)
        return super().on_press()
        
    def on_release(self):
        if self.parent is not None:
            ripple = RippleEffect(
                center=self.center,
                ripple_color=self.ripple_color,
                radius=max(self.width, self.height) * 0.8
            )
            self.parent.add_widget(ripple)
        return super().on_release()

class RippleEffect(BoxLayout):
    """تأثير التموج عند الضغط على الأزرار"""
    def __init__(self, center, ripple_color, radius, **kwargs):
        super().__init__(**kwargs)
        self.size = (radius * 2, radius * 2)
        self.pos = (center[0] - radius, center[1] - radius)
        self.ripple_color = ripple_color
        self.radius = radius
        self.alpha = 1
        self.scale = 0.1
        Clock.schedule_once(self.start_animation, 0)
        
    def start_animation(self, dt):
        anim = Animation(scale=1, alpha=0, duration=0.4)
        anim.bind(on_complete=lambda *x: self.parent.remove_widget(self) if self.parent is not None else None)
        anim.start(self)
        
    def on_scale(self, instance, value):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(rgba=[*self.ripple_color[:3], self.alpha])
            Ellipse(
                pos=(
                    self.center_x - self.radius * value,
                    self.center_y - self.radius * value
                ),
                size=(self.radius * 2 * value, self.radius * 2 * value)
            )

class ModernTextInput(TextInput):
    """حقل إدخال عصري مع تأثيرات"""
    border_color = ListProperty([0.7, 0.7, 0.7, 1])
    active_color = ListProperty(COLOR_PRIMARY)
    font_name = StringProperty("ArabicFont")
    multiline = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_active = ''
        self.background_color = [0, 0, 0, 0]
        self.bind(pos=self.update_canvas, size=self.update_canvas, focus=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # الخلفية
            Color(rgba=COLOR_LIGHT)
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(10)]
            )
            
            # الحدود
            line_width = dp(2) if self.focus else dp(1)
            line_color = self.active_color if self.focus else self.border_color
            Color(rgba=line_color)
            Line(
                rounded_rectangle=[
                    self.pos[0], self.pos[1],
                    self.size[0], self.size[1],
                    dp(10)
                ],
                width=line_width
            )
            
    def on_focus(self, instance, value):
        anim = Animation(
            active_color=COLOR_PRIMARY if value else self.border_color,
            duration=0.2
        )
        anim.start(self)
        self.update_canvas()

class GradientLabel(Label, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'):
    """نص بتدرج لوني"""
    gradient = ListProperty(GRADIENT_BLUE)
    font_name = StringProperty("ArabicFont")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # تأثير التدرج اللوني للنص
            Color(rgba=self.gradient[0])
            Rectangle(
                pos=self.pos,
                size=(self.size[0], self.size[1] * 0.6)
            )
            Color(rgba=self.gradient[1])
            Rectangle(
                pos=(self.pos[0], self.pos[1] + self.size[1] * 0.4),
                size=(self.size[0], self.size[1] * 0.6)
            )

class ModernPopup(Popup):
    """نافذة منبثقة عصرية"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background = ''
        self.separator_color = [0, 0, 0, 0]
        self.background_color = [1, 1, 1, 0]  # شفاف
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # الظل
            Color(rgba=[0, 0, 0, 0.3])
            RoundedRectangle(
                pos=(self.pos[0] - dp(5), self.pos[1] - dp(5)),
                size=(self.size[0] + dp(10), self.size[1] + dp(10)),
                radius=[dp(20)]
            )
            
            # الخلفية الرئيسية
            Color(rgba=[1, 1, 1, 1])
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[dp(15)]
            )
            
            # الحدود
            Color(rgba=COLOR_PRIMARY)
            Line(
                rounded_rectangle=[
                    self.pos[0], self.pos[1],
                    self.size[0], self.size[1],
                    dp(15)
                ],
                width=dp(1.5)
            )

class ModernScrollView(ScrollView):
    """منطقة تمرير عصرية"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effect_cls = ScrollEffect
        self.bar_width = dp(10)
        self.bar_color = [*COLOR_PRIMARY[:3], 0.5]
        self.bar_inactive_color = [*COLOR_PRIMARY[:3], 0.2]
        self.scroll_type = ['bars', 'content']

# === وظائف مساعدة ===
def reshape(text):
    """تحسين النص العربي"""
    if not text:
        return text
        
    try:
        if text.strip().isdigit():
            return text
            
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"Error in reshape: {e}")
        return text

def get_app_storage_path():
    """الحصول على مسار التخزين الأمثل"""
    try:
        from android.storage import app_storage_path
        return app_storage_path()
    except:
        return "//storage/emulated/0/accountant"

def ensure_data_directory():
    """إنشاء مجلد التخزين إذا لم يكن موجودًا"""
    storage_path = os.path.join(get_app_storage_path(), "milk_account")
    os.makedirs(storage_path, exist_ok=True)
    return storage_path

def get_data_file_path():
    """مسار ملف البيانات الرئيسي"""
    return os.path.join(ensure_data_directory(), "milk_data.json")

def get_milk_records_path():
    """مسار ملفات سجلات اللبن"""
    return os.path.join(ensure_data_directory(), "milk_records")

def load_code_data():
    """تحميل البيانات مع التعامل مع جميع حالات الخطأ"""
    filepath = get_data_file_path()
    default_data = {
        "names": ["محمد"],
        "materials": ["لبن", "جبن", "زبدة"],
        "name_materials": {"محمد": ["لبن", "جبن", "زبدة"]},
        "material_types": {"لبن": "عدد", "جبن": "عدد", "زبدة": "عدد"},
        "material_weights": {"لبن": 1.0, "جبن": 1.0, "زبدة": 1.0}
    }
    
    try:
        if not os.path.exists(filepath):
            save_code_data(**default_data)
            return (
                default_data["names"],
                default_data["materials"],
                default_data["name_materials"],
                default_data["material_types"],
                default_data["material_weights"]
            )
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
            if not all(key in data for key in ["names", "materials", "name_materials"]):
                raise ValueError("هيكل البيانات غير صالح")
                
            material_types = data.get("material_types", {mat: "عدد" for mat in data["materials"]})
            material_weights = data.get("material_weights", {mat: 1.0 for mat in data["materials"]})
            
            for name in data["names"]:
                if name not in data["name_materials"]:
                    data["name_materials"][name] = []
                    
            return (
                data["names"],
                data["materials"],
                data["name_materials"],
                material_types,
                material_weights
            )
            
    except Exception as e:
        print(f"خطأ في التحميل: {e}")
        return (
            default_data["names"],
            default_data["materials"],
            default_data["name_materials"],
            default_data["material_types"],
            default_data["material_weights"]
        )

def save_code_data(names, materials, name_materials, material_types=None, material_weights=None):
    """حفظ البيانات بنظام آمن"""
    filepath = get_data_file_path()
    try:
        temp_path = filepath + ".tmp"
        data = {
            "names": names,
            "materials": materials,
            "name_materials": name_materials,
            "material_types": material_types or {mat: "عدد" for mat in materials},
            "material_weights": material_weights or {mat: 1.0 for mat in materials}
        }
        
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        if os.path.exists(temp_path):
            if os.path.exists(filepath):
                os.replace(filepath, filepath + ".bak")
            os.replace(temp_path, filepath)
            return True
        return False
    except Exception as e:
        print(f"خطأ في الحفظ: {e}")
        return False

# === نظام التشفير ===
class AdvancedEncryption:
    def __init__(self, key):
        self.key = hashlib.sha256(key.encode()).digest()[:32]
        self.iv = b'0123456789ABCDEF'
        
    def encrypt(self, data):
        try:
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            padded_data = pad(data.encode('utf-8'), AES.block_size)
            encrypted = cipher.encrypt(padded_data)
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            print(f"خطأ في التشفير: {str(e)}")
            traceback.print_exc()
            return None
            
    def decrypt(self, encrypted_data):
        try:
            enc_data = base64.b64decode(encrypted_data)
            cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
            decrypted = cipher.decrypt(enc_data)
            return unpad(decrypted, AES.block_size).decode('utf-8')
        except Exception as e:
            print(f"خطأ في فك التشفير: {str(e)}")
            traceback.print_exc()
            return None
        
    @staticmethod
    def generate_signature(data, secret):
        return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()

# === نظام التفعيل ===
class ActivationSystem:
    def __init__(self):
        self.activation_path = "/storage/emulated/0/accountant/milk_activation.dat"
        self.device_id_path = "/storage/emulated/0/accountant/device_id.dat"
        self.bot_token = "7349238904:AAFxPDdPvvOQ6mXpqAxWid2s30H9jLxSAHQ"
        self.admin_id = "5135126876"
        self.device_id = self.get_stable_device_id()
        self.encryption = AdvancedEncryption("milk_secret_key@12345")
        self.activation_request_sent = False
        self.last_update_time = 0
        self.activation_days = 0

    def get_stable_device_id(self):
        try:
            if os.path.exists(self.device_id_path):
                with open(self.device_id_path, 'r') as f:
                    device_id = f.read().strip()
                    if device_id:
                        return device_id
            try:
                from jnius import autoclass
                SettingsSecure = autoclass('android.provider.Settings$Secure')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                context = PythonActivity.mActivity
                android_id = SettingsSecure.getString(context.getContentResolver(), SettingsSecure.ANDROID_ID)
                if android_id:
                    os.makedirs(os.path.dirname(self.device_id_path), exist_ok=True)
                    with open(self.device_id_path, 'w') as f:
                        f.write(android_id)
                    return android_id
            except:
                pass
            new_id = str(uuid.uuid4())
            os.makedirs(os.path.dirname(self.device_id_path), exist_ok=True)
            with open(self.device_id_path, 'w') as f:
                f.write(new_id)
            return new_id
        except Exception as e:
            print(f"Error generating device ID: {e}")
            return str(uuid.getnode())

    def is_activated(self):
        if not os.path.exists(self.activation_path):
            print("Activation file not found")
            return False
        try:
            with open(self.activation_path, "r") as f:
                encrypted_data = f.read()
                if not encrypted_data:
                    print("Empty activation file")
                    return False
                data = self.encryption.decrypt(encrypted_data)
                if not data:
                    print("Decryption failed")
                    return False
                parts = data.split(":")
                if len(parts) != 4:
                    print("Invalid file format")
                    return False
                device_id, end_date, days, signature = parts
                expected_signature = self.encryption.generate_signature(f"{device_id}:{end_date}:{days}", "milk_signature")
                if signature != expected_signature:
                    print("Signature mismatch")
                    return False
                if device_id != self.device_id:
                    print("Device ID mismatch")
                    return False
                end_date = datetime.strptime(end_date, "%Y-%m-%d")
                if datetime.now() > end_date:
                    print("Activation expired")
                    return False
                print("Device successfully activated")
                return True
        except Exception as e:
            print(f"Activation check error: {e}")
            return False

    def activate(self, days):
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days)
            end_date_str = end_date.strftime("%Y-%m-%d")
            data = f"{self.device_id}:{end_date_str}:{days}"
            signature = self.encryption.generate_signature(data, "milk_signature")
            full_data = f"{data}:{signature}"
            encrypted_data = self.encryption.encrypt(full_data)
            if not encrypted_data:
                print("Encryption failed")
                return False
            os.makedirs(os.path.dirname(self.activation_path), exist_ok=True)
            temp_path = self.activation_path + ".tmp"
            with open(temp_path, "w") as f:
                f.write(encrypted_data)
            if os.path.exists(temp_path):
                with open(temp_path, "r") as f:
                    if f.read() == encrypted_data:
                        os.replace(temp_path, self.activation_path)
                        print("Activation file written successfully")
                        return True
            print("Failed to write activation file")
            return False
        except Exception as e:
            print(f"Activation error: {e}")
            return False

    def get_activation_info(self):
        if not self.is_activated():
            return None
        try:
            with open(self.activation_path, "r") as f:
                encrypted_data = f.read()
                data = self.encryption.decrypt(encrypted_data)
                parts = data.split(":")
                if len(parts) != 4:
                    return None
                device_id, end_date, days, signature = parts
                remaining_days = (datetime.strptime(end_date, "%Y-%m-%d") - datetime.now()).days
                return {
                    "device_id": device_id,
                    "end_date": end_date,
                    "days": days,
                    "remaining_days": remaining_days if remaining_days > 0 else 0
                }
        except Exception as e:
            print(f"Error getting activation info: {e}")
            return None

    def send_activation_request(self):
        if self.activation_request_sent:
            return True
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        text = (
            f"📌 New Activation Request\n\n"
            f"🆔 Device: {self.device_id}\n"
            f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
            f"Please reply with:\n"
            f"/approve7_{self.device_id} - 7 days\n"
            f"/approve180_{self.device_id} - 6 months\n"
            f"/approve365_{self.device_id} - 1 year\n"
            f"/reject_{self.device_id} - Reject"
        )
        try:
            response = requests.post(url, data={
                "chat_id": self.admin_id,
                "text": text,
                "parse_mode": "HTML"
            }, timeout=10)
            if response.status_code == 200:
                self.activation_request_sent = True
                self.last_update_time = time.time()
                print("Activation request sent successfully")
                return True
            else:
                print(f"Request failed: {response.text}")
        except Exception as e:
            print(f"Error sending request: {e}")
        return False

    def check_bot_response(self):
        if not self.activation_request_sent:
            return "not_sent"

        url = f"https://api.telegram.org/bot{self.bot_token}/getUpdates"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                updates = response.json().get("result", [])
                latest_approval = None
                latest_update_id = 0

                for update in updates:
                    if "message" in update and str(update["message"]["chat"]["id"]) == self.admin_id:
                        text = update["message"].get("text", "")
                        update_id = update["update_id"]
                        if update_id > latest_update_id and self.device_id in text:
                            if f"/approve7_{self.device_id}" in text:
                                latest_approval = 7
                                latest_update_id = update_id
                            elif f"/approve180_{self.device_id}" in text:
                                latest_approval = 180
                                latest_update_id = update_id
                            elif f"/approve365_{self.device_id}" in text:
                                latest_approval = 365
                                latest_update_id = update_id
                            elif f"/reject_{self.device_id}" in text:
                                latest_approval = "rejected"
                                latest_update_id = update_id

                if latest_approval == "rejected":
                    return "rejected"
                elif isinstance(latest_approval, int):
                    self.activation_days = latest_approval
                    self.activate(self.activation_days)
                    return "approved"
                return "pending"
        except Exception as e:
            print(f"Error checking response: {e}")

        return "error"

    def test_encryption(self):
        test_data = "test_activation_data"
        encrypted = self.encryption.encrypt(test_data)
        if not encrypted:
            return False
        decrypted = self.encryption.decrypt(encrypted)
        return decrypted == test_data

    def test_bot_connection(self):
        url = f"https://api.telegram.org/bot{self.bot_token}/getMe"
        try:
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except:
            return False

    def debug_activation_process(self):
        print("\n=== Debug Information ===")
        print(f"Device ID: {self.device_id}")
        print(f"Activation Path: {self.activation_path}")

        if not self.test_encryption():
            print("✖ Encryption test failed")
            return False
        else:
            print("✔ Encryption test passed")

        if not self.test_bot_connection():
            print("✖ Bot connection test failed")
            return False
        else:
            print("✔ Bot connection test passed")

        return True

# === واجهات التطبيق ===
class ActivationScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(30), padding=dp(40))
        
        self.activation = ActivationSystem()
        self.check_interval = None
        self.progress_popup = None
        
        # شريط الاتصال العلوي
        contact_bar = BoxLayout(size_hint_y=None, height=dp(40), padding=dp(5))
        contact_bar.add_widget(Label(text="+963930458096",
            font_size=dp(16, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            size_hint_x=0.5,
            halign="left"
        ))
        contact_bar.add_widget(Label(text="t.me/ssaanmm",
            font_size=dp(16, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            size_hint_x=0.5,
            halign="right"
        ))
        self.add_widget(contact_bar)
        
        self.add_widget(GradientLabel(text=reshape("نظام إدارة الكميات", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(30),
            size_hint_y=None,
            height=dp(60),
            gradient=GRADIENT_BLUE
        ))
        
        self.status_label = GradientLabel(text=reshape("الحالة: جاري التحقق...", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(24),
            color=(0.8, 0.5, 0, 1),
            size_hint_y=None,
            height=dp(50),
            gradient=GRADIENT_ORANGE
        )
        self.add_widget(self.status_label)
        
        self.details_label = Label(
            text="",
            font_name="ArabicFont",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(80),
            halign="center",
            valign="middle"
        )
        self.add_widget(self.details_label)
        
        self.activate_btn = ModernButton(
            text=reshape("طلب التفعيل"),
            font_size=dp(28),
            size_hint=(0.8, None),
            height=dp(80),
            pos_hint={'center_x': 0.5},
            button_color=COLOR_PRIMARY
        )
        self.activate_btn.bind(on_press=self.request_activation)
        self.add_widget(self.activate_btn)
        
        self.restart_btn = ModernButton(
            text=reshape("أعد تشغيل التطبيق"),
            font_size=dp(28),
            size_hint=(0.8, None),
            height=dp(80),
            pos_hint={'center_x': 0.5},
            button_color=COLOR_SECONDARY,
            disabled=True
        )
        self.restart_btn.bind(on_press=self.restart_app)
        self.add_widget(self.restart_btn)
        
        self.check_activation()
        
    def check_activation(self):
        if self.activation.is_activated():
            info = self.activation.get_activation_info()
            if info:
                remaining_days = info['remaining_days']
                if remaining_days <= 5:
                    self.status_label.text = reshape(f"⚠️ انتبه! لقد بقي {remaining_days} أيام لانتهاء التفعيل")
                    self.status_label.gradient = GRADIENT_ORANGE
                else:
                    self.status_label.text = reshape("الحالة: مفعل")
                    self.status_label.gradient = GRADIENT_GREEN
                
                self.details_label.text = reshape(
                    f"مدة التفعيل: {info['days']} يوم\n"
                    f"تاريخ الانتهاء: {info['end_date']}\n"
                    f"الأيام المتبقية: {info['remaining_days']}"
                )
                self.activate_btn.disabled = True
                self.restart_btn.disabled = False
                return True
            else:
                self.status_label.text = reshape("الحالة: خطأ في بيانات التفعيل")
                self.status_label.gradient = GRADIENT_RED
                return False
        else:
            self.status_label.text = reshape("الحالة: غير مفعل")
            self.status_label.gradient = GRADIENT_RED
            self.details_label.text = ""
            self.activate_btn.disabled = False
            self.restart_btn.disabled = True
            return False
            
    def request_activation(self, instance):
        if not self.activation.debug_activation_process():
            self.show_message(reshape("هناك مشكلة في إعدادات التفعيل الأساسية. يرجى التحقق من السجلات."))
            return
            
        if self.activation.send_activation_request():
            self.activate_btn.disabled = True
            self.show_progress_popup()
            self.check_interval = Clock.schedule_interval(self.check_bot_response, 5)
        else:
            self.show_message(reshape("فشل في إرسال طلب التفعيل. يرجى التحقق من اتصال الإنترنت والمحاولة لاحقاً."))
            
    def show_progress_popup(self):
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        content.add_widget(Label(text=reshape("جاري انتظار رد المسؤول...", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(20)
        ))
        
        self.progress_label = Label(text=reshape("تم إرسال طلب التفعيل إلى المسؤول", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(18)
        )
        content.add_widget(self.progress_label)
        
        self.progress_popup = ModernPopup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(200)),
            auto_dismiss=False
        )
        self.progress_popup.open()
            
    def check_bot_response(self, dt):
        try:
            response = self.activation.check_bot_response()
            
            if response == "approved":
                Clock.unschedule(self.check_interval)
                self.progress_label.text = reshape(f"تمت الموافقة على طلبك! جاري التفعيل...")
                
                if self.activation.activate(self.activation.activation_days):
                    if self.activation.is_activated():
                        self.progress_label.text = reshape(f"تم التفعيل بنجاح لمدة {self.activation.activation_days} يوم!")
                        Clock.schedule_once(lambda dt: self.progress_popup.dismiss(), 2)
                        self.check_activation()
                    else:
                        self.progress_label.text = reshape("تم التفعيل ولكن التحقق فشل!")
                else:
                    self.progress_label.text = reshape("حدث خطأ أثناء التفعيل.")
                    
            elif response == "rejected":
                Clock.unschedule(self.check_interval)
                self.progress_label.text = reshape("تم رفض طلب التفعيل من قبل المسؤول.")
                Clock.schedule_once(lambda dt: self.progress_popup.dismiss(), 2)
                self.activate_btn.disabled = False
                
            elif response == "error":
                self.progress_label.text = reshape("حدث خطأ في التحقق من حالة التفعيل.")
                
        except Exception as e:
            self.progress_label.text = reshape("حدث استثناء غير متوقع")
            print(f"Exception in check_bot_response: {str(e)}")
            traceback.print_exc()
            
    def show_message(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        content.add_widget(Label(
            text=message,
            font_name="ArabicFont",
            font_size=dp(20),
            color=(0, 0, 0, 1)  # لون النص أسود ليكون واضحًا
        ))
        
        btn = ModernButton(
            text=reshape("موافق"),
            size_hint=(None, None),
            size=(dp(100), dp(50)),
            pos_hint={'center_x': 0.5},
            button_color=COLOR_PRIMARY
        )
        content.add_widget(btn)
        
        popup = ModernPopup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(200))
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()
            
    def restart_app(self, instance):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(MainMenu())

class MilkRecordsViewer(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), padding=dp(10), **kwargs)
        self.build_ui()
        
    def build_ui(self, *args):
        self.clear_widgets()
        
        # زر الرجوع
        btn_back = ModernButton(
            text=reshape("رجوع"),
            size_hint=(1, None),
            height=dp(50),
            button_color=COLOR_DANGER
        )
        btn_back.bind(on_press=lambda x: self.safe_go_back())
        self.add_widget(btn_back)
        
        # عنوان الشاشة
        self.add_widget(GradientLabel(text=reshape("السجلات المحفوظة", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(24),
            size_hint_y=None,
            height=dp(60),
            gradient=GRADIENT_BLUE
        ))
        
        # زر حذف الكل
        btn_delete_all = ModernButton(
            text=reshape("حذف جميع السجلات"),
            size_hint=(1, None),
            height=dp(50),
            button_color=COLOR_DANGER
        )
        btn_delete_all.bind(on_press=self.confirm_delete_all)
        self.add_widget(btn_delete_all)
        
        # عرض الملفات
        scroll = ModernScrollView()
        self.records_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(10)
        )
        self.records_layout.bind(minimum_height=self.records_layout.setter('height'))
        
        self.load_records()
        scroll.add_widget(self.records_layout)
        self.add_widget(scroll)
        
    def safe_go_back(self):
        """طريقة آمنة للعودة للقائمة الرئيسية"""
        try:
            app = App.get_running_app()
            if app and hasattr(app, 'root'):
                app.root.clear_widgets()
                app.root.add_widget(MainMenu())
        except Exception as e:
            print(f"Error in safe_go_back: {e}")

    def load_records(self):
        """تحميل وعرض الملفات المحفوظة"""
        records_dir = get_milk_records_path()
        if not os.path.exists(records_dir):
            os.makedirs(records_dir, exist_ok=True)
            self.records_layout.add_widget(Label(text=reshape("لا توجد سجلات محفوظة بعد", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(20),
                size_hint_y=None,
                height=dp(50),
                color=(0.5, 0, 0, 1)
            ))
            return
        
        files = sorted(
            [f for f in os.listdir(records_dir) if f.endswith('.txt')],
            key=lambda x: os.path.getmtime(os.path.join(records_dir, x)),
            reverse=True
        )
        
        if not files:
            self.records_layout.add_widget(Label(text=reshape("لا توجد سجلات محفوظة بعد", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(20),
                size_hint_y=None,
                height=dp(50),
                color=(0.5, 0, 0, 1)
            ))
            return
        
        for filename in files:
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(5))
            
            btn_view = ModernButton(
                text=reshape(filename),
                size_hint_x=0.7,
                button_color=COLOR_SECONDARY
            )
            btn_view.bind(on_press=lambda instance, f=filename: self.show_record_content(f))
            
            btn_delete = ModernButton(
                text=reshape("حذف"),
                size_hint_x=0.3,
                button_color=COLOR_DANGER
            )
            btn_delete.bind(on_press=lambda instance, f=filename: self.confirm_delete_file(f))
            
            row.add_widget(btn_view)
            row.add_widget(btn_delete)
            self.records_layout.add_widget(row)
    
    def show_record_content(self, filename):
        """عرض محتوى الملف المحدد"""
        filepath = os.path.join(get_milk_records_path(), filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # إنشاء شاشة عرض المحتوى
            self.clear_widgets()
            
            # زر الرجوع
            btn_back = ModernButton(
                text=reshape("رجوع للسجلات"),
                size_hint=(1, None),
                height=dp(50),
                button_color=COLOR_DANGER
            )
            btn_back.bind(on_press=lambda x: self.build_ui())
            self.add_widget(btn_back)
            
            # عنوان الملف
            self.add_widget(GradientLabel(text=reshape(f"سجل: {filename}", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_size=dp(22),
                size_hint_y=None,
                height=dp(50),
                gradient=GRADIENT_BLUE
            ))
            
            # محتوى الملف
            scroll = ModernScrollView()
            content_label = Label(text=reshape(content, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(18),
                size_hint_y=None,
                halign="right",
                valign="top",
                text_size=(Window.width - dp(40), None),
                color=(0, 0, 0, 1)
            )
            content_label.bind(texture_size=lambda lbl, size: setattr(lbl, 'height', size[1]))
            scroll.add_widget(content_label)
            self.add_widget(scroll)
            
        except Exception as e:
            print(f"Error reading file: {e}")
            self.show_message(reshape("حدث خطأ أثناء قراءة الملف"))

    def confirm_delete_file(self, filename):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text=reshape(f"هل أنت متأكد من حذف الملف:\n{filename}؟", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(20),
            color=(0, 0, 0, 1)  # لون النص أسود ليكون واضحًا
        ))
        
        btn_box = BoxLayout(spacing=dp(10))
        btn_yes = ModernButton(
            text=reshape("نعم"),
            button_color=COLOR_DANGER
        )
        btn_yes.bind(on_press=lambda x: (self.delete_file(filename), popup.dismiss()))
        
        btn_no = ModernButton(
            text=reshape("لا"),
            button_color=COLOR_SECONDARY
        )
        btn_no.bind(on_press=lambda x: popup.dismiss())
        
        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)
        
        popup = ModernPopup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(200))
        )
        popup.open()
    
    def delete_file(self, filename):
        filepath = os.path.join(get_milk_records_path(), filename)
        try:
            os.remove(filepath)
            self.build_ui()
            self.show_message(reshape(f"تم حذف الملف {filename} بنجاح"))
        except Exception as e:
            self.show_message(reshape(f"فشل حذف الملف: {str(e)}"))

    def confirm_delete_all(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(text=reshape("هل أنت متأكد من حذف جميع السجلات؟", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(20),
            color=(0, 0, 0, 1)  # لون النص أسود ليكون واضحًا
        ))
        
        btn_box = BoxLayout(spacing=dp(10))
        btn_yes = ModernButton(
            text=reshape("نعم"),
            button_color=COLOR_DANGER
        )
        btn_yes.bind(on_press=lambda x: (self.delete_all_records(), popup.dismiss()))
        
        btn_no = ModernButton(
            text=reshape("لا"),
            button_color=COLOR_SECONDARY
        )
        btn_no.bind(on_press=lambda x: popup.dismiss())
        
        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)
        
        popup = ModernPopup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(200))
        )
        popup.open()
    
    def delete_all_records(self):
        records_dir = get_milk_records_path()
        try:
            for filename in os.listdir(records_dir):
                filepath = os.path.join(records_dir, filename)
                if os.path.isfile(filepath):
                    os.remove(filepath)
            self.build_ui()
            self.show_message(reshape("تم حذف جميع السجلات بنجاح"))
        except Exception as e:
            self.show_message(reshape(f"فشل حذف السجلات: {str(e)}"))

    def show_message(self, message):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(Label(
            text=message,
            font_name="ArabicFont",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(50),
            color=(0, 0, 0, 1)  # لون النص أسود ليكون واضحًا
        ))
        
        btn = ModernButton(
            text=reshape("موافق"),
            size_hint=(None, None),
            size=(dp(100), dp(50)),
            pos_hint={'center_x': 0.5},
            button_color=COLOR_PRIMARY
        )
        content.add_widget(btn)
        
        popup = ModernPopup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(300), dp(200))
        )
        btn.bind(on_press=popup.dismiss)
        popup.open()

class MainMenu(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(30), padding=dp(40), **kwargs)
        self.build_ui()
    
    def build_ui(self):
        self.clear_widgets()
        
        # شريط الاتصال العلوي
        contact_bar = BoxLayout(size_hint_y=None, height=dp(40), padding=dp(5))
        contact_bar.add_widget(Label(text="+963930458096",
            font_size=dp(16, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            size_hint_x=0.5,
            halign="left"
        ))
        contact_bar.add_widget(Label(text="t.me/ssaanmm",
            font_size=dp(16, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            size_hint_x=0.5,
            halign="right"
        ))
        self.add_widget(contact_bar)
        
        # إضافة معلومات التفعيل
        activation = ActivationSystem()
        if activation.is_activated():
            info = activation.get_activation_info()
            if info:
                remaining_days = info['remaining_days']
                if remaining_days <= 5:
                    warning_label = Label(text=reshape(f"⚠️ انتبه! لقد بقي {remaining_days} أيام لانتهاء التفعيل", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                        font_name="ArabicFont",
                        font_size=dp(16),
                        color=(1, 0, 0, 1),
                        size_hint_y=None,
                        height=dp(30)
                    )
                    self.add_widget(warning_label)
                else:
                    days_label = Label(text=reshape(f"الأيام المتبقية: {remaining_days} يوم", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                        font_name="ArabicFont",
                        font_size=dp(16),
                        color=(0, 0.6, 0, 1),
                        size_hint_y=None,
                        height=dp(30)
                    )
                    self.add_widget(days_label)
        
        # عنوان التطبيق
        self.add_widget(GradientLabel(text=reshape("نظام إدارة الكميات", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(30),
            size_hint_y=None,
            height=dp(60),
            gradient=GRADIENT_BLUE
        ))
        
        # زر جمع اللبن
        milk_btn = ModernButton(
            text=reshape("إدخال الكميات"),
            font_size=dp(28),
            size_hint=(0.9, None),
            height=dp(80),
            pos_hint={'center_x': 0.5},
            button_color=COLOR_PRIMARY
        )
        milk_btn.bind(on_press=self.start_milk_app)
        self.add_widget(milk_btn)
        
        # زر تعديل الأسماء والمواد
        edit_btn = ModernButton(
            text=reshape("تعديل الأسماء والمواد"),
            font_size=dp(28),
            size_hint=(0.9, None),
            height=dp(80),
            pos_hint={'center_x': 0.5},
            button_color=COLOR_SECONDARY
        )
        edit_btn.bind(on_press=self.start_editor_app)
        self.add_widget(edit_btn)
        
        # زر عرض السجلات المحفوظة
        records_btn = ModernButton(
            text=reshape("عرض السجلات"),
            font_size=dp(28),
            size_hint=(0.9, None),
            height=dp(80),
            pos_hint={'center_x': 0.5},
            button_color=COLOR_WARNING
        )
        records_btn.bind(on_press=self.show_records)
        self.add_widget(records_btn)
    
    def start_milk_app(self, instance):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(MilkAppLayout())
    
    def start_editor_app(self, instance):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(NameEditorLayout())
    
    def show_records(self, instance):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(MilkRecordsViewer())

class MilkAppLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), padding=dp(12), **kwargs)
        self.names, self.materials, self.name_materials, self.material_types, self.material_weights = load_code_data()
        if not self.names:
            self.add_widget(Label(text=reshape("""لا يوجد أسماء زبائن للمعالجة.
الرجاء إضافتهم أولاً.""", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(22),
                color=(1, 0, 0, 1),
                halign="center",
                valign="middle"
            ))
            btn_back = ModernButton(
                text=reshape("رجوع للقائمة"),
                font_size=dp(20),
                size_hint=(0.6, None),
                height=dp(50),
                pos_hint={'center_x': 0.5},
                button_color=COLOR_WARNING
            )
            btn_back.bind(on_press=self.go_back_to_main)
            self.add_widget(btn_back)
            return
        self.index = 0
        self.preview_mode = False
        self.data = {name: {mat: 0 for mat in self.materials} for name in self.names}
        self.inputs = {}
        self.build_ui()

    def go_back_to_main(self, instance):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(MainMenu())

    def build_ui(self):
        self.clear_widgets()
        self.inputs = {}

        # إضافة اسم الزبون الحالي
        name_label = GradientLabel(text=reshape(self.names[self.index], font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30),
            gradient=GRADIENT_BLUE
        )
        self.add_widget(name_label)

        scroll = ModernScrollView()
        fields = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=None, padding=dp(8))
        fields.bind(minimum_height=fields.setter('height'))

        mat_list = self.name_materials[self.names[self.index]]

        for i, mat in enumerate(mat_list):
            fields.add_widget(Label(text=reshape(mat, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(21),
                size_hint_y=None,
                height=dp(35),
                color=(0, 0, 0, 1)
            ))

            inp = ModernTextInput(
                font_size=dp(18),
                size_hint_y=None,
                height=dp(50),
                input_filter='int',
                input_type='number',
                halign="center"
            )
            inp.text = str(self.data[self.names[self.index]][mat])
            self.inputs[mat] = inp
            fields.add_widget(inp)

            if i < len(mat_list) - 1:
                next_mat = mat_list[i + 1]
                def focus_next(instance, nxt=next_mat):
                    self.inputs[nxt].focus = True
                inp.bind(on_text_validate=focus_next)
            else:
                inp.bind(on_text_validate=self.save_and_next)

        scroll.add_widget(fields)
        self.add_widget(scroll)

        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        buttons.add_widget(ModernButton(
            text=reshape("التالي"),
            font_size=dp(18),
            on_press=self.save_and_next,
            button_color=COLOR_PRIMARY
        ))
        buttons.add_widget(ModernButton(
            text=reshape("رجوع"),
            font_size=dp(18),
            on_press=self.go_back,
            button_color=COLOR_SECONDARY
        ))
        self.add_widget(buttons)

        first_mat = mat_list[0]
        def focus_input(dt):
            self.inputs[first_mat].focus = True
        Clock.schedule_once(focus_input, 0.1)

    def save_and_next(self, instance):
        name = self.names[self.index]
        for mat, inp in self.inputs.items():
            try:
                self.data[name][mat] = max(0, int(inp.text))
            except:
                self.data[name][mat] = 0

        self.index += 1
        if self.index < len(self.names):
            self.build_ui()
        else:
            self.preview_mode = True
            self.preview_screen()

    def go_back(self, instance):
        if self.preview_mode:
            self.preview_mode = False
            self.index = len(self.names) - 1
            self.build_ui()
        elif self.index > 0:
            self.index -= 1
            self.build_ui()
        else:
            app = App.get_running_app()
            app.root.clear_widgets()
            app.root.add_widget(MainMenu())

    def preview_screen(self):
        self.clear_widgets()
        scroll = ModernScrollView()
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(15), padding=dp(10))
        layout.bind(minimum_height=layout.setter('height'))

        for name in self.names:
            box = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(6), size_hint_y=None)
            box.bind(minimum_height=box.setter('height'))

            box.add_widget(GradientLabel(text=reshape(name, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_size=dp(20),
                size_hint_y=None,
                height=dp(30),
                gradient=GRADIENT_BLUE
            ))
            for mat in self.name_materials[name]:
                qty = self.data[name][mat]
                if self.material_types.get(mat) == "وزن":
                    weight = qty * self.material_weights.get(mat, 1.0)
                    mat_text = reshape(f"{mat}: {qty} (كجم: {weight:.3f})")
                else:
                    mat_text = reshape(f"{mat}: {qty}")
                
                box.add_widget(Label(
                    text=mat_text,
                    font_name="ArabicFont",
                    font_size=dp(18),
                    color=(0, 0, 0, 1),
                    size_hint_y=None,
                    height=dp(25)
                ))
            layout.add_widget(box)

        layout.add_widget(GradientLabel(text=reshape("المجاميع النهائية:", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(20),
            size_hint_y=None,
            height=dp(35),
            gradient=GRADIENT_BLUE
        ))
        for mat in self.materials:
            total = sum(self.data[name][mat] for name in self.names if mat in self.name_materials[name])
            if self.material_types.get(mat) == "وزن":
                weight = total * self.material_weights.get(mat, 1.0)
                mat_text = reshape(f"{mat}: {total} (كجم: {weight:.3f})")
            else:
                mat_text = reshape(f"{mat}: {total}")
                
            layout.add_widget(Label(
                text=mat_text,
                font_name="ArabicFont",
                font_size=dp(18),
                color=(0, 0, 0, 1),
                size_hint_y=None,
                height=dp(25)
            ))

        scroll.add_widget(layout)
        self.add_widget(scroll)

        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
        buttons.add_widget(ModernButton(
            text=reshape("حفظ"),
            on_press=self.save_file,
            button_color=COLOR_PRIMARY
        ))
        buttons.add_widget(ModernButton(
            text=reshape("رجوع للتعديل"),
            on_press=self.go_back,
            button_color=COLOR_SECONDARY
        ))
        self.add_widget(buttons)

    def save_file(self, *args):
        output = []
        for name in self.names:
            output.append(f"{name}:")
            for mat in self.name_materials.get(name, []):
                qty = self.data[name][mat]
                if self.material_types.get(mat) == "وزن":
                    weight = qty * self.material_weights.get(mat, 1.0)
                    line = f"{mat}: {qty} (كجم: {weight:.3f})"
                else:
                    line = f"{mat}: {qty}"
                output.append(line)
            output.append("-" * 40)

        output.append("المجاميع النهائية:")
        for mat in self.materials:
            total = sum(self.data[name][mat] for name in self.names if mat in self.name_materials[name])
            if self.material_types.get(mat) == "وزن":
                weight = total * self.material_weights.get(mat, 1.0)
                line = f"{mat}: {total} (كجم: {weight:.3f})"
            else:
                line = f"{mat}: {total}"
            output.append(line)

        now = datetime.now()
        days = ["الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت", "الأحد"]
        filename = f"{days[now.weekday()]}_{now.strftime('%d-%m-%Y')}.txt"
        save_dir = get_milk_records_path()
        os.makedirs(save_dir, exist_ok=True)

        with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
            f.write("\n".join(output))

        self.clear_widgets()
        self.add_widget(Label(text=reshape(f"تم حفظ الملف:\n{filename}", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(20),
            color=(0, 0, 0, 1)
        ))
        
        btn_back = ModernButton(
            text=reshape("العودة للقائمة الرئيسية"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_PRIMARY
        )
        btn_back.bind(on_press=lambda x: self.go_back(None))
        self.add_widget(btn_back)

class NameEditorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', spacing=dp(10), padding=dp(10), **kwargs)
        self.names, self.materials, self.name_materials, self.material_types, self.material_weights = load_code_data()
        self.main_menu()

    def clear_root(self):
        self.clear_widgets()

    def main_menu(self):
        self.clear_root()
        self.add_widget(GradientLabel(text=reshape("قائمة الخيارات", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(22),
            size_hint_y=None,
            height=dp(40),
            gradient=GRADIENT_BLUE
        ))

        options = [
            ("إضافة اسم جديد مع المواد", self.add_new_name),
            ("تعديل مواد لاسم موجود", self.modify_existing),
            ("حذف اسم مع المواد", self.delete_name),
            ("إدارة المواد (إضافة/حذف)", self.manage_materials),
            ("عرض جميع الأسماء والمواد", self.show_all),
            ("رجوع للقائمة الرئيسية", self.back_to_main)
        ]

        for text, callback in options:
            btn = ModernButton(
                text=reshape(text),
                font_size=dp(18),
                size_hint_y=None,
                height=dp(50),
                button_color=COLOR_PRIMARY
            )
            btn.bind(on_press=lambda inst, cb=callback: cb())
            self.add_widget(btn)

    def back_to_main(self):
        app = App.get_running_app()
        app.root.clear_widgets()
        app.root.add_widget(MainMenu())

    def add_new_name(self):
        self.clear_root()
        self.add_widget(Label(text=reshape("أدخل اسم الزبون", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            color=(0, 0, 0, 1)
        ))
        self.name_input = ModernTextInput(
            font_size=dp(18),
            size_hint_y=None,
            height=dp(50),
            text=reshape("")
        )
        self.add_widget(self.name_input)
        
        btn_save = ModernButton(
            text=reshape("حفظ"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_PRIMARY
        )
        btn_save.bind(on_press=self.save_new_name)
        self.add_widget(btn_save)

        btn_back = ModernButton(
            text=reshape("رجوع"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_SECONDARY
        )
        btn_back.bind(on_press=lambda x: self.main_menu())
        self.add_widget(btn_back)

    def save_new_name(self, instance):
        name = self.name_input.text.strip()
        if name and name not in self.names:
            self.names.append(name)
            self.name_materials[name] = []
            save_code_data(self.names, self.materials, self.name_materials, self.material_types, self.material_weights)
        self.edit_materials(name)

    def modify_existing(self):
        self.clear_root()
        self.add_widget(Label(text=reshape("اختر اسماً للتعديل", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            color=(0, 0, 0, 1)
        ))
        scroll = ModernScrollView()
        box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(10)
        )
        box.bind(minimum_height=box.setter('height'))

        for name in self.names:
            btn = ModernButton(
                text=reshape(name),
                size_hint_y=None,
                height=dp(50),
                button_color=COLOR_PRIMARY
            )
            btn.bind(on_press=lambda inst, nm=name: self.edit_materials(nm))
            box.add_widget(btn)

        scroll.add_widget(box)
        self.add_widget(scroll)

        btn_back = ModernButton(
            text=reshape("رجوع"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_SECONDARY
        )
        btn_back.bind(on_press=lambda x: self.main_menu())
        self.add_widget(btn_back)

    def delete_name(self):
        self.clear_root()
        self.add_widget(Label(text=reshape("اختر اسماً للحذف", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            color=(0, 0, 0, 1)
        ))
        
        scroll = ModernScrollView()
        box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(10)
        )
        box.bind(minimum_height=box.setter('height'))
        
        for name in self.names:
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            row.add_widget(Label(text=reshape(name, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(18),
                size_hint_x=0.7,
                color=(0, 0, 0, 1)
            ))
            
            delete_btn = ModernButton(
                text=reshape("حذف"),
                button_color=COLOR_DANGER,
                size_hint_x=0.3
            )
            delete_btn.bind(on_press=lambda inst, nm=name: self.confirm_delete(nm))
            row.add_widget(delete_btn)
            
            box.add_widget(row)
        
        scroll.add_widget(box)
        self.add_widget(scroll)
        
        btn_back = ModernButton(
            text=reshape("رجوع"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_SECONDARY
        )
        btn_back.bind(on_press=lambda x: self.main_menu())
        self.add_widget(btn_back)

    def confirm_delete(self, name):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        content.add_widget(Label(text=reshape(f"هل أنت متأكد من حذف '{name}'؟", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(22),
            color=(0, 0, 0, 1)  # لون النص أسود ليكون واضحًا
        ))
        
        btn_box = BoxLayout(spacing=dp(20))
        btn_yes = ModernButton(
            text=reshape("نعم"),
            button_color=COLOR_DANGER
        )
        btn_yes.bind(on_press=lambda x: self.perform_delete(name, popup))
        
        btn_no = ModernButton(
            text=reshape("لا"),
            button_color=COLOR_SECONDARY
        )
        btn_no.bind(on_press=lambda x: popup.dismiss())
        
        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)
        
        popup = ModernPopup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(200))
        )
        popup.open()

    def perform_delete(self, name, popup):
        if name in self.names:
            self.names.remove(name)
        if name in self.name_materials:
            del self.name_materials[name]
        
        save_code_data(self.names, self.materials, self.name_materials, self.material_types, self.material_weights)
        popup.dismiss()
        self.delete_name()

    def manage_materials(self):
        self.clear_root()
        self.add_widget(GradientLabel(text=reshape("إدارة المواد", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(22),
            size_hint_y=None,
            height=dp(40),
            gradient=GRADIENT_BLUE
        ))
        
        self.add_widget(Label(text=reshape("إضافة مادة جديدة:", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1)
        ))
        
        self.new_material_input = ModernTextInput(
            font_size=dp(18),
            size_hint_y=None,
            height=dp(50),
            text=reshape("")
        )
        self.add_widget(self.new_material_input)
        
        add_btn = ModernButton(
            text=reshape("إضافة مادة"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_PRIMARY
        )
        add_btn.bind(on_press=self.add_new_material)
        self.add_widget(add_btn)
        
        self.add_widget(Label(text=reshape("حذف مادة موجودة:", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(18),
            size_hint_y=None,
            height=dp(30),
            color=(0, 0, 0, 1)
        ))
        
        scroll = ModernScrollView()
        box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(5),
            padding=dp(10)
        )
        box.bind(minimum_height=box.setter('height'))
        
        for material in self.materials:
            row = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(10))
            row.add_widget(Label(text=reshape(material, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(18),
                size_hint_x=0.7,
                color=(0, 0, 0, 1)
            ))
            
            delete_btn = ModernButton(
                text=reshape("حذف"),
                button_color=COLOR_DANGER,
                size_hint_x=0.3
            )
            delete_btn.bind(on_press=lambda inst, mat=material: self.confirm_delete_material(mat))
            row.add_widget(delete_btn)
            
            box.add_widget(row)
        
        scroll.add_widget(box)
        self.add_widget(scroll)
        
        btn_back = ModernButton(
            text=reshape("رجوع"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_SECONDARY
        )
        btn_back.bind(on_press=lambda x: self.main_menu())
        self.add_widget(btn_back)

    def add_new_material(self, instance):
        new_material = self.new_material_input.text.strip()
        if new_material and new_material not in self.materials:
            content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
            content.add_widget(Label(text=reshape(f"اختر نوع المادة '{new_material}'", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(22),
                color=(0, 0, 0, 1)  # لون النص أسود ليكون واضحًا
            ))
            
            btn_type_count = ModernButton(
                text=reshape("عدد"),
                button_color=COLOR_PRIMARY
            )
            btn_type_weight = ModernButton(
                text=reshape("وزن"),
                button_color=COLOR_SECONDARY
            )
            
            content.add_widget(btn_type_count)
            content.add_widget(btn_type_weight)
            
            popup = ModernPopup(
                title="",
                content=content,
                size_hint=(None, None),
                size=(dp(350), dp(200))
            )
            
            def set_type(m_type):
                self.materials.append(new_material)
                self.material_types[new_material] = m_type
                if m_type == "وزن":
                    self.get_material_weight(new_material, popup)
                else:
                    self.material_weights[new_material] = 1.0
                    save_code_data(self.names, self.materials, self.name_materials, self.material_types, self.material_weights)
                    popup.dismiss()
                    self.manage_materials()
            
            btn_type_count.bind(on_press=lambda x: set_type("عدد"))
            btn_type_weight.bind(on_press=lambda x: set_type("وزن"))
            popup.open()

    def get_material_weight(self, material, prev_popup):
        prev_popup.dismiss()
        content = BoxLayout(orientation='vertical', spacing=dp(20), padding=dp(20))
        content.add_widget(Label(text=reshape(f"أدخل وزن الوحدة للمادة '{material}' (كجم, font_name='fonts/ArabicFont.ttf', halign='right', valign='top')"),
            font_name="ArabicFont",
            font_size=dp(22),
            color=(0, 0, 0, 1)  # لون النص أسود ليكون واضحًا
        ))
        
        weight_input = ModernTextInput(
            input_filter='float',
            multiline=False
        )
        
        btn_save = ModernButton(
            text=reshape("حفظ"),
            button_color=COLOR_PRIMARY
        )
        
        content.add_widget(weight_input)
        content.add_widget(btn_save)
        
        popup = ModernPopup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(200))
        )
        
        def save_weight(instance):
            try:
                weight = float(weight_input.text)
                self.material_weights[material] = weight
                save_code_data(self.names, self.materials, self.name_materials, self.material_types, self.material_weights)
                popup.dismiss()
                self.manage_materials()
            except ValueError:
                pass
        
        btn_save.bind(on_press=save_weight)
        popup.open()

    def confirm_delete_material(self, material):
        content = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(20))
        content.add_widget(Label(text=reshape(f"هل أنت متأكد من حذف '{material}'؟", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_name="ArabicFont",
            font_size=dp(22),
            color=(0, 0, 0, 1)  # لون النص أسود ليكون واضحًا
        ))
        
        btn_box = BoxLayout(spacing=dp(20))
        btn_yes = ModernButton(
            text=reshape("نعم"),
            button_color=COLOR_DANGER
        )
        btn_yes.bind(on_press=lambda x: self.perform_delete_material(material, popup))
        
        btn_no = ModernButton(
            text=reshape("لا"),
            button_color=COLOR_SECONDARY
        )
        btn_no.bind(on_press=lambda x: popup.dismiss())
        
        btn_box.add_widget(btn_yes)
        btn_box.add_widget(btn_no)
        content.add_widget(btn_box)
        
        popup = ModernPopup(
            title="",
            content=content,
            size_hint=(None, None),
            size=(dp(350), dp(200))
        )
        popup.open()

    def perform_delete_material(self, material, popup):
        if material in self.materials:
            self.materials.remove(material)
            
            for name in self.name_materials:
                if material in self.name_materials[name]:
                    self.name_materials[name].remove(material)
        
        save_code_data(self.names, self.materials, self.name_materials, self.material_types, self.material_weights)
        popup.dismiss()
        self.manage_materials()

    def edit_materials(self, name):
        self.clear_root()
        self.add_widget(GradientLabel(text=reshape(name, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            gradient=GRADIENT_BLUE
        ))
        selected = set(self.name_materials.get(name, []))
        self.mat_btns = {}

        for mat in self.materials:
            btn = ModernButton(
                text=reshape(mat),
                size_hint_y=None,
                height=dp(45),
                button_color=COLOR_SECONDARY if mat in selected else [0.8, 0.8, 0.8, 1]
            )
            btn.bind(on_press=lambda inst, m=mat: self.toggle_material(name, m))
            self.mat_btns[mat] = btn
            self.add_widget(btn)

        btn_save = ModernButton(
            text=reshape("حفظ"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_PRIMARY
        )
        btn_save.bind(on_press=lambda x: (save_code_data(self.names, self.materials, self.name_materials, self.material_types, self.material_weights), self.main_menu()))
        self.add_widget(btn_save)

        btn_back = ModernButton(
            text=reshape("رجوع"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_SECONDARY
        )
        btn_back.bind(on_press=lambda x: self.main_menu())
        self.add_widget(btn_back)

    def toggle_material(self, name, mat):
        if mat in self.name_materials[name]:
            self.name_materials[name].remove(mat)
            self.mat_btns[mat].button_color = [0.8, 0.8, 0.8, 1]
        else:
            self.name_materials[name].append(mat)
            self.mat_btns[mat].button_color = COLOR_SECONDARY
        save_code_data(self.names, self.materials, self.name_materials, self.material_types, self.material_weights)

    def show_all(self):
        self.clear_root()
        self.add_widget(GradientLabel(text=reshape("جميع الزبائن والمواد", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
            font_size=dp(20),
            size_hint_y=None,
            height=dp(40),
            gradient=GRADIENT_BLUE
        ))
        scroll = ModernScrollView()
        box = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=dp(8),
            padding=dp(10)
        )
        box.bind(minimum_height=box.setter('height'))

        for name in self.names:
            box.add_widget(Label(text=reshape(name, font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                font_name="ArabicFont",
                font_size=dp(18),
                color=(0, 0.2, 0.6, 1),
                size_hint_y=None,
                height=dp(30)
            ))
            for mat in self.name_materials.get(name, []):
                box.add_widget(Label(text=reshape(f"\u2022 {mat}", font_name='fonts/ArabicFont.ttf', halign='right', valign='top'),
                    font_name="ArabicFont",
                    font_size=dp(16),
                    color=(0, 0, 0, 1),
                    size_hint_y=None,
                    height=dp(25)
                ))

        scroll.add_widget(box)
        self.add_widget(scroll)

        btn_back = ModernButton(
            text=reshape("رجوع"),
            size_hint_y=None,
            height=dp(50),
            button_color=COLOR_SECONDARY
        )
        btn_back.bind(on_press=lambda x: self.main_menu())
        self.add_widget(btn_back)

# === التطبيق الرئيسي ===
class MilkApp(App):
    def build(self):
        # إنشاء المجلدات المطلوبة عند التشغيل
        ensure_data_directory()
        os.makedirs(get_milk_records_path(), exist_ok=True)
        
        # تحميل الخط إذا لم يكن موجودًا
        download_font()
        
        self.root = BoxLayout()
        activation = ActivationSystem()
        if not activation.is_activated():
            self.root.add_widget(ActivationScreen())
        else:
            self.root.add_widget(MainMenu())
        return self.root

if __name__ == "__main__":
    MilkApp().run()
