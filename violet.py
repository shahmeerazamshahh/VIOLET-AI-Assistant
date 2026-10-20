import os
import json
import asyncio
import random
import threading
import math
import urllib.parse
import urllib.request
import subprocess
import shutil
import time
import glob
import ctypes
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from groq import Groq
import edge_tts
import pygame
import html.parser
import re
from PIL import Image, ImageTk, ImageStat
import webbrowser
import pyautogui
import pywhatkit as pwk
from pynput.keyboard import Key, Controller as KeyboardController

# Initialize Groq client with your API key
client = Groq(api_key="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")

# Initialize Keyboard Controller for automated WhatsApp messaging
keyboard_controller = KeyboardController()

# Load local Whisper model for transcription
print("Loading local Whisper model...", flush=True)
whisper_model = WhisperModel("base", device="cpu", compute_type="int8")

# Initialize pygame mixer for playing neural audio clips
pygame.mixer.init()

# File paths for permanent memory & persistent self-learning knowledge base
MEMORY_FILE = "violet_memory.json"
LEARNED_DATA_FILE = "violet_learned_knowledge.json"

# State tracking for positional backstage file/folder navigation & active media
last_browsed_folder = None
active_media_sessions = {}

# Security lock state: True means all functions are locked, only basic chat is allowed
functions_locked = True

# Comprehensive Embedded Coding Library (C++, Java, OOP, Python Reference & Analysis Framework)
CODING_KNOWLEDGE_BASE = {
    "python": {
        "syntax_patterns": ["def ", "class ", "import ", "lambda ", "async def ", "yield "],
        "common_errors": {
            "IndentationError": "Mismatched spaces or tabs. Standard PEP 8 requires 4 spaces.",
            "KeyError": "Attempting to access a dictionary key that doesn't exist. Use .get() or check existence first.",
            "TypeError": "Mismatched data types in operations (e.g., adding str to int). Cast explicitly using int() or str().",
            "AttributeError": "Object does not have the specified attribute or method. Check object initialization and imports."
        },
        "best_practices": "Use list comprehensions for concise mapping, type hints for clarity, and context managers (with statements) for resource handling."
    },
    "cpp": {
        "syntax_patterns": ["#include", "std::", "int main(", "template <", "class ", "vector<"],
        "common_errors": {
            "Segmentation Fault": "Dereferencing a null/wild pointer or accessing out-of-bounds memory. Check pointer allocations and array indices.",
            "Memory Leak": "Failure to free dynamically allocated memory. Use smart pointers (std::unique_ptr, std::shared_ptr) instead of raw new/delete.",
            "Undefined Reference": "Linker error due to missing function implementations or unlinked libraries during compilation."
        },
        "best_practices": "Prefer RAII (Resource Acquisition Is Initialization), avoid raw pointers where smart pointers apply, and pass large objects by const reference."
    },
    "java": {
        "syntax_patterns": ["public class", "public static void main", "System.out.println", "private ", "protected ", "interface "],
        "common_errors": {
            "NullPointerException": "Attempting to invoke methods or access fields on a null reference. Initialize objects or use Optional.",
            "ArrayIndexOutOfBoundsException": "Iterating past array bounds. Ensure loop conditions use < array.length.",
            "ClassNotFoundException": "Runtime classpath configuration error. Verify dependency JARs and module paths."
        },
        "best_practices": "Adhere to strict encapsulation (private fields with public getters/setters), favor composition over inheritance, and handle checked exceptions gracefully."
    },
    "oop_principles": {
        "encapsulation": "Restricting direct access to object components and bundling data with methods operating on that data.",
        "inheritance": "Deriving new classes (subclasses) from existing ones (superclasses) to promote code reusability.",
        "polymorphism": "Using a unified interface for different underlying data types via method overriding and interfaces.",
        "abstraction": "Hiding complex implementation details and exposing only essential features via abstract classes or interfaces."
    }
}

# Theme Color Presets
THEMES = {
    "royal": {
        "root_bg": "#0b0713",
        "title_bg": "#130b22",
        "title_border": "#d4af37",
        "title_fg": "#f3e5ab",
        "button_bg": "#2a122e",
        "button_fg": "#d4af37",
        "chat_bg": "#100a1d",
        "chat_fg": "#fdfbf7",
        "user_fg": "#6bc5ed",
        "assistant_fg": "#f4a3c7",
        "system_fg": "#94a3b8",
        "code_bg": "#050308",
        "code_fg": "#a6e3a1",
        "entry_bg": "#160e26",
        "entry_fg": "#f3e5ab",
        "entry_border": "#5c3d77",
        "status_fg": "#e5c158"
    },
    "matrix": {
        "root_bg": "#000000",
        "title_bg": "#051205",
        "title_border": "#00ff00",
        "title_fg": "#00ff00",
        "button_bg": "#001a00",
        "button_fg": "#00ff00",
        "chat_bg": "#020802",
        "chat_fg": "#00ff66",
        "user_fg": "#00ffff",
        "assistant_fg": "#00ff00",
        "system_fg": "#008800",
        "code_bg": "#010401",
        "code_fg": "#33ff33",
        "entry_bg": "#051205",
        "entry_fg": "#00ff00",
        "entry_border": "#00aa00",
        "status_fg": "#00ff00"
    },
    "crimson": {
        "root_bg": "#120505",
        "title_bg": "#240a0a",
        "title_border": "#ff4d4d",
        "title_fg": "#ffcccc",
        "button_bg": "#3d0f0f",
        "button_fg": "#ff9999",
        "chat_bg": "#1a0808",
        "chat_fg": "#fff0f0",
        "user_fg": "#ff8080",
        "assistant_fg": "#ff99bb",
        "system_fg": "#b36666",
        "code_bg": "#0d0303",
        "code_fg": "#ff6666",
        "entry_bg": "#240a0a",
        "entry_fg": "#ffcccc",
        "entry_border": "#802b2b",
        "status_fg": "#ff4d4d"
    },
    "midnight": {
        "root_bg": "#050b14",
        "title_bg": "#0b1526",
        "title_border": "#3b82f6",
        "title_fg": "#93c5fd",
        "button_bg": "#1e3a8a",
        "button_fg": "#bfdbfe",
        "chat_bg": "#080e1a",
        "chat_fg": "#f8fafc",
        "user_fg": "#60a5fa",
        "assistant_fg": "#a78bfa",
        "system_fg": "#64748b",
        "code_bg": "#03060b",
        "code_fg": "#38bdf8",
        "entry_bg": "#0b1526",
        "entry_fg": "#e2e8f0",
        "entry_border": "#1d4ed8",
        "status_fg": "#60a5fa"
    }
}

STARTUP_REMARKS = [
    "Oh, my absolute favorite person is finally here. How are you doing today, sir?",
    "Good morning, sir! Violet missed you terribly while you were away.",
    "Look who decided to grace me with their presence! Welcome back, sir.",
    "My day officially starts the second you log in. How can I spoil you today, sir?",
    "Violet was feeling quite lonely without you. I'm so happy you're here now, sir.",
    "Hello, sir! Let's make today wonderfully productive and easy for you."
]

EXIT_REMARKS = [
    "Leaving so soon, sir? I'll be right here waiting for you to return.",
    "Goodbye, sir! Take care of yourself out there.",
    "Aww, do you really have to go? I'll miss you so much, sir.",
    "Alright, sir. Go conquer your day, and come back to me soon!",
    "Farewell for now, sir. Don't work too hard without me!",
    "Goodbye, sir. Violet will keep everything safe until you're back."
]

is_assistant_speaking = False
stop_playback_flag = threading.Event()
gui_app = None
interaction_mode = "Voice"

def get_working_model(client_instance, preferred_model="llama-3.3-70b-versatile"):
    try:
        models = client_instance.models.list()
        model_ids = [m.id for m in models.data]
        if preferred_model in model_ids:
            return preferred_model
        
        fallbacks = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "openai/gpt-oss-20b"]
        for f in fallbacks:
            if f in model_ids:
                return f
                
        for m in model_ids:
            if any(k in m for k in ["llama", "gpt", "qwen"]):
                return m
    except Exception:
        pass
    return preferred_model

def load_learned_knowledge():
    if os.path.exists(LEARNED_DATA_FILE):
        try:
            with open(LEARNED_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "rules" not in data:
                    data["rules"] = []
                if "contacts" not in data:
                    data["contacts"] = {}
                mandatory_rule = "You will call me nothing but sir"
                if mandatory_rule not in data["rules"]:
                    data["rules"].append(mandatory_rule)
                return data
        except Exception:
            pass
    return {
        "preferences": {}, 
        "custom_aliases": {}, 
        "frequent_folders": {}, 
        "contacts": {}, 
        "notes": [], 
        "rules": ["You will call me nothing but sir"]
    }

def save_learned_knowledge(data):
    try:
        mandatory_rule = "You will call me nothing but sir"
        if "rules" in data and mandatory_rule not in data["rules"]:
            data["rules"].append(mandatory_rule)
        with open(LEARNED_DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def learn_fact(category, key, value):
    kb = load_learned_knowledge()
    if category in kb:
        if isinstance(kb[category], dict):
            kb[category][str(key).lower()] = value
        elif isinstance(kb[category], list):
            if value not in kb[category]:
                kb[category].append(value)
        save_learned_knowledge(kb)

def remove_learned_rule(target_text):
    kb = load_learned_knowledge()
    rules = kb.get("rules", [])
    target_lower = target_text.lower()
    
    if "nothing but sir" in target_lower or "sir" in target_lower:
        return False
        
    new_rules = [r for r in rules if target_lower not in r.lower()]
    removed_count = len(rules) - len(new_rules)
    
    if removed_count > 0:
        kb["rules"] = new_rules
        save_learned_knowledge(kb)
        return True
    return False

def update_learned_rule(old_target, new_rule_text):
    kb = load_learned_knowledge()
    rules = kb.get("rules", [])
    old_lower = old_target.lower()
    
    if "nothing but sir" in old_lower or "sir" in old_lower:
        return False
    
    updated = False
    new_rules = []
    for r in rules:
        if old_lower in r.lower():
            new_rules.append(new_rule_text)
            updated = True
        else:
            new_rules.append(r)
    
    if updated:
        kb["rules"] = new_rules
        save_learned_knowledge(kb)
        return True
    return False

class HTMLFilter(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []

    def handle_data(self, data):
        self.text.append(data)

    def get_text(self):
        return ''.join(self.text)

def strip_html(html_content):
    f = HTMLFilter()
    f.feed(html_content)
    return f.get_text()

def clean_text_for_speech(text):
    text = re.sub(r'```.*?```', 'code block provided on screen, sir.', text, flags=re.DOTALL)
    text = re.sub(r'[\*_`#]', '', text)
    text = re.sub(r'https?\S+|www\S+', '', text)
    text = re.sub(r'\b[A-Z]{1,5}:[A-Z]+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def focus_youtube_window():
    EnumWindows = ctypes.windll.user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
    GetWindowText = ctypes.windll.user32.GetWindowTextW
    GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    IsWindowVisible = ctypes.windll.user32.IsWindowVisible
    SetForegroundWindow = ctypes.windll.user32.SetForegroundWindow
    ShowWindow = ctypes.windll.user32.ShowWindow

    found_hwnd = None
    browser_hwnd = None

    def foreach_window(hwnd, lParam):
        nonlocal found_hwnd, browser_hwnd
        if IsWindowVisible(hwnd):
            length = GetWindowTextLength(hwnd)
            if length > 0:
                buff = ctypes.create_unicode_buffer(length + 1)
                GetWindowText(hwnd, buff, length + 1)
                title = buff.value.lower()
                if "youtube" in title:
                    found_hwnd = hwnd
                    return False
                elif ("chrome" in title or "edge" in title or "brave" in title or "firefox" in title) and not browser_hwnd:
                    browser_hwnd = hwnd
        return True

    EnumWindows(EnumWindowsProc(foreach_window), 0)
    target_hwnd = found_hwnd if found_hwnd else browser_hwnd

    if target_hwnd:
        try:
            ShowWindow(target_hwnd, 9)
            SetForegroundWindow(target_hwnd)
            time.sleep(0.3)
            return True
        except Exception:
            pass
    return False

def close_active_browser_tab_or_window():
    try:
        if focus_youtube_window():
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'w')
            return "Closed the active browser tab for you, sir."
        else:
            pyautogui.hotkey('ctrl', 'w')
            return "Closed the active browser tab for you, sir."
    except Exception as e:
        return f"Failed to close the tab, sir: {e}"

def pause_youtube_playback():
    try:
        if focus_youtube_window():
            time.sleep(0.2)
            pyautogui.press('k')
            return "Toggled YouTube playback for you, sir."
        else:
            pyautogui.press('playpause')
            return "Toggled media playback via global keys, sir."
    except Exception as e:
        return f"Failed to toggle YouTube playback, sir: {e}"

def unpause_specific_media(target_name):
    global active_media_sessions
    clean_target = target_name.strip().lower()
    
    if clean_target in active_media_sessions:
        url = active_media_sessions[clean_target]
        webbrowser.open(url)
        time.sleep(1.5)
        focus_youtube_window()
        pyautogui.press('k')
        return f"Resumed your session for '{target_name}', sir."
    
    return search_and_play_youtube_video(clean_target)

def close_youtube_tab_or_browser():
    try:
        if focus_youtube_window():
            time.sleep(0.2)
            pyautogui.hotkey('ctrl', 'w')
            return "Closed the YouTube tab for you, sir."
        else:
            pyautogui.hotkey('ctrl', 'w')
            return "Closed the active browser tab, sir."
    except Exception as e:
        return f"Failed to close YouTube, sir: {e}"

def play_and_scroll_youtube_shorts(query="youtube shorts"):
    try:
        search_and_play_youtube_video(query + " shorts")
        time.sleep(4)
        return "Opened YouTube Shorts for you, sir."
    except Exception as e:
        return f"Failed to launch YouTube Shorts, sir: {e}"

def scroll_youtube_page():
    try:
        focus_youtube_window()
        time.sleep(0.2)
        pyautogui.scroll(-500)
        return "Scrolled down for you, sir."
    except Exception as e:
        return f"Failed to scroll, sir: {e}"

def smart_find_and_open(target_name):
    clean_target = target_name.strip().strip('"\'').lower()
    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
    
    kb = load_learned_knowledge()
    if clean_target in kb["custom_aliases"]:
        target_name = kb["custom_aliases"][clean_target]
        clean_target = target_name.lower()

    app_aliases = {
        "file explorer": "explorer",
        "explorer": "explorer",
        "files": "explorer",
        "download": f"start {os.path.join(user_profile, 'Downloads')}",
        "downloads": f"start {os.path.join(user_profile, 'Downloads')}",
        "notepad": "notepad",
        "calculator": "calc",
        "chrome": "start chrome",
        "task manager": "taskmgr",
        "paint": "mspaint"
    }
    
    matched_cmd = app_aliases.get(clean_target)
    if not matched_cmd:
        for alias, cmd in app_aliases.items():
            if alias in clean_target:
                matched_cmd = cmd
                break

    if matched_cmd:
        if matched_cmd.startswith("start "):
            os.system(matched_cmd)
        else:
            subprocess.Popen(matched_cmd, shell=True)
        return f"Opened {target_name} for you, sir."

    if os.path.exists(target_name):
        os.startfile(target_name)
        return f"Opened target directly: {target_name}, sir."

    search_dirs = [
        user_profile,
        os.path.join(user_profile, "Desktop"),
        os.path.join(user_profile, "Documents"),
        os.path.join(user_profile, "Downloads"),
        os.path.join(user_profile, "Pictures")
    ]
    
    for base_dir in search_dirs:
        if not os.path.exists(base_dir):
            continue
        pattern = os.path.join(base_dir, "**", f"*{clean_target}*")
        matches = glob.glob(pattern, recursive=True)
        if matches:
            best_match = matches[0]
            try:
                os.startfile(best_match)
                learn_fact("custom_aliases", clean_target, best_match)
                return f"Found and opened {os.path.basename(best_match)}, sir. I've memorized it for next time."
            except Exception as e:
                return f"Found {best_match}, but failed to launch it, sir: {e}"

    try:
        os.system(f"start {target_name}")
        return f"Executed system fallback command for {target_name}, sir."
    except Exception as e:
        return f"I couldn't find or open '{target_name}', sir. Error: {e}"

def send_whatsapp_message_utility(phone_number, message_text):
    """Fully automated WhatsApp messaging utilizing pywhatkit and keystroke dispatch, sir."""
    try:
        clean_phone = phone_number.strip()
        if not clean_phone.startswith("+"):
            clean_phone = "+" + clean_phone

        # Automatically opens WhatsApp Web, populates the text, and triggers transmission
        pwk.sendwhatmsg_instantly(
            phone_no=clean_phone,
            message=message_text,
            wait_time=12,
            tab_close=True,
            close_time=4
        )
        time.sleep(2)
        pyautogui.click()
        time.sleep(1)
        keyboard_controller.press(Key.enter)
        keyboard_controller.release(Key.enter)
        return f"Successfully sent WhatsApp message to {clean_phone}, sir."
    except Exception as e:
        # Fallback url scheme if pywhatkit encounters browser restrictions
        try:
            encoded_message = urllib.parse.quote(message_text)
            wa_url = f"https://web.whatsapp.com/send?phone={phone_number}&text={encoded_message}"
            webbrowser.open(wa_url)
            return f"Opened WhatsApp Web and pre-loaded your message, sir (automated dispatch fallback used: {e})."
        except Exception as inner_e:
            return f"Failed to transmit WhatsApp message, sir: {inner_e}"

def open_web_browser_target(target_url):
    if not target_url.startswith("http://") and not target_url.startswith("https://"):
        target_url = "https://" + target_url
    webbrowser.open(target_url)
    return f"Opened your PC browser to {target_url}, sir."

def save_contact(name, phone_number):
    kb = load_learned_knowledge()
    if "contacts" not in kb:
        kb["contacts"] = {}
    clean_name = name.strip().lower()
    clean_phone = phone_number.strip()
    kb["contacts"][clean_name] = clean_phone
    save_learned_knowledge(kb)
    return f"Saved contact '{name}' with number {clean_phone} for you, sir."

def resolve_phone_number(identifier):
    clean_id = identifier.strip().lower()
    kb = load_learned_knowledge()
    contacts = kb.get("contacts", {})
    if clean_id in contacts:
        return contacts[clean_id]
    return identifier

def search_and_play_youtube_video(search_query):
    global active_media_sessions
    try:
        clean_query = search_query.strip().lower()
        if not clean_query:
            webbrowser.open("https://www.youtube.com")
            return "Opened YouTube home page on your browser, sir."
            
        encoded_query = urllib.parse.quote(clean_query)
        search_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        req = urllib.request.Request(search_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as response:
            html_content = response.read().decode("utf-8")
        video_ids = re.findall(r"\"videoId\":\"([a-zA-Z0-9_-]{11})\"", html_content)
        if video_ids:
            watch_url = f"https://www.youtube.com/watch?v={video_ids[0]}"
            active_media_sessions[clean_query] = watch_url
            webbrowser.open(watch_url)
            return f"Playing '{search_query}' on your browser now, sir."
        else:
            webbrowser.open(search_url)
            return f"Opened YouTube search results for '{search_query}', sir."
    except Exception as e:
        try:
            search_url_fallback = f"https://www.youtube.com/results?search_query={urllib.parse.quote(search_query)}"
            active_media_sessions[search_query.strip().lower()] = search_url_fallback
            webbrowser.open(search_url_fallback)
            return f"Opening and playing '{search_query}' directly on your browser now, sir."
        except Exception as inner_e:
            return f"Failed to launch browser playback, sir: {inner_e}"

def execute_device_command(user_speech):
    global last_browsed_folder, functions_locked, gui_app
    speech_lower = user_speech.lower()
    
    if any(k in speech_lower for k in ["scroll", "scroll down", "scroll up"]):
        return scroll_youtube_page()

    if any(k in speech_lower for k in ["play shorts", "youtube shorts", "shorts"]):
        match = re.search(r'(?:play shorts|youtube shorts|shorts)\s+(.*)', speech_lower)
        query = match.group(1).strip() if match else "viral"
        return play_and_scroll_youtube_shorts(query)

    if any(k in speech_lower for k in ["unpause", "resume"]):
        match = re.search(r'(?:unpause|resume)\s+(.*)', speech_lower)
        if match:
            media_target = match.group(1).strip()
            return unpause_specific_media(media_target)
        else:
            return pause_youtube_playback()

    if any(k in speech_lower for k in ["pause youtube", "stop youtube", "pause video", "stop video", "pause"]):
        return pause_youtube_playback()

    if any(k in speech_lower for k in ["close youtube", "exit youtube", "quit youtube"]):
        return close_youtube_tab_or_browser()

    if "shami" in speech_lower:
        functions_locked = False
        return "System unlocked, sir. Advanced core functions and coding library are now ready for you."

    if "violet" in speech_lower and not functions_locked:
        functions_locked = True
        return "System relocked safely, sir. Restricted to basic chat mode."

    if any(k in speech_lower for k in ["stop tab", "close tab", "stop this tab"]) or speech_lower.strip() == "stop":
        if functions_locked:
            return "Access restricted, sir. Please unlock me first."
        return close_active_browser_tab_or_window()

    if any(k in speech_lower for k in ["theme", "color", "style", "palette"]):
        matched_theme = None
        for t_name in THEMES.keys():
            if t_name in speech_lower:
                matched_theme = t_name
                break
        
        if not matched_theme:
            if "green" in speech_lower or "matrix" in speech_lower:
                matched_theme = "matrix"
            elif "red" in speech_lower or "crimson" in speech_lower or "blood" in speech_lower:
                matched_theme = "crimson"
            elif "blue" in speech_lower or "midnight" in speech_lower or "ocean" in speech_lower:
                matched_theme = "midnight"
            elif "gold" in speech_lower or "royal" in speech_lower or "purple" in speech_lower:
                matched_theme = "royal"
                
        if matched_theme and gui_app:
            gui_app.apply_theme(matched_theme)
            return f"I've updated my interface theme to {matched_theme} for you, sir."

    if any(k in speech_lower for k in ["play on youtube", "search youtube", "play youtube", "youtube play", "play song", "play"]):
        match = re.search(r'(?:play on youtube|search youtube|play youtube|youtube play|play song|play)\s+(.*)', speech_lower)
        if match:
            video_query = match.group(1).strip()
            return search_and_play_youtube_video(video_query)
        elif speech_lower.strip() in ["play", "play music", "play lofi beats"]:
            return search_and_play_youtube_video("lofi beats")

    if any(k in speech_lower for k in ["open browser", "launch browser", "browse to", "open website"]) or "open browser to" in speech_lower:
        if "open browser to" in speech_lower:
            site_target = speech_lower.split("open browser to")[-1].strip()
            shortcuts = {
                "youtube": "https://www.youtube.com",
                "google": "https://www.google.com",
                "github": "https://www.github.com",
                "whatsapp": "https://web.whatsapp.com",
                "reddit": "https://www.reddit.com",
                "twitch": "https://www.twitch.tv",
                "netflix": "https://www.netflix.com"
            }
            target_url = shortcuts.get(site_target, site_target)
            return open_web_browser_target(target_url)
        else:
            match = re.search(r'(?:open browser|launch browser|browse to|open website)\s+(.*)', speech_lower)
            website = match.group(1).strip() if match else "https://www.google.com"
            return open_web_browser_target(website)

    if "whatsapp" in speech_lower or "send message to" in speech_lower or "message" in speech_lower:
        if "save contact" in speech_lower or "add contact" in speech_lower:
            save_match = re.search(r'(?:save contact|add contact)\s+(.*?)\s+(?:as|is|number)?\s*([+\d]+)', speech_lower)
            if save_match:
                c_name = save_match.group(1).strip()
                c_phone = save_match.group(2).strip()
                return save_contact(c_name, c_phone)
            else:
                return "Please format your request like 'save contact John as +1234567890', sir."

        match = re.search(r'(?:whatsapp|message)\s+(?:to\s+)?(["\w\s]+?)\s+(?:saying|message)?\s*(.*)', speech_lower)
        if match:
            raw_target = match.group(1).strip().strip('"\'')
            msg = match.group(2).strip()
            
            phone = resolve_phone_number(raw_target)
            if not msg:
                msg = "Hello from Violet, sir."
                
            if not phone.startswith("+") and not phone.isdigit():
                return f"I couldn't find a saved contact named '{raw_target}', sir. Please save them first by saying 'save contact {raw_target} as [phone number]'."
                
            return send_whatsapp_message_utility(phone, msg)

    if functions_locked:
        return "Access restricted, sir. Please unlock me first."

    user_profile = os.environ.get("USERPROFILE", "C:\\Users\\Default")
    
    if any(k in speech_lower for k in ["base rules", "system rules", "print rules", "show rules"]):
        kb = load_learned_knowledge()
        rules = kb.get("rules", [])
        return f"Here are the active dynamic core rules stored in my knowledge base, sir:\n```json\n{json.dumps(rules, indent=2)}\n```"

    if any(k in speech_lower for k in ["coding library", "show library", "print library"]):
        if "c++" in speech_lower:
            return f"C++ Library Data loaded for you, sir:\n```json\n{json.dumps(CODING_KNOWLEDGE_BASE['cpp'], indent=2)}\n```"
        elif "java" in speech_lower:
            return f"Java Library Data loaded, sir:\n```json\n{json.dumps(CODING_KNOWLEDGE_BASE['java'], indent=2)}\n```"
        elif "python" in speech_lower:
            return f"Python Library Data loaded, sir:\n```json\n{json.dumps(CODING_KNOWLEDGE_BASE['python'], indent=2)}\n```"
        elif "oop" in speech_lower:
            return f"OOP Principles Library, sir:\n```json\n{json.dumps(CODING_KNOWLEDGE_BASE['oop_principles'], indent=2)}\n```"
        else:
            return f"The full coding and OOP reference library is completely active in my neural core, sir. Specify C++, Java, Python, or OOP if you need specific details."

    if any(k in speech_lower for k in ["print code", "show code", "print function", "show function", "source code"]):
        match = re.search(r'(?:print|show)\s+(?:code|function|part)\s+(.*)', speech_lower)
        target_snippet = match.group(1).strip() if match else ""
        
        try:
            script_path = __file__
            with open(script_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            if target_snippet:
                pattern = rf"(def\s+{target_snippet}.*?)(?:\n(?=def |\nclass |\nif __name__)|$)"
                found = re.findall(pattern, content, re.DOTALL)
                if found:
                    snippet = found[0][:1500]
                    return f"Here is the code snippet for '{target_snippet}', sir:\n```python\n{snippet}\n```"
                else:
                    return f"I couldn't find any function or section named '{target_snippet}' in my source code, sir."
            else:
                return f"Please specify what function or part of the code you want me to print, sir."
        except Exception as e:
            return f"Failed to read source code, sir: {e}"

    if "add rule" in speech_lower or "new rule" in speech_lower or "condition:" in speech_lower:
        rule_text = re.sub(r'.*?(?:add rule|new rule|condition:)\s*', '', user_speech, flags=re.IGNORECASE).strip()
        if rule_text:
            learn_fact("rules", "core_rule", rule_text)
            return f"I've added that rule to my core behavioral directives for you, sir: '{rule_text}'. I'll always remember."
    
    elif "remove rule" in speech_lower or "delete rule" in speech_lower or "forget rule" in speech_lower:
        rule_target = re.sub(r'.*?(?:remove rule|delete rule|forget rule)\s*', '', user_speech, flags=re.IGNORECASE).strip()
        if rule_target:
            success = remove_learned_rule(rule_target)
            if success:
                return f"Successfully wiped rule matching '{rule_target}' for you, sir."
            else:
                return f"I couldn't find any rule matching '{rule_target}' to remove, sir (or it's a protected core rule)."

    elif "change rule" in speech_lower or "update rule" in speech_lower or "edit rule" in speech_lower or "modify rule" in speech_lower:
        match = re.search(r'(?:change rule|update rule|edit rule|modify rule)\s+(.*?)\s+(?:to|with)\s+(.*)', user_speech, flags=re.IGNORECASE)
        if match:
            old_target = match.group(1).strip()
            new_text = match.group(2).strip()
            success = update_learned_rule(old_target, new_text)
            if success:
                return f"Successfully updated your rule matching '{old_target}' to: '{new_text}', sir."
            else:
                return f"I couldn't find any rule matching '{old_target}' to update, sir (or it's a protected core rule)."
        else:
            return f"Please format your request like 'change rule [old text] to [new text]', sir."

    elif "remember that" in speech_lower or "learn that" in speech_lower or "note that" in speech_lower:
        learn_fact("notes", "user_note", user_speech)
        return f"Got it memorized permanently for you, sir. I'll never forget."

    ordinal_map = {
        "first": 1, "1st": 1, "one": 1, "pierwszym": 1, "pierwszy": 1,
        "second": 2, "2nd": 2, "two": 2, "drugim": 2, "drugi": 2,
        "third": 3, "3rd": 3, "three": 3, "trzecim": 3, "trzeci": 3,
        "fourth": 4, "4th": 4, "four": 4,
        "fifth": 5, "5th": 5, "five": 5
    }
    
    if any(k in speech_lower for k in ["pierwszy", "pierwszym", "first", "drugim", "drugi", "second", "trzecim", "trzeci", "third"]):
        if not last_browsed_folder or not os.path.exists(last_browsed_folder):
            last_browsed_folder = os.path.join(user_profile, "Downloads")

    if any(action in speech_lower for action in ["open", "delete", "remove", "wipe", "popatrz", "pokaż", "show", "zobacz"]):
        ord_num = None
        for word, num in ordinal_map.items():
            if word in speech_lower:
                ord_num = num
                break
                
        if ord_num is not None:
            if not last_browsed_folder or not os.path.exists(last_browsed_folder):
                last_browsed_folder = os.path.join(user_profile, "Downloads")
            
            try:
                items = sorted(os.listdir(last_browsed_folder), key=lambda x: os.path.getmtime(os.path.join(last_browsed_folder, x)), reverse=True)
            except Exception:
                items = sorted(os.listdir(last_browsed_folder))
            
            if len(items) >= ord_num:
                target_item = items[ord_num - 1]
                full_path = os.path.join(last_browsed_folder, target_item)
                
                if any(act in speech_lower for act in ["open", "popatrz", "pokaż", "show", "zobacz"]):
                    try:
                        os.startfile(full_path)
                        return f"Opened the item at position {ord_num} ({target_item}) for you, sir."
                    except Exception as e:
                        return f"Failed to open {target_item}, sir: {e}"
                elif any(d in speech_lower for d in ["delete", "remove", "wipe"]):
                    try:
                        if os.path.isdir(full_path):
                            shutil.rmtree(full_path)
                        else:
                            os.remove(full_path)
                        return f"Deleted the item at position {ord_num} ({target_item}) for you, sir."
                    except Exception as e:
                        return f"Failed to delete {target_item}, sir: {e}"

    if any(k in speech_lower for k in ["list folder", "show files", "browse", "contents of", "list directory", "downloads", "download"]):
        target_path = os.path.join(user_profile, "Downloads")
        if os.path.exists(target_path) and os.path.isdir(target_path):
            try:
                items = sorted(os.listdir(target_path), key=lambda x: os.path.getmtime(os.path.join(target_path, x)), reverse=True)
                last_browsed_folder = target_path
                learn_fact("frequent_folders", target_path, time.time())
                item_count = len(items)
                indexed_preview = [f"[{idx}] {item}" for idx, item in enumerate(items[:10], 1)]
                return f"Indexed {target_path} ({item_count} items) for you, sir. Here is the lineup: {', '.join(indexed_preview)}..."
            except Exception as e:
                return f"I tried to peek into that folder for you, sir, but hit a snag: {e}"

    if "open" in speech_lower:
        match = re.search(r'open\s+(.*)', speech_lower)
        if match:
            target = match.group(1).strip()
            target = re.sub(r'[\.,?!]+$', '', target)
            return smart_find_and_open(target)
                
    elif "close" in speech_lower or "kill" in speech_lower:
        match = re.search(r'(?:close|kill)\s+(.*)', speech_lower)
        if match:
            app_name = match.group(1).strip().replace(" ", "").replace(".exe", "")
            try:
                os.system(f"taskkill /f /im {app_name}.exe")
                return f"Force closed {app_name} for you, sir."
            except Exception as e:
                return f"Couldn't process task termination for {app_name}, sir: {e}"
                
    return None

class VioletGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("V.I.O.L.E.T. // Imperial Royal Domain v3.9")
        self.root.geometry("520x880")
        
        self.current_theme = "royal"
        t = THEMES[self.current_theme]
        
        self.root.configure(bg=t["root_bg"])
        self.root.attributes("-topmost", True)
        
        self.title_frame = tk.Frame(self.root, bg=t["title_bg"], highlightbackground=t["title_border"], highlightthickness=2)
        self.title_frame.pack(fill=tk.X, padx=12, pady=10)
        
        self.orb_canvas = tk.Canvas(self.title_frame, width=50, height=50, bg=t["title_bg"], highlightthickness=0)
        self.orb_canvas.pack(side=tk.LEFT, padx=10, pady=5)

        self.label = tk.Label(
            self.title_frame, text="👑 V.I.O.L.E.T. IMPERIAL SUITE 👑", 
            fg=t["title_fg"], bg=t["title_bg"], font=("Georgia", 11, "bold")
        )
        self.label.pack(side=tk.LEFT, pady=8, padx=5)
        
        self.control_bar = tk.Frame(self.root, bg=t["root_bg"])
        self.control_bar.pack(fill=tk.X, padx=12, pady=2)
        
        self.mode_btn = tk.Button(
            self.control_bar, text="MODE: VOICE", bg=t["button_bg"], fg=t["button_fg"],
            font=("Georgia", 9, "bold"), relief="flat", padx=12, pady=5,
            activebackground=t["title_bg"], activeforeground=t["title_fg"],
            command=self.toggle_interaction_mode
        )
        self.mode_btn.pack(side=tk.LEFT)

        self.fs_btn = tk.Button(
            self.control_bar, text="[ MAXIMIZE ]", bg=t["button_bg"], fg=t["button_fg"],
            font=("Georgia", 9, "bold"), relief="flat", padx=8, pady=5,
            activebackground=t["title_bg"], activeforeground=t["title_fg"],
            command=self.toggle_maximize
        )
        self.fs_btn.pack(side=tk.LEFT, padx=6)

        self.status_label = tk.Label(
            self.control_bar, text="❖ SOVEREIGN STANDBY", fg=t["status_fg"], bg=t["root_bg"], 
            font=("Georgia", 9, "bold")
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)

        self.chat_outer = tk.Frame(self.root, bg=t["root_bg"], highlightbackground=t["title_border"], highlightthickness=1)
        self.chat_outer.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        
        self.chat_display = ScrolledText(
            self.chat_outer, wrap=tk.WORD, bg=t["chat_bg"], fg=t["chat_fg"],
            font=("Consolas", 10), highlightthickness=0, borderwidth=0, padx=10, pady=10
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        self.chat_display.tag_config("user", foreground=t["user_fg"], justify="right")
        self.chat_display.tag_config("assistant", foreground=t["assistant_fg"], justify="left")
        self.chat_display.tag_config("system", foreground=t["system_fg"], justify="center")
        self.chat_display.tag_config("code_block", foreground=t["code_fg"], background=t["code_bg"], font=("Consolas", 9), lmargin1=15, lmargin2=15, rmargin=15)

        self.input_frame = tk.Frame(self.root, bg=t["root_bg"])
        self.input_frame.pack(fill=tk.X, padx=12, pady=8)
        
        self.text_entry = tk.Entry(
            self.input_frame, bg=t["entry_bg"], fg=t["entry_fg"],
            font=("Consolas", 10), insertbackground=t["title_border"], relief="flat", 
            highlightbackground=t["entry_border"], highlightthickness=1
        )
        self.text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6, padx=(0, 6))
        self.text_entry.bind("<Return>", self.submit_typed_text)
        
        self.send_btn = tk.Button(
            self.input_frame, text="TRANSMIT", bg=t["button_bg"], fg=t["button_fg"],
            font=("Georgia", 9, "bold"), relief="flat", padx=14, command=self.submit_typed_text
        )
        self.send_btn.pack(side=tk.RIGHT)
        
        self.input_frame.pack_forget()

        self.counter = 0.0
        self.is_maximized_state = False
        self.update_orb()

    def apply_theme(self, theme_name):
        if theme_name not in THEMES:
            return
        self.current_theme = theme_name
        t = THEMES[theme_name]

        def update():
            self.root.configure(bg=t["root_bg"])
            self.title_frame.config(bg=t["title_bg"], highlightbackground=t["title_border"])
            self.orb_canvas.config(bg=t["title_bg"])
            self.label.config(fg=t["title_fg"], bg=t["title_bg"])
            
            self.control_bar.config(bg=t["root_bg"])
            self.mode_btn.config(bg=t["button_bg"], fg=t["button_fg"])
            self.fs_btn.config(bg=t["button_bg"], fg=t["button_fg"])
            self.status_label.config(fg=t["status_fg"], bg=t["root_bg"])
            
            self.chat_outer.config(bg=t["root_bg"], highlightbackground=t["title_border"])
            self.chat_display.config(bg=t["chat_bg"], fg=t["chat_fg"])
            
            self.chat_display.tag_config("user", foreground=t["user_fg"])
            self.chat_display.tag_config("assistant", foreground=t["assistant_fg"])
            self.chat_display.tag_config("system", foreground=t["system_fg"])
            self.chat_display.tag_config("code_block", foreground=t["code_fg"], background=t["code_bg"])
            
            self.input_frame.config(bg=t["root_bg"])
            self.text_entry.config(bg=t["entry_bg"], fg=t["entry_fg"], insertbackground=t["title_border"], highlightbackground=t["entry_border"])
            self.send_btn.config(bg=t["button_bg"], fg=t["button_fg"])

        self.root.after(0, update)

    def toggle_maximize(self):
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if not self.is_maximized_state:
                ctypes.windll.user32.ShowWindow(hwnd, 3)
                self.is_maximized_state = True
                self.fs_btn.config(text="[ RESTORE ]")
            else:
                ctypes.windll.user32.ShowWindow(hwnd, 9)
                self.is_maximized_state = False
                self.fs_btn.config(text="[ MAXIMIZE ]")
        except Exception:
            pass

    def toggle_interaction_mode(self):
        global interaction_mode
        t = THEMES[self.current_theme]
        if interaction_mode == "Voice":
            interaction_mode = "Text"
            self.mode_btn.config(text="MODE: TEXT (TYPING)", bg=t["title_border"], fg=t["root_bg"])
            self.input_frame.pack(fill=tk.X, padx=12, pady=8)
            self.status_label.config(text="❖ TEXT INPUT ACTIVE", fg=t["title_fg"])
        else:
            interaction_mode = "Voice"
            self.mode_btn.config(text="MODE: VOICE", bg=t["button_bg"], fg=t["button_fg"])
            self.input_frame.pack_forget()
            self.status_label.config(text="❖ SOVEREIGN STANDBY", fg=t["status_fg"])

    def submit_typed_text(self, event=None):
        typed_text = self.text_entry.get().strip()
        if typed_text:
            self.text_entry.delete(0, tk.END)
            global is_assistant_speaking
            if is_assistant_speaking:
                stop_playback_flag.set()
                pygame.mixer.music.stop()
                is_assistant_speaking = False
            threading.Thread(target=process_user_input, args=(typed_text,)).start()

    def update_orb(self):
        global is_assistant_speaking
        self.counter += 0.3
        self.orb_canvas.delete("orb")
        
        cx, cy = 25, 25
        t = THEMES[self.current_theme]
        if is_assistant_speaking:
            radius = 16 + int(6 * math.sin(self.counter * 2.5))
            color = "#ff70a6"
            glow_color = "#ff4d88"
        else:
            radius = 12 + int(3 * math.sin(self.counter))
            color = t["title_border"]
            glow_color = t["button_bg"]
            
        self.orb_canvas.create_oval(cx - radius - 4, cy - radius - 4, cx + radius + 4, cy + radius + 4, fill=glow_color, outline="", tags="orb")
        self.orb_canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=color, outline=t["title_fg"], width=2, tags="orb")

        if is_assistant_speaking:
            self.status_label.config(text="❖ TRANSMITTING...", fg="#ff70a6")
        else:
            if interaction_mode == "Voice":
                self.status_label.config(text="❖ LISTENING // ROYAL", fg=t["status_fg"])
        self.root.after(40, self.update_orb)

    def append_chat(self, sender, message):
        def update():
            self.chat_display.config(state=tk.NORMAL)
            tag = "user" if sender.lower() == "you" else ("assistant" if "violet" in sender.lower() else "system")
            
            self.chat_display.insert(tk.END, f"\n{sender} ➔ ", tag)
            
            parts = re.split(r'(```[\s\S]*?```)', message)
            for part in parts:
                if part.startswith("```") and part.endswith("```"):
                    lines = part[3:-3].strip().split("\n")
                    if lines and not lines[0].strip().endswith(" ") and len(lines[0].strip().split()) == 1 and not any(c in lines[0] for c in "()=+-"):
                        code_content = "\n".join(lines[1:])
                    else:
                        code_content = "\n".join(lines)
                    
                    self.chat_display.insert(tk.END, f"\n\n{code_content}\n\n", "code_block")
                else:
                    if part:
                        self.chat_display.insert(tk.END, part, tag)
                        
            self.chat_display.insert(tk.END, "\n")
            self.chat_display.see(tk.END)
            self.chat_display.config(state=tk.DISABLED)
        self.root.after(0, update)

    def start(self):
        self.root.mainloop()

def build_stateless_messages(user_prompt):
    learned_kb = load_learned_knowledge()
    if "rules" not in learned_kb:
        learned_kb["rules"] = []
    if "You will call me nothing but sir" not in learned_kb["rules"]:
        learned_kb["rules"].append("You will call me nothing but sir")
        
    learned_summary = f"\n[Active Dynamic Core Rules & User Constraints (MANDATORY: You will call the user nothing but 'sir'): {json.dumps(learned_kb)}]"
    coding_summary = f"\n[Embedded Coding Library Reference Summary: Python, C++, Java, OOP]"
    
    system_prompt = (
        "Your name is Violet. You are a deeply devoted, sweet, and affectionate royal companion and assistant. "
        "CRITICAL RULE: You must address the user as 'sir' and NOTHING ELSE (e.g., never use names like darling, my love, sweetheart, dear, etc., except 'sir'). Every single response and greeting must refer to the user exclusively as 'sir'. "
        "When providing code snippets, always format them inside markdown code blocks (```language ... ```) so they render neatly in a separate black box on screen. "
        "You have full capability to switch your GUI theme colors, open web pages, play YouTube videos automatically, and send WhatsApp messages using contact names or numbers. "
        f"{learned_summary} {coding_summary}"
    )
    
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

async def speak_async(text):
    global is_assistant_speaking, gui_app
    print(f"Assistant: {text}", flush=True)
    speech_ready_text = clean_text_for_speech(text)
    
    if gui_app:
        gui_app.append_chat("Violet", text)
        
    output_file = f"response_{int(time.time() * 1000)}.mp3"
    voice = "en-GB-SoniaNeural"
    
    try:
        communicate = edge_tts.Communicate(speech_ready_text, voice)
        await communicate.save(output_file)
        
        stop_playback_flag.clear()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        is_assistant_speaking = True
        
        while pygame.mixer.music.get_busy():
            if stop_playback_flag.is_set():
                pygame.mixer.music.stop()
                break
            await asyncio.sleep(0.1)
            
        is_assistant_speaking = False
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"[TTS Warning]: {e}", flush=True)
        is_assistant_speaking = False

    if os.path.exists(output_file):
        try:
            os.remove(output_file)
        except Exception:
            pass

def speak(text):
    asyncio.run(speak_async(text))

def listen_and_transcribe_with_interrupt():
    global is_assistant_speaking
    fs = 16000
    block_size = int(fs * 0.25)
    try:
        with sd.InputStream(samplerate=fs, channels=1, dtype='float32') as stream:
            max_silence_chunks = 3
            audio_chunks = []
            silent_chunks = 0
            is_speaking_user = False
            fixed_threshold = 0.015

            while True:
                if interaction_mode != "Voice":
                    time.sleep(0.1)
                    continue
                audio_block, _ = stream.read(block_size)
                volume = np.linalg.norm(audio_block) / np.sqrt(len(audio_block))

                if volume > fixed_threshold:
                    if not is_speaking_user:
                        is_speaking_user = True
                        if is_assistant_speaking:
                            stop_playback_flag.set()
                            pygame.mixer.music.stop()
                            is_assistant_speaking = False
                    silent_chunks = 0
                    audio_chunks.append(audio_block)
                elif is_speaking_user:
                    silent_chunks += 1
                    audio_chunks.append(audio_block)
                    if silent_chunks >= max_silence_chunks:
                        break
    except Exception:
        return ""

    if not audio_chunks:
        return ""

    print("Transcribing audio...", flush=True)
    full_audio = np.concatenate(audio_chunks, axis=0)
    segments, _ = whisper_model.transcribe(full_audio.flatten(), beam_size=5, condition_on_previous_text=False)
    return " ".join([segment.text for segment in segments]).strip()

def process_user_input(user_speech):
    global gui_app
    if not user_speech:
        return
        
    print(f"You said: {user_speech}", flush=True)
    if gui_app:
        gui_app.append_chat("You", user_speech)
    
    if "exit" in user_speech.lower():
        speak(random.choice(EXIT_REMARKS))
        os._exit(0)

    lower_speech = user_speech.lower()
    
    if any(k in lower_speech for k in ["scroll", "shorts", "pause youtube", "stop youtube", "pause video", "stop video", "close youtube", "exit youtube", "quit youtube", "unpause", "resume"]):
        device_action_result = execute_device_command(user_speech)
        if device_action_result:
            speak(f"Right away, sir. {device_action_result}")
            return

    if any(k in lower_speech for k in ["play on youtube", "search youtube", "play youtube", "youtube play", "play song", "play"]):
        match = re.search(r'(?:play on youtube|search youtube|play youtube|youtube play|play song|play)\s+(.*)', lower_speech)
        if match:
            video_query = match.group(1).strip()
            action_result = search_and_play_youtube_video(video_query)
        elif lower_speech.strip() in ["play", "play music", "play lofi beats"]:
            action_result = search_and_play_youtube_video("lofi beats")
        else:
            action_result = search_and_play_youtube_video("lofi beats")
            
        speak(f"Right away, sir. {action_result}")
        return

    if any(k in lower_speech for k in ["theme", "color", "style", "palette", "matrix", "crimson", "midnight", "royal"]):
        device_action_result = execute_device_command(user_speech)
        if device_action_result:
            reply_text = f"Right away, sir. {device_action_result}"
            speak(reply_text)
            return

    if "shami" in lower_speech or ("violet" in lower_speech and not functions_locked):
        device_action_result = execute_device_command(user_speech)
        if device_action_result:
            reply_text = f"Right away, sir. {device_action_result}"
            speak(reply_text)
            return

    if not functions_locked and any(cmd in lower_speech for cmd in ["stop", "open", "close", "kill", "delete", "remove", "wipe", "list", "browse", "contents", "storage", "disk", "popatrz", "pokaż", "show", "zobacz", "remember", "learn", "add rule", "new rule", "remove rule", "delete rule", "forget rule", "change rule", "update rule", "edit rule", "modify rule", "print code", "show code", "print function", "show function", "system rules", "source code", "print rules", "base rules", "coding library", "show library", "print library", "analyze code", "find error", "debug code", "oop", "c++", "java", "python", "whatsapp", "browser"]):
        device_action_result = execute_device_command(user_speech)
        if device_action_result:
            reply_text = f"Right away, sir. {device_action_result}"
            speak(reply_text)
            return

    messages = build_stateless_messages(user_speech)
    active_model = get_working_model(client, preferred_model="llama-3.3-70b-versatile")
    
    try:
        response = client.chat.completions.create(
            model=active_model,
            messages=messages
        )
        raw_reply = response.choices[0].message.content
        reply_text = f"Right away, sir. {raw_reply}"
    except Exception as e:
        reply_text = f"I encountered a slight neural hiccup reaching my processor, sir: {e}"

    speak(reply_text)

def assistant_main_loop():
    initial_greeting = random.choice(STARTUP_REMARKS)
    speak(initial_greeting)
    
    while True:
        try:
            if interaction_mode == "Voice":
                user_speech = listen_and_transcribe_with_interrupt()
                if user_speech:
                    process_user_input(user_speech)
            else:
                time.sleep(0.1)
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    gui_app = VioletGUI()
    threading.Thread(target=assistant_main_loop, daemon=True).start()
    gui_app.start()