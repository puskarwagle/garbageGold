import os
import json
from time import sleep
from random import randint
from datetime import datetime, timedelta
from pyautogui import alert

from .logger import log, log_error


def make_directories(paths: list[str]) -> None:
    for path in paths:
        path = path.replace("//", "/")
        if '/' in path and '.' in path:
            path = path[:path.rfind('/')]
        try:
            if not os.path.exists(path):
                os.makedirs(path)
                log(f"✅ Created directory: {path}")
            else:
                log(f"📁 Directory already exists: {path}")
        except Exception as e:
            log_error(e, f"❌ Error while creating directory: {path}")


def find_default_profile_directory() -> str | None:
    default_locations = [
        r"%LOCALAPPDATA%\Google\Chrome\User Data",
        r"%USERPROFILE%\AppData\Local\Google\Chrome\User Data",
        r"%USERPROFILE%\Local Settings\Application Data\Google\Chrome\User Data"
    ]
    for location in default_locations:
        profile_dir = os.path.expandvars(location)
        if os.path.exists(profile_dir):
            log(f"✅ Found Chrome profile directory: {profile_dir}")
            return profile_dir
    log("❌ No default Chrome profile directories found")
    return None


def buffer(speed: int = 0) -> None:
    if speed <= 0:
        return
    elif speed <= 2:
        delay = randint(6, 18) * 0.1
    else:
        delay = randint(18, round(speed) * 10) * 0.1
    log(f"⏳ Buffer delay: {round(delay, 2)} seconds")
    sleep(delay)


def manual_login_retry(is_logged_in: callable, limit: int = 2) -> None:
    count = 0
    while not is_logged_in():
        log("⚠️  Not logged into LinkedIn. Prompting user to confirm login...")
        button = "Confirm Login"
        message = f'Please login and click "{button}" below.'
        if count > limit:
            button = "Skip Confirmation"
            message = f'If already logged in but still seeing this, click "{button}".'
        count += 1
        result = alert(message, "Login Required", button)
        if result and count > limit:
            return


def calculate_date_posted(time_string: str) -> datetime | None:
    try:
        time_string = time_string.strip()
        now = datetime.now()
        unit_map = {
            "second": ("seconds", 1),
            "minute": ("minutes", 1),
            "hour": ("hours", 1),
            "day": ("days", 1),
            "week": ("weeks", 1),
            "month": ("days", 30),
            "year": ("days", 365)
        }

        for unit, (delta_attr, multiplier) in unit_map.items():
            if unit in time_string:
                value = int(time_string.split()[0])
                delta = timedelta(**{delta_attr: value * multiplier})
                result = now - delta
                log(f"📅 Parsed posting date '{time_string}' as {result.strftime('%Y-%m-%d %H:%M')}")
                return result

        log(f"⚠️ Could not parse time string: {time_string}")
        return None
    except Exception as e:
        log_error(e, f"❌ Failed to calculate posting date from string: {time_string}")
        return None


def convert_to_lakhs(value: str) -> str:
    value = value.strip()
    l = len(value)
    result = "0.00"
    try:
        if l > 0:
            if l > 5:
                result = value[:l - 5] + "." + value[l - 5:l - 3]
            else:
                result = "0." + "0" * (5 - l) + value[:2]
        log(f"₹ Converted '{value}' to lakhs: {result}")
        return result
    except Exception as e:
        log_error(e, f"❌ Failed to convert value to lakhs: {value}")
        return result


def convert_to_json(data) -> dict:
    try:
        result_json = json.loads(data)
        log("✅ Successfully parsed JSON")
        return result_json
    except json.JSONDecodeError as e:
        log_error(e, "❌ Unable to parse JSON data")
        return {"error": "Unable to parse the response as JSON", "data": data}
