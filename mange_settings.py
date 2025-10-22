import json
import os

SETTINGS_FILE = "settings.json"

# ✅ القيم الافتراضية
DEFAULT_SETTINGS = {
    "ways_to_send": {
        "google_contacts": True,
        "chat_me_link": True,
        "chat_me_number": False,
    }
}


# ==========================
# 🔹 تحميل الإعدادات
# ==========================
def load_settings() -> dict:
    """تحميل الإعدادات من الملف أو من القيم الافتراضية إذا لم يكن موجود."""
    if not os.path.exists(SETTINGS_FILE):
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        # ✅ إكمال أي مفاتيح ناقصة من الافتراضي
        data = _merge_with_defaults(data, DEFAULT_SETTINGS)
        return data

    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()


# ==========================
# 🔹 حفظ الإعدادات
# ==========================
def save_settings(settings: dict):
    """حفظ الإعدادات الحالية في ملف JSON."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
        print("✅ Settings saved.")
    except Exception as e:
        print(f"❌ Error saving settings: {e}")


# ==========================
# 🔹 قراءة قيمة إعداد
# ==========================
def get_setting(key_path: str, default=None):
    """
    قراءة قيمة إعداد معينة باستخدام path مثل:
    get_setting("ways_to_send.google_contacts")
    """
    settings = load_settings()
    keys = key_path.split(".")
    current = settings
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return default
    return current if current is not None else default


# ==========================
# 🔹 تعديل قيمة إعداد
# ==========================
def set_setting(key_path: str, value):
    """
    تعديل إعداد معين وحفظ التغيير في الملف.
    مثال: set_setting("ways_to_send.chat_me_link", False)
    """
    settings = load_settings()
    keys = key_path.split(".")
    current = settings

    for key in keys[:-1]:
        current = current.setdefault(key, {})

    current[keys[-1]] = value
    save_settings(settings)
    return settings


# ==========================
# 🔹 إعادة تعيين القيم الافتراضية
# ==========================
def reset_settings():
    """إرجاع جميع الإعدادات إلى القيم الافتراضية."""
    save_settings(DEFAULT_SETTINGS)
    print("🔄 Settings reset to default.")
    return DEFAULT_SETTINGS.copy()


# ==========================
# 🔹 أداة داخلية: دمج القيم الناقصة
# ==========================
def _merge_with_defaults(data: dict, defaults: dict) -> dict:
    """دمج القيم الناقصة من الافتراضي داخل البيانات الموجودة."""
    merged = defaults.copy()
    for key, value in defaults.items():
        if key in data:
            if isinstance(value, dict):
                merged[key] = _merge_with_defaults(data[key], value)
            else:
                merged[key] = data[key]
    # أضف أي مفاتيح أخرى غير موجودة في الافتراضي
    for key, value in data.items():
        if key not in merged:
            merged[key] = value
    return merged
