from botasaurus.browser import Driver
import json
import time 
import pyautogui
import random
from pathlib import Path
from typing import Any, Dict, Optional
import sys



def write_safe_message(driver, message: str, prefer: str = "chat"):
    """
    يكتب الرسالة في مربع الدردشة أو في البحث حسب الاختيار.
    🔸 prefer = "chat" -> يكتب في مربع الرسائل
    🔸 prefer = "search" -> يكتب في مربع البحث

    الدالة:
      - آمنة ضد البان ✅
      - تكتب الحروف بترتيب صحيح ✅
      - تدعم السطور الجديدة واللينكات والإيموجي ✅
      - تمنع الكتابة في search بالغلط ✅
    """

    # تنظيف الرسالة من الرموز الخاصة قبل تمريرها لـ JS
    safe_message = (
        message.replace("\\", "\\\\")
               .replace("`", "\\`")
               .replace("$", "\\$")
               .replace("\r", "")
    )

    js = f"""
    (function() {{
        const prefer = "{prefer}";
        const text = `{safe_message}`;
        const lines = text.split(/\\n/g);
        let input = null;

        // تحديد المربع المناسب (بحث أو شات)
        const boxes = Array.from(document.querySelectorAll('div[contenteditable="true"][role="textbox"]'));
        for (const el of boxes) {{
            const lbl = (el.getAttribute('aria-label') || '').toLowerCase();
            const ph = (el.getAttribute('aria-placeholder') || '').toLowerCase();
            const isSearch = lbl.includes('search') || ph.includes('search');
            const isChat = el.closest('#main') !== null;

            if (prefer === "chat" && isChat) {{
                input = el;
                break;
            }}
            if (prefer === "search" && isSearch) {{
                input = el;
                break;
            }}
        }}

        if (!input) {{
            console.warn("⚠️ write_safe_message_v2: لم يتم العثور على صندوق الكتابة");
            return {{ ok: false, reason: "no-input" }};
        }}

        // تجهيز الصندوق
        input.focus();
        input.textContent = "";
        const sel = window.getSelection();
        sel.removeAllRanges();
        const range = document.createRange();
        range.selectNodeContents(input);
        range.collapse(false);
        sel.addRange(range);

        // دالة لكتابة حرف بحرف بشكل طبيعي
        function typeChar(ch, done) {{
            const before = new InputEvent('beforeinput', {{
                bubbles: true,
                data: ch,
                inputType: 'insertText'
            }});
            const inputEvt = new InputEvent('input', {{
                bubbles: true,
                data: ch,
                inputType: 'insertText'
            }});
            input.dispatchEvent(before);
            document.execCommand('insertText', false, ch);
            input.dispatchEvent(inputEvt);
            if (done) done();
        }}

        // دالة لكتابة الأسطر واحد ورا التاني
        function typeAllLines(i = 0) {{
            if (i >= lines.length) {{
                input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                return;
            }}
            const line = lines[i];
            let j = 0;

            function typeNextChar() {{
                if (j >= line.length) {{
                    if (i < lines.length - 1) {{
                        document.execCommand('insertLineBreak');
                    }}
                    setTimeout(() => typeAllLines(i + 1), 120 + Math.random() * 120);
                    return;
                }}
                const ch = line[j];
                j++;
                typeChar(ch, () => {{
                    setTimeout(typeNextChar, 40 + Math.random() * 60);
                }});
            }}

            typeNextChar();
        }}

        typeAllLines();
        return {{ ok: true }};
    }})();
    """

    try:
        return driver.run_js(js)
    except Exception as e:
        print("❌ JS Error in write_safe_message_v2:", e)
        return {"ok": False, "error": str(e)}







def read_json():
    with open("locations.json", "r") as file:
        json_data = json.load(file)
        return json_data


def moving_for_duration(duration_seconds):
    start_time = time.time()
    screenW, screenH = pyautogui.size()
    while time.time() - start_time < duration_seconds:
        x = random.randint(0, screenW - 1)
        y = random.randint(0, screenH - 1)
        duration = random.uniform(0.2, 1.0)
        pyautogui.moveTo(x, y, duration=duration, _pause=False)
        time.sleep(random.uniform(0.5, 2.0))
        time.sleep(1)

    print("Time finished")


def get_program_dir() -> Path:
    """ترجع المسار الحقيقي للبرنامج (حتى بعد التحزيم)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def ensure_profiles_folder(base_dir: Optional[str] = None) -> Path:
    """ينشئ أو يرجع فولدر profiles في نفس مسار البرنامج أو base_dir."""
    base = Path(base_dir) if base_dir else get_program_dir()
    profiles = base / "profiles"
    profiles.mkdir(parents=True, exist_ok=True)
    return profiles


def normalize_phone(phone: str) -> str:
    return "".join(ch for ch in str(phone) if ch.isdigit())


def get_profile(data: Any, base_dir: Optional[str] = None) -> Optional[str]:
    try:
        if isinstance(data, dict):
            phone = data.get("phone_number") or data.get("sender_phone")
            if not phone:
                return None
            safe = normalize_phone(phone)
            profiles_dir = ensure_profiles_folder(base_dir)
            profile_path = profiles_dir / safe
            profile_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Using profile path: {profile_path}")
            return str(profile_path.resolve())
    except Exception as e:
        print(f"⚠️ Error in get_profile: {e}")
    return None


def make_data_item(
    phone: str, extra: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    item = {
        "phone_number": str(phone),
        "profile": normalize_phone(phone),
    }
    if extra:
        item.update(extra)
    return item
