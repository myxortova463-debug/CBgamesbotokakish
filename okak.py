# -*- coding: utf-8 -*-
import json
import os
import random
import time
import threading
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta
import telebot
from telebot import types

# --- ТОКЕН БОТА ---
TOKEN = '8992018799:AAHdd4yXtIVZk-wehBRRGMYHDHWl_mckmP8'
bot = telebot.TeleBot(TOKEN)

# --- АДМИНЫ ---
ADMIN_IDS = [5956091492, 7588378879, 6200621395]

# --- ФАЙЛЫ ---
COINS_FILE = "user_coins.json"
CARDS_FILE = "user_cards.json"
COOLDOWNS_FILE = "user_cooldowns.json"
EXP_FILE = "user_exp.json"
RANKS_FILE = "user_ranks.json"
CARDS_DB_FILE = "cards.json"
PROMO_FILE = "promo_codes.json"
YOUTUBER_USERS_FILE = "user_youtuber_users.json"
VIP_FILE = "user_vip.json"
VIP_PROMOS_FILE = "user_vip_promos.json"
BONUS_FILE = "user_bonus.json"
UPGRADES_FILE = "user_upgrades.json"
CHATS_FILE = "known_chats.json"
DAILY_FILE = "user_daily.json"
DAILY_PLAYERS_FILE = "daily_players.json"
BLOCKED_FILE = "blocked_users.json"
HISTORY_FILE = "user_history.json"
TECH_MODE_FILE = "tech_mode.json"
TEXTS_FILE = "bot_texts.json"
SETTINGS_FILE = "bot_settings.json"
RARITY_CHANCES_FILE = "rarity_chances.json"
RARITY_REWARDS_FILE = "rarity_rewards.json"
EVENTS_FILE = "events.json"
VIP_PRICE_FILE = "vip_price.json"
BUTTONS_FILE = "bot_buttons.json"

# --- КУЛДАУНЫ ---
COOLDOWN_NORMAL_SECONDS = 90 * 60
COOLDOWN_VIP_SECONDS = 45 * 60
COOLDOWN_MOVEMENT_SECONDS = 5

# --- БОНУС ---
BONUS_CHANNEL = "@CountryBallsGames"
BONUS_CHAT = "@CountryBallsGames_Chat"
BONUS_CHANNEL_URL = "https://t.me/CountryBallsGames"
BONUS_CHAT_URL = "https://t.me/CountryBallsGames_Chat"
BONUS_COOLDOWN_NORMAL = 3 * 60 * 60
BONUS_COOLDOWN_VIP = 90 * 60

# --- ПРОКАЧКА ---
UPGRADE_COSTS_COOLDOWN = [500, 2000, 5000, 12500, 22000]
UPGRADE_COSTS_COINS    = [500, 2000, 5000, 12500, 25000]
UPGRADE_COSTS_EXP      = [500, 2000, 5000, 12500, 25000]
UPGRADE_COOLDOWN_BONUS = [0.05, 0.10, 0.15, 0.20, 0.25]
UPGRADE_COINS_BONUS    = [0.05, 0.10, 0.15, 0.20, 0.25]
UPGRADE_EXP_BONUS      = [0.05, 0.10, 0.15, 0.20, 0.25]

# --- ИНВЕНТАРЬ ---
INVENTORY_PER_PAGE = 6
SELL_PRICES = {
    "Обычная": 5,
    "Редкая": 15,
    "Эпическая": 40,
    "Легендарная": 100,
    "Мифическая": 300,
    "Секретная": 1000,
}

# --- СПИСКИ ---
PLAYERS_PER_PAGE = 10
CHATS_PER_PAGE = 10
BLOCKED_PER_PAGE = 10
CARDS_PER_PAGE = 10

# --- СЕЗОН ---
SEASON_END = datetime(2026, 9, 26, 16, 0)

# --- ЖИРНАЯ ЛИНИЯ ---
THICK_LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

# --- РЕДКОСТИ ---
RARITIES = {
    "Обычная": "⚪",
    "Редкая": "🔵",
    "Эпическая": "🟣",
    "Легендарная": "🟡",
    "Мифическая": "🔴",
    "Секретная": "🔮",
}

# --- НАГРАДЫ ПО УМОЛЧАНИЮ ---
RARITY_REWARDS = {
    "Обычная":     {"exp": (25, 50),      "coins": (50, 150),     "chance": 35.0},
    "Редкая":      {"exp": (75, 100),     "coins": (80, 270),     "chance": 30.0},
    "Эпическая":   {"exp": (125, 170),    "coins": (140, 420),    "chance": 20.0},
    "Легендарная": {"exp": (200, 280),    "coins": (300, 800),    "chance": 12.0},
    "Мифическая":  {"exp": (325, 500),    "coins": (650, 1250),   "chance": 3.0},
    "Секретная":   {"exp": (1000, 2000),  "coins": (5000, 15000), "chance": 0.1},
}

# --- РАНГИ ---
RANKS = {
    1: {"name": "🥉 Новичок", "exp_needed": 500},
    2: {"name": "🥈 Любитель", "exp_needed": 1000},
    3: {"name": "🥇 Опытный", "exp_needed": 1500},
    4: {"name": "💎 Продвинутый", "exp_needed": 2000},
    5: {"name": "⭐ Мастер", "exp_needed": 2500},
    6: {"name": "🌟 Эксперт", "exp_needed": 3000},
    7: {"name": "👑 Гуру", "exp_needed": 3500},
    8: {"name": "🏆 Легенда", "exp_needed": 4000},
    9: {"name": "🔥 Элита", "exp_needed": 4500},
    10: {"name": "💠 Профессионал", "exp_needed": None},
}

# --- НАСТРАИВАЕМЫЕ КОНСТАНТЫ (загружаются из файлов) ---
rarity_chances = {
    "Обычная": 35.0,
    "Редкая": 30.0,
    "Эпическая": 20.0,
    "Легендарная": 12.0,
    "Мифическая": 3.0,
}

custom_rewards = {}  # {"Обычная": {"exp": (25,50), "coins": (50,150)}, ...}

active_events = {
    "double_exp": None,
    "double_coins": None,
}

vip_price = {
    "price": 20,
    "duration_days": 30,
}

bot_buttons = {}  # переопределения текста кнопок


# ============================================================
# --- ГЛОБАЛЬНЫЕ ПЕРЕМЕННЫЕ ---
# ============================================================

# --- ИГРОВЫЕ ДАННЫЕ ---
user_coins = {}          # {user_id: монеты}
user_cards = {}          # {user_id: [карты]}
user_cooldowns = {}      # {user_id: datetime последней карты}
user_exp = {}            # {user_id: опыт}
user_ranks = {}          # {user_id: ранг 1-10}
user_bonus = {}          # {user_id: {"last_used": iso}}
user_upgrades = {}       # {user_id: {"cooldown": 0-5, "coins": 0-5, "exp": 0-5}}
user_daily = {}          # {user_id: {"streak": int, "last_claim": iso}}

# --- КАРТЫ ---
cards_db = {}            # {card_name: {"rarity": str, "photo": file_id, "allowed": bool}}

# --- VIP ---
user_vip = {}            # {user_id: True} — вечный VIP (устаревшее)
user_vip_promos = {}     # {user_id: {"expires_at": datetime}}

# --- ПРОМОКОДЫ ---
promo_codes = {}         # {code: {...}}
youtuber_activated_by = set()  # user_id, кто активировал ютуберский промо

# --- ЧАТЫ И ИГРОКИ ЗА ДЕНЬ ---
known_chats = {}         # {chat_id: {"title": str, "type": str, "username": str, "added_at": iso}}
daily_players = {"date": "", "players": []}

# --- МОДЕРАЦИЯ ---
blocked_users = set()    # {user_id, ...}

# --- ИСТОРИЯ ---
user_history = {}        # {user_id: [{"time": iso, "action": str, "details": str}, ...]}

# --- ТЕХ. РЕЖИМ ---
tech_mode = {"enabled": False, "message": "🔧 Бот на технических работах. Заходите позже."}

# --- ТЕКСТЫ ---
bot_texts = {}           # {"help": "...", "start": "...", "season": "..."}

# --- ВРЕМЕННЫЕ ДАННЫЕ (не сохраняются) ---
pending_cards = {}       # {admin_id: {"name": str, "rarity": str}}
pending_promos = {}      # {admin_id: {...}}

MOVEMENT_UNTIL = None    # datetime окончания движухи

# --- ПАГИНАЦИЯ (не сохраняется) ---
edit_card_page = {}      # {admin_id: page}
promo_page = {}          # {admin_id: page}
promo_edit_page = {}     # {admin_id: page}
players_page = {}        # {admin_id: page}
chats_page = {}          # {admin_id: page}
blocked_page = {}        # {admin_id: page}
cards_list_page = {}     # {admin_id: page}


# ============================================================
# --- ЗАГРУЗКА ДАННЫХ ---
# ============================================================
def load_data():
    global user_coins, user_cards, user_cooldowns, user_exp, user_ranks
    global cards_db, promo_codes, user_vip, youtuber_activated_by, user_vip_promos
    global user_bonus, user_upgrades, known_chats, user_daily, daily_players
    global blocked_users, user_history, tech_mode, bot_texts
    global rarity_chances, custom_rewards, active_events, vip_price, bot_buttons

    # --- ИГРОВЫЕ ---
    try:
        if os.path.exists(COINS_FILE):
            with open(COINS_FILE, "r", encoding="utf-8") as f:
                user_coins = {int(k): v for k, v in json.load(f).items()}
    except: user_coins = {}

    try:
        if os.path.exists(CARDS_FILE):
            with open(CARDS_FILE, "r", encoding="utf-8") as f:
                user_cards = {int(k): v for k, v in json.load(f).items()}
    except: user_cards = {}

    try:
        if os.path.exists(COOLDOWNS_FILE):
            with open(COOLDOWNS_FILE, "r", encoding="utf-8") as f:
                user_cooldowns = {int(k): datetime.fromisoformat(v) for k, v in json.load(f).items()}
    except: user_cooldowns = {}

    try:
        if os.path.exists(EXP_FILE):
            with open(EXP_FILE, "r", encoding="utf-8") as f:
                user_exp = {int(k): v for k, v in json.load(f).items()}
    except: user_exp = {}

    try:
        if os.path.exists(RANKS_FILE):
            with open(RANKS_FILE, "r", encoding="utf-8") as f:
                user_ranks = {int(k): v for k, v in json.load(f).items()}
    except: user_ranks = {}

    # --- КАРТЫ ---
    try:
        if os.path.exists(CARDS_DB_FILE):
            with open(CARDS_DB_FILE, "r", encoding="utf-8") as f:
                cards_db = json.load(f)
    except: cards_db = {}

    # --- ПРОМОКОДЫ ---
    try:
        if os.path.exists(PROMO_FILE):
            with open(PROMO_FILE, "r", encoding="utf-8") as f:
                promo_codes = json.load(f)
    except: promo_codes = {}

    # --- VIP ---
    try:
        if os.path.exists(VIP_FILE):
            with open(VIP_FILE, "r", encoding="utf-8") as f:
                user_vip = {int(k): v for k, v in json.load(f).items()}
    except: user_vip = {}

    try:
        if os.path.exists(YOUTUBER_USERS_FILE):
            with open(YOUTUBER_USERS_FILE, "r", encoding="utf-8") as f:
                youtuber_activated_by = set(json.load(f))
    except: youtuber_activated_by = set()

    try:
        if os.path.exists(VIP_PROMOS_FILE):
            with open(VIP_PROMOS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                user_vip_promos = {
                    int(k): {"expires_at": datetime.fromisoformat(v["expires_at"])}
                    for k, v in data.items()
                }
    except: user_vip_promos = {}

    # --- БОНУС И ПРОКАЧКА ---
    try:
        if os.path.exists(BONUS_FILE):
            with open(BONUS_FILE, "r", encoding="utf-8") as f:
                user_bonus = {int(k): v for k, v in json.load(f).items()}
    except: user_bonus = {}

    try:
        if os.path.exists(UPGRADES_FILE):
            with open(UPGRADES_FILE, "r", encoding="utf-8") as f:
                user_upgrades = {int(k): v for k, v in json.load(f).items()}
    except: user_upgrades = {}

    # --- ЧАТЫ ---
    try:
        if os.path.exists(CHATS_FILE):
            with open(CHATS_FILE, "r", encoding="utf-8") as f:
                known_chats = {int(k): v for k, v in json.load(f).items()}
    except: known_chats = {}

    # --- DAILY ---
    try:
        if os.path.exists(DAILY_FILE):
            with open(DAILY_FILE, "r", encoding="utf-8") as f:
                user_daily = {int(k): v for k, v in json.load(f).items()}
    except: user_daily = {}

    try:
        if os.path.exists(DAILY_PLAYERS_FILE):
            with open(DAILY_PLAYERS_FILE, "r", encoding="utf-8") as f:
                daily_players = json.load(f)
    except: daily_players = {"date": "", "players": []}

    # --- МОДЕРАЦИЯ ---
    try:
        if os.path.exists(BLOCKED_FILE):
            with open(BLOCKED_FILE, "r", encoding="utf-8") as f:
                blocked_users = set(json.load(f))
    except: blocked_users = set()

    # --- ИСТОРИЯ ---
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                user_history = {int(k): v for k, v in json.load(f).items()}
    except: user_history = {}

    # --- ТЕХ. РЕЖИМ ---
    try:
        if os.path.exists(TECH_MODE_FILE):
            with open(TECH_MODE_FILE, "r", encoding="utf-8") as f:
                tech_mode = json.load(f)
    except: tech_mode = {"enabled": False, "message": "🔧 Бот на технических работах."}

    # --- ТЕКСТЫ ---
    try:
        if os.path.exists(TEXTS_FILE):
            with open(TEXTS_FILE, "r", encoding="utf-8") as f:
                bot_texts = json.load(f)
    except: bot_texts = {}

    # --- КНОПКИ ---
    try:
        if os.path.exists(BUTTONS_FILE):
            with open(BUTTONS_FILE, "r", encoding="utf-8") as f:
                bot_buttons = json.load(f)
    except: bot_buttons = {}

    # --- НАСТРОЙКИ (RANKS, RARITIES, SELL_PRICES) ---
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "ranks" in data:
                    for k, v in data["ranks"].items():
                        if int(k) in RANKS:
                            RANKS[int(k)]["name"] = v
                if "rarities" in data:
                    for k, v in data["rarities"].items():
                        RARITIES[k] = v
                if "sell_prices" in data:
                    for k, v in data["sell_prices"].items():
                        SELL_PRICES[k] = v
                if "ranks_exp" in data:
                    for k, v in data["ranks_exp"].items():
                        if int(k) in RANKS:
                            RANKS[int(k)]["exp_needed"] = v
    except: pass

    # --- ШАНСЫ РЕДКОСТЕЙ ---
    try:
        if os.path.exists(RARITY_CHANCES_FILE):
            with open(RARITY_CHANCES_FILE, "r", encoding="utf-8") as f:
                rarity_chances = json.load(f)
    except: pass

    # --- КАСТОМНЫЕ НАГРАДЫ ---
    try:
        if os.path.exists(RARITY_REWARDS_FILE):
            with open(RARITY_REWARDS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                custom_rewards = {}
                for k, v in data.items():
                    custom_rewards[k] = {
                        "exp": tuple(v["exp"]),
                        "coins": tuple(v["coins"]),
                    }
    except: pass

    # --- ИВЕНТЫ ---
    try:
        if os.path.exists(EVENTS_FILE):
            with open(EVENTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                active_events = {
                    "double_exp": datetime.fromisoformat(data["double_exp"]) if data.get("double_exp") else None,
                    "double_coins": datetime.fromisoformat(data["double_coins"]) if data.get("double_coins") else None,
                }
    except:
        active_events = {"double_exp": None, "double_coins": None}

    # --- ЦЕНА VIP ---
    try:
        if os.path.exists(VIP_PRICE_FILE):
            with open(VIP_PRICE_FILE, "r", encoding="utf-8") as f:
                vip_price = json.load(f)
    except: pass


# Загружаем данные при старте
load_data()
TOTAL_CARDS = len(cards_db)


# ============================================================
# --- СОХРАНЕНИЕ ДАННЫХ ---
# ============================================================
def save_coins():
    with open(COINS_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_coins.items()}, f, ensure_ascii=False, indent=2)

def save_cards():
    with open(CARDS_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_cards.items()}, f, ensure_ascii=False, indent=2)

def save_cooldowns():
    with open(COOLDOWNS_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v.isoformat() for k, v in user_cooldowns.items()}, f, ensure_ascii=False, indent=2)

def save_exp():
    with open(EXP_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_exp.items()}, f, ensure_ascii=False, indent=2)

def save_ranks():
    with open(RANKS_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_ranks.items()}, f, ensure_ascii=False, indent=2)

def save_cards_db():
    with open(CARDS_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(cards_db, f, ensure_ascii=False, indent=2)

def save_promos():
    with open(PROMO_FILE, "w", encoding="utf-8") as f:
        json.dump(promo_codes, f, ensure_ascii=False, indent=2)

def save_vip():
    with open(VIP_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_vip.items()}, f, ensure_ascii=False, indent=2)

def save_youtuber_users():
    with open(YOUTUBER_USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(list(youtuber_activated_by), f, ensure_ascii=False)

def save_vip_promos():
    with open(VIP_PROMOS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            str(k): {"expires_at": v["expires_at"].isoformat()}
            for k, v in user_vip_promos.items()
        }, f, ensure_ascii=False, indent=2)

def save_bonus():
    with open(BONUS_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_bonus.items()}, f, ensure_ascii=False, indent=2)

def save_upgrades():
    with open(UPGRADES_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_upgrades.items()}, f, ensure_ascii=False, indent=2)

def save_known_chats():
    with open(CHATS_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in known_chats.items()}, f, ensure_ascii=False, indent=2)

def save_daily():
    with open(DAILY_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_daily.items()}, f, ensure_ascii=False, indent=2)

def save_daily_players():
    with open(DAILY_PLAYERS_FILE, "w", encoding="utf-8") as f:
        json.dump(daily_players, f, ensure_ascii=False, indent=2)

def save_blocked_users():
    with open(BLOCKED_FILE, "w", encoding="utf-8") as f:
        json.dump(list(blocked_users), f, ensure_ascii=False)

def save_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({str(k): v for k, v in user_history.items()}, f, ensure_ascii=False, indent=2)

def save_tech_mode():
    with open(TECH_MODE_FILE, "w", encoding="utf-8") as f:
        json.dump(tech_mode, f, ensure_ascii=False, indent=2)

def save_bot_texts():
    with open(TEXTS_FILE, "w", encoding="utf-8") as f:
        json.dump(bot_texts, f, ensure_ascii=False, indent=2)

def save_bot_buttons():
    with open(BUTTONS_FILE, "w", encoding="utf-8") as f:
        json.dump(bot_buttons, f, ensure_ascii=False, indent=2)

def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "ranks": {str(k): v["name"] for k, v in RANKS.items()},
            "ranks_exp": {str(k): v["exp_needed"] for k, v in RANKS.items()},
            "rarities": RARITIES,
            "sell_prices": SELL_PRICES,
        }, f, ensure_ascii=False, indent=2)

def save_rarity_chances():
    with open(RARITY_CHANCES_FILE, "w", encoding="utf-8") as f:
        json.dump(rarity_chances, f, ensure_ascii=False, indent=2)

def save_custom_rewards():
    data = {}
    for k, v in custom_rewards.items():
        data[k] = {"exp": list(v["exp"]), "coins": list(v["coins"])}
    with open(RARITY_REWARDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def save_events():
    with open(EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "double_exp": active_events["double_exp"].isoformat() if active_events.get("double_exp") else None,
            "double_coins": active_events["double_coins"].isoformat() if active_events.get("double_coins") else None,
        }, f, ensure_ascii=False, indent=2)

def save_vip_price():
    with open(VIP_PRICE_FILE, "w", encoding="utf-8") as f:
        json.dump(vip_price, f, ensure_ascii=False, indent=2)


# Пересчитываем TOTAL_CARDS после загрузки
TOTAL_CARDS = len(cards_db)


# ============================================================
# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
# ============================================================

def format_time(seconds):
    """Форматирует секунды в 'Xч Yм Zс'"""
    seconds = int(seconds)
    if seconds < 0:
        seconds = 0
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours}ч {minutes}м {secs}с"


def get_username(user):
    """Возвращает @username или first_name"""
    if user.username:
        return f"@{user.username}"
    return user.first_name


def escape_html(text):
    """Экранирует HTML-символы"""
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def is_admin(user_id):
    """Проверяет, является ли пользователь админом"""
    return user_id in ADMIN_IDS


def is_cancel(message):
    """Проверяет, является ли сообщение командой отмены (с учётом @username)"""
    if not message.text:
        return False
    text = message.text.strip().lower()
    return text == "/cancel" or text.startswith("/cancel@")


def get_card_rarity(card_name):
    """Возвращает редкость карты"""
    if card_name in cards_db:
        return cards_db[card_name].get("rarity", "Обычная")
    return "Обычная"


def get_card_photo(card_name):
    """Возвращает file_id фото карты"""
    if card_name in cards_db:
        return cards_db[card_name].get("photo", "")
    return ""


def get_inventory(user_id):
    """Возвращает Counter: {название карты: количество}"""
    if user_id not in user_cards:
        return Counter()
    return Counter(user_cards[user_id])


def get_text(key, default):
    """Возвращает кастомный текст или default"""
    return bot_texts.get(key, default)


def get_button(key, default):
    """Возвращает кастомный текст кнопки или default"""
    return bot_buttons.get(key, default)


def log_action(user_id, action, details=""):
    """Логирует действие игрока"""
    if user_id not in user_history:
        user_history[user_id] = []
    user_history[user_id].append({
        "time": datetime.now().isoformat(),
        "action": action,
        "details": details,
    })
    # Оставляем только последние 100
    if len(user_history[user_id]) > 100:
        user_history[user_id] = user_history[user_id][-100:]
    save_history()


def get_all_players():
    """Собирает всех игроков из всех словарей"""
    all_ids = set()
    all_ids.update(user_coins.keys())
    all_ids.update(user_cards.keys())
    all_ids.update(user_exp.keys())
    all_ids.update(user_ranks.keys())
    all_ids.update(user_upgrades.keys())
    all_ids.update(user_vip.keys())
    all_ids.update(user_vip_promos.keys())
    all_ids.update(user_daily.keys())
    return sorted(all_ids)
    
    
# ============================================================
# --- VIP И КУЛДАУНЫ ---
# ============================================================

def is_movement_active():
    """Проверяет, активна ли движуха"""
    global MOVEMENT_UNTIL
    if MOVEMENT_UNTIL is None:
        return False
    if datetime.now() < MOVEMENT_UNTIL:
        return True
    MOVEMENT_UNTIL = None
    return False


def has_active_vip(user_id):
    """Проверяет, есть ли у игрока активный VIP (вечный или временный)"""
    if user_id in user_vip:
        return True
    if user_id in user_vip_promos:
        exp = user_vip_promos[user_id]["expires_at"]
        if datetime.now() < exp:
            return True
        else:
            del user_vip_promos[user_id]
            save_vip_promos()
    return False


def get_vip_expiry_text(user_id):
    """Возвращает текст о сроке VIP"""
    if user_id in user_vip:
        return "⭐ Навсегда"
    if user_id in user_vip_promos:
        exp = user_vip_promos[user_id]["expires_at"]
        if datetime.now() < exp:
            delta = exp - datetime.now()
            days = delta.days
            hours = delta.seconds // 3600
            if days > 0:
                return f"⭐ Осталось: {days}д {hours}ч"
            return f"⭐ Осталось: {hours}ч"
    return ""


def get_cooldown_for_user(user_id):
    """Итоговый кулдаун карты: 0 у админов, 5 сек движуха, 45м VIP, 1ч30м обычный + прокачка"""
    if is_admin(user_id):
        return 0
    if is_movement_active():
        base = COOLDOWN_MOVEMENT_SECONDS
    elif has_active_vip(user_id):
        base = COOLDOWN_VIP_SECONDS
    else:
        base = COOLDOWN_NORMAL_SECONDS
    bonus = get_upgrade_bonus(user_id, "cooldown")
    return int(base * (1 - bonus))


def get_bonus_cooldown(user_id):
    """Кулдаун бонуса: 0 у админов, 1ч30м VIP, 3ч обычный"""
    if is_admin(user_id):
        return 0
    if has_active_vip(user_id):
        return BONUS_COOLDOWN_VIP
    return BONUS_COOLDOWN_NORMAL


# ============================================================
# --- ПРОКАЧКА ---
# ============================================================

def get_upgrade_level(user_id, branch):
    """Возвращает уровень прокачки (0-5)"""
    if user_id not in user_upgrades:
        return 0
    return user_upgrades[user_id].get(branch, 0)


def get_upgrade_bonus(user_id, branch):
    """Возвращает бонус (0.0-0.25) для указанной ветки"""
    lvl = get_upgrade_level(user_id, branch)
    if lvl == 0:
        return 0.0
    if branch == "cooldown":
        return UPGRADE_COOLDOWN_BONUS[lvl - 1]
    if branch == "coins":
        return UPGRADE_COINS_BONUS[lvl - 1]
    if branch == "exp":
        return UPGRADE_EXP_BONUS[lvl - 1]
    return 0.0


# ============================================================
# --- РОЛЛЫ КАРТ ---
# ============================================================

def roll_rarity():
    """Выбирает редкость по шансам. Секретная — 1 из 1000."""
    if random.randint(1, 1000) == 1:
        return "Секретная"
    rarities = ["Обычная", "Редкая", "Эпическая", "Легендарная", "Мифическая"]
    weights = [rarity_chances.get(r, RARITY_REWARDS[r]["chance"]) for r in rarities]
    return random.choices(rarities, weights=weights, k=1)[0]


def get_random_card_by_rarity(rarity):
    """Возвращает случайную карту указанной редкости (с allowed=True)"""
    pool = [
        name for name, data in cards_db.items()
        if data.get("rarity") == rarity and data.get("allowed", True)
    ]
    if not pool:
        return None
    return random.choice(pool)


def roll_reward(rarity):
    """Возвращает (опыт, монеты) с учётом кастомных наград и ивентов"""
    if rarity in custom_rewards:
        r = custom_rewards[rarity]
    else:
        r = RARITY_REWARDS.get(rarity, RARITY_REWARDS["Обычная"])
    exp = random.randint(*r["exp"])
    coins = random.randint(*r["coins"])

    # Ивенты ×2
    if has_double_exp():
        exp *= 2
    if has_double_coins():
        coins *= 2

    return exp, coins


# ============================================================
# --- ИВЕНТЫ ---
# ============================================================

def has_double_exp():
    """Активен ли ивент ×2 опыта"""
    exp = active_events.get("double_exp")
    if exp and datetime.now() < exp:
        return True
    if exp and datetime.now() >= exp:
        active_events["double_exp"] = None
        save_events()
    return False


def has_double_coins():
    """Активен ли ивент ×2 монет"""
    coins = active_events.get("double_coins")
    if coins and datetime.now() < coins:
        return True
    if coins and datetime.now() >= coins:
        active_events["double_coins"] = None
        save_events()
    return False


def get_event_remaining(event_key):
    """Оставшееся время ивента или None"""
    exp = active_events.get(event_key)
    if not exp:
        return None
    if datetime.now() >= exp:
        active_events[event_key] = None
        save_events()
        return None
    return exp - datetime.now()
    
    
# ============================================================
# --- СТАТИСТИКА ---
# ============================================================

def get_economy_stats():
    """Возвращает статистику экономики"""
    total_coins = sum(user_coins.values())
    total_users = len(user_coins)
    avg_coins = total_coins // total_users if total_users else 0
    max_coins = max(user_coins.values()) if user_coins else 0

    top_user = None
    if user_coins:
        top_id = max(user_coins, key=user_coins.get)
        top_user = (top_id, user_coins[top_id])

    return {
        "total_coins": total_coins,
        "total_users": total_users,
        "avg_coins": avg_coins,
        "max_coins": max_coins,
        "top_user": top_user,
    }


def get_activity_stats():
    """Статистика активности за сегодня"""
    today = datetime.now().strftime("%Y-%m-%d")
    today_count = len(daily_players.get("players", []))
    return {
        "today": today_count,
        "today_date": today,
    }


def get_chat_stats():
    """Статистика по чатам (сортировка по количеству участников)"""
    chats = list(known_chats.items())
    if not chats:
        return []

    def get_members(cid):
        try:
            return bot.get_chat_member_count(cid)
        except:
            return 0

    result = []
    for cid, data in chats:
        members = get_members(cid)
        result.append({
            "id": cid,
            "title": data.get("title", "—"),
            "username": data.get("username"),
            "type": data.get("type", "?"),
            "members": members,
        })

    result.sort(key=lambda x: x["members"], reverse=True)
    return result


# ============================================================
# --- ДЕКОРАТОРЫ ---
# ============================================================

def blocked(func):
    """Декоратор для message-обработчиков — игнорирует заблокированных"""
    def wrapper(message, *args, **kwargs):
        if message.from_user and message.from_user.id in blocked_users:
            return
        return func(message, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def blocked_cb(func):
    """Декоратор для callback-обработчиков — игнорирует заблокированных"""
    def wrapper(call, *args, **kwargs):
        if call.from_user and call.from_user.id in blocked_users:
            return
        return func(call, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


def not_in_tech_mode(func):
    """Декоратор — не пускает в тех. режим (кроме админов)"""
    def wrapper(message, *args, **kwargs):
        if message.from_user and is_admin(message.from_user.id):
            return func(message, *args, **kwargs)
        if tech_mode.get("enabled"):
            if message.content_type == 'text':
                try:
                    bot.reply_to(message, tech_mode.get("message", "🔧 Тех. работы."))
                except:
                    pass
            return
        return func(message, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# ============================================================
# --- ФОНОВЫЕ ПОТОКИ ---
# ============================================================

def register_player_today(user_id):
    """Регистрирует игрока в списке сегодняшних"""
    today = datetime.now().strftime("%Y-%m-%d")
    if daily_players.get("date") != today:
        daily_players["date"] = today
        daily_players["players"] = []
    if user_id not in daily_players["players"]:
        daily_players["players"].append(user_id)
        save_daily_players()


def daily_reset_loop():
    """Обнуляет daily_players в 00:00"""
    while True:
        try:
            now = datetime.now()
            next_midnight = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            wait_seconds = (next_midnight - now).total_seconds()
            time.sleep(wait_seconds)
            daily_players["date"] = next_midnight.strftime("%Y-%m-%d")
            daily_players["players"] = []
            save_daily_players()
            print(f"[DAILY RESET] {daily_players['date']} — список игроков обнулён")
        except Exception as e:
            print(f"[DAILY RESET] Ошибка: {e}")
            time.sleep(60)


def vip_expiry_check_loop():
    """Проверяет окончание VIP каждые 5 минут"""
    while True:
        try:
            time.sleep(300)
            now = datetime.now()
            expired = []
            for uid, data in list(user_vip_promos.items()):
                exp = data.get("expires_at")
                if exp and now >= exp:
                    expired.append(uid)
            for uid in expired:
                del user_vip_promos[uid]
                try:
                    bot.send_message(uid,
                        f"⭐ <b>Ваш VIP закончился!</b>\n\n"
                        f"Хотите продлить? Введите <code>/vip</code>",
                        parse_mode="HTML")
                except:
                    pass
            if expired:
                save_vip_promos()
                print(f"[VIP EXPIRY] У {len(expired)} игроков закончился VIP")
        except Exception as e:
            print(f"[VIP EXPIRY] Ошибка: {e}")
            time.sleep(60)
            
            
# ============================================================
# --- ПРИВЕТСТВИЕ ПРИ ДОБАВЛЕНИИ В ЧАТ ---
# ============================================================
@bot.message_handler(content_types=['new_chat_members'])
@blocked
def bot_added_to_chat(message):
    chat_id = message.chat.id
    if message.chat.type != 'private':
        if chat_id not in known_chats:
            known_chats[chat_id] = {
                "title": message.chat.title or f"Чат {chat_id}",
                "type": message.chat.type,
                "username": message.chat.username,
                "added_at": datetime.now().isoformat(),
            }
            save_known_chats()

    for member in message.new_chat_members:
        if member.id == bot.get_me().id:
            how_to_play = (
                f"🎯 <b>КАК ИГРАТЬ:</b>\n"
                f"1️⃣ Напишите /help и выберите игру!\n"
                f"2️⃣ Играйте и становитесь крутым!\n"
                f"3️⃣ Копите опыт, монетки и поднимайтесь в ТОПе"
            )
            text = (
                f"🎮 <b>ВНИМАНИЕ, ГЕЙМЕРЫ!</b>\n\n"
                f"<i>Меня добавили в этот чат, чтобы вы могли играть в разные игры!</i>\n\n"
                f"<blockquote>{how_to_play}</blockquote>\n\n"
                f"{THICK_LINE}\n\n"
                f"💡 <b>Вы также можете добавить бота в свой чат или играть в личном чате с ботом</b>\n"
                f"Узнать все функции можно по команде /help"
            )
            bot.send_message(message.chat.id, text, parse_mode="HTML")
            return


# ============================================================
# --- /start ---
# ============================================================
@bot.message_handler(commands=['start'])
@blocked
def start_command(message):
    chat_type = message.chat.type

    if chat_type != 'private':
        chat_id = message.chat.id
        if chat_id not in known_chats:
            known_chats[chat_id] = {
                "title": message.chat.title or f"Чат {chat_id}",
                "type": chat_type,
                "username": message.chat.username,
                "added_at": datetime.now().isoformat(),
            }
            save_known_chats()

    # Кнопка "Добавить в группу" — для всех
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(
            "➕ Добавить бота в группу",
            url=f"https://t.me/{bot.get_me().username}?startgroup=start"
        ),
    )

    if chat_type == 'private':
        default_text = (
            f"👋 <b>Привет геймер!</b>\n"
            f"Тут ты можешь играть в разные игры нашего бота, развлекаться с друзьями "
            f"и становится лучшим в нашем боте!\n\n"
            f"<b>Как начать играть?</b>\n"
            f"<i>Отправь команду «игры»</i>\n\n"
            f"<blockquote>Узнать все функции можно по команде /help</blockquote>"
        )
        text = get_text("start", default_text)
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    else:
        how_to_play = (
            f"🎯 <b>КАК ИГРАТЬ:</b>\n"
            f"1️⃣ Напишите /help и выберите игру!\n"
            f"2️⃣ Играйте и становитесь крутым!\n"
            f"3️⃣ Копите опыт, монетки и поднимайтесь в ТОПе"
        )
        text = (
            f"🎮 <b>ВНИМАНИЕ, ГЕЙМЕРЫ!</b>\n\n"
            f"<i>Меня добавили в этот чат, чтобы вы могли играть в разные игры!</i>\n\n"
            f"<blockquote>{how_to_play}</blockquote>\n\n"
            f"{THICK_LINE}\n\n"
            f"💡 <b>Вы также можете добавить бота в свой чат или играть в личном чате с ботом</b>\n"
            f"Узнать все функции можно по команде /help"
        )
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")


# ============================================================
# --- /help ---
# ============================================================
@bot.message_handler(commands=['help'])
@blocked
def help_command(message):
    default_text = (
        f"📖 <b>ПОМОЩЬ И ПОДДЕРЖКА</b>\n\n"
        f"🎮 <b>Команды:</b>\n"
        f"<blockquote>"
        f"• /start — Приветствие\n"
        f"• /countryball — Получить карточку\n"
        f"• /profile — Ваш профиль\n"
        f"• /inventory — Ваш инвентарь\n"
        f"• /daily — Ежедневный бонус\n"
        f"• промо #КОД — Активировать промокод\n"
        f"• /vip — Купить VIP на 30 дней\n"
        f"• /top — Рейтинг игроков\n"
        f"• /bonus — Бонусная карточка\n"
        f"• /upgrade — Прокачка (за монеты)\n"
        f"• /season — Информация о сезоне"
        f"</blockquote>\n\n"
        f"{THICK_LINE}"
    )
    text = get_text("help", default_text)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("👨‍💻 Тех. поддержка", url="https://t.me/papaedetBvolgograd"),
        types.InlineKeyboardButton("🧑‍💻 Разработчик", url="https://t.me/BlockDavidYT"),
    )
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")


# ============================================================
# --- /season ---
# ============================================================
@bot.message_handler(commands=['season'])
@blocked
def season_command(message):
    now = datetime.now()
    delta = SEASON_END - now
    if delta.total_seconds() < 0:
        time_text = "Сезон завершён"
    else:
        days = delta.days
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        time_text = f"{days}д {hours}ч {minutes}м {seconds}с"

    default_text = (
        f"🤖 <b>СЕЗОН 0: \"БЕТА-ТЕСТ\"</b>\n"
        f"Добро пожаловать в бета тест CountryBallsGames!\n\n"
        f"Бот открылся совсем недавно! Могут присутствовать баги, ошибки и не только.\n"
        f"Но мы стараемся делать всë качественно!\n\n"
        f"{THICK_LINE}\n\n"
        f"📦 <b>В СЕЗОНЕ 0:</b>\n\n"
        f"🌏 30+ уникальных карточек\n"
        f"⭐️ 6 редкостей: от Обычной до Секретной\n"
        f"🏅 10 Рангов\n"
        f"👑 VIP-статус\n\n"
        f"{THICK_LINE}\n\n"
        f"🔥 <b>ЧТО ДАЛЬШЕ?</b>\n"
        f"Этот сезон лишь закладывает фундамент для будущего бота!\n\n"
        f"{THICK_LINE}\n"
        f"📅 Сезон заканчивается: <b>26.09.2026 16:00 МСК</b>\n"
        f"⏳ Осталось: <b>{{time}}</b>\n\n"
        f"{THICK_LINE}\n\n"
        f"👉 Напиши <b>КОНТРИБОЛ</b> — и получи свою первую карту прямо сейчас!\n"
        f"<blockquote>📢 Подписывайся на канал: @CountryBallsGames\n"
        f"💬 Наш чат: @CountryBallsGames_Chat</blockquote>"
    )
    text = get_text("season", default_text)
    text = text.replace("{time}", time_text)

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("👨‍💻 Тех.Поддержка", url="https://t.me/papaedetBvolgograd"))
    bot.send_message(message.chat.id, text, parse_mode="HTML",
                     reply_markup=markup, reply_to_message_id=message.message_id)


# ============================================================
# --- /countryball ---
# ============================================================
@bot.message_handler(commands=['countryball'])
@blocked
def countryball_command(message):
    card_command(message)
    
    
# ============================================================
# --- ПРОФИЛЬ ---
# ============================================================
@bot.message_handler(commands=['profile'])
@bot.message_handler(func=lambda message: message.text and message.text.lower().strip() == "профиль")
@blocked
def profile_command(message):
    global TOTAL_CARDS
    TOTAL_CARDS = len(cards_db)

    user_id = message.from_user.id
    username = get_username(message.from_user)

    if user_id not in user_coins: user_coins[user_id] = 0
    if user_id not in user_cards: user_cards[user_id] = []
    if user_id not in user_exp: user_exp[user_id] = 0
    if user_id not in user_ranks: user_ranks[user_id] = 1
    save_coins(); save_cards(); save_exp(); save_ranks()

    coins = user_coins[user_id]
    cards_count = len(set(user_cards[user_id]))
    exp = user_exp[user_id]
    rank = user_ranks[user_id]
    rank_data = RANKS[rank]
    rank_name = rank_data["name"]

    vip_mark = " ⭐VIP" if has_active_vip(user_id) else ""
    vip_text = get_vip_expiry_text(user_id)

    # Как на фото: заголовок отдельно, данные отдельно
    header_quote = "🖥️ ПРОФИЛЬ ИГРОКА"
    body_quote = (
        f"🆔 Айди: {user_id}\n"
        f"📝 Имя: {escape_html(username)}{vip_mark}\n"
        f"🃏 В коллекции: [{cards_count}/{TOTAL_CARDS}]\n"
        f"💎 Опыта: {exp}\n"
        f"💸 Монеток: {coins}\n"
        f"🎖️ Ранг: {rank_name} [{rank}/10]"
    )
    if vip_text:
        body_quote += f"\n{vip_text}"

    if rank < 10:
        exp_needed = rank_data["exp_needed"]
        next_rank_text = f"🎖️ Следующий ранг: {escape_html(username)} [{exp}/{exp_needed}]"
    else:
        next_rank_text = "🎖️ Максимальный ранг достигнут!"

    text = (
        f"<blockquote>{header_quote}</blockquote>\n\n"
        f"<blockquote>{body_quote}</blockquote>\n\n"
        f"{THICK_LINE}\n\n"
        f"{next_rank_text}"
    )

    markup = types.InlineKeyboardMarkup()
    if rank < 10:
        exp_needed = rank_data["exp_needed"]
        if exp >= exp_needed:
            markup.add(types.InlineKeyboardButton(text="🎖️ ПОВЫСИТЬ РАНГ", callback_data="rank_up"))

    bot.send_message(message.chat.id, text, reply_markup=markup,
                     parse_mode="HTML", reply_to_message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == "rank_up")
@blocked_cb
def rank_up_callback(call):
    user_id = call.from_user.id
    if user_id not in user_ranks: user_ranks[user_id] = 1
    if user_id not in user_exp: user_exp[user_id] = 0

    rank = user_ranks[user_id]
    if rank >= 10:
        bot.answer_callback_query(call.id, "🏅 Максимальный ранг!", show_alert=True)
        return

    exp_needed = RANKS[rank]["exp_needed"]
    if user_exp[user_id] < exp_needed:
        bot.answer_callback_query(call.id, f"❌ Недостаточно опыта! Нужно: {exp_needed}", show_alert=True)
        return

    user_ranks[user_id] = rank + 1
    save_ranks()

    new_rank = user_ranks[user_id]
    new_rank_name = RANKS[new_rank]["name"]
    bot.answer_callback_query(call.id, f"🎉 Ранг повышен: {new_rank_name}!", show_alert=True)

    text = (
        f"🎉 <b>ПОЗДРАВЛЯЕМ!</b>\n"
        f"{THICK_LINE}\n"
        f"🎖️ Новый ранг: {new_rank_name} [{new_rank}/10]\n"
        f"💎 Опыт: {user_exp[user_id]}\n"
        f"{THICK_LINE}\n"
        f"🚀 Продолжай собирать карточки!"
    )
    bot.send_message(call.message.chat.id, text, parse_mode="HTML")


# ============================================================
# --- ТОП ---
# ============================================================
@bot.message_handler(commands=['top'])
@bot.message_handler(func=lambda message: message.text and message.text.lower().strip() in ("топ", "рейтинг"))
@blocked
def top_command(message):
    top_coins = sorted(user_coins.items(), key=lambda x: x[1], reverse=True)[:10]
    top_exp = sorted(user_exp.items(), key=lambda x: x[1], reverse=True)[:10]
    medals = ["🥇", "🥈", "🥉"]

    def build_top(data):
        out = ""
        for i, (uid, amount) in enumerate(data, start=1):
            medal = medals[i-1] if i <= 3 else f"{i}."
            try:
                chat_member = bot.get_chat(uid)
                name = chat_member.first_name or f"ID {uid}"
            except:
                name = f"ID {uid}"
            out += f"{medal} {escape_html(name)} — {amount}\n"
        return out or "Пока пусто\n"

    coins_text = build_top(top_coins)
    exp_text = build_top(top_exp)

    text = (
        f"🏆 <b>РЕЙТИНГ ИГРОКОВ</b>\n"
        f"{THICK_LINE}\n"
        f"💸 <b>ТОП ПО МОНЕТКАМ:</b>\n"
        f"<blockquote>{coins_text}</blockquote>\n"
        f"{THICK_LINE}\n"
        f"💎 <b>ТОП ПО ОПЫТУ:</b>\n"
        f"<blockquote>{exp_text}</blockquote>\n"
        f"{THICK_LINE}"
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML",
                     reply_to_message_id=message.message_id)


# ============================================================
# --- /cancel ---
# ============================================================
@bot.message_handler(commands=['cancel'])
@blocked
def cancel_command(message):
    user_id = message.from_user.id
    if user_id in pending_cards:
        del pending_cards[user_id]
    if user_id in pending_promos:
        del pending_promos[user_id]
    bot.clear_step_handler_by_chat_id(message.chat.id)
    bot.send_message(message.chat.id, "❌ Действие отменено.")


# ============================================================
# --- ВЫДАЧА КАРТЫ ---
# ============================================================
CARD_TRIGGERS = ["карта", "карточка", "кантрибол", "контрибол", "кантри"]


def give_card(user_id, user_name, chat_id, reply_to=None, show_bonus_button=True):
    global TOTAL_CARDS
    TOTAL_CARDS = len(cards_db)

    if not cards_db:
        bot.send_message(chat_id, "⚠️ В базе пока нет карточек!")
        return False

    rarity = roll_rarity()
    card_name = get_random_card_by_rarity(rarity)

    if not card_name:
        available = [name for name, data in cards_db.items() if data.get("allowed", True)]
        if not available:
            bot.send_message(chat_id, "⚠️ Нет доступных карт!")
            return False
        card_name = random.choice(available)
        rarity = get_card_rarity(card_name)

    card_photo = get_card_photo(card_name)
    rarity_emoji = RARITIES.get(rarity, "⚪")
    exp_reward, coins_reward = roll_reward(rarity)

    if has_active_vip(user_id):
        exp_reward *= 2
        coins_reward *= 2

    coins_bonus = get_upgrade_bonus(user_id, "coins")
    exp_bonus = get_upgrade_bonus(user_id, "exp")
    coins_reward = int(coins_reward * (1 + coins_bonus))
    exp_reward = int(exp_reward * (1 + exp_bonus))

    # Проверяем, есть ли уже такая карта
    is_duplicate = card_name in user_cards.get(user_id, [])

    if user_id not in user_cards:
        user_cards[user_id] = []
    user_cards[user_id].append(card_name)
    save_cards()

    if user_id not in user_coins:
        user_coins[user_id] = 0
    user_coins[user_id] += coins_reward
    save_coins()

    if user_id not in user_exp:
        user_exp[user_id] = 0
    user_exp[user_id] += exp_reward
    save_exp()

    if user_id not in user_ranks:
        user_ranks[user_id] = 1
        save_ranks()

    collection_count = len(set(user_cards[user_id]))

    quote_text = (
        f"{rarity_emoji} Редкость: {rarity}\n"
        f"📚 Ваша коллекция: [{collection_count}/{TOTAL_CARDS}]\n"
        f"💎 Получено опыта: +{exp_reward}\n"
        f"💸 Получено монеток: +{coins_reward}"
    )

    cooldown_seconds = get_cooldown_for_user(user_id)
    cooldown_text = format_time(cooldown_seconds)

    if is_duplicate:
        title_word = "повторка"
    else:
        title_word = "карточка"

    # Строка про повторку — в цитате, сразу под заголовком
    dup_line = "\n\n<blockquote>Эта карточка уже есть в коллекции</blockquote>" if is_duplicate else ""

    if show_bonus_button:
        caption = (
            f"👤 {escape_html(user_name)}, Вам выпала {title_word} «{escape_html(card_name)}»"
            f"{dup_line}\n\n"
            f"<blockquote>{quote_text}</blockquote>\n\n"
            f"<blockquote>До следующей карточки: {cooldown_text}</blockquote>"
        )
    else:
        bonus_cd_seconds = get_bonus_cooldown(user_id)
        bonus_cd_text = format_time(bonus_cd_seconds)
        caption = (
            f"👤 {escape_html(user_name)}, Вам выпала {title_word} «{escape_html(card_name)}»"
            f"{dup_line}\n\n"
            f"<blockquote>{quote_text}</blockquote>\n\n"
            f"<blockquote>До следующего бонуса: {bonus_cd_text}</blockquote>"
        )

    if show_bonus_button:
        cooldown = get_bonus_cooldown(user_id)
        show = True
        if user_id in user_bonus:
            last = user_bonus[user_id].get("last_used")
            if last:
                last_dt = datetime.fromisoformat(last)
                if (datetime.now() - last_dt).total_seconds() < cooldown:
                    show = False
        if show:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🎁 Бонус", callback_data="bonus_from_card"))
        else:
            markup = None
    else:
        markup = None

    if card_photo:
        try:
            bot.send_photo(chat_id, card_photo, caption=caption,
                           parse_mode="HTML", reply_markup=markup,
                           reply_to_message_id=reply_to)
        except Exception as e:
            bot.send_message(chat_id, f"{caption}\n\n⚠️ Ошибка фото: {e}",
                             reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, caption, parse_mode="HTML",
                         reply_markup=markup, reply_to_message_id=reply_to)

    log_action(user_id, "Получил карту", f"{card_name} [{rarity}]")
    return True


@bot.message_handler(func=lambda message: message.text and message.text.lower().strip() in CARD_TRIGGERS)
@blocked
def card_command(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    now = datetime.now()
    cooldown_seconds = get_cooldown_for_user(user_id)

    if user_id in user_cooldowns:
        next_time = user_cooldowns[user_id] + timedelta(seconds=cooldown_seconds)
        if now < next_time:
            remaining = int((next_time - now).total_seconds())
            text = (
                f"🚫 {escape_html(user_name)} вы уже получали ранее карточку!\n\n"
                f"<blockquote>Возвращайтесь через: {format_time(remaining)}</blockquote>"
            )
            bot.reply_to(message, text, parse_mode="HTML")
            return

    if give_card(user_id, user_name, message.chat.id, reply_to=message.message_id):
        user_cooldowns[user_id] = now
        save_cooldowns()


@bot.callback_query_handler(func=lambda call: call.data == "card_again")
@blocked_cb
def card_again_callback(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    now = datetime.now()
    cooldown_seconds = get_cooldown_for_user(user_id)

    if user_id in user_cooldowns:
        next_time = user_cooldowns[user_id] + timedelta(seconds=cooldown_seconds)
        if now < next_time:
            remaining = int((next_time - now).total_seconds())
            bot.answer_callback_query(call.id,
                f"🚫 Подождите: {format_time(remaining)}", show_alert=True)
            return

    bot.answer_callback_query(call.id)
    if give_card(user_id, user_name, call.message.chat.id):
        user_cooldowns[user_id] = now
        save_cooldowns()
        
        
# ============================================================
# --- ЕЖЕДНЕВНЫЙ БОНУС /daily ---
# ============================================================
@bot.message_handler(commands=['daily'])
@bot.message_handler(func=lambda message: message.text and message.text.lower().strip() in ("дейли", "ежедневка"))
@blocked
def daily_command(message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    now = datetime.now()

    if user_id not in user_daily:
        user_daily[user_id] = {"streak": 0, "last_claim": None}

    streak = user_daily[user_id].get("streak", 0)
    last_claim_str = user_daily[user_id].get("last_claim")

    # Проверка кулдауна — пропускается для админов
    if last_claim_str and not is_admin(user_id):
        last_claim = datetime.fromisoformat(last_claim_str)
        elapsed = (now - last_claim).total_seconds()

        if elapsed < 24 * 60 * 60:
            remaining = 24 * 60 * 60 - int(elapsed)
            text = (
                f"[ 🚫 ] {escape_html(user_name)} <b>Вы уже получали сегодня ежедневную серию!</b>\n\n"
                f"<blockquote>Приходи через: {format_time(remaining)}</blockquote>"
            )
            bot.reply_to(message, text, parse_mode="HTML")
            return

        if elapsed > 48 * 60 * 60:
            streak = 0

    if streak < 50:
        streak += 1

    coin_reward = 500 + int((5000 - 500) / 49 * (streak - 1))
    exp_reward = 250 + int((2500 - 250) / 49 * (streak - 1))

    # Ивенты ×2
    if has_double_exp():
        exp_reward *= 2
    if has_double_coins():
        coin_reward *= 2

    if user_id not in user_coins: user_coins[user_id] = 0
    if user_id not in user_exp: user_exp[user_id] = 0
    user_coins[user_id] += coin_reward
    user_exp[user_id] += exp_reward
    save_coins()
    save_exp()

    user_daily[user_id] = {
        "streak": streak,
        "last_claim": now.isoformat(),
    }
    save_daily()

    log_action(user_id, "Забрал daily", f"streak={streak}")

    quote_text = (
        f"💵 {coin_reward} монет.\n"
        f"💎 {exp_reward} опыта."
    )
    text = (
        f"🎉 \"{escape_html(user_name)}\" Вы успешно получили ежедневный бонус!\n"
        f"<i>Вы получили:</i>\n\n"
        f"<blockquote>{quote_text}</blockquote>\n\n"
        f"Приходи завтра через 24 часа!\n\n"
        f"<blockquote>🔥 Текущая серия: {streak}/50</blockquote>"
    )
    bot.reply_to(message, text, parse_mode="HTML")
    
    
# ============================================================
# --- ИНВЕНТАРЬ ---
# ============================================================
def show_inventory_page(chat_id, user_id, page, message_id=None):
    inv = get_inventory(user_id)

    if not inv:
        text = (
            f"🎒 <b>ВАШ ИНВЕНТАРЬ</b>\n"
            f"{THICK_LINE}\n"
            f"📭 У вас пока нет карточек."
        )
        if message_id:
            try:
                bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                      parse_mode="HTML")
            except:
                bot.send_message(chat_id, text, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, parse_mode="HTML")
        return

    items = sorted(inv.items(), key=lambda x: x[0])
    total_items = len(items)
    total_pages = max(1, (total_items + INVENTORY_PER_PAGE - 1) // INVENTORY_PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * INVENTORY_PER_PAGE
    page_items = items[start:start + INVENTORY_PER_PAGE]

    markup = types.InlineKeyboardMarkup(row_width=1)
    for idx_in_page, (card_name, count) in enumerate(page_items):
        global_idx = start + idx_in_page
        rarity = get_card_rarity(card_name)
        markup.add(types.InlineKeyboardButton(
            f"{escape_html(card_name)} [{rarity}] — {count} шт.",
            callback_data=f"inv_open_{user_id}_{global_idx}"
        ))

    nav = []
    if page > 1:
        nav.append(types.InlineKeyboardButton("◀️", callback_data=f"invnav_{user_id}_{page-1}"))
    nav.append(types.InlineKeyboardButton(f"{page}/{total_pages}", callback_data="inv_noop"))
    if page < total_pages:
        nav.append(types.InlineKeyboardButton("▶️", callback_data=f"invnav_{user_id}_{page+1}"))
    markup.row(*nav)

    text = (
        f"🎒 <b>ВАШ ИНВЕНТАРЬ [{page}/{total_pages}]</b>\n"
        f"{THICK_LINE}\n"
        f"Нажмите на карточку, чтобы открыть её."
    )

    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except Exception as e:
            if "message is not modified" not in str(e).lower():
                try:
                    bot.delete_message(chat_id, message_id)
                except:
                    pass
                bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=['inventory', 'inv'])
@bot.message_handler(func=lambda message: message.text and message.text.lower().strip() in ("инвентарь", "инв", "мешок"))
@blocked
def inventory_command(message):
    show_inventory_page(message.chat.id, message.from_user.id, 1)


@bot.callback_query_handler(func=lambda call: call.data == "inv_noop")
@blocked_cb
def inv_noop(call):
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("invnav_"))
@blocked_cb
def inventory_nav(call):
    try:
        _, owner_id_str, page_str = call.data.split("_")
        owner_id = int(owner_id_str)
        page = int(page_str)
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!")
        return

    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "Бро, не туда лезешь.", show_alert=True)
        return

    bot.answer_callback_query(call.id)
    time.sleep(0.3)
    show_inventory_page(call.message.chat.id, owner_id, page,
                        message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("inv_open_"))
@blocked_cb
def inventory_open_card(call):
    try:
        raw = call.data.replace("inv_open_", "")
        parts = raw.split("_")
        owner_id = int(parts[0])
        global_idx = int(parts[1])
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!")
        return

    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "Бро, не туда лезешь.", show_alert=True)
        return

    inv = get_inventory(owner_id)
    items = sorted(inv.items(), key=lambda x: x[0])

    if global_idx < 0 or global_idx >= len(items):
        bot.answer_callback_query(call.id, "❌ Карточки больше нет!", show_alert=True)
        return

    card_name, count = items[global_idx]
    if count <= 0:
        bot.answer_callback_query(call.id, "❌ Карточки нет!", show_alert=True)
        return

    rarity = get_card_rarity(card_name)
    photo = get_card_photo(card_name)
    price = SELL_PRICES.get(rarity, 5)

    caption = (
        f"🃏 <b>{escape_html(card_name)}</b>\n"
        f"{THICK_LINE}\n"
        f"🎨 Редкость: <b>{rarity}</b>\n"
        f"📦 У вас: <b>{count} шт.</b>\n"
        f"💰 Цена за 1: <b>{price}</b> монет\n"
        f"{THICK_LINE}"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"💸 Продать 1 шт. (+{price})",
                                    callback_data=f"inv_sell_1_{owner_id}_{global_idx}"),
        types.InlineKeyboardButton(f"💰 Продать всё (+{price*count})",
                                    callback_data=f"inv_sell_all_{owner_id}_{global_idx}"),
        types.InlineKeyboardButton("🔙 Назад", callback_data=f"inv_back_{owner_id}"),
    )

    if photo:
        try:
            bot.edit_message_media(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                media=types.InputMediaPhoto(photo, caption=caption, parse_mode="HTML"),
                reply_markup=markup
            )
        except:
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_photo(call.message.chat.id, photo, caption=caption,
                           reply_markup=markup, parse_mode="HTML")
    else:
        try:
            bot.edit_message_text(caption, chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except:
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except:
                pass
            bot.send_message(call.message.chat.id, caption,
                             reply_markup=markup, parse_mode="HTML")

    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("inv_sell_"))
@blocked_cb
def inventory_sell(call):
    try:
        raw = call.data.replace("inv_sell_", "")
        parts = raw.split("_")
        if parts[0] == "1":
            sell_type = "1"
            owner_id = int(parts[1])
            global_idx = int(parts[2])
        elif parts[0] == "all":
            sell_type = "all"
            owner_id = int(parts[1])
            global_idx = int(parts[2])
        else:
            bot.answer_callback_query(call.id, "❌ Ошибка!"); return
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "Бро, не туда лезешь.", show_alert=True)
        return

    inv = get_inventory(owner_id)
    items = sorted(inv.items(), key=lambda x: x[0])

    if global_idx < 0 or global_idx >= len(items):
        bot.answer_callback_query(call.id, "❌ Карточки нет!"); return

    card_name, count = items[global_idx]
    if count <= 0:
        bot.answer_callback_query(call.id, "❌ Карточки нет!"); return

    rarity = get_card_rarity(card_name)
    price = SELL_PRICES.get(rarity, 5)
    sell_count = 1 if sell_type == "1" else count
    total = price * sell_count

    for _ in range(sell_count):
        if card_name in user_cards.get(owner_id, []):
            user_cards[owner_id].remove(card_name)
    save_cards()

    user_coins[owner_id] = user_coins.get(owner_id, 0) + total
    save_coins()

    log_action(owner_id, "Продал карту", f"{card_name} x{sell_count} (+{total})")

    bot.answer_callback_query(call.id, f"✅ Продано {sell_count} шт. +{total} монет", show_alert=True)

    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    show_inventory_page(call.message.chat.id, owner_id, 1)


@bot.callback_query_handler(func=lambda call: call.data.startswith("inv_back_"))
@blocked_cb
def inventory_back(call):
    try:
        owner_id = int(call.data.replace("inv_back_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    if call.from_user.id != owner_id:
        bot.answer_callback_query(call.id, "Бро, не туда лезешь.", show_alert=True)
        return

    bot.answer_callback_query(call.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except:
        pass
    show_inventory_page(call.message.chat.id, owner_id, 1)
    
    
# ============================================================
# --- ПРОКАЧКА ---
# ============================================================
def _show_upgrade_menu(call):
    user_id = call.from_user.id
    if user_id not in user_upgrades:
        user_upgrades[user_id] = {"cooldown": 0, "coins": 0, "exp": 0}
    if user_id not in user_coins:
        user_coins[user_id] = 0

    cd_lvl = user_upgrades[user_id]["cooldown"]
    co_lvl = user_upgrades[user_id]["coins"]
    ex_lvl = user_upgrades[user_id]["exp"]

    cd_cost = UPGRADE_COSTS_COOLDOWN[cd_lvl] if cd_lvl < 5 else "ПРОЙДЕНО"
    co_cost = UPGRADE_COSTS_COINS[co_lvl] if co_lvl < 5 else "ПРОЙДЕНО"
    ex_cost = UPGRADE_COSTS_EXP[ex_lvl] if ex_lvl < 5 else "ПРОЙДЕНО"

    text = (
        f"⚡ <b>ПРОКАЧКА</b>\n"
        f"{THICK_LINE}\n"
        f"💸 Ваши монеты: <b>{user_coins.get(user_id, 0)}</b>\n\n"
        f"🔹 <b>Кулдаун карт</b> — ур. {cd_lvl}/5\n"
        f"   Бонус: -{int(get_upgrade_bonus(user_id, 'cooldown')*100)}%\n"
        f"   Следующий: <b>{cd_cost}</b>\n\n"
        f"🔹 <b>Монетки</b> — ур. {co_lvl}/5\n"
        f"   Бонус: +{int(get_upgrade_bonus(user_id, 'coins')*100)}%\n"
        f"   Следующий: <b>{co_cost}</b>\n\n"
        f"🔹 <b>Опыт</b> — ур. {ex_lvl}/5\n"
        f"   Бонус: +{int(get_upgrade_bonus(user_id, 'exp')*100)}%\n"
        f"   Следующий: <b>{ex_cost}</b>\n"
        f"{THICK_LINE}\n"
        f"Выберите, что прокачать:"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"⏱️ Кулдаун (ур. {cd_lvl}/5)", callback_data="upg_cooldown"),
        types.InlineKeyboardButton(f"💸 Монетки (ур. {co_lvl}/5)", callback_data="upg_coins"),
        types.InlineKeyboardButton(f"💎 Опыт (ур. {ex_lvl}/5)", callback_data="upg_exp"),
    )
    try:
        bot.edit_message_text(text, chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")


@bot.message_handler(commands=['upgrade', 'upgrades'])
@bot.message_handler(func=lambda message: message.text and message.text.lower().strip() in ("прокачка", "апгрейд"))
@blocked
def upgrade_command(message):
    user_id = message.from_user.id
    if user_id not in user_upgrades:
        user_upgrades[user_id] = {"cooldown": 0, "coins": 0, "exp": 0}
    if user_id not in user_coins:
        user_coins[user_id] = 0

    cd_lvl = user_upgrades[user_id]["cooldown"]
    co_lvl = user_upgrades[user_id]["coins"]
    ex_lvl = user_upgrades[user_id]["exp"]

    cd_cost = UPGRADE_COSTS_COOLDOWN[cd_lvl] if cd_lvl < 5 else "ПРОЙДЕНО"
    co_cost = UPGRADE_COSTS_COINS[co_lvl] if co_lvl < 5 else "ПРОЙДЕНО"
    ex_cost = UPGRADE_COSTS_EXP[ex_lvl] if ex_lvl < 5 else "ПРОЙДЕНО"

    text = (
        f"⚡ <b>ПРОКАЧКА</b>\n"
        f"{THICK_LINE}\n"
        f"💸 Ваши монеты: <b>{user_coins[user_id]}</b>\n\n"
        f"🔹 <b>Кулдаун карт</b> — ур. {cd_lvl}/5\n"
        f"   Бонус: -{int(get_upgrade_bonus(user_id, 'cooldown')*100)}%\n"
        f"   Следующий: <b>{cd_cost}</b>\n\n"
        f"🔹 <b>Монетки</b> — ур. {co_lvl}/5\n"
        f"   Бонус: +{int(get_upgrade_bonus(user_id, 'coins')*100)}%\n"
        f"   Следующий: <b>{co_cost}</b>\n\n"
        f"🔹 <b>Опыт</b> — ур. {ex_lvl}/5\n"
        f"   Бонус: +{int(get_upgrade_bonus(user_id, 'exp')*100)}%\n"
        f"   Следующий: <b>{ex_cost}</b>\n"
        f"{THICK_LINE}\n"
        f"Выберите, что прокачать:"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton(f"⏱️ Кулдаун (ур. {cd_lvl}/5)", callback_data="upg_cooldown"),
        types.InlineKeyboardButton(f"💸 Монетки (ур. {co_lvl}/5)", callback_data="upg_coins"),
        types.InlineKeyboardButton(f"💎 Опыт (ур. {ex_lvl}/5)", callback_data="upg_exp"),
    )
    bot.send_message(message.chat.id, text, reply_markup=markup,
                     parse_mode="HTML", reply_to_message_id=message.message_id)


@bot.callback_query_handler(func=lambda call: call.data in ("upg_cooldown", "upg_coins", "upg_exp"))
@blocked_cb
def upgrade_callback(call):
    branch = call.data.replace("upg_", "")
    user_id = call.from_user.id

    if user_id not in user_upgrades:
        user_upgrades[user_id] = {"cooldown": 0, "coins": 0, "exp": 0}
    if user_id not in user_coins:
        user_coins[user_id] = 0

    lvl = user_upgrades[user_id].get(branch, 0)

    if lvl >= 5:
        bot.answer_callback_query(call.id, "🏅 Максимальный уровень!", show_alert=True)
        return

    costs = {
        "cooldown": UPGRADE_COSTS_COOLDOWN,
        "coins": UPGRADE_COSTS_COINS,
        "exp": UPGRADE_COSTS_EXP,
    }[branch]
    cost = costs[lvl]

    if user_coins[user_id] < cost:
        bot.answer_callback_query(call.id,
            f"❌ Нужно {cost} монет. У вас: {user_coins[user_id]}", show_alert=True)
        return

    user_coins[user_id] -= cost
    user_upgrades[user_id][branch] = lvl + 1
    save_coins()
    save_upgrades()

    names = {"cooldown": "⏱️ Кулдаун", "coins": "💸 Монетки", "exp": "💎 Опыт"}
    bonus = get_upgrade_bonus(user_id, branch)
    sign = "-" if branch == "cooldown" else "+"

    log_action(user_id, "Прокачал", f"{branch} → ур.{lvl+1}")

    bot.answer_callback_query(call.id,
        f"✅ {names[branch]} → ур. {lvl+1} ({sign}{int(bonus*100)}%)", show_alert=True)
    _show_upgrade_menu(call)


# ============================================================
# --- БОНУС ---
# ============================================================
def check_subscription(user_id):
    ch_ok = False
    chat_ok = False
    try:
        ch = bot.get_chat_member(BONUS_CHANNEL, user_id)
        ch_ok = ch.status in ("member", "administrator", "creator")
    except:
        pass
    try:
        ch2 = bot.get_chat_member(BONUS_CHAT, user_id)
        chat_ok = ch2.status in ("member", "administrator", "creator")
    except:
        pass
    return ch_ok, chat_ok


def _send_bonus_subscription_msg(chat_id, ch_ok, chat_ok, cooldown, reply_to=None):
    markup = types.InlineKeyboardMarkup(row_width=1)
    if not ch_ok:
        markup.add(types.InlineKeyboardButton("📢 Подписаться на канал", url=BONUS_CHANNEL_URL))
    if not chat_ok:
        markup.add(types.InlineKeyboardButton("💬 Подписаться на чат", url=BONUS_CHAT_URL))
    markup.add(types.InlineKeyboardButton("✅ Проверить подписку", callback_data="bonus_check"))

    cd_text = "3 часа" if cooldown == BONUS_COOLDOWN_NORMAL else "1 час 30 минут"

    text = (
        f"🎁 <b>БОНУС</b>\n"
        f"{THICK_LINE}\n"
        f"Чтобы получить бонусную карточку, подпишись:\n\n"
        f"{'✅' if ch_ok else '❌'} Канал: {BONUS_CHANNEL}\n"
        f"{'✅' if chat_ok else '❌'} Чат: {BONUS_CHAT}\n\n"
        f"🎁 Бонус: <b>+1 карточка</b> вне кулдауна\n"
        f"⏱️ Перезарядка: <b>{cd_text}</b>"
    )
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML",
                     reply_to_message_id=reply_to)


@bot.message_handler(commands=['bonus'])
@bot.message_handler(func=lambda message: message.text and message.text.lower().strip() in ("бонус", "боны"))
@blocked
def bonus_command(message):
    user_id = message.from_user.id
    cooldown = get_bonus_cooldown(user_id)

    if user_id in user_bonus:
        last = user_bonus[user_id].get("last_used")
        if last:
            last_dt = datetime.fromisoformat(last)
            elapsed = (datetime.now() - last_dt).total_seconds()
            if elapsed < cooldown:
                remaining = cooldown - int(elapsed)
                text = (
                    f"[ 🚫 ] {escape_html(message.from_user.first_name)} уже получили бонусную карточку!\n\n"
                    f"<blockquote>Возвращайтесь через: {format_time(remaining)}</blockquote>"
                )
                bot.reply_to(message, text, parse_mode="HTML")
                return

    ch_ok, chat_ok = check_subscription(user_id)
    if not ch_ok or not chat_ok:
        _send_bonus_subscription_msg(message.chat.id, ch_ok, chat_ok, cooldown,
                                     reply_to=message.message_id)
        return

    give_card(user_id, message.from_user.first_name, message.chat.id,
              reply_to=message.message_id, show_bonus_button=False)
    user_bonus[user_id] = {"last_used": datetime.now().isoformat()}
    save_bonus()
    log_action(user_id, "Получил бонус")


@bot.callback_query_handler(func=lambda call: call.data == "bonus_check")
@blocked_cb
def bonus_check_callback(call):
    user_id = call.from_user.id
    cooldown = get_bonus_cooldown(user_id)

    if user_id in user_bonus:
        last = user_bonus[user_id].get("last_used")
        if last:
            last_dt = datetime.fromisoformat(last)
            if (datetime.now() - last_dt).total_seconds() < cooldown:
                bot.answer_callback_query(call.id, "⏳ Бонус уже использован", show_alert=True)
                return

    ch_ok, chat_ok = check_subscription(user_id)
    if not (ch_ok and chat_ok):
        bot.answer_callback_query(call.id, "❌ Вы ещё не подписались!", show_alert=True)
        return

    bot.answer_callback_query(call.id, "✅ Подписка подтверждена!")
    give_card(user_id, call.from_user.first_name, call.message.chat.id,
              show_bonus_button=False)
    user_bonus[user_id] = {"last_used": datetime.now().isoformat()}
    save_bonus()
    log_action(user_id, "Получил бонус (проверка)")


@bot.callback_query_handler(func=lambda call: call.data == "bonus_from_card")
@blocked_cb
def bonus_from_card_callback(call):
    user_id = call.from_user.id
    user_name = call.from_user.first_name
    cooldown = get_bonus_cooldown(user_id)

    if user_id in user_bonus:
        last = user_bonus[user_id].get("last_used")
        if last:
            last_dt = datetime.fromisoformat(last)
            elapsed = (datetime.now() - last_dt).total_seconds()
            if elapsed < cooldown:
                remaining = cooldown - int(elapsed)
                text = (
                    f"[ 🚫 ] {escape_html(user_name)} уже получили бонусную карточку!\n\n"
                    f"<blockquote>Возвращайтесь через: {format_time(remaining)}</blockquote>"
                )
                bot.answer_callback_query(call.id)
                bot.send_message(call.message.chat.id, text, parse_mode="HTML",
                                 reply_to_message_id=call.message.message_id)
                return

    ch_ok, chat_ok = check_subscription(user_id)
    if not ch_ok or not chat_ok:
        bot.answer_callback_query(call.id)
        _send_bonus_subscription_msg(call.message.chat.id, ch_ok, chat_ok, cooldown,
                                     reply_to=call.message.message_id)
        return

    bot.answer_callback_query(call.id, "🎁 Бонус получен!")
    give_card(user_id, user_name, call.message.chat.id, show_bonus_button=False)
    user_bonus[user_id] = {"last_used": datetime.now().isoformat()}
    save_bonus()
    log_action(user_id, "Получил бонус (из карты)")
    
    
# ============================================================
# --- ГЛАВНОЕ МЕНЮ АДМИНКИ ---
# ============================================================
@bot.message_handler(commands=['admin'])
def admin_command(message):
    if not is_admin(message.from_user.id):
        return

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎛️ Управление игроком", callback_data="adm_player_menu"),
        types.InlineKeyboardButton("⭐ Управление VIP", callback_data="adm_vip_menu"),
        types.InlineKeyboardButton("📜 История игрока", callback_data="adm_history"),
        types.InlineKeyboardButton("👥 Список игроков", callback_data="adm_players_list"),
        types.InlineKeyboardButton("💬 Список чатов", callback_data="adm_chats_list"),
        types.InlineKeyboardButton("🚫 Блок Пользователей", callback_data="adm_block_menu"),
        types.InlineKeyboardButton("🃏 Добавить карту", callback_data="adm_add_card"),
        types.InlineKeyboardButton("📝 Редактировать карту", callback_data="adm_edit_card"),
        types.InlineKeyboardButton("📋 Список карт", callback_data="adm_cards_list"),
        types.InlineKeyboardButton("📊 Статистика", callback_data="adm_stats"),
        types.InlineKeyboardButton("📝 Редакторы", callback_data="adm_editors_menu"),
        types.InlineKeyboardButton("🎁 Промокоды", callback_data="adm_promo_menu"),
        types.InlineKeyboardButton("🎉 Движуха", callback_data="adm_movement"),
        types.InlineKeyboardButton("🎊 Ивенты", callback_data="adm_events_menu"),
        types.InlineKeyboardButton("🔧 Тех. режим", callback_data="adm_tech_menu"),
        types.InlineKeyboardButton("🔍 Проверка данных", callback_data="adm_integrity_check"),
    )
    bot.send_message(message.chat.id,
        f"🛠️ <b>Админ-панель</b>\n{THICK_LINE}",
        reply_markup=markup, parse_mode="HTML")


# ============================================================
# --- ГЛАВНЫЙ ОБРАБОТЧИК АДМИН-КНОПОК ---
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_"))
def admin_callbacks(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    action = call.data

    # --- УПРАВЛЕНИЕ ИГРОКОМ ---
    if action == "adm_player_menu":
        msg = bot.send_message(call.message.chat.id,
            "🎛️ <b>Управление игроком</b>\n\n"
            "Введите ID или @username:\n"
            "(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_player_find_step)
        bot.answer_callback_query(call.id)

    # --- УПРАВЛЕНИЕ VIP ---
    elif action == "adm_vip_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("✅ Выдать VIP", callback_data="adm_vip_give"),
            types.InlineKeyboardButton("❌ Забрать VIP", callback_data="adm_vip_take"),
            types.InlineKeyboardButton("📋 Список VIP", callback_data="adm_vip_list"),
        )
        bot.send_message(call.message.chat.id, f"⭐ <b>Управление VIP</b>\n{THICK_LINE}",
                         reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif action == "adm_vip_give":
        msg = bot.send_message(call.message.chat.id,
            "⭐ <b>Выдать VIP</b>\n\nВведите ID игрока:\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_vip_give_step)
        bot.answer_callback_query(call.id)

    elif action == "adm_vip_take":
        msg = bot.send_message(call.message.chat.id,
            "❌ <b>Забрать VIP</b>\n\nВведите ID игрока:\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_vip_take_step)
        bot.answer_callback_query(call.id)

    elif action == "adm_vip_list":
        bot.answer_callback_query(call.id)
        show_vip_list_page(call.message.chat.id, call.from_user.id)

    # --- ИСТОРИЯ ---
    elif action == "adm_history":
        msg = bot.send_message(call.message.chat.id,
            "📜 <b>История игрока</b>\n\nВведите ID игрока:\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_history_step)
        bot.answer_callback_query(call.id)

    # --- СПИСКИ ---
    elif action == "adm_players_list":
        bot.answer_callback_query(call.id)
        players_page[call.from_user.id] = 0
        show_players_page(call.message.chat.id, call.from_user.id)

    elif action == "adm_chats_list":
        bot.answer_callback_query(call.id)
        chats_page[call.from_user.id] = 0
        show_chats_page(call.message.chat.id, call.from_user.id)

    elif action == "adm_cards_list":
        bot.answer_callback_query(call.id)
        cards_list_page[call.from_user.id] = 0
        show_cards_list_page(call.message.chat.id, call.from_user.id)

    # --- БЛОКИРОВКА ---
    elif action == "adm_block_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("🚫 Заблокировать", callback_data="adm_block_add"),
            types.InlineKeyboardButton("✅ Разблокировать", callback_data="adm_block_remove"),
            types.InlineKeyboardButton("📋 Список заблокированных", callback_data="adm_block_list"),
        )
        bot.send_message(call.message.chat.id, f"🚫 <b>Блок пользователей</b>\n{THICK_LINE}",
                         reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif action == "adm_block_add":
        msg = bot.send_message(call.message.chat.id,
            "🚫 <b>Заблокировать</b>\n\nВведите ID пользователя:\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_block_add_step)
        bot.answer_callback_query(call.id)

    elif action == "adm_block_remove":
        msg = bot.send_message(call.message.chat.id,
            "✅ <b>Разблокировать</b>\n\nВведите ID пользователя:\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_block_remove_step)
        bot.answer_callback_query(call.id)

    elif action == "adm_block_list":
        bot.answer_callback_query(call.id)
        blocked_page[call.from_user.id] = 0
        show_blocked_page(call.message.chat.id, call.from_user.id)

    # --- ДОБАВИТЬ КАРТУ ---
    elif action == "adm_add_card":
        msg = bot.send_message(call.message.chat.id,
            "🃏 <b>Добавить карту</b>\n\nВведите название карты:\n(или /cancel для отмены)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_add_card_step1)
        bot.answer_callback_query(call.id)

    # --- РЕДАКТОР КАРТ ---
    elif action == "adm_edit_card":
        if not cards_db:
            bot.answer_callback_query(call.id, "❌ База карт пуста!", show_alert=True); return
        edit_card_page[call.from_user.id] = 0
        show_card_page(call.message.chat.id, call.from_user.id)
        bot.answer_callback_query(call.id)

    # --- СТАТИСТИКА ---
    elif action == "adm_stats":
        total_users = len(set(list(user_coins.keys()) + list(user_cards.keys()) + list(user_exp.keys())))
        total_coins = sum(user_coins.values())
        total_exp = sum(user_exp.values())
        today_players = len(daily_players.get("players", []))
        today_date = daily_players.get("date", "—")

        econ = get_economy_stats()
        avg_coins = econ["avg_coins"]
        top_user = econ["top_user"]
        top_name = "—"
        if top_user:
            try:
                ch = bot.get_chat(top_user[0])
                top_name = ch.first_name or f"ID {top_user[0]}"
            except:
                top_name = f"ID {top_user[0]}"

        chat_stats = get_chat_stats()
        top_chat_text = "—"
        if chat_stats:
            top_chat = chat_stats[0]
            top_chat_text = f"{top_chat['title']} ({top_chat['members']} уч.)"

        text = (
            f"📊 <b>Статистика бота</b>\n{THICK_LINE}\n"
            f"👥 Всего игроков: {total_users}\n"
            f"🃏 Карт в базе: {len(cards_db)}\n"
            f"💎 Опыта всего: {total_exp}\n"
            f"⭐ VIP: {len(user_vip) + len(user_vip_promos)}\n"
            f"{THICK_LINE}\n"
            f"📅 <b>За сегодня ({today_date}):</b>\n"
            f"🎮 Играло: <b>{today_players}</b>\n"
            f"{THICK_LINE}\n"
            f"💰 <b>Экономика:</b>\n"
            f"💸 Монет в обороте: <b>{total_coins}</b>\n"
            f"📊 Средний баланс: <b>{avg_coins}</b>\n"
            f"🏆 Богатейший: <b>{escape_html(top_name)}</b> ({top_user[1] if top_user else 0})\n"
            f"{THICK_LINE}\n"
            f"💬 <b>Топ-чат:</b>\n"
            f"📢 {escape_html(top_chat_text)}\n"
            f"{THICK_LINE}"
        )
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    # --- РЕДАКТОРЫ ---
    elif action == "adm_editors_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("✏️ Текст /help", callback_data="adm_edit_text_help"),
            types.InlineKeyboardButton("✏️ Текст /start", callback_data="adm_edit_text_start"),
            types.InlineKeyboardButton("✏️ Текст /season", callback_data="adm_edit_text_season"),
            types.InlineKeyboardButton("✏️ Текст /daily", callback_data="adm_edit_text_daily"),
            types.InlineKeyboardButton("🎖️ Названия рангов", callback_data="adm_edit_ranks"),
            types.InlineKeyboardButton("🎖️ Опыт для рангов", callback_data="adm_edit_ranks_exp"),
            types.InlineKeyboardButton("⚪ Эмодзи редкостей", callback_data="adm_edit_rarities"),
            types.InlineKeyboardButton("🎲 Шансы редкостей", callback_data="adm_edit_chances"),
            types.InlineKeyboardButton("💰 Награды редкостей", callback_data="adm_edit_rewards"),
            types.InlineKeyboardButton("💸 Цены продажи", callback_data="adm_edit_prices"),
            types.InlineKeyboardButton("⭐ Цена и срок VIP", callback_data="adm_edit_vip"),
            types.InlineKeyboardButton("🔤 Текст кнопок", callback_data="adm_edit_buttons"),
        )
        bot.send_message(call.message.chat.id, f"📝 <b>Редакторы</b>\n{THICK_LINE}",
                         reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_text_help":
        msg = bot.send_message(call.message.chat.id,
            "✏️ Введите новый текст /help (HTML поддерживается):\n(или /cancel)")
        bot.register_next_step_handler(msg, adm_edit_text_step, "help")
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_text_start":
        msg = bot.send_message(call.message.chat.id,
            "✏️ Введите новый текст /start (ЛС):\n(или /cancel)")
        bot.register_next_step_handler(msg, adm_edit_text_step, "start")
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_text_season":
        msg = bot.send_message(call.message.chat.id,
            "✏️ Введите новый текст /season:\n"
            "(можно вставить <code>{time}</code> — покажет оставшееся время)\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_edit_text_step, "season")
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_text_daily":
        msg = bot.send_message(call.message.chat.id,
            "✏️ Введите новый текст /daily:\n(или /cancel)")
        bot.register_next_step_handler(msg, adm_edit_text_step, "daily")
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_ranks":
        await_rank_edit(call.message.chat.id)
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_ranks_exp":
        await_rank_exp_edit(call.message.chat.id)
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_rarities":
        await_rarity_edit(call.message.chat.id)
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_chances":
        await_chances_edit(call.message.chat.id)
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_rewards":
        await_rewards_edit(call.message.chat.id)
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_prices":
        await_price_edit(call.message.chat.id)
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_vip":
        await_vip_edit(call.message.chat.id)
        bot.answer_callback_query(call.id)

    elif action == "adm_edit_buttons":
        await_buttons_edit(call.message.chat.id)
        bot.answer_callback_query(call.id)

    # --- ПРОМОКОДЫ ---
    elif action == "adm_promo_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("➕ Создать промо", callback_data="adm_promo_create"),
            types.InlineKeyboardButton("✏️ Редактор промо", callback_data="adm_promo_editor"),
            types.InlineKeyboardButton("🗑️ Удаление промо", callback_data="adm_promo_delete"),
            types.InlineKeyboardButton("📊 Статистика промокодов", callback_data="adm_promo_stats"),
        )
        bot.send_message(call.message.chat.id, f"🎁 <b>Промокоды</b>\n{THICK_LINE}",
                         reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif action == "adm_promo_create":
        bot.answer_callback_query(call.id)
        _adm_create_promo_start(call.message.chat.id)

    elif action == "adm_promo_editor":
        bot.answer_callback_query(call.id)
        promo_edit_page[call.from_user.id] = 0
        show_promo_editor_page(call.message.chat.id, call.from_user.id)

    elif action == "adm_promo_delete":
        bot.answer_callback_query(call.id)
        promo_page[call.from_user.id] = 0
        show_promo_delete_page(call.message.chat.id, call.from_user.id)

    elif action == "adm_promo_stats":
        bot.answer_callback_query(call.id)
        promo_page[call.from_user.id] = 0
        show_promo_page(call.message.chat.id, call.from_user.id)

    # --- ДВИЖУХА ---
    elif action == "adm_movement":
        msg = bot.send_message(call.message.chat.id,
            "🎉 <b>Движуха</b>\n\nВведите секунды для Движухи.\n/cancel — отмена.",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_movement_step)
        bot.answer_callback_query(call.id)

    # --- ИВЕНТЫ ---
    elif action == "adm_events_menu":
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton("💎 ×2 Опыт", callback_data="adm_event_exp"),
            types.InlineKeyboardButton("💸 ×2 Монеты", callback_data="adm_event_coins"),
        )
        text = (
            f"🎊 <b>Ивенты</b>\n{THICK_LINE}\n"
            f"💎 ×2 Опыт: {'✅ активен' if has_double_exp() else '❌ выкл'}\n"
            f"💸 ×2 Монеты: {'✅ активен' if has_double_coins() else '❌ выкл'}"
        )
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif action == "adm_event_exp":
        if has_double_exp():
            active_events["double_exp"] = None
            save_events()
            bot.answer_callback_query(call.id, "💎 ×2 Опыт выключен", show_alert=True)
        else:
            msg = bot.send_message(call.message.chat.id,
                "💎 На сколько минут включить ×2 Опыт?\n(/cancel — отмена)")
            bot.register_next_step_handler(msg, adm_event_exp_step)
            bot.answer_callback_query(call.id)

    elif action == "adm_event_coins":
        if has_double_coins():
            active_events["double_coins"] = None
            save_events()
            bot.answer_callback_query(call.id, "💸 ×2 Монеты выключены", show_alert=True)
        else:
            msg = bot.send_message(call.message.chat.id,
                "💸 На сколько минут включить ×2 Монеты?\n(/cancel — отмена)")
            bot.register_next_step_handler(msg, adm_event_coins_step)
            bot.answer_callback_query(call.id)

    # --- ТЕХ. РЕЖИМ ---
    elif action == "adm_tech_menu":
        status = "ВКЛЮЧЁН" if tech_mode.get("enabled") else "выключен"
        markup = types.InlineKeyboardMarkup(row_width=1)
        markup.add(
            types.InlineKeyboardButton(
                f"🔧 Переключить (сейчас: {status})",
                callback_data="adm_tech_toggle"
            ),
            types.InlineKeyboardButton("✏️ Изменить текст", callback_data="adm_tech_text"),
        )
        bot.send_message(call.message.chat.id, f"🔧 <b>Тех. режим</b>\n{THICK_LINE}\nСтатус: <b>{status}</b>",
                         reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)

    elif action == "adm_tech_toggle":
        tech_mode["enabled"] = not tech_mode.get("enabled", False)
        save_tech_mode()
        status = "ВКЛЮЧЁН" if tech_mode["enabled"] else "выключен"
        bot.answer_callback_query(call.id, f"🔧 Тех. режим {status}", show_alert=True)

    elif action == "adm_tech_text":
        msg = bot.send_message(call.message.chat.id,
            f"✏️ Текущий текст:\n<code>{escape_html(tech_mode.get('message',''))}</code>\n\nВведите новый:\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_tech_text_step)
        bot.answer_callback_query(call.id)

    # --- ПРОВЕРКА ДАННЫХ ---
    elif action == "adm_integrity_check":
        problems = []
        for uid, cards in user_cards.items():
            for c in cards:
                if c not in cards_db:
                    problems.append(f"У игрока <code>{uid}</code> есть карта «{c}», которой нет в базе")
        for uid, coins in user_coins.items():
            if coins < 0:
                problems.append(f"У <code>{uid}</code> отрицательный баланс: {coins}")
        for code, data in promo_codes.items():
            if "activations" not in data:
                problems.append(f"Промокод <code>{code}</code> без поля activations")

        if not problems:
            bot.send_message(call.message.chat.id,
                f"✅ <b>Проверка пройдена</b>\n{THICK_LINE}\nПроблем не найдено.",
                parse_mode="HTML")
        else:
            text = (
                f"⚠️ <b>Найдено проблем: {len(problems)}</b>\n{THICK_LINE}\n"
                + "\n".join(f"• {p}" for p in problems[:30])
            )
            if len(problems) > 30:
                text += f"\n… и ещё {len(problems) - 30}"
            bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)


# ============================================================
# --- РЕДАКТОР КАРТ ---
# ============================================================
def show_card_page(chat_id, user_id, message_id=None):
    page = edit_card_page.get(user_id, 0)
    cards_list = list(cards_db.keys())
    per_page = 10
    total_pages = max(1, (len(cards_list) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    edit_card_page[user_id] = page
    start = page * per_page
    page_cards = cards_list[start:start + per_page]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for card_name in page_cards:
        rarity = cards_db[card_name].get("rarity", "?")
        allowed = cards_db[card_name].get("allowed", True)
        mark = "🎲" if allowed else "🚫"
        markup.add(types.InlineKeyboardButton(
            f"{mark} {card_name} [{rarity}]", callback_data=f"ec_open_{card_name}"))
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("⬅️ Назад", callback_data="ec_page_prev"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("Вперёд ➡️", callback_data="ec_page_next"))
    if nav:
        markup.row(*nav)
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="ec_cancel"))
    text = (f"📝 <b>Редактор карт</b>\n{THICK_LINE}\n"
            f"📄 Страница {page+1}/{total_pages}\n🃏 Всего карт: {len(cards_list)}\n"
            f"🎲 — выпадает, 🚫 — запрещена")
    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in ("ec_page_prev", "ec_page_next"))
def ec_page_nav(call):
    if not is_admin(call.from_user.id): return
    uid = call.from_user.id
    page = edit_card_page.get(uid, 0)
    if call.data == "ec_page_prev": page -= 1
    else: page += 1
    edit_card_page[uid] = page
    show_card_page(call.message.chat.id, uid, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ec_open_"))
def ec_open_card(call):
    if not is_admin(call.from_user.id): return
    card_name = call.data.replace("ec_open_", "")
    if card_name not in cards_db:
        bot.answer_callback_query(call.id, "❌ Карта не найдена!"); return
    _show_card_editor(call, card_name)


def _show_card_editor(call, card_name):
    card = cards_db[card_name]
    photo_id = card.get("photo", "")
    photo_preview = f"<code>{photo_id[:50]}...</code>" if photo_id else "—"
    status = "✅ Разрешено" if card.get("allowed", True) else "🚫 Запрещено"
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("✏️ Изменить название", callback_data=f"ec_name_{card_name}"),
        types.InlineKeyboardButton("🎨 Изменить редкость", callback_data=f"ec_rarity_{card_name}"),
        types.InlineKeyboardButton("📷 Изменить фото", callback_data=f"ec_photo_{card_name}"),
        types.InlineKeyboardButton(f"🎲 Выпадение: {status}", callback_data=f"ec_toggle_{card_name}"),
        types.InlineKeyboardButton("🗑️ Удалить карту", callback_data=f"ec_delete_{card_name}"),
        types.InlineKeyboardButton("🔙 К списку", callback_data="ec_back_to_list"),
    )
    try:
        bot.edit_message_text(
            f"📝 <b>Карта:</b> {card_name}\n{THICK_LINE}\n"
            f"🎨 Редкость: <b>{card['rarity']}</b>\n"
            f"🎲 Выпадение: <b>{status}</b>\n"
            f"📷 File ID: {photo_preview}\n{THICK_LINE}",
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id,
            f"📝 <b>Карта:</b> {card_name}\n{THICK_LINE}\n"
            f"🎨 Редкость: <b>{card['rarity']}</b>\n"
            f"🎲 Выпадение: <b>{status}</b>\n{THICK_LINE}",
            reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "ec_back_to_list")
def ec_back_to_list(call):
    if not is_admin(call.from_user.id): return
    show_card_page(call.message.chat.id, call.from_user.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "ec_cancel")
def ec_cancel(call):
    try:
        bot.edit_message_text("❌ Отменено.", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    except:
        pass
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ec_toggle_"))
def ec_toggle_drop(call):
    if not is_admin(call.from_user.id): return
    card_name = call.data.replace("ec_toggle_", "")
    if card_name in cards_db:
        current = cards_db[card_name].get("allowed", True)
        cards_db[card_name]["allowed"] = not current
        save_cards_db()
        status = "✅ Разрешено" if cards_db[card_name]["allowed"] else "🚫 Запрещено"
        bot.answer_callback_query(call.id, f"🎲 {status}", show_alert=True)
        _show_card_editor(call, card_name)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ec_name_"))
def ec_name_start(call):
    if not is_admin(call.from_user.id): return
    card_name = call.data.replace("ec_name_", "")
    msg = bot.send_message(call.message.chat.id,
        f"✏️ Введите новое название для «{card_name}»:\n(или /cancel)", parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_card_rename, card_name)
    bot.answer_callback_query(call.id)


def adm_edit_card_rename(message, old_name):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if not message.text or message.text.startswith("/"):
        bot.send_message(message.chat.id, "❌ Введите название текстом."); return
    new_name = message.text.strip()
    if new_name in cards_db:
        bot.send_message(message.chat.id, f"❌ Карта «{new_name}» уже существует!"); return
    if old_name in cards_db:
        cards_db[new_name] = cards_db.pop(old_name)
        save_cards_db()
        bot.send_message(message.chat.id, f"✅ Переименовано: «{old_name}» → «{new_name}»", parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("ec_rarity_"))
def ec_rarity_start(call):
    if not is_admin(call.from_user.id): return
    card_name = call.data.replace("ec_rarity_", "")
    if card_name not in cards_db:
        bot.answer_callback_query(call.id, "❌ Карта не найдена!", show_alert=True); return
    markup = types.InlineKeyboardMarkup(row_width=2)
    for rarity, emoji in RARITIES.items():
        markup.add(types.InlineKeyboardButton(
            f"{emoji} {rarity}", callback_data=f"ec_setrarity_{card_name}||{rarity}"))
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="ec_cancel"))
    try:
        bot.edit_message_text(f"🎨 Выберите новую редкость для «{card_name}»:",
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            reply_markup=markup, parse_mode="HTML")
    except Exception as e:
        bot.send_message(call.message.chat.id, f"⚠️ Ошибка: {e}")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ec_setrarity_"))
def ec_setrarity(call):
    if not is_admin(call.from_user.id): return
    raw = call.data.replace("ec_setrarity_", "")
    if "||" not in raw:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return
    card_name, new_rarity = raw.split("||", 1)
    if card_name in cards_db and new_rarity in RARITIES:
        cards_db[card_name]["rarity"] = new_rarity
        save_cards_db()
        bot.edit_message_text(f"✅ Редкость карты «{card_name}» изменена на <b>{new_rarity}</b>!",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ec_photo_"))
def ec_photo_start(call):
    if not is_admin(call.from_user.id): return
    card_name = call.data.replace("ec_photo_", "")
    msg = bot.send_message(call.message.chat.id,
        f"📷 Отправьте новое изображение для «{card_name}»:\n(или /cancel)", parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_card_photo, card_name)
    bot.answer_callback_query(call.id)


def adm_edit_card_photo(message, card_name):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Отправьте изображение."); return
    photo_id = message.photo[-1].file_id
    if card_name in cards_db:
        cards_db[card_name]["photo"] = photo_id
        save_cards_db()
        bot.send_message(message.chat.id,
            f"✅ Фото карты «{card_name}» обновлено!\n📷 File ID: <code>{photo_id[:50]}...</code>",
            parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("ec_delete_"))
def ec_delete_confirm(call):
    if not is_admin(call.from_user.id): return
    card_name = call.data.replace("ec_delete_", "")
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Да, удалить", callback_data=f"ec_confirmdelete_{card_name}"),
        types.InlineKeyboardButton("❌ Отмена", callback_data="ec_cancel"),
    )
    bot.edit_message_text(
        f"🗑️ Удалить карту «{card_name}»?\n\n<b>Это действие нельзя отменить!</b>",
        chat_id=call.message.chat.id, message_id=call.message.message_id,
        reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("ec_confirmdelete_"))
def ec_confirmdelete(call):
    global TOTAL_CARDS
    if not is_admin(call.from_user.id): return
    card_name = call.data.replace("ec_confirmdelete_", "")
    if card_name in cards_db:
        del cards_db[card_name]
        save_cards_db()
        TOTAL_CARDS = len(cards_db)
        removed_count = 0
        for uid, cards in user_cards.items():
            if card_name in cards:
                cards.remove(card_name)
                removed_count += 1
        save_cards()
        bot.edit_message_text(
            f"🗑️ Карта «{card_name}» удалена!\n"
            f"👥 Удалена у {removed_count} игроков\n"
            f"📊 Всего карт в базе: <b>{TOTAL_CARDS}</b>",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
    bot.answer_callback_query(call.id)


# ============================================================
# --- ДОБАВИТЬ КАРТУ ---
# ============================================================
def adm_add_card_step1(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if not message.text or message.text.startswith("/"):
        bot.send_message(message.chat.id, "❌ Введите название текстом."); return
    card_name = message.text.strip()
    if card_name in cards_db:
        bot.send_message(message.chat.id, f"❌ Карта «{card_name}» уже существует!"); return
    pending_cards[message.from_user.id] = {"name": card_name}
    markup = types.InlineKeyboardMarkup(row_width=2)
    for rarity, emoji in RARITIES.items():
        markup.add(types.InlineKeyboardButton(f"{emoji} {rarity}", callback_data=f"acr_{rarity}"))
    markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="ac_cancel"))
    bot.send_message(message.chat.id,
        f"🃏 Карта: <b>{card_name}</b>\n\nВыберите редкость:",
        reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("acr_"))
def adm_add_card_step2(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    rarity = call.data.replace("acr_", "")
    user_id = call.from_user.id
    if user_id not in pending_cards:
        bot.answer_callback_query(call.id, "❌ Сессия истекла!", show_alert=True); return
    pending_cards[user_id]["rarity"] = rarity
    msg = bot.send_message(call.message.chat.id,
        f"🎨 Редкость: <b>{rarity}</b>\n\n📷 Отправьте изображение карты.\n(или /cancel для отмены)",
        parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_add_card_step3)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "ac_cancel")
def adm_add_card_cancel(call):
    user_id = call.from_user.id
    if user_id in pending_cards:
        del pending_cards[user_id]
    bot.edit_message_text("❌ Отменено.", chat_id=call.message.chat.id,
                          message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


def adm_add_card_step3(message):
    global TOTAL_CARDS
    if not is_admin(message.from_user.id): return
    user_id = message.from_user.id
    if user_id not in pending_cards:
        bot.send_message(message.chat.id, "❌ Сессия истекла."); return
    if is_cancel(message):
        del pending_cards[user_id]
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if not message.photo:
        bot.send_message(message.chat.id, "❌ Отправьте изображение."); return
    photo_id = message.photo[-1].file_id
    card_name = pending_cards[user_id]["name"]
    rarity = pending_cards[user_id]["rarity"]
    cards_db[card_name] = {"rarity": rarity, "photo": photo_id, "allowed": True}
    save_cards_db()
    TOTAL_CARDS = len(cards_db)
    del pending_cards[user_id]
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔄 Добавить ещё карту", callback_data="adm_add_card"))
    bot.send_message(message.chat.id,
        f"✅ <b>Карта добавлена!</b>\n{THICK_LINE}\n"
        f"🃏 Название: <b>{card_name}</b>\n"
        f"🎨 Редкость: <b>{rarity}</b>\n"
        f"🎲 Выпадение: ✅ Разрешено\n"
        f"📷 File ID: <code>{photo_id}</code>\n"
        f"{THICK_LINE}\n📊 Всего карт: <b>{TOTAL_CARDS}</b>",
        reply_markup=markup, parse_mode="HTML")
        
        
# ============================================================
# --- СПИСОК КАРТ (С НАГРАДАМИ) ---
# ============================================================
def show_cards_list_page(chat_id, user_id, message_id=None):
    page = cards_list_page.get(user_id, 0)
    cards_list = list(cards_db.keys())

    if not cards_list:
        text = f"📋 <b>СПИСОК КАРТ</b>\n{THICK_LINE}\n📭 База пуста."
        if message_id:
            try: bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
            except: bot.send_message(chat_id, text, parse_mode="HTML")
        else: bot.send_message(chat_id, text, parse_mode="HTML")
        return

    total_pages = max(1, (len(cards_list) + CARDS_PER_PAGE - 1) // CARDS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    cards_list_page[user_id] = page
    start = page * CARDS_PER_PAGE
    page_cards = cards_list[start:start + CARDS_PER_PAGE]

    markup = types.InlineKeyboardMarkup(row_width=1)
    for i, card_name in enumerate(page_cards):
        rarity = cards_db[card_name].get("rarity", "?")
        emoji = RARITIES.get(rarity, "⚪")
        markup.add(types.InlineKeyboardButton(
            f"{emoji} {card_name} [{rarity}]",
            callback_data=f"cards_view_{start + i}"
        ))

    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("◀️ Назад", callback_data="cards_page_prev"))
    nav.append(types.InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="cards_noop"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("Вперёд ▶️", callback_data="cards_page_next"))
    if nav:
        markup.row(*nav)
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="cards_close"))

    text = (
        f"📋 <b>СПИСОК КАРТ [{page+1}/{total_pages}]</b>\n"
        f"{THICK_LINE}\n"
        f"Всего: <b>{len(cards_list)}</b>\n"
        f"Нажмите на карту, чтобы посмотреть детали."
    )
    if message_id:
        try: bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="HTML")
        except: bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else: bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in ("cards_page_prev", "cards_page_next"))
def cards_page_nav(call):
    if not is_admin(call.from_user.id): return
    uid = call.from_user.id
    page = cards_list_page.get(uid, 0)
    if call.data == "cards_page_prev": page -= 1
    else: page += 1
    cards_list_page[uid] = page
    show_cards_list_page(call.message.chat.id, uid, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "cards_noop")
def cards_noop(call):
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "cards_close")
def cards_close(call):
    try: bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id, message_id=call.message.message_id)
    except: pass
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("cards_view_"))
def cards_view(call):
    if not is_admin(call.from_user.id): return
    try:
        idx = int(call.data.replace("cards_view_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    cards_list = list(cards_db.keys())
    if idx < 0 or idx >= len(cards_list):
        bot.answer_callback_query(call.id, "❌ Карта не найдена!"); return

    card_name = cards_list[idx]
    card = cards_db[card_name]
    rarity = card.get("rarity", "Обычная")

    if rarity in custom_rewards:
        r = custom_rewards[rarity]
    else:
        r = RARITY_REWARDS.get(rarity, RARITY_REWARDS["Обычная"])
    exp_min, exp_max = r["exp"]
    coins_min, coins_max = r["coins"]

    if rarity == "Секретная":
        chance_text = "1 из 1000"
    else:
        chance_text = f"{rarity_chances.get(rarity, RARITY_REWARDS[rarity]['chance'])}%"

    total_owners = 0
    for uid, cards in user_cards.items():
        total_owners += cards.count(card_name)

    status = "✅ Разрешено" if card.get("allowed", True) else "🚫 Запрещено"

    text = (
        f"🃏 <b>{escape_html(card_name)}</b>\n"
        f"{THICK_LINE}\n"
        f"🎨 Редкость: <b>{RARITIES.get(rarity, '⚪')} {rarity}</b>\n"
        f"🎲 Выпадение: <b>{status}</b>\n"
        f"💎 Опыт: <b>{exp_min}–{exp_max}</b>\n"
        f"💸 Монеты: <b>{coins_min}–{coins_max}</b>\n"
        f"📊 Шанс редкости: <b>{chance_text}</b>\n"
        f"👥 Экземпляров у игроков: <b>{total_owners}</b>\n"
        f"{THICK_LINE}"
    )

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 К списку", callback_data="cards_back"))

    try:
        bot.edit_message_text(text, chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "cards_back")
def cards_back(call):
    if not is_admin(call.from_user.id): return
    cards_list_page[call.from_user.id] = 0
    show_cards_list_page(call.message.chat.id, call.from_user.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


# ============================================================
# --- СПИСОК ИГРОКОВ ---
# ============================================================
def show_players_page(chat_id, user_id, message_id=None):
    page = players_page.get(user_id, 0)
    players = get_all_players()

    if not players:
        text = (
            f"👥 <b>СПИСОК ИГРОКОВ</b>\n"
            f"{THICK_LINE}\n"
            f"📭 Игроков пока нет."
        )
        if message_id:
            try: bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
            except: bot.send_message(chat_id, text, parse_mode="HTML")
        else: bot.send_message(chat_id, text, parse_mode="HTML")
        return

    total_pages = max(1, (len(players) + PLAYERS_PER_PAGE - 1) // PLAYERS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    players_page[user_id] = page

    start = page * PLAYERS_PER_PAGE
    page_players = players[start:start + PLAYERS_PER_PAGE]

    markup = types.InlineKeyboardMarkup(row_width=1)
    for uid in page_players:
        coins = user_coins.get(uid, 0)
        exp = user_exp.get(uid, 0)
        try:
            ch = bot.get_chat(uid)
            name = ch.first_name or f"ID {uid}"
            if ch.username:
                name += f" (@{ch.username})"
        except:
            name = f"ID {uid}"
        markup.add(types.InlineKeyboardButton(
            f"{escape_html(name)} | 💸{coins} 💎{exp}",
            callback_data=f"plr_view_{uid}"
        ))

    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("◀️ Назад", callback_data="plr_page_prev"))
    nav.append(types.InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="plr_noop"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("Вперёд ▶️", callback_data="plr_page_next"))
    if nav:
        markup.row(*nav)

    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="plr_close"))

    text = (
        f"👥 <b>СПИСОК ИГРОКОВ [{page+1}/{total_pages}]</b>\n"
        f"{THICK_LINE}\n"
        f"Всего игроков: <b>{len(players)}</b>\n"
        f"Нажмите на игрока, чтобы открыть профиль."
    )

    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "plr_noop")
def plr_noop(call):
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data in ("plr_page_prev", "plr_page_next"))
def plr_page_nav(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    uid = call.from_user.id
    page = players_page.get(uid, 0)
    if call.data == "plr_page_prev":
        page -= 1
    else:
        page += 1
    players_page[uid] = page
    show_players_page(call.message.chat.id, uid, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "plr_close")
def plr_close(call):
    try:
        bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    except:
        pass
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("plr_view_"))
def plr_view(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    try:
        target_id = int(call.data.replace("plr_view_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!")
        return

    coins = user_coins.get(target_id, 0)
    exp = user_exp.get(target_id, 0)
    rank = user_ranks.get(target_id, 1)
    rank_name = RANKS.get(rank, RANKS[1])["name"]
    cards_count = len(set(user_cards.get(target_id, [])))
    vip_status = "⭐ Есть" if has_active_vip(target_id) else "—"
    vip_text = get_vip_expiry_text(target_id)

    upg = user_upgrades.get(target_id, {"cooldown": 0, "coins": 0, "exp": 0})
    daily_streak = user_daily.get(target_id, {}).get("streak", 0)

    try:
        ch = bot.get_chat(target_id)
        name = ch.first_name or f"ID {target_id}"
        if ch.username:
            name += f" (@{ch.username})"
    except:
        name = f"ID {target_id}"

    text = (
        f"👤 <b>Профиль игрока</b>\n"
        f"{THICK_LINE}\n"
        f"📝 Имя: {escape_html(name)}\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"💸 Монетки: <b>{coins}</b>\n"
        f"💎 Опыт: <b>{exp}</b>\n"
        f"🎖️ Ранг: <b>{rank_name} [{rank}/10]</b>\n"
        f"🃏 Карт: <b>{cards_count}/{TOTAL_CARDS}</b>\n"
        f"⭐ VIP: <b>{vip_status}</b>"
    )
    if vip_text:
        text += f" ({vip_text})"

    text += (
        f"\n{THICK_LINE}\n"
        f"⚡ <b>Прокачка:</b>\n"
        f"⏱️ Кулдаун: ур. {upg.get('cooldown', 0)}/5\n"
        f"💸 Монетки: ур. {upg.get('coins', 0)}/5\n"
        f"💎 Опыт: ур. {upg.get('exp', 0)}/5\n"
        f"📅 Daily серия: <b>{daily_streak}/50</b>\n"
        f"{THICK_LINE}"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🎛️ Управление игроком", callback_data=f"plr_edit_{target_id}"),
        types.InlineKeyboardButton("🔙 К списку", callback_data="plr_back_to_list"),
    )

    try:
        bot.edit_message_text(text, chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text,
                         reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "plr_back_to_list")
def plr_back_to_list(call):
    if not is_admin(call.from_user.id): return
    players_page[call.from_user.id] = 0
    show_players_page(call.message.chat.id, call.from_user.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("plr_edit_"))
def plr_edit(call):
    if not is_admin(call.from_user.id): return
    try:
        target_id = int(call.data.replace("plr_edit_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    bot.answer_callback_query(call.id)
    adm_player_show_menu(call.message.chat.id, target_id)


# ============================================================
# --- СПИСОК ЧАТОВ ---
# ============================================================
def show_chats_page(chat_id, user_id, message_id=None):
    page = chats_page.get(user_id, 0)
    chats_list = list(known_chats.items())

    if not chats_list:
        text = (
            f"💬 <b>СПИСОК ЧАТОВ</b>\n"
            f"{THICK_LINE}\n"
            f"📭 Пока нет известных чатов."
        )
        if message_id:
            try: bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
            except: bot.send_message(chat_id, text, parse_mode="HTML")
        else: bot.send_message(chat_id, text, parse_mode="HTML")
        return

    total_pages = max(1, (len(chats_list) + CHATS_PER_PAGE - 1) // CHATS_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    chats_page[user_id] = page

    start = page * CHATS_PER_PAGE
    page_chats = chats_list[start:start + CHATS_PER_PAGE]

    markup = types.InlineKeyboardMarkup(row_width=1)
    for cid, data in page_chats:
        title = data.get("title", f"Чат {cid}")
        ctype = data.get("type", "?")
        username = data.get("username")
        type_emoji = {"group": "👥", "supergroup": "👥", "channel": "📢"}.get(ctype, "💬")
        uname_text = f" @{username}" if username else ""
        markup.add(types.InlineKeyboardButton(
            f"{type_emoji} {escape_html(title)}{uname_text}",
            callback_data=f"chat_view_{cid}"
        ))

    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("◀️ Назад", callback_data="chat_page_prev"))
    nav.append(types.InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="chat_noop"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("Вперёд ▶️", callback_data="chat_page_next"))
    if nav:
        markup.row(*nav)

    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="chat_close"))

    text = (
        f"💬 <b>СПИСОК ЧАТОВ [{page+1}/{total_pages}]</b>\n"
        f"{THICK_LINE}\n"
        f"Всего чатов: <b>{len(chats_list)}</b>\n"
        f"Нажмите на чат, чтобы посмотреть детали."
    )

    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "chat_noop")
def chat_noop(call):
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data in ("chat_page_prev", "chat_page_next"))
def chat_page_nav(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    uid = call.from_user.id
    page = chats_page.get(uid, 0)
    if call.data == "chat_page_prev":
        page -= 1
    else:
        page += 1
    chats_page[uid] = page
    show_chats_page(call.message.chat.id, uid, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "chat_close")
def chat_close(call):
    try:
        bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    except:
        pass
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("chat_view_"))
def chat_view(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!")
        return
    try:
        target_id = int(call.data.replace("chat_view_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!")
        return

    if target_id not in known_chats:
        bot.answer_callback_query(call.id, "❌ Чат не найден!", show_alert=True)
        return

    data = known_chats[target_id]
    title = data.get("title", "—")
    added_at = data.get("added_at", "—")

    username = data.get("username")
    if not username:
        try:
            ch = bot.get_chat(target_id)
            if ch.username:
                username = ch.username
                known_chats[target_id]["username"] = username
                save_known_chats()
        except:
            pass

    uname_text = f"@{username}" if username else "нет"

    try:
        added_dt = datetime.fromisoformat(added_at)
        added_text = added_dt.strftime("%d.%m.%Y %H:%M")
    except:
        added_text = added_at

    members_text = "—"
    try:
        count = bot.get_chat_member_count(target_id)
        members_text = str(count)
    except:
        pass

    text = (
        f"💬 <b>Информация о чате</b>\n"
        f"{THICK_LINE}\n"
        f"📝 Название: <b>{escape_html(title)}</b>\n"
        f"🏷️ Юзер: <b>{uname_text}</b>\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"👥 Участников: <b>{members_text}</b>\n"
        f"📅 Добавлен: {added_text}\n"
        f"{THICK_LINE}"
    )

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("🔙 К списку", callback_data="chat_back_to_list"))

    try:
        bot.edit_message_text(text, chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text,
                         reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "chat_back_to_list")
def chat_back_to_list(call):
    if not is_admin(call.from_user.id): return
    chats_page[call.from_user.id] = 0
    show_chats_page(call.message.chat.id, call.from_user.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)
    
    
# ============================================================
# --- УПРАВЛЕНИЕ ИГРОКОМ ---
# ============================================================
def adm_player_find_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if not message.text:
        bot.send_message(message.chat.id, "❌ Введите ID или @username."); return

    text = message.text.strip()
    target_id = None

    if text.startswith("@"):
        username_clean = text[1:].lower()
        for uid in get_all_players():
            try:
                ch = bot.get_chat(uid)
                if ch.username and ch.username.lower() == username_clean:
                    target_id = uid
                    break
            except:
                continue
        if target_id is None:
            bot.send_message(message.chat.id, f"❌ Пользователь {text} не найден."); return
    else:
        try:
            target_id = int(text)
        except:
            bot.send_message(message.chat.id, "❌ Неверный формат."); return

    adm_player_show_menu(message.chat.id, target_id)


def adm_player_show_menu(chat_id, target_id):
    if target_id not in user_coins: user_coins[target_id] = 0
    if target_id not in user_exp: user_exp[target_id] = 0
    if target_id not in user_ranks: user_ranks[target_id] = 1
    if target_id not in user_cards: user_cards[target_id] = []
    save_coins(); save_exp(); save_ranks(); save_cards()

    coins = user_coins[target_id]
    exp = user_exp[target_id]
    rank = user_ranks[target_id]
    cards_count = len(set(user_cards[target_id]))
    vip_status = "⭐ Есть" if has_active_vip(target_id) else "—"
    vip_text = get_vip_expiry_text(target_id)

    try:
        ch = bot.get_chat(target_id)
        name = ch.first_name or f"ID {target_id}"
        if ch.username:
            name += f" (@{ch.username})"
    except:
        name = f"ID {target_id}"

    text = (
        f"🎛️ <b>Управление игроком</b>\n"
        f"{THICK_LINE}\n"
        f"👤 {escape_html(name)}\n"
        f"🆔 ID: <code>{target_id}</code>\n"
        f"💸 Монеты: <b>{coins}</b>\n"
        f"💎 Опыт: <b>{exp}</b>\n"
        f"🎖️ Ранг: <b>{rank}/10</b>\n"
        f"🃏 Карт: <b>{cards_count}/{TOTAL_CARDS}</b>\n"
        f"⭐ VIP: <b>{vip_status}</b>"
    )
    if vip_text:
        text += f" ({vip_text})"

    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💸 Монеты", callback_data=f"ep_coins_{target_id}"),
        types.InlineKeyboardButton("💎 Опыт", callback_data=f"ep_exp_{target_id}"),
        types.InlineKeyboardButton("🎖️ Ранг", callback_data=f"ep_rank_{target_id}"),
        types.InlineKeyboardButton("⭐ VIP", callback_data=f"ep_vip_{target_id}"),
        types.InlineKeyboardButton("🃏 Выдать карту", callback_data=f"plr_give_card_{target_id}"),
        types.InlineKeyboardButton("🗑️ Забрать карту", callback_data=f"plr_take_card_{target_id}"),
        types.InlineKeyboardButton("🔄 Сбросить кд", callback_data=f"plr_reset_cd_{target_id}"),
        types.InlineKeyboardButton("📅 Сбросить daily", callback_data=f"plr_reset_daily_{target_id}"),
    )
    markup.add(
        types.InlineKeyboardButton("❌ Закрыть", callback_data="plr_close"),
    )
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


# ============================================================
# --- ИЗМЕНИТЬ ИГРОКА (монеты/опыт/ранг/VIP) ---
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("ep_"))
def adm_edit_player_step2(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    parts = call.data.split("_")
    if len(parts) < 3:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return
    field = parts[1]
    target_id = int(parts[2])
    field_names = {"coins": "💸 Монетки", "exp": "💎 Опыт", "rank": "🎖️ Ранг", "vip": "⭐ VIP"}
    msg = bot.send_message(call.message.chat.id,
        f"✏️ Изменение: <b>{field_names[field]}</b> у игрока <code>{target_id}</code>\n\n"
        f"Введите новое значение:\n(или /cancel для отмены)", parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_player_step3, target_id, field)
    bot.answer_callback_query(call.id)


def adm_edit_player_step3(message, target_id, field):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        value = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Введите число."); return
    if field == "coins": user_coins[target_id] = value; save_coins()
    elif field == "exp": user_exp[target_id] = value; save_exp()
    elif field == "rank":
        if value < 1 or value > 10:
            bot.send_message(message.chat.id, "❌ Ранг от 1 до 10."); return
        user_ranks[target_id] = value; save_ranks()
    elif field == "vip":
        if value == 1:
            expires_at = datetime.now() + timedelta(days=vip_price.get("duration_days", 30))
            user_vip_promos[target_id] = {"expires_at": expires_at}
            save_vip_promos()
            user_vip.pop(target_id, None)
            save_vip()
        else:
            user_vip_promos.pop(target_id, None)
            save_vip_promos()
            user_vip.pop(target_id, None)
            save_vip()
    bot.send_message(message.chat.id,
        f"✅ <b>Изменено!</b>\n\nИгрок: <code>{target_id}</code>\n"
        f"Поле: {field}\nНовое значение: <b>{value}</b>", parse_mode="HTML")


# ============================================================
# --- ВЫДАТЬ/ЗАБРАТЬ КАРТУ ---
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("plr_give_card_"))
def plr_give_card(call):
    if not is_admin(call.from_user.id): return
    try:
        target_id = int(call.data.replace("plr_give_card_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    if not cards_db:
        bot.answer_callback_query(call.id, "❌ База карт пуста!", show_alert=True); return

    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
        f"🃏 Введите название карты для выдачи игроку <code>{target_id}</code>:\n"
        f"(или /cancel)",
        parse_mode="HTML")
    bot.register_next_step_handler(msg, plr_give_card_step, target_id)


def plr_give_card_step(message, target_id):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if not message.text:
        bot.send_message(message.chat.id, "❌ Введите название текстом."); return

    card_name = message.text.strip()
    if card_name not in cards_db:
        bot.send_message(message.chat.id, f"❌ Карта «{card_name}» не найдена."); return

    if target_id not in user_cards:
        user_cards[target_id] = []
    user_cards[target_id].append(card_name)
    save_cards()

    bot.send_message(message.chat.id,
        f"✅ Игроку <code>{target_id}</code> выдана карта «{card_name}».",
        parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data.startswith("plr_take_card_"))
def plr_take_card(call):
    if not is_admin(call.from_user.id): return
    try:
        target_id = int(call.data.replace("plr_take_card_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    inv = get_inventory(target_id)
    if not inv:
        bot.answer_callback_query(call.id, "❌ У игрока нет карт.", show_alert=True); return

    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id,
        f"🗑️ Введите название карты для удаления у игрока <code>{target_id}</code>:\n"
        f"(или /cancel)",
        parse_mode="HTML")
    bot.register_next_step_handler(msg, plr_take_card_step, target_id)


def plr_take_card_step(message, target_id):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if not message.text:
        bot.send_message(message.chat.id, "❌ Введите название текстом."); return

    card_name = message.text.strip()
    if card_name not in user_cards.get(target_id, []):
        bot.send_message(message.chat.id, f"❌ У игрока нет карты «{card_name}»."); return

    user_cards[target_id].remove(card_name)
    save_cards()

    bot.send_message(message.chat.id,
        f"✅ У игрока <code>{target_id}</code> удалена карта «{card_name}».",
        parse_mode="HTML")


# ============================================================
# --- СБРОС КУЛДАУНОВ И DAILY ---
# ============================================================
@bot.callback_query_handler(func=lambda call: call.data.startswith("plr_reset_cd_"))
def plr_reset_cd(call):
    if not is_admin(call.from_user.id): return
    try:
        target_id = int(call.data.replace("plr_reset_cd_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    if target_id in user_cooldowns:
        del user_cooldowns[target_id]
        save_cooldowns()
    if target_id in user_bonus:
        del user_bonus[target_id]
        save_bonus()

    bot.answer_callback_query(call.id, f"✅ Кулдауны игрока {target_id} сброшены", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith("plr_reset_daily_"))
def plr_reset_daily(call):
    if not is_admin(call.from_user.id): return
    try:
        target_id = int(call.data.replace("plr_reset_daily_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    if target_id in user_daily:
        user_daily[target_id] = {"streak": 0, "last_claim": None}
        save_daily()

    bot.answer_callback_query(call.id, f"✅ Daily-серия игрока {target_id} сброшена", show_alert=True)
    
    
# ============================================================
# --- УПРАВЛЕНИЕ VIP ---
# ============================================================
def adm_vip_give_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        target_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID."); return

    days = vip_price.get("duration_days", 30)
    expires_at = datetime.now() + timedelta(days=days)
    if target_id in user_vip_promos and datetime.now() < user_vip_promos[target_id]["expires_at"]:
        expires_at = user_vip_promos[target_id]["expires_at"] + timedelta(days=days)
    user_vip_promos[target_id] = {"expires_at": expires_at}
    save_vip_promos()

    bot.send_message(message.chat.id,
        f"✅ Игроку <code>{target_id}</code> выдан VIP на {days} дней.\n"
        f"Действует до: <b>{expires_at.strftime('%d.%m.%Y %H:%M')}</b>",
        parse_mode="HTML")


def adm_vip_take_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        target_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID."); return

    user_vip_promos.pop(target_id, None)
    user_vip.pop(target_id, None)
    save_vip_promos()
    save_vip()
    bot.send_message(message.chat.id,
        f"✅ У игрока <code>{target_id}</code> забран VIP.",
        parse_mode="HTML")


def show_vip_list_page(chat_id, user_id, message_id=None):
    all_vip = set(user_vip.keys()) | set(user_vip_promos.keys())
    if not all_vip:
        text = f"📋 <b>СПИСОК VIP</b>\n{THICK_LINE}\n📭 Пусто."
        if message_id:
            try:
                bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
            except:
                bot.send_message(chat_id, text, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, parse_mode="HTML")
        return

    lines = []
    for uid in sorted(all_vip):
        try:
            ch = bot.get_chat(uid)
            name = ch.first_name or f"ID {uid}"
            if ch.username:
                name += f" (@{ch.username})"
        except:
            name = f"ID {uid}"
        if uid in user_vip:
            expiry = "⭐ Навсегда"
        else:
            exp = user_vip_promos[uid]["expires_at"]
            if datetime.now() < exp:
                delta = exp - datetime.now()
                days = delta.days
                hours = delta.seconds // 3600
                expiry = f"⏳ {days}д {hours}ч"
            else:
                expiry = "❌ Истёк"
        lines.append(f"• {escape_html(name)} — {expiry}")

    text = (
        f"📋 <b>СПИСОК VIP ({len(all_vip)})</b>\n"
        f"{THICK_LINE}\n"
        + "\n".join(lines)
    )
    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, parse_mode="HTML")


# ============================================================
# --- ИСТОРИЯ ИГРОКА ---
# ============================================================
def adm_history_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        target_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID."); return

    hist = user_history.get(target_id, [])
    if not hist:
        bot.send_message(message.chat.id, f"📜 У игрока <code>{target_id}</code> нет истории.", parse_mode="HTML")
        return

    lines = []
    for entry in hist[-30:]:
        t = entry.get("time", "")[:16].replace("T", " ")
        a = entry.get("action", "?")
        d = entry.get("details", "")
        lines.append(f"• <b>{t}</b> — {escape_html(a)} {escape_html(d)}")

    text = (
        f"📜 <b>История игрока</b> <code>{target_id}</code>\n"
        f"{THICK_LINE}\n"
        + "\n".join(lines)
    )
    bot.send_message(message.chat.id, text, parse_mode="HTML")


# ============================================================
# --- БЛОКИРОВКА ПОЛЬЗОВАТЕЛЕЙ ---
# ============================================================
def adm_block_add_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        target_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID."); return

    if target_id in ADMIN_IDS:
        bot.send_message(message.chat.id, "❌ Нельзя блокировать админа."); return

    if target_id in blocked_users:
        bot.send_message(message.chat.id, f"⚠️ Пользователь <code>{target_id}</code> уже заблокирован.", parse_mode="HTML")
        return

    blocked_users.add(target_id)
    save_blocked_users()
    bot.send_message(message.chat.id,
        f"✅ Пользователь <code>{target_id}</code> заблокирован.\n"
        f"Теперь бот игнорирует его сообщения.",
        parse_mode="HTML")


def adm_block_remove_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        target_id = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Неверный ID."); return

    if target_id not in blocked_users:
        bot.send_message(message.chat.id, f"⚠️ Пользователь <code>{target_id}</code> не заблокирован.", parse_mode="HTML")
        return

    blocked_users.discard(target_id)
    save_blocked_users()
    bot.send_message(message.chat.id,
        f"✅ Пользователь <code>{target_id}</code> разблокирован.",
        parse_mode="HTML")


def show_blocked_page(chat_id, user_id, message_id=None):
    page = blocked_page.get(user_id, 0)
    blist = sorted(blocked_users)

    if not blist:
        text = (
            f"📋 <b>СПИСОК ЗАБЛОКИРОВАННЫХ</b>\n"
            f"{THICK_LINE}\n"
            f"📭 Пусто."
        )
        if message_id:
            try:
                bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="HTML")
            except:
                bot.send_message(chat_id, text, parse_mode="HTML")
        else:
            bot.send_message(chat_id, text, parse_mode="HTML")
        return

    total_pages = max(1, (len(blist) + BLOCKED_PER_PAGE - 1) // BLOCKED_PER_PAGE)
    page = max(0, min(page, total_pages - 1))
    blocked_page[user_id] = page
    start = page * BLOCKED_PER_PAGE
    page_items = blist[start:start + BLOCKED_PER_PAGE]

    markup = types.InlineKeyboardMarkup(row_width=1)
    for uid in page_items:
        try:
            ch = bot.get_chat(uid)
            name = ch.first_name or f"ID {uid}"
            if ch.username:
                name += f" (@{ch.username})"
        except:
            name = f"ID {uid}"
        markup.add(types.InlineKeyboardButton(
            f"✅ Разблокировать {name}",
            callback_data=f"adm_block_remove_id_{uid}"
        ))

    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("◀️ Назад", callback_data="adm_block_page_prev"))
    nav.append(types.InlineKeyboardButton(f"{page+1}/{total_pages}", callback_data="adm_block_noop"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("Вперёд ▶️", callback_data="adm_block_page_next"))
    if nav:
        markup.row(*nav)

    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="adm_block_close"))

    text = (
        f"📋 <b>СПИСОК ЗАБЛОКИРОВАННЫХ [{page+1}/{total_pages}]</b>\n"
        f"{THICK_LINE}\n"
        f"Всего: <b>{len(blist)}</b>\n"
        f"Нажмите на игрока, чтобы разблокировать."
    )

    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data == "adm_block_noop")
def adm_block_noop(call):
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data in ("adm_block_page_prev", "adm_block_page_next"))
def adm_block_page_nav(call):
    if not is_admin(call.from_user.id): return
    uid = call.from_user.id
    page = blocked_page.get(uid, 0)
    if call.data == "adm_block_page_prev": page -= 1
    else: page += 1
    blocked_page[uid] = page
    show_blocked_page(call.message.chat.id, uid, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "adm_block_close")
def adm_block_close(call):
    try:
        bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    except:
        pass
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("adm_block_remove_id_"))
def adm_block_remove_id(call):
    if not is_admin(call.from_user.id): return
    try:
        target_id = int(call.data.replace("adm_block_remove_id_", ""))
    except:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return

    blocked_users.discard(target_id)
    save_blocked_users()
    bot.answer_callback_query(call.id, f"✅ {target_id} разблокирован", show_alert=True)
    show_blocked_page(call.message.chat.id, call.from_user.id, message_id=call.message.message_id)
    
    
# ============================================================
# --- ДВИЖУХА ---
# ============================================================
def adm_movement_step(message):
    global MOVEMENT_UNTIL
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        seconds = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Введите число."); return
    MOVEMENT_UNTIL = datetime.now() + timedelta(seconds=seconds)
    bot.send_message(message.chat.id,
        f"🎉 <b>Движуха активирована!</b>\n{THICK_LINE}\n"
        f"⏱️ Кулдаун: <b>5 сек</b>\n"
        f"⌛ Длительность: <b>{seconds} сек</b>\n"
        f"🔚 Закончится: <b>{MOVEMENT_UNTIL.strftime('%H:%M:%S')}</b>\n{THICK_LINE}",
        parse_mode="HTML")


# ============================================================
# --- ТЕХ. РЕЖИМ ---
# ============================================================
def adm_tech_text_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    tech_mode["message"] = message.text.strip()
    save_tech_mode()
    bot.send_message(message.chat.id, "✅ Текст тех. режима обновлён.")


# ============================================================
# --- ИВЕНТЫ ---
# ============================================================
def adm_event_exp_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        minutes = int(message.text.strip())
        if minutes < 1:
            bot.send_message(message.chat.id, "❌ Минимум 1 минута."); return
        active_events["double_exp"] = datetime.now() + timedelta(minutes=minutes)
        save_events()
        bot.send_message(message.chat.id,
            f"✅ <b>×2 Опыт включён</b> на {minutes} мин.\n"
            f"Закончится: <b>{active_events['double_exp'].strftime('%H:%M:%S')}</b>",
            parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, "❌ Введите число минут.")


def adm_event_coins_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        minutes = int(message.text.strip())
        if minutes < 1:
            bot.send_message(message.chat.id, "❌ Минимум 1 минута."); return
        active_events["double_coins"] = datetime.now() + timedelta(minutes=minutes)
        save_events()
        bot.send_message(message.chat.id,
            f"✅ <b>×2 Монеты включены</b> на {minutes} мин.\n"
            f"Закончится: <b>{active_events['double_coins'].strftime('%H:%M:%S')}</b>",
            parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, "❌ Введите число минут.")
        
        
# ============================================================
# --- РЕДАКТОР ТЕКСТОВ ---
# ============================================================
def adm_edit_text_step(message, key):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    bot_texts[key] = message.text
    save_bot_texts()
    bot.send_message(message.chat.id, f"✅ Текст <code>{key}</code> обновлён.", parse_mode="HTML")


# ============================================================
# --- РЕДАКТОР РАНГОВ (НАЗВАНИЯ) ---
# ============================================================
def await_rank_edit(chat_id):
    lines = []
    for lvl, data in RANKS.items():
        lines.append(f"{lvl}. {data['name']}")
    text = (
        f"🎖️ <b>Редактор названий рангов</b>\n{THICK_LINE}\n"
        + "\n".join(lines) +
        f"\n\nВведите: <code>уровень новое_название</code>\n"
        f"Например: <code>1 🥇 Новичок</code>\n(или /cancel)"
    )
    msg = bot.send_message(chat_id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_rank_step)


def adm_edit_rank_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: <code>уровень название</code>", parse_mode="HTML"); return
    try:
        lvl = int(parts[0])
    except:
        bot.send_message(message.chat.id, "❌ Уровень должен быть числом."); return
    if lvl not in RANKS:
        bot.send_message(message.chat.id, "❌ Уровень от 1 до 10."); return
    RANKS[lvl]["name"] = parts[1]
    save_settings()
    bot.send_message(message.chat.id, f"✅ Ранг {lvl} → {parts[1]}", parse_mode="HTML")


# ============================================================
# --- РЕДАКТОР ОПЫТА РАНГОВ ---
# ============================================================
def await_rank_exp_edit(chat_id):
    lines = []
    for lvl, data in RANKS.items():
        lines.append(f"{lvl}. {data['name']} — {data['exp_needed']}")
    text = (
        f"🎖️ <b>Редактор опыта для рангов</b>\n{THICK_LINE}\n"
        + "\n".join(lines) +
        f"\n\nВведите: <code>уровень новое_значение</code>\n"
        f"Например: <code>1 500</code>\n"
        f"Для 10 ранга можно поставить <code>None</code> (не требуется).\n(или /cancel)"
    )
    msg = bot.send_message(chat_id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_rank_exp_step)


def adm_edit_rank_exp_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: <code>уровень значение</code>", parse_mode="HTML"); return
    try:
        lvl = int(parts[0])
    except:
        bot.send_message(message.chat.id, "❌ Уровень должен быть числом."); return
    if lvl not in RANKS:
        bot.send_message(message.chat.id, "❌ Уровень от 1 до 10."); return
    raw = parts[1].strip()
    if raw.lower() == "none":
        RANKS[lvl]["exp_needed"] = None
    else:
        try:
            val = int(raw)
            RANKS[lvl]["exp_needed"] = val
        except:
            bot.send_message(message.chat.id, "❌ Введите число или None."); return
    save_settings()
    bot.send_message(message.chat.id, f"✅ Ранг {lvl} — опыт {RANKS[lvl]['exp_needed']}", parse_mode="HTML")


# ============================================================
# --- РЕДАКТОР ЭМОДЗИ РЕДКОСТЕЙ ---
# ============================================================
def await_rarity_edit(chat_id):
    lines = []
    for name, emoji in RARITIES.items():
        lines.append(f"{emoji} {name}")
    text = (
        f"⚪ <b>Редактор эмодзи редкостей</b>\n{THICK_LINE}\n"
        + "\n".join(lines) +
        f"\n\nВведите: <code>Название новый_эмодзи</code>\n"
        f"Например: <code>Обычная 🟢</code>\n(или /cancel)"
    )
    msg = bot.send_message(chat_id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_rarity_step)


def adm_edit_rarity_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: <code>Название эмодзи</code>", parse_mode="HTML"); return
    name, emoji = parts[0], parts[1]
    if name not in RARITIES:
        bot.send_message(message.chat.id, f"❌ Редкость «{name}» не найдена."); return
    RARITIES[name] = emoji
    save_settings()
    bot.send_message(message.chat.id, f"✅ {name} → {emoji}", parse_mode="HTML")


# ============================================================
# --- РЕДАКТОР ШАНСОВ РЕДКОСТЕЙ ---
# ============================================================
def await_chances_edit(chat_id):
    lines = []
    for name in ["Обычная", "Редкая", "Эпическая", "Легендарная", "Мифическая"]:
        lines.append(f"{RARITIES.get(name, '')} {name} — {rarity_chances.get(name, RARITY_REWARDS[name]['chance'])}%")
    lines.append(f"🔮 Секретная — 1 из 1000 (не меняется)")
    total = sum(rarity_chances.get(n, RARITY_REWARDS[n]['chance']) for n in ["Обычная", "Редкая", "Эпическая", "Легендарная", "Мифическая"])
    text = (
        f"🎲 <b>Редактор шансов редкостей</b>\n{THICK_LINE}\n"
        + "\n".join(lines) +
        f"\n\n📊 Сумма: <b>{total}%</b> (должна быть 100)\n\n"
        f"Введите: <code>Название новый_процент</code>\n"
        f"Например: <code>Обычная 40</code>\n(или /cancel)"
    )
    msg = bot.send_message(chat_id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_chance_step)


def adm_edit_chance_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: <code>Название процент</code>", parse_mode="HTML"); return
    name = parts[0]
    if name not in ["Обычная", "Редкая", "Эпическая", "Легендарная", "Мифическая"]:
        bot.send_message(message.chat.id, f"❌ Редкость «{name}» не найдена или её нельзя менять."); return
    try:
        val = float(parts[1].replace(",", "."))
        if val < 0 or val > 100:
            bot.send_message(message.chat.id, "❌ Процент от 0 до 100."); return
        rarity_chances[name] = val
        save_rarity_chances()
        bot.send_message(message.chat.id, f"✅ {name} → {val}%", parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, "❌ Введите число.")


# ============================================================
# --- РЕДАКТОР НАГРАД РЕДКОСТЕЙ ---
# ============================================================
def await_rewards_edit(chat_id):
    lines = []
    for name in ["Обычная", "Редкая", "Эпическая", "Легендарная", "Мифическая", "Секретная"]:
        if name in custom_rewards:
            r = custom_rewards[name]
        else:
            r = RARITY_REWARDS.get(name, RARITY_REWARDS["Обычная"])
        lines.append(f"{RARITIES.get(name, '')} {name}: 💎{r['exp'][0]}–{r['exp'][1]} 💸{r['coins'][0]}–{r['coins'][1]}")
    text = (
        f"💰 <b>Редактор наград редкостей</b>\n{THICK_LINE}\n"
        + "\n".join(lines) +
        f"\n\nВведите: <code>Название exp_min exp_max coins_min coins_max</code>\n"
        f"Например: <code>Обычная 25 60 50 200</code>\n(или /cancel)"
    )
    msg = bot.send_message(chat_id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_reward_step)


def adm_edit_reward_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    parts = message.text.strip().split()
    if len(parts) < 5:
        bot.send_message(message.chat.id, "❌ Формат: <code>Название exp_min exp_max coins_min coins_max</code>", parse_mode="HTML"); return
    name = parts[0]
    if name not in RARITIES:
        bot.send_message(message.chat.id, f"❌ Редкость «{name}» не найдена."); return
    try:
        exp_min = int(parts[1]); exp_max = int(parts[2])
        coins_min = int(parts[3]); coins_max = int(parts[4])
        if exp_min > exp_max or coins_min > coins_max:
            bot.send_message(message.chat.id, "❌ Минимум не может быть больше максимума."); return
        custom_rewards[name] = {"exp": (exp_min, exp_max), "coins": (coins_min, coins_max)}
        save_custom_rewards()
        bot.send_message(message.chat.id,
            f"✅ {name}: 💎{exp_min}–{exp_max} 💸{coins_min}–{coins_max}", parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, "❌ Все значения должны быть числами.")


# ============================================================
# --- РЕДАКТОР ЦЕН ПРОДАЖИ ---
# ============================================================
def await_price_edit(chat_id):
    lines = []
    for name, price in SELL_PRICES.items():
        lines.append(f"{RARITIES.get(name, '')} {name} — {price}")
    text = (
        f"💸 <b>Редактор цен продажи</b>\n{THICK_LINE}\n"
        + "\n".join(lines) +
        f"\n\nВведите: <code>Название новая_цена</code>\n"
        f"Например: <code>Обычная 10</code>\n(или /cancel)"
    )
    msg = bot.send_message(chat_id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_price_step)


def adm_edit_price_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: <code>Название цена</code>", parse_mode="HTML"); return
    name = parts[0]
    try:
        price = int(parts[1])
    except:
        bot.send_message(message.chat.id, "❌ Цена должна быть числом."); return
    if name not in SELL_PRICES:
        bot.send_message(message.chat.id, f"❌ Редкость «{name}» не найдена."); return
    SELL_PRICES[name] = price
    save_settings()
    bot.send_message(message.chat.id, f"✅ {name} → {price} монет", parse_mode="HTML")


# ============================================================
# --- РЕДАКТОР VIP ---
# ============================================================
def await_vip_edit(chat_id):
    text = (
        f"⭐ <b>Редактор VIP</b>\n{THICK_LINE}\n"
        f"💰 Цена: <b>{vip_price.get('price', 20)}</b> звёзд\n"
        f"📅 Длительность: <b>{vip_price.get('duration_days', 30)}</b> дней\n"
        f"\nВведите: <code>цена длительность</code>\n"
        f"Например: <code>50 60</code>\n(или /cancel)"
    )
    msg = bot.send_message(chat_id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_vip_step)


def adm_edit_vip_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    parts = message.text.strip().split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: <code>цена длительность</code>", parse_mode="HTML"); return
    try:
        price = int(parts[0])
        days = int(parts[1])
        if price < 1 or days < 1:
            bot.send_message(message.chat.id, "❌ Значения должны быть ≥ 1."); return
        vip_price["price"] = price
        vip_price["duration_days"] = days
        save_vip_price()
        bot.send_message(message.chat.id,
            f"✅ VIP: {price} звёзд на {days} дней", parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, "❌ Введите два числа.")


# ============================================================
# --- РЕДАКТОР КНОПОК ---
# ============================================================
def await_buttons_edit(chat_id):
    default_buttons = {
        "bonus": "🎁 Бонус",
        "rank_up": "🎖️ ПОВЫСИТЬ РАНГ",
        "card_again": "🔄 Создать карту",
        "add_to_group": "➕ Добавить бота в группу",
    }
    lines = []
    for key, default in default_buttons.items():
        current = bot_buttons.get(key, default)
        lines.append(f"<code>{key}</code> → {current}")
    text = (
        f"🔤 <b>Редактор текста кнопок</b>\n{THICK_LINE}\n"
        + "\n".join(lines) +
        f"\n\nВведите: <code>ключ новый_текст</code>\n"
        f"Например: <code>bonus 🎁 Подарок</code>\n(или /cancel)"
    )
    msg = bot.send_message(chat_id, text, parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_edit_button_step)


def adm_edit_button_step(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    parts = message.text.strip().split(maxsplit=1)
    if len(parts) < 2:
        bot.send_message(message.chat.id, "❌ Формат: <code>ключ текст</code>", parse_mode="HTML"); return
    key = parts[0]
    val = parts[1]
    bot_buttons[key] = val
    save_bot_buttons()
    bot.send_message(message.chat.id, f"✅ <code>{key}</code> → {val}", parse_mode="HTML")
    
    
# ============================================================
# --- СОЗДАНИЕ ПРОМОКОДА ---
# ============================================================
def _adm_create_promo_start(chat_id):
    msg = bot.send_message(chat_id,
        "🎁 <b>Создать промокод</b>\n\nВведите код промокода:\n(например: SUMMER2026)\n(или /cancel для отмены)",
        parse_mode="HTML")
    bot.register_next_step_handler(msg, adm_create_promo_step1)


def adm_create_promo_step1(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if not message.text or message.text.startswith("/"):
        bot.send_message(message.chat.id, "❌ Введите код текстом."); return
    promo_code = message.text.strip().upper().lstrip("#")
    if promo_code in promo_codes:
        bot.send_message(message.chat.id, f"❌ Промокод «{promo_code}» уже существует!"); return
    pending_promos[message.from_user.id] = {
        "code": promo_code, "coins": 0, "exp": 0, "card": None,
        "activations": 1, "used": 0, "used_by": [],
        "youtuber": False, "vip_days": 0,
        "expires_at": None,
    }
    ask_vip_for_promo(message.chat.id, message.from_user.id)


def ask_vip_for_promo(chat_id, user_id):
    if user_id not in pending_promos: return
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("✅ Да", callback_data="pr_vip_yes"),
        types.InlineKeyboardButton("❌ Нет", callback_data="pr_vip_no"),
    )
    bot.send_message(chat_id,
        f"🎁 Промокод: <code>{pending_promos[user_id]['code']}</code>\n\n"
        f"⭐ <b>Добавить VIP в промокод?</b>",
        reply_markup=markup, parse_mode="HTML")


def adm_promo_menu(chat_id, user_id):
    if user_id not in pending_promos: return
    p = pending_promos[user_id]
    card_text = p["card"] if p["card"] else "не выбрана"
    if p.get("vip_days", 0) > 0:
        ptype = f"📦 Обычный + ⭐ VIP на {p['vip_days']} дн."
    elif p.get("youtuber"):
        ptype = "🎬 Ютуберский"
    else:
        ptype = "📦 Обычный"

    expires_text = "нет"
    if p.get("expires_at"):
        try:
            exp_dt = datetime.fromisoformat(p["expires_at"])
            expires_text = exp_dt.strftime("%d.%m.%Y")
        except:
            expires_text = "?"

    text = (
        f"🎁 <b>Создание промокода:</b> <code>{p['code']}</code>\n{THICK_LINE}\n"
        f"💸 Монетки: <b>{p['coins']}</b>\n"
        f"💎 Опыт: <b>{p['exp']}</b>\n"
        f"🃏 Карта: <b>{card_text}</b>\n"
        f"🔁 Активаций: <b>{p['activations']}</b>\n"
        f"🏷️ Тип: <b>{ptype}</b>\n"
        f"⭐ VIP: <b>{p.get('vip_days', 0)} дн.</b>\n"
        f"📅 До: <b>{expires_text}</b>\n"
        f"{THICK_LINE}\nНастройте промокод:"
    )
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💸 Монетки", callback_data="pr_coins"),
        types.InlineKeyboardButton("💎 Опыт", callback_data="pr_exp"),
        types.InlineKeyboardButton("🃏 Карта", callback_data="pr_card"),
        types.InlineKeyboardButton("🔁 Активации", callback_data="pr_activations"),
        types.InlineKeyboardButton("🏷️ Тип (Ютубер)", callback_data="pr_type"),
        types.InlineKeyboardButton("⭐ Изменить VIP", callback_data="pr_vip_change"),
        types.InlineKeyboardButton("📅 Дата", callback_data="pr_expires"),
        types.InlineKeyboardButton("✅ Сохранить", callback_data="pr_save"),
        types.InlineKeyboardButton("❌ Отмена", callback_data="pr_cancel"),
    )
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in ("pr_vip_yes", "pr_vip_no"))
def pr_vip_choice(call):
    if not is_admin(call.from_user.id): return
    user_id = call.from_user.id
    if user_id not in pending_promos:
        bot.answer_callback_query(call.id, "❌ Сессия истекла!", show_alert=True); return
    if call.data == "pr_vip_no":
        pending_promos[user_id]["vip_days"] = 0
        bot.delete_message(call.message.chat.id, call.message.message_id)
        adm_promo_menu(call.message.chat.id, user_id)
        bot.answer_callback_query(call.id, "✅ Промокод без VIP")
    else:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id,
            "⭐ Введите длительность VIP в днях:\n"
            "(например: 1, 2, 3, 7, 30)\n"
            "(или /cancel для отмены)")
        bot.register_next_step_handler(msg, adm_promo_set_vip_days)
        bot.answer_callback_query(call.id)


def adm_promo_set_vip_days(message):
    if not is_admin(message.from_user.id): return
    user_id = message.from_user.id
    if user_id not in pending_promos:
        bot.send_message(message.chat.id, "❌ Сессия истекла."); return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        days = int(message.text.strip())
        if days < 1:
            bot.send_message(message.chat.id, "❌ Минимум 1 день."); return
        if days > 3650:
            bot.send_message(message.chat.id, "❌ Слишком много дней."); return
        pending_promos[user_id]["vip_days"] = days
        adm_promo_menu(message.chat.id, user_id)
    except:
        bot.send_message(message.chat.id, "❌ Введите целое число дней.")


@bot.callback_query_handler(
    func=lambda call: call.data.startswith("pr_")
    and not call.data.startswith("pr_del_")
    and not call.data.startswith("pr_setcard_")
    and not call.data.startswith("pr_edit_")
    and not call.data.startswith("pr_stats_")
    and call.data not in ("pr_vip_yes", "pr_vip_no")
)
def adm_promo_callbacks(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    user_id = call.from_user.id
    action = call.data
    if user_id not in pending_promos:
        bot.answer_callback_query(call.id, "❌ Сессия истекла!", show_alert=True); return

    if action == "pr_coins":
        msg = bot.send_message(call.message.chat.id, "💸 Введите количество монеток:\n(/cancel для отмены)")
        bot.register_next_step_handler(msg, adm_promo_set_coins)
        bot.answer_callback_query(call.id)
    elif action == "pr_exp":
        msg = bot.send_message(call.message.chat.id, "💎 Введите количество опыта:\n(/cancel для отмены)")
        bot.register_next_step_handler(msg, adm_promo_set_exp)
        bot.answer_callback_query(call.id)
    elif action == "pr_activations":
        msg = bot.send_message(call.message.chat.id,
            "🔁 Введите количество активаций:\n(/cancel для отмены)")
        bot.register_next_step_handler(msg, adm_promo_set_activations)
        bot.answer_callback_query(call.id)
    elif action == "pr_card":
        if not cards_db:
            bot.answer_callback_query(call.id, "❌ База карт пуста!", show_alert=True); return
        markup = types.InlineKeyboardMarkup(row_width=1)
        for i, card_name in enumerate(list(cards_db.keys())[:30]):
            markup.add(types.InlineKeyboardButton(f"🃏 {card_name}", callback_data=f"pr_setcard_{i}"))
        markup.add(types.InlineKeyboardButton("🚫 Без карты", callback_data="pr_setcard_none"))
        markup.add(types.InlineKeyboardButton("❌ Отмена", callback_data="pr_cancel"))
        bot.edit_message_text("🃏 Выберите карту для промокода:",
            chat_id=call.message.chat.id, message_id=call.message.message_id,
            reply_markup=markup, parse_mode="HTML")
        bot.answer_callback_query(call.id)
    elif action == "pr_type":
        p = pending_promos[user_id]
        p["youtuber"] = not p.get("youtuber", False)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        adm_promo_menu(call.message.chat.id, user_id)
        bot.answer_callback_query(call.id)
    elif action == "pr_vip_change":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        ask_vip_for_promo(call.message.chat.id, user_id)
        bot.answer_callback_query(call.id)
    elif action == "pr_expires":
        bot.delete_message(call.message.chat.id, call.message.message_id)
        msg = bot.send_message(call.message.chat.id,
            "📅 Введите дату в формате <code>ДД.ММ.ГГГГ</code> (например 31.12.2026):\n"
            "Или <code>0</code> чтобы убрать срок.\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, adm_promo_set_expires)
        bot.answer_callback_query(call.id)
    elif action == "pr_save":
        p = pending_promos[user_id]
        promo_codes[p["code"]] = {
            "coins": p["coins"], "exp": p["exp"], "card": p["card"],
            "activations": p["activations"], "used": 0, "used_by": [],
            "youtuber": p.get("youtuber", False),
            "vip_days": p.get("vip_days", 0),
        }
        if p.get("expires_at"):
            promo_codes[p["code"]]["expires_at"] = p["expires_at"]
        save_promos()
        card_text = p["card"] if p["card"] else "нет"
        if p.get("vip_days", 0) > 0:
            ptype = f"📦 Обычный + ⭐ VIP на {p['vip_days']} дн."
        elif p.get("youtuber"):
            ptype = "🎬 Ютуберский"
        else:
            ptype = "📦 Обычный"

        expires_text = "нет"
        if p.get("expires_at"):
            try:
                expires_text = datetime.fromisoformat(p["expires_at"]).strftime("%d.%m.%Y")
            except: pass

        text = (
            f"✅ <b>Промокод сохранён!</b>\n{THICK_LINE}\n"
            f"🎁 Код: <code>{p['code']}</code>\n"
            f"💸 Монетки: {p['coins']}\n"
            f"💎 Опыт: {p['exp']}\n"
            f"🃏 Карта: {card_text}\n"
            f"🔁 Активаций: {p['activations']}\n"
            f"🏷️ Тип: {ptype}\n"
            f"⭐ VIP: {p.get('vip_days', 0)} дн.\n"
            f"📅 До: {expires_text}\n{THICK_LINE}"
        )
        bot.edit_message_text(text, chat_id=call.message.chat.id,
                              message_id=call.message.message_id, parse_mode="HTML")
        del pending_promos[user_id]
        bot.answer_callback_query(call.id, "✅ Сохранено!")
    elif action == "pr_cancel":
        if user_id in pending_promos:
            del pending_promos[user_id]
        bot.edit_message_text("❌ Отменено.", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
        bot.answer_callback_query(call.id)


def adm_promo_set_expires(message):
    if not is_admin(message.from_user.id): return
    user_id = message.from_user.id
    if user_id not in pending_promos:
        bot.send_message(message.chat.id, "❌ Сессия истекла."); return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    text = message.text.strip()
    if text == "0":
        pending_promos[user_id]["expires_at"] = None
        bot.send_message(message.chat.id, "✅ Дата убрана.")
        adm_promo_menu(message.chat.id, user_id)
        return
    try:
        dt = datetime.strptime(text, "%d.%m.%Y")
        pending_promos[user_id]["expires_at"] = dt.isoformat()
        bot.send_message(message.chat.id, f"✅ До {dt.strftime('%d.%m.%Y')}.")
        adm_promo_menu(message.chat.id, user_id)
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат. Используйте ДД.ММ.ГГГГ.")


@bot.callback_query_handler(func=lambda call: call.data.startswith("pr_setcard_"))
def pr_setcard(call):
    if not is_admin(call.from_user.id): return
    user_id = call.from_user.id
    if user_id not in pending_promos:
        bot.answer_callback_query(call.id, "❌ Сессия истекла!", show_alert=True); return
    val = call.data.replace("pr_setcard_", "")
    if val == "none":
        pending_promos[user_id]["card"] = None
    else:
        try:
            idx = int(val)
            card_name = list(cards_db.keys())[idx]
            pending_promos[user_id]["card"] = card_name
        except:
            pass
    bot.delete_message(call.message.chat.id, call.message.message_id)
    adm_promo_menu(call.message.chat.id, user_id)
    bot.answer_callback_query(call.id)


def adm_promo_set_coins(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        val = int(message.text.strip())
        pending_promos[message.from_user.id]["coins"] = val
        adm_promo_menu(message.chat.id, message.from_user.id)
    except:
        bot.send_message(message.chat.id, "❌ Введите число.")


def adm_promo_set_exp(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        val = int(message.text.strip())
        pending_promos[message.from_user.id]["exp"] = val
        adm_promo_menu(message.chat.id, message.from_user.id)
    except:
        bot.send_message(message.chat.id, "❌ Введите число.")


def adm_promo_set_activations(message):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        val = int(message.text.strip())
        if val < 1: val = 1
        pending_promos[message.from_user.id]["activations"] = val
        adm_promo_menu(message.chat.id, message.from_user.id)
    except:
        bot.send_message(message.chat.id, "❌ Введите число.")


# ============================================================
# --- РЕДАКТОР ПРОМО ---
# ============================================================
def show_promo_editor_page(chat_id, user_id, message_id=None):
    page = promo_edit_page.get(user_id, 0)
    codes = list(promo_codes.keys())
    per_page = 10
    total_pages = max(1, (len(codes) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    promo_edit_page[user_id] = page
    start = page * per_page
    page_codes = codes[start:start + per_page]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for code in page_codes:
        markup.add(types.InlineKeyboardButton(f"✏️ {code}", callback_data=f"pr_edit_{code}"))
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("⬅️ Назад", callback_data="pr_edit_prev"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("Вперёд ➡️", callback_data="pr_edit_next"))
    if nav:
        markup.row(*nav)
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="pr_edit_close"))
    text = (f"✏️ <b>Редактор промо</b>\n{THICK_LINE}\n"
            f"📄 Страница {page+1}/{total_pages}\n🎁 Всего: {len(codes)}")
    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in ("pr_edit_prev", "pr_edit_next"))
def pr_edit_nav(call):
    if not is_admin(call.from_user.id): return
    uid = call.from_user.id
    page = promo_edit_page.get(uid, 0)
    if call.data == "pr_edit_prev": page -= 1
    else: page += 1
    promo_edit_page[uid] = page
    show_promo_editor_page(call.message.chat.id, uid, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "pr_edit_close")
def pr_edit_close(call):
    bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id,
                          message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "pr_edit_back")
def pr_edit_back_handler(call):
    if not is_admin(call.from_user.id): return
    show_promo_editor_page(call.message.chat.id, call.from_user.id, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("pr_edit_") and call.data not in ("pr_edit_prev", "pr_edit_next", "pr_edit_close", "pr_edit_back"))
def pr_edit_open(call):
    if not is_admin(call.from_user.id): return
    code = call.data.replace("pr_edit_", "")
    if code not in promo_codes:
        bot.answer_callback_query(call.id, "❌ Промокод не найден!"); return
    _show_promo_edit(call, code)


def _show_promo_edit(call, code):
    data = promo_codes[code]
    vip_days = data.get("vip_days", 0)
    youtuber = "🎬 Да" if data.get("youtuber") else "📦 Нет"
    expires_text = "нет"
    if data.get("expires_at"):
        try:
            exp_dt = datetime.fromisoformat(data["expires_at"])
            expires_text = exp_dt.strftime("%d.%m.%Y")
        except: pass
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("💸 Монетки", callback_data=f"pe_coins_{code}"),
        types.InlineKeyboardButton("💎 Опыт", callback_data=f"pe_exp_{code}"),
        types.InlineKeyboardButton("🔁 Активации", callback_data=f"pe_acts_{code}"),
        types.InlineKeyboardButton("⭐ VIP дни", callback_data=f"pe_vip_{code}"),
        types.InlineKeyboardButton("🎬 Ютубер", callback_data=f"pe_yt_{code}"),
        types.InlineKeyboardButton("📅 Дата", callback_data=f"pe_date_{code}"),
        types.InlineKeyboardButton("🔙 К списку", callback_data="pr_edit_back"),
    )
    text = (
        f"✏️ <b>Редактор:</b> <code>{code}</code>\n{THICK_LINE}\n"
        f"💸 Монетки: {data.get('coins', 0)}\n"
        f"💎 Опыт: {data.get('exp', 0)}\n"
        f"🔁 Активаций: {data.get('used', 0)}/{data.get('activations', 1)}\n"
        f"⭐ VIP: {vip_days} дн.\n"
        f"🎬 Ютубер: {youtuber}\n"
        f"📅 До: {expires_text}\n{THICK_LINE}"
    )
    try:
        bot.edit_message_text(text, chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("pe_"))
def pr_edit_field(call):
    if not is_admin(call.from_user.id): return
    parts = call.data.split("_", 2)
    if len(parts) < 3:
        bot.answer_callback_query(call.id, "❌ Ошибка!"); return
    field = parts[1]
    code = parts[2]
    if field == "yt":
        if code in promo_codes:
            promo_codes[code]["youtuber"] = not promo_codes[code].get("youtuber", False)
            save_promos()
            bot.answer_callback_query(call.id,
                f"🎬 {'Включен' if promo_codes[code]['youtuber'] else 'Выключен'}", show_alert=True)
            _show_promo_edit(call, code)
        return
    if field == "date":
        msg = bot.send_message(call.message.chat.id,
            f"📅 Введите дату в формате <code>ДД.ММ.ГГГГ</code> (например 31.12.2026):\n"
            f"Или <code>0</code> чтобы убрать срок.\n(или /cancel)",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, pr_edit_date_apply, code)
        bot.answer_callback_query(call.id)
        return
    field_names = {"coins": "💸 Монетки", "exp": "💎 Опыт", "acts": "🔁 Активации", "vip": "⭐ VIP дни"}
    msg = bot.send_message(call.message.chat.id,
        f"✏️ Введите новое значение для <b>{field_names[field]}</b> промокода <code>{code}</code>:\n"
        f"(или /cancel для отмены)", parse_mode="HTML")
    bot.register_next_step_handler(msg, pr_edit_field_apply, code, field)
    bot.answer_callback_query(call.id)


def pr_edit_field_apply(message, code, field):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    try:
        val = int(message.text.strip())
    except:
        bot.send_message(message.chat.id, "❌ Введите число."); return
    if code not in promo_codes:
        bot.send_message(message.chat.id, "❌ Промокод не найден."); return
    if field == "coins": promo_codes[code]["coins"] = val
    elif field == "exp": promo_codes[code]["exp"] = val
    elif field == "acts": promo_codes[code]["activations"] = max(1, val)
    elif field == "vip": promo_codes[code]["vip_days"] = max(0, val)
    save_promos()
    bot.send_message(message.chat.id, f"✅ Обновлено: <code>{code}</code> → {field} = {val}", parse_mode="HTML")


def pr_edit_date_apply(message, code):
    if not is_admin(message.from_user.id): return
    if is_cancel(message):
        bot.send_message(message.chat.id, "❌ Отменено."); return
    if code not in promo_codes:
        bot.send_message(message.chat.id, "❌ Промокод не найден."); return
    text = message.text.strip()
    if text == "0":
        promo_codes[code].pop("expires_at", None)
        save_promos()
        bot.send_message(message.chat.id, "✅ Дата убрана."); return
    try:
        dt = datetime.strptime(text, "%d.%m.%Y")
        promo_codes[code]["expires_at"] = dt.isoformat()
        save_promos()
        bot.send_message(message.chat.id,
            f"✅ Промокод действует до {dt.strftime('%d.%m.%Y')}.", parse_mode="HTML")
    except:
        bot.send_message(message.chat.id, "❌ Неверный формат.")
        
        
# ============================================================
# --- СТАТИСТИКА ПРОМОКОДОВ ---
# ============================================================
def show_promo_page(chat_id, user_id, message_id=None):
    page = promo_page.get(user_id, 0)
    codes = list(promo_codes.keys())
    per_page = 10
    total_pages = max(1, (len(codes) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    promo_page[user_id] = page
    start = page * per_page
    page_codes = codes[start:start + per_page]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for code in page_codes:
        data = promo_codes[code]
        used = data.get("used", 0); acts = data.get("activations", 0)
        status = "🟢" if used < acts else "🔴"
        tags = ""
        if data.get("vip_days", 0) > 0: tags += f"⭐{data['vip_days']}д"
        if data.get("youtuber"): tags += "🎬"
        if not tags: tags = "📦"
        markup.add(types.InlineKeyboardButton(
            f"{status}{tags} {code} ({used}/{acts})", callback_data=f"pr_stats_{code}"))
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("⬅️ Назад", callback_data="promo_page_prev"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("Вперёд ➡️", callback_data="promo_page_next"))
    if nav:
        markup.row(*nav)
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="promo_close"))
    text = (f"📊 <b>Статистика промокодов</b>\n{THICK_LINE}\n"
            f"📄 Страница {page+1}/{total_pages}\n🎁 Всего: {len(codes)}\n"
            f"Нажмите на промокод для деталей")
    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in ("promo_page_prev", "promo_page_next"))
def promo_page_nav(call):
    if not is_admin(call.from_user.id): return
    uid = call.from_user.id
    page = promo_page.get(uid, 0)
    if call.data == "promo_page_prev": page -= 1
    else: page += 1
    promo_page[uid] = page
    show_promo_page(call.message.chat.id, uid, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "promo_close")
def promo_close(call):
    bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id,
                          message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("pr_stats_"))
def pr_stats_show(call):
    if not is_admin(call.from_user.id): return
    code = call.data.replace("pr_stats_", "")
    if code not in promo_codes:
        bot.answer_callback_query(call.id, "❌ Не найден!"); return
    data = promo_codes[code]
    youtuber = "🎬 Да" if data.get("youtuber") else "📦 Нет"
    card = data.get("card") or "нет"
    vip_days = data.get("vip_days", 0)
    used_by = data.get("used_by", [])
    expires_at = data.get("expires_at")

    text = (
        f"📊 <b>Промокод:</b> <code>{code}</code>\n{THICK_LINE}\n"
        f"💸 Монетки: {data.get('coins', 0)}\n"
        f"💎 Опыт: {data.get('exp', 0)}\n"
        f"🃏 Карта: {card}\n"
        f"🔁 Активаций: {data.get('used', 0)}/{data.get('activations', 1)}\n"
        f"⭐ VIP: {vip_days} дн.\n"
        f"🎬 Ютубер: {youtuber}\n"
    )

    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(expires_at)
            if datetime.now() > exp_dt:
                text += f"📅 Срок: ❌ истёк ({exp_dt.strftime('%d.%m.%Y')})\n"
            else:
                text += f"📅 Срок: до {exp_dt.strftime('%d.%m.%Y %H:%M')}\n"
        except:
            pass

    if used_by:
        text += f"\n{THICK_LINE}\n👥 <b>Активировали ({len(used_by)}):</b>\n"
        for uid in used_by[-15:]:
            try:
                ch = bot.get_chat(uid)
                name = ch.first_name or f"ID {uid}"
                if ch.username:
                    name += f" (@{ch.username})"
            except:
                name = f"ID {uid}"
            text += f"• {escape_html(name)}\n"
        if len(used_by) > 15:
            text += f"… и ещё {len(used_by) - 15}\n"

    bot.edit_message_text(text, chat_id=call.message.chat.id,
                          message_id=call.message.message_id, parse_mode="HTML")
    bot.answer_callback_query(call.id)


# ============================================================
# --- УДАЛЕНИЕ ПРОМО ---
# ============================================================
def show_promo_delete_page(chat_id, user_id, message_id=None):
    page = promo_page.get(user_id, 0)
    codes = list(promo_codes.keys())
    per_page = 10
    total_pages = max(1, (len(codes) + per_page - 1) // per_page)
    page = max(0, min(page, total_pages - 1))
    promo_page[user_id] = page
    start = page * per_page
    page_codes = codes[start:start + per_page]
    markup = types.InlineKeyboardMarkup(row_width=1)
    for code in page_codes:
        markup.add(types.InlineKeyboardButton(f"🗑️ {code}", callback_data=f"pr_del_{code}"))
    nav = []
    if page > 0:
        nav.append(types.InlineKeyboardButton("⬅️ Назад", callback_data="promo_del_prev"))
    if page < total_pages - 1:
        nav.append(types.InlineKeyboardButton("Вперёд ➡️", callback_data="promo_del_next"))
    if nav:
        markup.row(*nav)
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="promo_del_close"))
    text = (f"🗑️ <b>Удаление промо</b>\n{THICK_LINE}\n"
            f"📄 Страница {page+1}/{total_pages}\n🎁 Всего: {len(codes)}")
    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id,
                                  reply_markup=markup, parse_mode="HTML")
        except:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="HTML")


@bot.callback_query_handler(func=lambda call: call.data in ("promo_del_prev", "promo_del_next"))
def promo_del_nav(call):
    if not is_admin(call.from_user.id): return
    uid = call.from_user.id
    page = promo_page.get(uid, 0)
    if call.data == "promo_del_prev": page -= 1
    else: page += 1
    promo_page[uid] = page
    show_promo_delete_page(call.message.chat.id, uid, message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "promo_del_close")
def promo_del_close(call):
    bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id,
                          message_id=call.message.message_id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("pr_del_"))
def pr_del_callback(call):
    if not is_admin(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Нет доступа!"); return
    code = call.data.replace("pr_del_", "")
    if code not in promo_codes:
        bot.answer_callback_query(call.id, "❌ Не найден!", show_alert=True); return
    promo_data = promo_codes[code]
    was_youtuber = promo_data.get("youtuber", False)
    used_by = promo_data.get("used_by", [])
    del promo_codes[code]
    save_promos()
    if was_youtuber:
        for uid in used_by:
            youtuber_activated_by.discard(uid)
            try:
                bot.send_message(uid,
                    f"🎬 <b>Ютуберский промо был удалён!</b>\n\n"
                    f"Промокод <code>{code}</code> больше не активен.\n"
                    f"Вы можете активировать промокод другого ютубера.",
                    parse_mode="HTML")
            except:
                pass
        save_youtuber_users()
    bot.answer_callback_query(call.id, f"✅ Промокод {code} удалён!", show_alert=True)
    promo_page[call.from_user.id] = 0
    show_promo_delete_page(call.message.chat.id, call.from_user.id, message_id=call.message.message_id)


# ============================================================
# --- АКТИВАЦИЯ ПРОМОКОДА ---
# ============================================================
@bot.message_handler(commands=['promo'])
@bot.message_handler(func=lambda message: message.text and 
    (message.text.lower().strip().startswith("промо") or 
     message.text.lower().strip().startswith("промокод") or
     message.text.lower().strip().startswith("промик")))
@blocked
def promo_user_command(message):
    raw = message.text or ""
    raw = raw.replace("#", " ")
    args = raw.split()

    if len(args) < 2:
        instruction = (
            f"🎁 <b>Активация промокода:</b>\n"
            f"<blockquote>промо #название</blockquote>\n\n"
            f"<i>Пример: промокод <b>#СТАРТ</b></i>"
        )
        bot.reply_to(message, instruction, parse_mode="HTML")
        return

    code = args[1].upper()
    user_id = message.from_user.id

    promo = None
    actual_code = None
    for variant in (code, f"#{code}"):
        if variant in promo_codes:
            promo = promo_codes[variant]
            actual_code = variant
            break

    if promo is None:
        bot.reply_to(message, "❌ Промокод не найден!")
        return

    # Проверка срока действия
    expires_at = promo.get("expires_at")
    if expires_at:
        try:
            exp_dt = datetime.fromisoformat(expires_at)
            if datetime.now() > exp_dt:
                bot.reply_to(message, "❌ Срок действия промокода истёк!")
                return
        except:
            pass

    if promo.get("used", 0) >= promo.get("activations", 1):
        bot.reply_to(message, "❌ Лимит активаций промокода исчерпан!")
        return

    if user_id in promo.get("used_by", []) and not is_admin(user_id):
        bot.reply_to(message, "❌ Вы уже использовали этот промокод!")
        return

    if promo.get("youtuber"):
        if user_id in youtuber_activated_by:
            bot.reply_to(message,
                "❌ <b>Вы уже получили ранее ютуберский промокод!</b>\n\n"
                "Вы можете активировать промокод другого ютубера после удаления предыдущего.",
                parse_mode="HTML")
            return

    coins = promo.get("coins", 0)
    exp = promo.get("exp", 0)
    card = promo.get("card")
    vip_days = promo.get("vip_days", 0)

    if coins > 0:
        user_coins[user_id] = user_coins.get(user_id, 0) + coins
        save_coins()
    if exp > 0:
        user_exp[user_id] = user_exp.get(user_id, 0) + exp
        save_exp()
    if card and card in cards_db:
        if user_id not in user_cards:
            user_cards[user_id] = []
        user_cards[user_id].append(card)
        save_cards()

    if vip_days > 0:
        expires_at_new = datetime.now() + timedelta(days=vip_days)
        if user_id in user_vip_promos and datetime.now() < user_vip_promos[user_id]["expires_at"]:
            expires_at_new = user_vip_promos[user_id]["expires_at"] + timedelta(days=vip_days)
        user_vip_promos[user_id] = {"expires_at": expires_at_new}
        save_vip_promos()

    promo["used"] = promo.get("used", 0) + 1
    if user_id not in promo.get("used_by", []):
        promo["used_by"] = promo.get("used_by", []) + [user_id]
    save_promos()

    if promo.get("youtuber"):
        youtuber_activated_by.add(user_id)
        save_youtuber_users()

    log_action(user_id, "Активировал промо", actual_code)

    text = f"✅ <b>Промокод активирован!</b>\n{THICK_LINE}\n🎁 Код: <code>{actual_code}</code>\n"
    if coins > 0: text += f"💸 Монетки: +{coins}\n"
    if exp > 0: text += f"💎 Опыт: +{exp}\n"
    if card: text += f"🃏 Карта: {card}\n"
    if vip_days > 0: text += f"⭐ VIP: +{vip_days} дней\n"
    if promo.get("youtuber"): text += "🎬 Тип: Ютуберский\n"
    text += f"{THICK_LINE}"
    bot.reply_to(message, text, parse_mode="HTML")
    
    
# ============================================================
# --- VIP ЗА 20 ЗВЁЗД ---
# ============================================================
@bot.message_handler(commands=['vip'])
@blocked
def vip_command(message):
    user_id = message.from_user.id
    chat_type = message.chat.type

    if has_active_vip(user_id):
        bot.reply_to(message, "⭐ <b>У вас уже есть активный VIP!</b>", parse_mode="HTML")
        return

    price = vip_price.get("price", 20)
    days = vip_price.get("duration_days", 30)

    if chat_type != 'private':
        info_text = (
            f"⭐ <b>VIP СТАТУС</b>\n{THICK_LINE}\n"
            f"• 💎 ×2 опыт\n"
            f"• 💸 ×2 монетки\n"
            f"• ⏱️ Кулдаун 45 мин\n"
            f"{THICK_LINE}\n"
            f"💰 <b>{price} звёзд</b> на <b>{days} дней</b>\n\n"
            f"⚠️ VIP можно купить только в личных сообщениях бота.\n"
            f"👉 Напишите боту в личку и введите /vip там."
        )
        bot.reply_to(message, info_text, parse_mode="HTML")
        return

    prices = [types.LabeledPrice(label=f"VIP на {days} дней", amount=price)]
    bot.send_invoice(
        message.chat.id,
        title=f"⭐ VIP на {days} дней",
        description="×2 опыт, ×2 монетки, кулдаун карточек 45 минут",
        invoice_payload="vip_purchase",
        provider_token="",
        currency="XTR",
        prices=prices,
        start_parameter="vip"
    )


@bot.pre_checkout_query_handler(func=lambda q: True)
def pre_checkout(query):
    bot.answer_pre_checkout_query(query.id, ok=True)


@bot.message_handler(content_types=['successful_payment'])
@blocked
def got_payment(message):
    user_id = message.from_user.id
    days = vip_price.get("duration_days", 30)

    expires_at = datetime.now() + timedelta(days=days)
    if user_id in user_vip_promos and datetime.now() < user_vip_promos[user_id]["expires_at"]:
        expires_at = user_vip_promos[user_id]["expires_at"] + timedelta(days=days)
    user_vip_promos[user_id] = {"expires_at": expires_at}
    save_vip_promos()

    if user_id in user_vip:
        del user_vip[user_id]
        save_vip()

    log_action(user_id, "Купил VIP", f"{days} дней")

    bot.send_message(
        message.chat.id,
        f"⭐ <b>VIP активирован на {days} дней!</b>\n{THICK_LINE}\n"
        f"Действует до: <b>{expires_at.strftime('%d.%m.%Y %H:%M')}</b>\n\n"
        f"💡 Введите команду <code>/statusvip</code>, чтобы посмотреть статистику бота.",
        parse_mode="HTML"
    )


# ============================================================
# --- /statusvip ---
# ============================================================
@bot.message_handler(commands=['statusvip'])
@blocked
def statusvip_command(message):
    user_id = message.from_user.id
    if not has_active_vip(user_id) and not is_admin(user_id):
        return
    total_users = len(set(list(user_coins.keys()) + list(user_cards.keys()) + list(user_exp.keys())))
    total_coins = sum(user_coins.values())
    total_exp = sum(user_exp.values())
    total_cards_in_db = len(cards_db)
    total_vip = len(user_vip) + len(user_vip_promos)
    text = (
        f"📊 <b>Статистика бота</b>\n{THICK_LINE}\n"
        f"👥 Игроков: {total_users}\n"
        f"🃏 Карт в базе: {total_cards_in_db}\n"
        f"💸 Монеток всего: {total_coins}\n"
        f"💎 Опыта всего: {total_exp}\n"
        f"⭐ VIP: {total_vip}\n{THICK_LINE}"
    )
    bot.reply_to(message, text, parse_mode="HTML")
    
    
# ============================================================
# --- ТРЕКИНГ ЧАТОВ + РЕГИСТРАЦИЯ ИГРОКОВ ---
# ============================================================
@bot.message_handler(func=lambda message: True, content_types=[
    'text', 'photo', 'video', 'audio', 'document', 'sticker',
    'voice', 'video_note', 'location', 'contact', 'new_chat_members',
    'left_chat_member', 'new_chat_title', 'new_chat_photo', 'delete_chat_photo',
    'group_chat_created', 'supergroup_chat_created', 'channel_chat_created'
])
def track_chat(message):
    # Проверка блокировки — самая первая
    if message.from_user and message.from_user.id in blocked_users:
        return

    # Проверка тех. режима — админы всегда работают
    if not is_admin(message.from_user.id if message.from_user else 0):
        if tech_mode.get("enabled"):
            if message.content_type == 'text':
                try:
                    bot.reply_to(message, tech_mode.get("message", "🔧 Тех. работы."))
                except:
                    pass
            return

    # Регистрируем игрока
    if message.from_user:
        register_player_today(message.from_user.id)

    chat_id = message.chat.id
    chat_type = message.chat.type
    if chat_type == 'private':
        return

    if chat_id not in known_chats:
        known_chats[chat_id] = {
            "title": message.chat.title or f"Чат {chat_id}",
            "type": chat_type,
            "username": message.chat.username,
            "added_at": datetime.now().isoformat(),
        }
        save_known_chats()
    else:
        if message.chat.username and known_chats[chat_id].get("username") != message.chat.username:
            known_chats[chat_id]["username"] = message.chat.username
            save_known_chats()


# ============================================================
# --- ПРОСМОТР JSON ---
# ============================================================
JSON_FILES = {
    "coins": COINS_FILE,
    "cards": CARDS_FILE,
    "exp": EXP_FILE,
    "ranks": RANKS_FILE,
    "cards_db": CARDS_DB_FILE,
    "promo": PROMO_FILE,
    "vip": VIP_FILE,
    "vip_promos": VIP_PROMOS_FILE,
    "daily": DAILY_FILE,
    "daily_players": DAILY_PLAYERS_FILE,
    "blocked": BLOCKED_FILE,
    "history": HISTORY_FILE,
    "tech_mode": TECH_MODE_FILE,
    "texts": TEXTS_FILE,
    "events": EVENTS_FILE,
    "vip_price": VIP_PRICE_FILE,
}


@bot.message_handler(commands=['viewjson'])
def viewjson_command(message):
    if not is_admin(message.from_user.id):
        return

    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, filename in JSON_FILES.items():
        buttons.append(types.InlineKeyboardButton(
            f"📄 {key}",
            callback_data=f"json_view_{key}"
        ))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="json_close"))

    bot.send_message(
        message.chat.id,
        f"📄 <b>Просмотр JSON</b>\n{THICK_LINE}\nВыберите файл:",
        reply_markup=markup, parse_mode="HTML"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("json_view_"))
def json_view(call):
    if not is_admin(call.from_user.id): return
    key = call.data.replace("json_view_", "")
    if key not in JSON_FILES:
        bot.answer_callback_query(call.id, "❌ Файл не найден!"); return

    filename = JSON_FILES[key]
    if not os.path.exists(filename):
        bot.answer_callback_query(call.id, f"❌ Файл {filename} не существует", show_alert=True)
        return

    try:
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        # Ограничиваем длину
        if len(content) > 3500:
            content = content[:3500] + "\n\n... (обрезано)"
        text = f"📄 <b>{filename}</b>\n{THICK_LINE}\n<pre>{escape_html(content)}</pre>"
    except Exception as e:
        text = f"❌ Ошибка чтения: {e}"

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔙 К списку", callback_data="json_back"))
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="json_close"))

    try:
        bot.edit_message_text(text, chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=markup, parse_mode="HTML")
    except:
        bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "json_back")
def json_back(call):
    if not is_admin(call.from_user.id): return
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for key, filename in JSON_FILES.items():
        buttons.append(types.InlineKeyboardButton(f"📄 {key}", callback_data=f"json_view_{key}"))
    markup.add(*buttons)
    markup.add(types.InlineKeyboardButton("❌ Закрыть", callback_data="json_close"))

    try:
        bot.edit_message_text(
            f"📄 <b>Просмотр JSON</b>\n{THICK_LINE}\nВыберите файл:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup, parse_mode="HTML"
        )
    except: pass
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "json_close")
def json_close(call):
    try:
        bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    except: pass
    bot.answer_callback_query(call.id)


# ============================================================
# --- ПРОВЕРКА ДАННЫХ + АВТОИСПРАВЛЕНИЕ ---
# ============================================================
def collect_integrity_problems():
    """Собирает проблемы целостности"""
    problems = []

    # 1. Карты в инвентарях без записи в базе
    broken_cards = []
    for uid, cards in user_cards.items():
        for c in cards:
            if c not in cards_db:
                broken_cards.append((uid, c))
    if broken_cards:
        problems.append({
            "type": "broken_cards",
            "count": len(broken_cards),
            "desc": f"Карты в инвентарях, которых нет в базе: {len(broken_cards)}",
        })

    # 2. Отрицательные балансы
    neg_balances = [(uid, c) for uid, c in user_coins.items() if c < 0]
    if neg_balances:
        problems.append({
            "type": "negative_coins",
            "count": len(neg_balances),
            "desc": f"Игроков с отрицательным балансом: {len(neg_balances)}",
        })

    # 3. Промокоды без activations
    broken_promos = []
    for code, data in promo_codes.items():
        if "activations" not in data:
            broken_promos.append(code)
    if broken_promos:
        problems.append({
            "type": "broken_promos",
            "count": len(broken_promos),
            "desc": f"Промокодов без поля activations: {len(broken_promos)}",
        })

    # 4. Истёкшие VIP в user_vip_promos
    expired_vip = []
    now = datetime.now()
    for uid, data in list(user_vip_promos.items()):
        if data.get("expires_at") and now >= data["expires_at"]:
            expired_vip.append(uid)
    if expired_vip:
        problems.append({
            "type": "expired_vip",
            "count": len(expired_vip),
            "desc": f"Истёкших VIP: {len(expired_vip)}",
        })

    # 5. Ранги вне 1-10
    broken_ranks = [(uid, r) for uid, r in user_ranks.items() if r < 1 or r > 10]
    if broken_ranks:
        problems.append({
            "type": "broken_ranks",
            "count": len(broken_ranks),
            "desc": f"Игроков с рангом вне 1-10: {len(broken_ranks)}",
        })

    # 6. Отрицательный опыт
    neg_exp = [(uid, e) for uid, e in user_exp.items() if e < 0]
    if neg_exp:
        problems.append({
            "type": "negative_exp",
            "count": len(neg_exp),
            "desc": f"Игроков с отрицательным опытом: {len(neg_exp)}",
        })

    return problems


def fix_integrity_problems():
    """Исправляет проблемы целостности. Возвращает список отчётов."""
    reports = []

    # 1. Удаляем битые карты
    removed = 0
    for uid, cards in list(user_cards.items()):
        new_cards = [c for c in cards if c in cards_db]
        if len(new_cards) != len(cards):
            removed += len(cards) - len(new_cards)
            user_cards[uid] = new_cards
    if removed:
        save_cards()
        reports.append(f"• Удалено битых карт из инвентарей: {removed}")

    # 2. Обнуляем отрицательные балансы
    fixed = 0
    for uid, c in list(user_coins.items()):
        if c < 0:
            user_coins[uid] = 0
            fixed += 1
    if fixed:
        save_coins()
        reports.append(f"• Обнулено отрицательных балансов: {fixed}")

    # 3. Промокоды без activations
    fixed = 0
    for code, data in promo_codes.items():
        if "activations" not in data:
            data["activations"] = 1
            fixed += 1
    if fixed:
        save_promos()
        reports.append(f"• Добавлено поле activations: {fixed}")

    # 4. Истёкшие VIP
    removed = 0
    now = datetime.now()
    for uid in list(user_vip_promos.keys()):
        data = user_vip_promos[uid]
        if data.get("expires_at") and now >= data["expires_at"]:
            del user_vip_promos[uid]
            removed += 1
    if removed:
        save_vip_promos()
        reports.append(f"• Удалено истёкших VIP: {removed}")

    # 5. Битые ранги
    fixed = 0
    for uid, r in list(user_ranks.items()):
        if r < 1 or r > 10:
            user_ranks[uid] = 1
            fixed += 1
    if fixed:
        save_ranks()
        reports.append(f"• Сброшено битых рангов: {fixed}")

    # 6. Отрицательный опыт
    fixed = 0
    for uid, e in list(user_exp.items()):
        if e < 0:
            user_exp[uid] = 0
            fixed += 1
    if fixed:
        save_exp()
        reports.append(f"• Обнулено отрицательного опыта: {fixed}")

    return reports


@bot.callback_query_handler(func=lambda call: call.data == "adm_integrity_check")
def adm_integrity_check(call):
    if not is_admin(call.from_user.id): return

    problems = collect_integrity_problems()

    if not problems:
        text = (
            f"✅ <b>Проверка пройдена</b>\n{THICK_LINE}\n"
            f"Проблем не найдено."
        )
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    text = f"⚠️ <b>Найдено проблем: {len(problems)}</b>\n{THICK_LINE}\n"
    for p in problems:
        text += f"• {p['desc']}\n"

    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🔧 Исправить автоматически", callback_data="adm_integrity_fix"),
        types.InlineKeyboardButton("❌ Закрыть", callback_data="adm_integrity_close"),
    )
    bot.send_message(call.message.chat.id, text, reply_markup=markup, parse_mode="HTML")
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == "adm_integrity_fix")
def adm_integrity_fix(call):
    if not is_admin(call.from_user.id): return
    reports = fix_integrity_problems()

    if not reports:
        text = "✅ Нечего исправлять."
    else:
        text = (
            f"🔧 <b>Исправление завершено</b>\n{THICK_LINE}\n"
            + "\n".join(reports)
        )
    bot.edit_message_text(text, chat_id=call.message.chat.id,
                          message_id=call.message.message_id, parse_mode="HTML")
    bot.answer_callback_query(call.id, "✅ Исправлено", show_alert=True)


@bot.callback_query_handler(func=lambda call: call.data == "adm_integrity_close")
def adm_integrity_close(call):
    try:
        bot.edit_message_text("❌ Закрыто.", chat_id=call.message.chat.id,
                              message_id=call.message.message_id)
    except: pass
    bot.answer_callback_query(call.id)


# ============================================================
# --- ПЕРЕЗАПУСК БОТА ---
# ============================================================
@bot.message_handler(commands=['restart'])
def restart_command(message):
    if not is_admin(message.from_user.id):
        return
    bot.send_message(message.chat.id, "🔄 <b>Перезапуск бота...</b>\nЧерез 2 секунды.", parse_mode="HTML")
    time.sleep(2)
    # Перезапускаем процесс (только если запущено через systemd/Railway и т.п.)
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Ошибка перезапуска: {e}")
        
        
# ============================================================
# --- ЗАПУСК ---
# ============================================================
if __name__ == '__main__':
    # Фоновые потоки
    threading.Thread(target=daily_reset_loop, daemon=True).start()
    threading.Thread(target=vip_expiry_check_loop, daemon=True).start()

    print("=" * 50)
    print("🎉 CBYT Cards v16.0 — ЗАПУЩЕН!")
    print("=" * 50)
    print(f"🃏 Карт в базе: {len(cards_db)}")
    print(f"⭐ VIP (вечных): {len(user_vip)}")
    print(f"⭐ VIP (промо): {len(user_vip_promos)}")
    print(f"🚫 Заблокировано: {len(blocked_users)}")
    print(f"💬 Известных чатов: {len(known_chats)}")
    print(f"📅 Игроков за сегодня: {len(daily_players.get('players', []))}")
    print(f"🎊 ×2 Опыт: {'ВКЛ' if has_double_exp() else 'выкл'}")
    print(f"🎊 ×2 Монеты: {'ВКЛ' if has_double_coins() else 'выкл'}")
    print(f"🔧 Тех. режим: {'ВКЛ' if tech_mode.get('enabled') else 'выкл'}")
    print(f"💰 VIP: {vip_price.get('price', 20)} звёзд на {vip_price.get('duration_days', 30)} дней")
    print("=" * 50)
    print("📌 /admin — админ-панель")
    print("📌 /help — помощь")
    print("📌 /daily — ежедневный бонус")
    print("📌 /vip — купить VIP")
    print("📌 /inventory — инвентарь")
    print("📌 /upgrade — прокачка")
    print("📌 /viewjson — просмотр JSON (админ)")
    print("📌 /restart — перезапуск бота (админ)")
    print("=" * 50)

    bot.infinity_polling(skip_pending=True, timeout=60)