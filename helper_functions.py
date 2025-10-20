from botasaurus.browser import Driver
import json
import time
import pyautogui
import random
from pathlib import Path
from typing import Any, Dict, Optional
import sys


def write_message(driver: Driver, message: str, is_message: bool):
    driver.run_js(
        f"""
        const input = document.querySelector('div[contenteditable="true"][role="textbox"][data-tab="{'10' if is_message else '3'}"]');
        const dataTransfer = new DataTransfer();
        dataTransfer.setData('text', `{message}`);

        const event = new ClipboardEvent('paste', {{
            clipboardData: dataTransfer,
            bubbles: true
        }});

        input.focus();
        input.dispatchEvent(event);
    """
    )


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
