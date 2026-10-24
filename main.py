import asyncio
import random
import re
import sqlite3
import logging
import time
import json
import urllib.request
from aiohttp import web
from collections import Counter
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, CommandObject, Command
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from phone_shop import phone_router

dp.include_router(phone_router)

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = "8880561409:AAFEXi6GKwDdmY4tWXPiT_l6ewnaazON0tk"
CHANNEL_ID = "@bfnsbercwjj"
CHANNEL_URL = "https://t.me/bfnsbercwjj"
CHANNEL_INVITE_URL = "https://t.me/+ihok5bRCYyhkYjcy"
DB_PATH = "bot_data.db"
MAX_ACCOUNTS = 10

# ================================================
# ТИТУЛЫ И ГАЛОЧКИ
# ================================================
CUSTOM_TITLES = {
    "kaka671488695242228": "😎 Владелец",
    "milennawqlololo": "🏷 крутая х#кер",
    "exsoid": "🍎 яблочный сок",
    "oiyres_corporate": "Помощник",
    
}
VERIFIED_USERS = {
    "oiyres_corporate": "✔",
    "kaka671488695242228": "✔",
    "milennawqlololo": "✔",
    "exsoid": "✔",
}

# ================================================
# ЛИЧНЫЕ 888 НОМЕРА
# ================================================
PERSONAL_888 = {
    "exsoid": "+88005553535",
    "kaka671488695242228": "+888 8888 8888",
    "milennawqlololo": "+88800228888",
    "exsoid": "+888 8888 8888",
}
LUXURY_888 = ["+888 0000 0004","+888 0000 0005","+888 0000 0006","+888 0000 0007",
              "+888 0000 0008","+888 0000 0009","+888 0000 0010","+888 0000 0011",
              "+888 0000 0012","+888 0000 0013","+888 0000 0014","+888 0000 0015","+8800 555 35 35"]

RESERVED_USERNAMES = {"kaka671488695242228": ["kaka671488695242228", "durov", "pavel"]}
USERNAME_PATTERN = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{4,31}$")
WALLET_NICK_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
CHECK_CODE_LEN = 8

# ================================================
# 100 НОМЕРОВ
# ================================================
FAKE_NUMBERS = {
    "🇷🇺 Россия": ["+7 900 123-45-67","+7 903 555-88-11","+7 926 777-33-22","+7 999 100-20-30","+7 985 444-12-99","+7 916 234-56-78","+7 925 111-22-33","+7 968 999-00-11","+7 977 555-44-55","+7 962 777-88-99"],
    "🇺🇦 Украина": ["+380 44 123-45-67","+380 50 555-22-11","+380 67 999-88-77","+380 63 111-22-33","+380 93 700-15-50","+380 96 333-44-55","+380 66 888-99-00","+380 95 222-33-44","+380 73 555-66-77","+380 68 444-11-22"],
    "🇺🇸 США": ["+1 212 555-0101","+1 415 555-0288","+1 305 555-0347","+1 702 555-0199","+1 213 555-0466","+1 202 555-0177","+1 617 555-0222","+1 312 555-0999","+1 404 555-0388","+1 206 555-0111"],
    "🇩🇪 Германия": ["+49 30 1234-5678","+49 89 5555-1111","+49 40 9999-2222","+49 69 3333-7777","+49 211 8080-4455","+49 221 1234-8888","+49 711 5555-4444","+49 30 9876-5432","+49 89 2468-1357","+49 40 1111-9999"],
    "🇬🇧 Великобритания": ["+44 20 7946-0958","+44 161 496-0123","+44 113 222-3344","+44 121 777-8899","+44 131 500-1122","+44 20 7123-4567","+44 151 234-5678","+44 191 555-1234","+44 141 999-8888","+44 117 333-4444"],
    "🇫🇷 Франция": ["+33 1 42 68 53 00","+33 1 55 55 12 34","+33 6 12 34 56 78","+33 4 91 22 33 44","+33 3 88 11 55 99","+33 1 44 55 66 77","+33 6 98 76 54 32","+33 5 56 12 34 56","+33 2 40 55 88 88","+33 4 78 22 11 00"],
    "🇯🇵 Япония": ["+81 3 1234-5678","+81 6 5555-1234","+81 90 1234-5678","+81 80 9999-0000","+81 3 5555-7777","+81 92 111-2222","+81 70 3333-4444","+81 11 555-6666","+81 75 888-9999","+81 45 100-2000"],
    "🇮🇳 Индия": ["+91 11 2345-6789","+91 98 7654-3210","+91 22 5555-1111","+91 80 1234-5678","+91 33 9999-2222","+91 40 4444-5555","+91 99 8888-7777","+91 12 3333-6666","+91 44 2222-9999","+91 79 1111-8888"],
    "🇰🇿 Казахстан": ["+7 700 123-45-67","+7 701 555-88-99","+7 705 111-22-33","+7 707 777-55-44","+7 771 200-30-40","+7 702 333-44-55","+7 747 888-99-00","+7 708 111-22-33","+7 747 555-66-77","+7 775 123-00-99"],
    "🇨🇳 Китай": ["+86 10 1234-5678","+86 21 5555-1122","+86 138 0013-8000","+86 139 1234-5678","+86 20 8888-9999","+86 755 1234-5678","+86 186 8888-7777","+86 133 9999-0000","+86 571 5555-4444","+86 25 2222-3333"],
}
PREMIUM_NUMBERS = ["+7 999 000-00-01","+7 999 000-00-02","+7 999 111-11-11","+7 900 555-55-55","+1 800 000-0001","+1 888 888-8888","+44 20 0000-0001","+49 30 1111-1111","+33 1 0000 0001","+81 3 0000-0001","+86 10 0000-0001","+91 11 0000-0001","+7 700 000-00-01","+380 44 000-00-01","+1 777 777-7777","+7 999 999-99-99","+86 138 0000-0000","+81 90 0000-0000","+49 170 000-0000","+44 7 700 000-000"]

# ================================================
# NFT
# ================================================
NFT_GIFTS = ["Chill Flame","Vice Cream","Liberty Figure","Snoop Dogg","Instant Ramen","Lol Pop","Ice Cream","Pool Float","Mood Pack","Xmas Stocking","Lunar Snake","Whip Cupcake","Swag Bag","Happy Brownie","Candy Cane","Clover Pin","Mirage Lamp","Snake Box","Fresh Socks","Mousse Cake","B-Day Candle","Cookie Heart","Pet Snake","Faith Amulet","Jester Hat","Victory Medal","Spring Basket","Snoop Cigar","Party Sparkler","Pretty Posy","Timeless Book","Light Sword","Input Key","Stellar Rocket","Desk Calendar","Ginger Cookie","Homemade Cake","Moon Pendant","Lush Bouquet","Fine Pen","Jolly Chimp","Tama Gadget","Holiday Drink","Restless Jar","Joyful Bundle","Spy Agaric","Evil Eye","Surge Board","Jelly Bunny","Easter Egg","UFC Strike","Hypno Lollipop","Spiced Wine","Winter Wreath","Sakura Flower","Money Pot","Big Year","Star Notepad","Bow Tie","Jack-in-the-Box","Hex Pot","Witch Hat","Berry Box","Eternal Candle","Snow Globe","Santa Hat","Jingle Bells","Hanging Star","Bunny Muffin","Khabib's Papakha","Top Hat","Sky Stilettos","Crystal Ball","Love Potion","Eternal Rose","Love Candle","Snow Mittens","Valentine Box","Sleigh Bell","Cupid Charm","Trapped Heart","Diamond Ring","Toy Bear","Record Player","Mad Pumpkin","Ionic Dryer","Flying Broom","Rare Bird","Signet Ring","Skull Flower","Vintage Cigar","Voodoo Doll","Swiss Watch","Neko Helmet","Bling Binky","Low Rider","Electric Skull","Sharp Tongue","Kissed Frog","Bonded Ring","Westside Sign","Genie Lamp","Astral Shard","Gem Signet","Loot Bag","Perfume Bottle","Mini Oscar","Scared Cat","Long Gem","Magic Potion","Durov's Cap","Durov's Glasses","Nail Bracelet","Heroic Helmet","Intelligence Cup","Heart Locket","Algorithm Cup","Plush Pepe"]

# ================================================
# NFT С ССЫЛКАМИ (заполняется через /gift_nft_to)
# ================================================
NFT_LINKS = {}


def parse_nft_link(url: str):
    """Парсит ссылку t.me/nft/PlushPepe-1830 → ('Plush Pepe #1830', 'https://t.me/nft/PlushPepe-1830')"""
    if not url:
        return None
    url = url.strip()
    url = url.replace("https://", "").replace("http://", "").strip("/")
    if not url.startswith("t.me/nft/") and not url.startswith("telegram.me/nft/"):
        return None
    try:
        slug = url.split("/nft/", 1)[1].split("?")[0].split("#")[0]
    except IndexError:
        return None
    if "-" not in slug:
        return None
    name_part, number = slug.rsplit("-", 1)
    if not number.isdigit():
        return None
    name_split = re.sub(r"(?<!^)(?=[A-Z])", " ", name_part)
    display_name = f"{name_split} #{number}"
    full_url = f"https://t.me/nft/{slug}"
    return (display_name, full_url)


def nft_display(nft_name):
    """Красивое отображение NFT — кликабельное название + видимая ссылка."""
    if nft_name in NFT_LINKS:
        url = NFT_LINKS[nft_name]
        short_url = url.replace("https://", "").replace("http://", "")
        return f'<a href="{url}">{nft_name}</a>\n   🔗 <code>{short_url}</code>'
    return f"<b>{nft_name}</b>"


# ================================================
# КРИПТОВАЛЮТЫ (11 монет)
# ================================================
CRYPTO = {
    "SOL":  {"name": "Solana",       "emoji": "🟣", "price": 119.43,  "change": -1.84},
    "TRX":  {"name": "TRON",         "emoji": "🔴", "price": 0.3363,  "change": +0.20},
    "BTC":  {"name": "Bitcoin",      "emoji": "🟠", "price": 86298.18,"change": +1.54},
    "ETH":  {"name": "Ethereum",     "emoji": "🔵", "price": 2726.00, "change": +1.44},
    "DOGE": {"name": "Dogecoin",     "emoji": "🟡", "price": 0.09485, "change": +0.62},
    "LTC":  {"name": "Litecoin",     "emoji": "🔷", "price": 70.22,   "change": -1.97},
    "BNB":  {"name": "Binance Coin", "emoji": "🟨", "price": 787.41,  "change": +0.01},
    "USDC": {"name": "USD Coin",     "emoji": "🔵", "price": 0.9999,  "change": 0.00},
    "XAUT": {"name": "Tether Gold",  "emoji": "🟡", "price": 4136.93, "change": -0.07},
    "USDT": {"name": "Tether",       "emoji": "🟢", "price": 0.9998,  "change": 0.00},
    "GRAM": {"name": "Gram",         "emoji": "💎", "price": 1.53,    "change": +0.34},
}

# ================================================
# АВТООБНОВЛЕНИЕ КУРСОВ
# ================================================
COINGECKO_IDS = {
    "SOL": "solana", "TRX": "tron", "BTC": "bitcoin", "ETH": "ethereum",
    "DOGE": "dogecoin", "LTC": "litecoin", "BNB": "binancecoin",
    "USDC": "usd-coin", "XAUT": "tether-gold", "USDT": "tether",
    "GRAM": "the-open-network",
}

LAST_RATES_UPDATE = 0
RATES_UPDATE_INTERVAL = 300


def fetch_rates_sync() -> dict:
    ids = ",".join(COINGECKO_IDS.values())
    url = (
        f"https://api.coingecko.com/api/v3/simple/price"
        f"?ids={ids}&vs_currencies=usd&include_24hr_change=true"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode())


async def update_rates_once() -> bool:
    global LAST_RATES_UPDATE
    try:
        data = await asyncio.to_thread(fetch_rates_sync)
        for coin, cg_id in COINGECKO_IDS.items():
            if cg_id in data:
                info = data[cg_id]
                new_price = info.get("usd")
                new_change = info.get("usd_24h_change", 0)
                if new_price is not None:
                    CRYPTO[coin]["price"] = round(float(new_price), 6)
                if new_change is not None:
                    CRYPTO[coin]["change"] = round(float(new_change), 2)
        LAST_RATES_UPDATE = time.time()
        return True
    except Exception as e:
        print(f"[rates] API error: {e}")
        return False


def simulate_rates():
    global LAST_RATES_UPDATE
    for coin, info in CRYPTO.items():
        delta_pct = random.uniform(-0.5, 0.5)
        info["price"] = round(info["price"] * (1 + delta_pct / 100), 6)
        info["change"] = round(info["change"] + random.uniform(-0.3, 0.3), 2)
    LAST_RATES_UPDATE = time.time()


async def rates_updater():
    while True:
        try:
            ok = await update_rates_once()
            if not ok:
                simulate_rates()
            print(f"[rates] Обновлены в {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"[rates] Ошибка цикла: {e}")
        await asyncio.sleep(RATES_UPDATE_INTERVAL)


STARS_PER_USD = 100
TON_PER_USD = 0.3

# ================================================
# КЕЙСЫ
# ================================================
NFT_CASES = {
    "nft_star_bronze": {"name":"⭐ Бронзовый NFT","price":50,"currency":"stars","nft_count":1},
    "nft_star_silver": {"name":"⭐ Серебряный NFT","price":150,"currency":"stars","nft_count":2},
    "nft_star_gold":   {"name":"⭐ Золотой NFT","price":400,"currency":"stars","nft_count":5},
    "nft_ton_bronze":  {"name":"💎 TON Бронза NFT","price":0.5,"currency":"ton","nft_count":1},
    "nft_ton_silver":  {"name":"💎 TON Серебро NFT","price":1.5,"currency":"ton","nft_count":3},
    "nft_ton_gold":    {"name":"💎 TON Золото NFT","price":5.0,"currency":"ton","nft_count":8},
}
NUMBER_CASES = {
    "num_basic":      {"name":"📞 Базовый номер","price":30,"currency":"stars","num_count":1,"pool":"basic"},
    "num_silver":     {"name":"📞 Серебряный номер","price":100,"currency":"stars","num_count":2,"pool":"basic"},
    "num_gold":       {"name":"📞 Золотой номер","price":250,"currency":"stars","num_count":3,"pool":"premium"},
    "num_ton_basic":  {"name":"💎 TON Базовый номер","price":0.3,"currency":"ton","num_count":1,"pool":"basic"},
    "num_ton_premium":{"name":"💎 TON Премиум номер","price":2.0,"currency":"ton","num_count":3,"pool":"premium"},
    "num_888_luxury": {"name":"👑 ЛЮКС 888 НОМЕР","price":25.0,"currency":"ton","num_count":1,"pool":"luxury_888"},
}
TASKS = {
    "sub_channel":   {"name":"📢 Подписаться на канал","reward_stars":50,"reward_ton":0.1},
    "invite_friend": {"name":"👥 Пригласить друга","reward_stars":100,"reward_ton":0.5},
    "get_number":    {"name":"📱 Получить номер","reward_stars":30,"reward_ton":0.05},
    "open_case":     {"name":"📦 Открыть кейс","reward_stars":75,"reward_ton":0.3},
    "daily":         {"name":"🎁 Ежедневная награда","reward_stars":25,"reward_ton":0.05},
}

# ================================================
# БАЗА ДАННЫХ
# ================================================
class Database:
    def __init__(self, path: str):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        c = self.cursor
        c.execute("""CREATE TABLE IF NOT EXISTS tg_users (user_id INTEGER PRIMARY KEY, active_account INTEGER DEFAULT 0)""")
        c.execute("""CREATE TABLE IF NOT EXISTS accounts (
            account_id INTEGER PRIMARY KEY AUTOINCREMENT, owner_tg_id INTEGER NOT NULL,
            slot INTEGER NOT NULL, activated INTEGER DEFAULT 0, stars INTEGER DEFAULT 0, ton REAL DEFAULT 0,
            UNIQUE (owner_tg_id, slot))""")
        c.execute("""CREATE TABLE IF NOT EXISTS nft_inventory (id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER NOT NULL, nft TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_numbers (id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER NOT NULL, number TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS usernames (username TEXT PRIMARY KEY, account_id INTEGER NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS market_nft (lot_id INTEGER PRIMARY KEY AUTOINCREMENT, seller_account INTEGER NOT NULL, seller_tg INTEGER NOT NULL, nft TEXT NOT NULL, price REAL NOT NULL, currency TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS market_num (lot_id INTEGER PRIMARY KEY AUTOINCREMENT, seller_account INTEGER NOT NULL, seller_tg INTEGER NOT NULL, number TEXT NOT NULL, price REAL NOT NULL, currency TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS market_uname (lot_id INTEGER PRIMARY KEY AUTOINCREMENT, seller_account INTEGER NOT NULL, seller_tg INTEGER NOT NULL, username TEXT NOT NULL, price REAL NOT NULL, currency TEXT NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS completed_tasks (account_id INTEGER NOT NULL, task_key TEXT NOT NULL, PRIMARY KEY (account_id, task_key))""")
        c.execute("""CREATE TABLE IF NOT EXISTS user_actions (account_id INTEGER NOT NULL, action TEXT NOT NULL, PRIMARY KEY (account_id, action))""")
        c.execute("""CREATE TABLE IF NOT EXISTS referrals (inviter_id INTEGER NOT NULL, referred_id INTEGER NOT NULL, PRIMARY KEY (inviter_id, referred_id))""")
        c.execute("""CREATE TABLE IF NOT EXISTS daily_claims (account_id INTEGER PRIMARY KEY, last_claim REAL NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS wallets (account_id INTEGER PRIMARY KEY, nick TEXT UNIQUE NOT NULL, code TEXT UNIQUE NOT NULL, created REAL NOT NULL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS crypto_balances (account_id INTEGER NOT NULL, coin TEXT NOT NULL, amount REAL DEFAULT 0, PRIMARY KEY (account_id, coin))""")
        c.execute("""CREATE TABLE IF NOT EXISTS checks (check_id INTEGER PRIMARY KEY AUTOINCREMENT, code TEXT UNIQUE NOT NULL, creator_tg INTEGER NOT NULL, coin TEXT NOT NULL, amount REAL NOT NULL, status TEXT DEFAULT 'active', created REAL NOT NULL, redeemed_by INTEGER)""")
        c.execute("""CREATE TABLE IF NOT EXISTS nft_links (
            nft_name TEXT PRIMARY KEY,
            nft_url TEXT NOT NULL)""")
        self.conn.commit()

    def get_tg_user(self, user_id):
        self.cursor.execute("SELECT * FROM tg_users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        if row is None:
            self.cursor.execute("INSERT INTO tg_users (user_id, active_account) VALUES (?, 0)", (user_id,))
            self.conn.commit()
            acc_id = self.create_account(user_id, slot=1)
            self.cursor.execute("UPDATE tg_users SET active_account = ? WHERE user_id = ?", (acc_id, user_id))
            self.conn.commit()
            return {"user_id": user_id, "active_account": acc_id}
        return dict(row)

    def set_active_account(self, user_id, account_id):
        self.cursor.execute("UPDATE tg_users SET active_account = ? WHERE user_id = ?", (account_id, user_id))
        self.conn.commit()

    def get_active_account_id(self, user_id):
        return self.get_tg_user(user_id)["active_account"]

    def create_account(self, owner_tg_id, slot):
        stars = random.randint(50, 500); ton = round(random.uniform(0.5, 5.0), 2)
        self.cursor.execute("INSERT INTO accounts (owner_tg_id, slot, activated, stars, ton) VALUES (?, ?, 0, ?, ?)", (owner_tg_id, slot, stars, ton))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_account(self, account_id):
        self.cursor.execute("SELECT * FROM accounts WHERE account_id = ?", (account_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_accounts(self, owner_tg_id):
        self.cursor.execute("SELECT * FROM accounts WHERE owner_tg_id = ? ORDER BY slot", (owner_tg_id,))
        return [dict(r) for r in self.cursor.fetchall()]

    def count_accounts(self, owner_tg_id):
        self.cursor.execute("SELECT COUNT(*) as c FROM accounts WHERE owner_tg_id = ?", (owner_tg_id,))
        return self.cursor.fetchone()["c"]

    def set_account_activated(self, account_id):
        self.cursor.execute("UPDATE accounts SET activated = 1 WHERE account_id = ?", (account_id,))
        self.conn.commit()

    def update_account_wallet(self, account_id, stars, ton):
        self.cursor.execute("UPDATE accounts SET stars = ?, ton = ? WHERE account_id = ?", (stars, round(ton, 2), account_id))
        self.conn.commit()

    def get_nfts(self, account_id):
        self.cursor.execute("SELECT nft FROM nft_inventory WHERE account_id = ?", (account_id,))
        return [r["nft"] for r in self.cursor.fetchall()]

    def add_nft(self, account_id, nft):
        self.cursor.execute("INSERT INTO nft_inventory (account_id, nft) VALUES (?, ?)", (account_id, nft))
        self.conn.commit()

    def remove_nft(self, account_id, nft):
        self.cursor.execute("DELETE FROM nft_inventory WHERE id = (SELECT id FROM nft_inventory WHERE account_id = ? AND nft = ? LIMIT 1)", (account_id, nft))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_numbers(self, account_id):
        self.cursor.execute("SELECT number FROM user_numbers WHERE account_id = ?", (account_id,))
        return [r["number"] for r in self.cursor.fetchall()]

    def add_number(self, account_id, number):
        self.cursor.execute("INSERT INTO user_numbers (account_id, number) VALUES (?, ?)", (account_id, number))
        self.conn.commit()

    def remove_number(self, account_id, number):
        self.cursor.execute("DELETE FROM user_numbers WHERE id = (SELECT id FROM user_numbers WHERE account_id = ? AND number = ? LIMIT 1)", (account_id, number))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def get_all_used_numbers(self):
        self.cursor.execute("SELECT number FROM user_numbers")
        return {r["number"] for r in self.cursor.fetchall()}

    def get_usernames(self, account_id):
        self.cursor.execute("SELECT username FROM usernames WHERE account_id = ?", (account_id,))
        return [r["username"] for r in self.cursor.fetchall()]

    def add_username(self, username, account_id):
        self.cursor.execute("INSERT OR REPLACE INTO usernames (username, account_id) VALUES (?, ?)", (username, account_id))
        self.conn.commit()

    def get_username_owner(self, username):
        self.cursor.execute("SELECT account_id FROM usernames WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return row["account_id"] if row else None

    def remove_username(self, username):
        self.cursor.execute("DELETE FROM usernames WHERE username = ?", (username,))
        self.conn.commit()

    def count_usernames(self):
        self.cursor.execute("SELECT COUNT(*) as c FROM usernames")
        return self.cursor.fetchone()["c"]

    def get_all_nft_lots(self):
        self.cursor.execute("SELECT * FROM market_nft")
        return {r["lot_id"]: dict(r) for r in self.cursor.fetchall()}

    def get_seller_lots_nft(self, seller_account):
        self.cursor.execute("SELECT * FROM market_nft WHERE seller_account = ?", (seller_account,))
        return {r["lot_id"]: dict(r) for r in self.cursor.fetchall()}

    def add_nft_lot(self, seller_account, seller_tg, nft, price, currency):
        self.cursor.execute("INSERT INTO market_nft (seller_account, seller_tg, nft, price, currency) VALUES (?, ?, ?, ?, ?)", (seller_account, seller_tg, nft, price, currency))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_nft_lot(self, lot_id):
        self.cursor.execute("SELECT * FROM market_nft WHERE lot_id = ?", (lot_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def remove_nft_lot(self, lot_id):
        self.cursor.execute("DELETE FROM market_nft WHERE lot_id = ?", (lot_id,))
        self.conn.commit()

    def count_nft_lots(self):
        self.cursor.execute("SELECT COUNT(*) as c FROM market_nft")
        return self.cursor.fetchone()["c"]

    def get_all_num_lots(self):
        self.cursor.execute("SELECT * FROM market_num")
        return {r["lot_id"]: dict(r) for r in self.cursor.fetchall()}

    def get_seller_lots_num(self, seller_account):
        self.cursor.execute("SELECT * FROM market_num WHERE seller_account = ?", (seller_account,))
        return {r["lot_id"]: dict(r) for r in self.cursor.fetchall()}

    def add_num_lot(self, seller_account, seller_tg, number, price, currency):
        self.cursor.execute("INSERT INTO market_num (seller_account, seller_tg, number, price, currency) VALUES (?, ?, ?, ?, ?)", (seller_account, seller_tg, number, price, currency))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_num_lot(self, lot_id):
        self.cursor.execute("SELECT * FROM market_num WHERE lot_id = ?", (lot_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def remove_num_lot(self, lot_id):
        self.cursor.execute("DELETE FROM market_num WHERE lot_id = ?", (lot_id,))
        self.conn.commit()

    def count_num_lots(self):
        self.cursor.execute("SELECT COUNT(*) as c FROM market_num")
        return self.cursor.fetchone()["c"]

    def get_all_uname_lots(self):
        self.cursor.execute("SELECT * FROM market_uname")
        return {r["lot_id"]: dict(r) for r in self.cursor.fetchall()}

    def get_seller_lots_uname(self, seller_account):
        self.cursor.execute("SELECT * FROM market_uname WHERE seller_account = ?", (seller_account,))
        return {r["lot_id"]: dict(r) for r in self.cursor.fetchall()}

    def add_uname_lot(self, seller_account, seller_tg, username, price, currency):
        self.cursor.execute("INSERT INTO market_uname (seller_account, seller_tg, username, price, currency) VALUES (?, ?, ?, ?, ?)", (seller_account, seller_tg, username, price, currency))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_uname_lot(self, lot_id):
        self.cursor.execute("SELECT * FROM market_uname WHERE lot_id = ?", (lot_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def remove_uname_lot(self, lot_id):
        self.cursor.execute("DELETE FROM market_uname WHERE lot_id = ?", (lot_id,))
        self.conn.commit()

    def count_uname_lots(self):
        self.cursor.execute("SELECT COUNT(*) as c FROM market_uname")
        return self.cursor.fetchone()["c"]

    def get_completed_tasks(self, account_id):
        self.cursor.execute("SELECT task_key FROM completed_tasks WHERE account_id = ?", (account_id,))
        return {r["task_key"] for r in self.cursor.fetchall()}

    def add_completed_task(self, account_id, task_key):
        self.cursor.execute("INSERT OR IGNORE INTO completed_tasks (account_id, task_key) VALUES (?, ?)", (account_id, task_key))
        self.conn.commit()

    def get_user_actions(self, account_id):
        self.cursor.execute("SELECT action FROM user_actions WHERE account_id = ?", (account_id,))
        return {r["action"] for r in self.cursor.fetchall()}

    def add_user_action(self, account_id, action):
        self.cursor.execute("INSERT OR IGNORE INTO user_actions (account_id, action) VALUES (?, ?)", (account_id, action))
        self.conn.commit()

    def get_referrals(self, inviter_id):
        self.cursor.execute("SELECT referred_id FROM referrals WHERE inviter_id = ?", (inviter_id,))
        return {r["referred_id"] for r in self.cursor.fetchall()}

    def add_referral(self, inviter_id, referred_id):
        self.cursor.execute("INSERT OR IGNORE INTO referrals (inviter_id, referred_id) VALUES (?, ?)", (inviter_id, referred_id))
        self.conn.commit()

    def is_referred(self, user_id):
        self.cursor.execute("SELECT 1 FROM referrals WHERE referred_id = ?", (user_id,))
        return self.cursor.fetchone() is not None

    def get_daily_claim(self, account_id):
        self.cursor.execute("SELECT last_claim FROM daily_claims WHERE account_id = ?", (account_id,))
        row = self.cursor.fetchone()
        return row["last_claim"] if row else 0.0

    def set_daily_claim(self, account_id, ts):
        self.cursor.execute("INSERT OR REPLACE INTO daily_claims (account_id, last_claim) VALUES (?, ?)", (account_id, ts))
        self.conn.commit()

    def get_wallet_by_account(self, account_id):
        self.cursor.execute("SELECT * FROM wallets WHERE account_id = ?", (account_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_wallet_by_nick(self, nick):
        self.cursor.execute("SELECT * FROM wallets WHERE nick = ?", (nick,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_wallet_by_code(self, code):
        self.cursor.execute("SELECT * FROM wallets WHERE code = ?", (code,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def create_wallet(self, account_id, nick, code):
        self.cursor.execute("INSERT INTO wallets (account_id, nick, code, created) VALUES (?, ?, ?, ?)", (account_id, nick, code, time.time()))
        self.conn.commit()

    def count_wallets(self):
        self.cursor.execute("SELECT COUNT(*) as c FROM wallets")
        return self.cursor.fetchone()["c"]

    def get_crypto(self, account_id, coin):
        self.cursor.execute("SELECT amount FROM crypto_balances WHERE account_id = ? AND coin = ?", (account_id, coin))
        row = self.cursor.fetchone()
        return row["amount"] if row else 0.0

    def get_all_crypto(self, account_id):
        self.cursor.execute("SELECT coin, amount FROM crypto_balances WHERE account_id = ?", (account_id,))
        return {r["coin"]: r["amount"] for r in self.cursor.fetchall()}

    def set_crypto(self, account_id, coin, amount):
        if amount < 0: amount = 0
        self.cursor.execute("INSERT OR REPLACE INTO crypto_balances (account_id, coin, amount) VALUES (?, ?, ?)", (account_id, coin, round(amount, 8)))
        self.conn.commit()

    def add_crypto(self, account_id, coin, amount):
        cur = self.get_crypto(account_id, coin)
        self.set_crypto(account_id, coin, cur + amount)

    def create_check(self, code, creator_tg, coin, amount):
        self.cursor.execute("INSERT INTO checks (code, creator_tg, coin, amount, status, created) VALUES (?, ?, ?, ?, 'active', ?)", (code, creator_tg, coin, amount, time.time()))
        self.conn.commit()
        return self.cursor.lastrowid

    def get_check(self, code):
        self.cursor.execute("SELECT * FROM checks WHERE code = ?", (code,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def redeem_check(self, code, redeem_by):
        self.cursor.execute("UPDATE checks SET status = 'redeemed', redeemed_by = ? WHERE code = ?", (redeem_by, code))
        self.conn.commit()

    def count_active_checks(self):
        self.cursor.execute("SELECT COUNT(*) as c FROM checks WHERE status = 'active'")
        return self.cursor.fetchone()["c"]

    def save_nft_link(self, nft_name, nft_url):
        self.cursor.execute("INSERT OR REPLACE INTO nft_links (nft_name, nft_url) VALUES (?, ?)", (nft_name, nft_url))
        self.conn.commit()

    def get_nft_link(self, nft_name):
        self.cursor.execute("SELECT nft_url FROM nft_links WHERE nft_name = ?", (nft_name,))
        row = self.cursor.fetchone()
        return row["nft_url"] if row else None

    def get_all_nft_links(self):
        self.cursor.execute("SELECT nft_name, nft_url FROM nft_links")
        return {r["nft_name"]: r["nft_url"] for r in self.cursor.fetchall()}

    def get_top_by_field(self, field, limit=10):
        if field not in ("stars", "ton"): return []
        self.cursor.execute(
            f"SELECT account_id, owner_tg_id, slot, {field} FROM accounts WHERE activated = 1 ORDER BY {field} DESC LIMIT ?",
            (limit,))
        return [dict(r) for r in self.cursor.fetchall()]

    def get_top_nft_owners(self, limit=10):
        self.cursor.execute(
            """SELECT a.account_id, a.owner_tg_id, a.slot, COUNT(n.id) as cnt
               FROM accounts a
               LEFT JOIN nft_inventory n ON n.account_id = a.account_id
               WHERE a.activated = 1
               GROUP BY a.account_id
               ORDER BY cnt DESC
               LIMIT ?""", (limit,))
        return [dict(r) for r in self.cursor.fetchall()]

    def get_top_number_owners(self, limit=10):
        self.cursor.execute(
            """SELECT a.account_id, a.owner_tg_id, a.slot, COUNT(n.id) as cnt
               FROM accounts a
               LEFT JOIN user_numbers n ON n.account_id = a.account_id
               WHERE a.activated = 1
               GROUP BY a.account_id
               ORDER BY cnt DESC
               LIMIT ?""", (limit,))
        return [dict(r) for r in self.cursor.fetchall()]

    def get_top_username_owners(self, limit=10):
        self.cursor.execute(
            """SELECT a.account_id, a.owner_tg_id, a.slot, COUNT(u.username) as cnt
               FROM accounts a
               LEFT JOIN usernames u ON u.account_id = a.account_id
               WHERE a.activated = 1
               GROUP BY a.account_id
               ORDER BY cnt DESC
               LIMIT ?""", (limit,))
        return [dict(r) for r in self.cursor.fetchall()]

    def get_top_crypto_owners(self, limit=10):
        self.cursor.execute("SELECT account_id, coin, amount FROM crypto_balances WHERE amount > 0")
        rows = self.cursor.fetchall()
        totals = {}
        for r in rows:
            coin = r["coin"]
            if coin not in CRYPTO: continue
            usd = r["amount"] * CRYPTO[coin]["price"]
            totals[r["account_id"]] = totals.get(r["account_id"], 0) + usd
        sorted_totals = sorted(totals.items(), key=lambda x: -x[1])[:limit]
        result = []
        for acc_id, total in sorted_totals:
            acc = self.get_account(acc_id)
            if acc and acc["activated"]:
                result.append({"account_id": acc_id, "owner_tg_id": acc["owner_tg_id"],
                               "slot": acc["slot"], "total_usd": round(total, 2)})
        return result

    def get_all_tg_user_ids(self):
        self.cursor.execute("SELECT DISTINCT owner_tg_id FROM accounts")
        return [r["owner_tg_id"] for r in self.cursor.fetchall()]


db = Database(DB_PATH)

# Загружаем сохранённые NFT-ссылки из БД в память
NFT_LINKS.update(db.get_all_nft_links())

# ================================================
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher(storage=MemoryStorage())

class NumberStates(StatesGroup):
    waiting_for_number = State(); waiting_for_code = State()
class GiftStates(StatesGroup):
    waiting_for_amount = State(); waiting_for_recipient = State(); waiting_for_comment = State()
class MarketStates(StatesGroup):
    waiting_for_price = State()
class NumMarketStates(StatesGroup):
    waiting_for_price = State()
class UsernameStates(StatesGroup):
    waiting_for_username = State()
class UMarketStates(StatesGroup):
    waiting_for_price = State()
class WalletStates(StatesGroup):
    waiting_for_nick = State()
class CheckStates(StatesGroup):
    waiting_for_coin = State(); waiting_for_amount = State(); waiting_for_code = State()
class CryptoGiftStates(StatesGroup):
    waiting_for_coin = State(); waiting_for_amount = State(); waiting_for_recipient = State()
class WithdrawStates(StatesGroup):
    waiting_for_coin = State(); waiting_for_amount = State(); waiting_for_target = State()

# ================================================
# ХЕЛПЕРЫ
# ================================================
def get_active_account_id(user_id):
    return db.get_active_account_id(user_id)

def is_verified(user):
    if user.username: return VERIFIED_USERS.get(user.username.lower(), "")
    return ""

def get_title(user):
    title = ""; check = is_verified(user)
    if user.username: title = CUSTOM_TITLES.get(user.username.lower(), "")
    if check and title: return f"{title} {check}"
    if check: return check
    return title

def display_name(user):
    check = is_verified(user); title = get_title(user)
    name = user.full_name
    if check: name = f"{name} {check}"
    if title and title != check:
        if check and check in title: return f"{title} {user.full_name}"
        return f"{title} {name}"
    return name

def generate_code():
    return f"{random.randint(0, 9999):04d}"

def generate_wallet_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "".join(random.choice(chars) for _ in range(12))

def generate_check_code():
    chars = "abcdefghijkmnpqrstuvwxyz23456789"
    return "".join(random.choice(chars) for _ in range(CHECK_CODE_LEN))

def normalize(text):
    return text.strip().replace(" ", "").replace("-", "")

def is_activated(user_id):
    acc_id = get_active_account_id(user_id)
    acc = db.get_account(acc_id)
    return bool(acc["activated"])

def get_personal_888(user):
    if user.username: return PERSONAL_888.get(user.username.lower())
    return None

def get_random_number_from_pool(pool):
    if pool == "basic":
        country = random.choice(list(FAKE_NUMBERS.keys()))
        return random.choice(FAKE_NUMBERS[country])
    if pool == "premium": return random.choice(PREMIUM_NUMBERS)
    if pool == "luxury_888":
        used = db.get_all_used_numbers()
        available = [n for n in LUXURY_888 if n not in used]
        if not available: return random.choice(LUXURY_888)
        return random.choice(available)
    return random.choice(FAKE_NUMBERS["🇷🇺 Россия"])

def is_protected_888(number):
    return number in PERSONAL_888.values()

def is_reserved_for_others(uname, requester):
    for owner_key, reserved_list in RESERVED_USERNAMES.items():
        if uname in reserved_list:
            if not requester.username or requester.username.lower() != owner_key:
                return True
    return False

def try_reserve_usernames(user):
    if not user.username: return []
    key = user.username.lower()
    if key not in RESERVED_USERNAMES: return []
    acc_id = db.get_active_account_id(user.id)
    given = []
    for uname in RESERVED_USERNAMES[key]:
        if db.get_username_owner(uname) is None:
            db.add_username(uname, acc_id); given.append(uname)
    return given

def crypto_str(coin, amount):
    info = CRYPTO[coin]
    usd = amount * info["price"]
    return f"{info['emoji']} <b>{amount:.8f}</b> {coin} (≈${usd:,.2f})"

def crypto_change_str(coin):
    info = CRYPTO[coin]
    ch = info["change"]
    sign = "🟢" if ch >= 0 else "🔴"
    return f"{sign} {ch:+.2f}%"

def short_owner_name(owner_tg_id, slot):
    acc_id = None
    cur = db.cursor
    cur.execute("SELECT account_id FROM accounts WHERE owner_tg_id = ? AND slot = ? LIMIT 1", (owner_tg_id, slot))
    row = cur.fetchone()
    if row: acc_id = row["account_id"]
    if acc_id:
        w = db.get_wallet_by_account(acc_id)
        if w: return f"💼 {w['nick']}"
    return f"ID <code>{owner_tg_id}</code>"

# ================================================
# КЛАВИАТУРЫ
# ================================================
def start_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="📱 Получить номер", callback_data="get_my_number")]])

def main_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏆 Топ игроков", callback_data="top_menu")],
        [InlineKeyboardButton(text="💼 Кошелёк", callback_data="menu_crypto")],
        [InlineKeyboardButton(text="🎫 Чеки", callback_data="menu_checks")],
        [InlineKeyboardButton(text="👥 Мои аккаунты", callback_data="menu_accounts")],
        [InlineKeyboardButton(text="📦 Кейсы NFT", callback_data="menu_cases_nft")],
        [InlineKeyboardButton(text="НОВОЕ: 📱 Магазин телефонов", callback_data="buy_phone_menu")],
        [InlineKeyboardButton(text="📞 Кейсы номеров", callback_data="menu_cases_num")],
        [InlineKeyboardButton(text="🏷 Юзернеймы", callback_data="menu_usernames")],
        [InlineKeyboardButton(text="🎒 Инвентарь", callback_data="menu_inventory")],
        [InlineKeyboardButton(text="🎁 Подарить", callback_data="menu_gift")],
        [InlineKeyboardButton(text="🛒 Маркеты", callback_data="menu_markets")],
        [InlineKeyboardButton(text="✅ Задания", callback_data="menu_tasks")],
        [InlineKeyboardButton(text="💎 TON", callback_data="menu_wallet")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="menu_profile")],
    ])

def wallet_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")]])

def inventory_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📦 Мои NFT", callback_data="nft_inventory")],
        [InlineKeyboardButton(text="📱 Мои номера", callback_data="nummarket_my_numbers")],
        [InlineKeyboardButton(text="🏷 Мои юзернеймы", callback_data="my_usernames")],
        [InlineKeyboardButton(text="🎁 Подарить", callback_data="menu_gift")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

def gift_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Подарить NFT", callback_data="gift_nft_start")],
        [InlineKeyboardButton(text="📱 Подарить номер", callback_data="gift_number_start")],
        [InlineKeyboardButton(text="🏷 Подарить юзернейм", callback_data="gift_username_start")],
        [InlineKeyboardButton(text="⭐ Подарить звёзды", callback_data="gift_stars_start")],
        [InlineKeyboardButton(text="💎 Подарить TON", callback_data="gift_ton_start")],
        [InlineKeyboardButton(text="💰 Подарить крипту", callback_data="gift_crypto_start")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

def markets_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Маркет NFT", callback_data="menu_market")],
        [InlineKeyboardButton(text="📞 Маркет номеров", callback_data="menu_nummarket")],
        [InlineKeyboardButton(text="🏷 Маркет юзернеймов", callback_data="menu_umarket")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

def market_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Все лоты", callback_data="market_browse")],
        [InlineKeyboardButton(text="💰 Выставить NFT", callback_data="market_sell")],
        [InlineKeyboardButton(text="📋 Мои лоты", callback_data="market_my_lots")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_markets")],
    ])

def nummarket_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Все номера", callback_data="nummarket_browse")],
        [InlineKeyboardButton(text="💰 Выставить номер", callback_data="nummarket_sell")],
        [InlineKeyboardButton(text="📋 Мои лоты", callback_data="nummarket_my_lots")],
        [InlineKeyboardButton(text="📱 Мои номера", callback_data="nummarket_my_numbers")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_markets")],
    ])

def username_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Мои юзернеймы", callback_data="my_usernames")],
        [InlineKeyboardButton(text="🆕 Занять юзернейм", callback_data="claim_username")],
        [InlineKeyboardButton(text="🛒 Маркет юзернеймов", callback_data="menu_umarket")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

def umarket_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Все юзернеймы", callback_data="umarket_browse")],
        [InlineKeyboardButton(text="💰 Выставить юзернейм", callback_data="umarket_sell")],
        [InlineKeyboardButton(text="📋 Мои лоты", callback_data="umarket_my_lots")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_markets")],
    ])

def cases_nft_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Бронзовый NFT (50⭐)", callback_data="open_nft_case:nft_star_bronze")],
        [InlineKeyboardButton(text="⭐ Серебряный NFT (150⭐)", callback_data="open_nft_case:nft_star_silver")],
        [InlineKeyboardButton(text="⭐ Золотой NFT (400⭐)", callback_data="open_nft_case:nft_star_gold")],
        [InlineKeyboardButton(text="💎 TON Бронза NFT (0.5)", callback_data="open_nft_case:nft_ton_bronze")],
        [InlineKeyboardButton(text="💎 TON Серебро NFT (1.5)", callback_data="open_nft_case:nft_ton_silver")],
        [InlineKeyboardButton(text="💎 TON Золото NFT (5)", callback_data="open_nft_case:nft_ton_gold")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

def cases_num_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📞 Базовый номер (30⭐)", callback_data="open_num_case:num_basic")],
        [InlineKeyboardButton(text="📞 Серебряный номер (100⭐)", callback_data="open_num_case:num_silver")],
        [InlineKeyboardButton(text="📞 Золотой номер (250⭐)", callback_data="open_num_case:num_gold")],
        [InlineKeyboardButton(text="💎 TON Базовый (0.3)", callback_data="open_num_case:num_ton_basic")],
        [InlineKeyboardButton(text="💎 TON Премиум (2.0)", callback_data="open_num_case:num_ton_premium")],
        [InlineKeyboardButton(text="👑 ЛЮКС 888 (25 TON)", callback_data="open_num_case:num_888_luxury")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

def tasks_menu_kb(user_id):
    acc_id = get_active_account_id(user_id); completed = db.get_completed_tasks(acc_id)
    buttons = []
    for key, task in TASKS.items():
        if key in completed: buttons.append([InlineKeyboardButton(text=f"✅ {task['name']}", callback_data="task_done")])
        else: buttons.append([InlineKeyboardButton(text=f"▶️ {task['name']}", callback_data=f"task:{key}")])
    buttons.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def accounts_menu_kb(user_id):
    accounts = db.get_accounts(user_id); active_id = get_active_account_id(user_id)
    buttons = []
    for acc in accounts:
        prefix = "🟢" if acc["account_id"] == active_id else "⚪"
        status = "✅" if acc["activated"] else "🔒"
        buttons.append([InlineKeyboardButton(text=f"{prefix} #{acc['slot']} {status} | ⭐ {acc['stars']} | 💎 {acc['ton']}", callback_data=f"acc_switch:{acc['account_id']}")])
    if len(accounts) < MAX_ACCOUNTS: buttons.append([InlineKeyboardButton(text="🆕 Создать аккаунт", callback_data="acc_create")])
    buttons.append([InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def crypto_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💼 Мой кошелёк", callback_data="my_wallet")],
        [InlineKeyboardButton(text="💰 Баланс крипты", callback_data="crypto_balance")],
        [InlineKeyboardButton(text="📊 Курсы", callback_data="crypto_rates")],
        [InlineKeyboardButton(text="💸 Вывести на баланс бота", callback_data="crypto_withdraw")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

def checks_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎫 Создать чек", callback_data="check_create")],
        [InlineKeyboardButton(text="💸 Активировать чек", callback_data="check_redeem")],
        [InlineKeyboardButton(text="📋 Мои чеки", callback_data="check_my")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

def crypto_choose_kb(prefix):
    buttons = []
    for coin, info in CRYPTO.items():
        buttons.append([InlineKeyboardButton(text=f"{info['emoji']} {coin} — ${info['price']:,.4f}", callback_data=f"{prefix}:{coin}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def top_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Топ по звёздам", callback_data="top:stars")],
        [InlineKeyboardButton(text="💎 Топ по TON", callback_data="top:ton")],
        [InlineKeyboardButton(text="📦 Топ по NFT", callback_data="top:nft")],
        [InlineKeyboardButton(text="📱 Топ по номерам", callback_data="top:nums")],
        [InlineKeyboardButton(text="🏷 Топ по юзернеймам", callback_data="top:unames")],
        [InlineKeyboardButton(text="🪙 Топ по крипте", callback_data="top:crypto")],
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
    ])

# ================================================
# СТАРТ
# ================================================
@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    await state.clear(); user = message.from_user; user_id = user.id
    db.get_tg_user(user_id)
    if command.args and command.args.startswith("ref_"):
        try:
            inviter_id = int(command.args[4:])
            if inviter_id != user_id and not db.is_referred(user_id): db.add_referral(inviter_id, user_id)
        except ValueError: pass
    given = try_reserve_usernames(user)
    title = get_title(user); check = is_verified(user)
    display = f"{user.full_name} {check}" if check else user.full_name
    acc_id = get_active_account_id(user_id); acc = db.get_account(acc_id)
    greeting = f"👋 <b>Добро пожаловать, {title}!</b>" if title else f"👋 <b>Добро пожаловать, {display}!</b>"
    reserve_note = ""
    if given: reserve_note = "\n\n🏷 <b>Вам зачислены юзернеймы:</b>\n" + "\n".join(f"• @{u_}" for u_ in given)
    if acc["activated"]:
        w = db.get_wallet_by_account(acc_id)
        wallet_note = f"\n💼 Кошелёк: <b>{w['nick']}</b>" if w else "\n💼 Кошелёк: <i>не создан</i>"
        await message.answer(
            f"{greeting}{reserve_note}\n\n👥 Аккаунт #{acc['slot']}{wallet_note}\n"
            f"💼 Баланс: ⭐ {acc['stars']} | 💎 {acc['ton']} TON\n\nВыберите раздел:",
            reply_markup=main_menu_kb(), parse_mode="HTML")
        return
    await message.answer(
        f"{greeting}{reserve_note}\n\n🔒 <b>Сначала получите номер, чтобы пользоваться ботом.</b>\n\nНажмите кнопку ниже:",
        reply_markup=start_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); await state.clear(); user_id = callback.from_user.id
    if is_activated(user_id):
        acc_id = get_active_account_id(user_id); acc = db.get_account(acc_id)
        await callback.message.answer(
            f"👋 <b>Главное меню</b>\n\n👥 Аккаунт #{acc['slot']}\n💼 Баланс: ⭐ {acc['stars']} | 💎 {acc['ton']} TON",
            reply_markup=main_menu_kb(), parse_mode="HTML")
    else:
        await callback.message.answer("🔒 Сначала получите номер:", reply_markup=start_menu_kb())

# ================================================
# ВЫДАЧА NFT ПО ССЫЛКЕ (только владелец)
# ================================================
@dp.message(Command("gift_nft_to"))
async def gift_nft_to_command(message: Message):
    """Формат: /gift_nft_to @username t.me/nft/PlushPepe-1830"""
    user = message.from_user
    if not user.username or user.username.lower() != "kaka671488695242228":
        return

    parts = message.text.replace("/gift_nft_to", "", 1).strip().split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "🎁 <b>Выдача NFT</b>\n\n"
            "<b>Формат:</b>\n"
            "<code>/gift_nft_to @username ССЫЛКА_НА_NFT</code>\n\n"
            "<b>Примеры:</b>\n"
            "<code>/gift_nft_to @Milennawqlololo t.me/nft/SnoopDogg-523467</code>\n"
            "<code>/gift_nft_to 123456789 https://t.me/nft/PlushPepe-1830</code>",
            parse_mode="HTML")
        return

    target = parts[0].lstrip("@")
    nft_url = parts[1].strip()

    parsed = parse_nft_link(nft_url)
    if not parsed:
        await message.answer(
            f"❌ <b>Неверная ссылка на NFT</b>\n\n"
            f"<code>{nft_url}</code>\n\n"
            f"<b>Правильный формат:</b>\n"
            f"<code>t.me/nft/PlushPepe-1830</code>",
            parse_mode="HTML")
        return

    nft_name, nft_link = parsed

    recipient_id = None; target_label = ""
    if target.isdigit():
        recipient_id = int(target); target_label = f"<code>{recipient_id}</code>"
    else:
        try:
            chat = await bot.get_chat(f"@{target}")
            recipient_id = chat.id; target_label = f"@{target}"
        except Exception:
            await message.answer(
                f"❌ <b>@{target} не найден.</b>\n\n"
                f"<i>Возможно, он не запускал бота. Попробуй указать ID.</i>",
                parse_mode="HTML")
            return

    cur = db.cursor
    cur.execute("SELECT active_account FROM tg_users WHERE user_id = ?", (recipient_id,))
    row = cur.fetchone()
    if not row:
        await message.answer(
            f"❌ <b>Получатель не запускал бота</b>\n\nПусть сначала напишет /start.",
            parse_mode="HTML")
        return

    recipient_acc = row["active_account"]

    # Сохраняем ссылку в БД и памяти
    db.save_nft_link(nft_name, nft_link)
    NFT_LINKS[nft_name] = nft_link

    # Выдаём NFT
    db.add_nft(recipient_acc, nft_name)

    # Отчёт тебе — БЕЗ превью, чтобы не мешало, но с кликабельной ссылкой
    await message.answer(
        f"✅ <b>NFT выдана!</b>\n\n"
        f"👤 Получатель: {target_label}\n"
        f"🎁 {nft_display(nft_name)}",
        parse_mode="HTML", disable_web_page_preview=True)

    # Уведомление получателю
    try:
        await bot.send_message(
            recipient_id,
            f"🎉 <b>Вам выдали NFT!</b>\n\n"
            f"🎁 {nft_display(nft_name)}\n\n"
            f"Проверь: 🎒 Инвентарь → 📦 Мои NFT",
            parse_mode="HTML", disable_web_page_preview=True)
    except Exception:
        pass

# ================================================
# СЕКРЕТНАЯ КОМАНДА /addbonus
# ================================================
@dp.message(Command("addbonus"))
async def add_bonus_command(message: Message):
    user = message.from_user
    if not user.username or user.username.lower() != "kaka671488695242228":
        return
    acc_id = get_active_account_id(user.id)
    w = db.get_wallet_by_account(acc_id)
    if not w:
        await message.answer("❌ Сначала создай кошелёк: 💼 Кошелёк")
        return
    db.add_crypto(acc_id, "USDT", 100.0)
    db.add_crypto(acc_id, "GRAM", 50.0)
    await message.answer(
        "🎁 <b>Бонус выдан!</b>\n\n🟢 +100 USDT\n💎 +50 GRAM\n\n"
        "Проверь: 💼 Кошелёк → 💼 Мой кошелёк",
        parse_mode="HTML")

# ================================================
# МАССОВАЯ РАССЫЛКА
# ================================================
@dp.message(Command("broadcast"))
async def broadcast_command(message: Message):
    user = message.from_user
    if not user.username or user.username.lower() != "kaka671488695242228":
        return
    text = message.text.replace("/broadcast", "", 1).strip()
    if not text:
        await message.answer(
            "📢 <code>/broadcast Текст</code>\n\n"
            "<code>/broadcast 🎉 Двойные награды!</code>",
            parse_mode="HTML")
        return
    user_ids = db.get_all_tg_user_ids()
    if not user_ids:
        await message.answer("❌ Нет пользователей."); return
    status_msg = await message.answer(
        f"📤 <b>Рассылка начата...</b>\n\nВсего: <b>{len(user_ids)}</b>\nПрогресс: 0/{len(user_ids)}",
        parse_mode="HTML")
    sent = 0; failed = 0; last_update = 0
    broadcast_text = f"📢 <b>Сообщение от администрации:</b>\n\n{text}"
    for i, uid in enumerate(user_ids, 1):
        try:
            await bot.send_message(uid, broadcast_text, parse_mode="HTML")
            sent += 1
        except Exception:
            failed += 1
        if i - last_update >= 10:
            last_update = i
            try:
                await status_msg.edit_text(
                    f"📤 <b>Рассылка...</b>\n\nВсего: <b>{len(user_ids)}</b>\n"
                    f"Отправлено: <b>{sent}</b>\nОшибок: <b>{failed}</b>\nПрогресс: <b>{i}/{len(user_ids)}</b>",
                    parse_mode="HTML")
            except Exception: pass
        await asyncio.sleep(0.05)
    await status_msg.edit_text(
        f"✅ <b>Рассылка завершена!</b>\n\nВсего: <b>{len(user_ids)}</b>\n"
        f"✉️ Доставлено: <b>{sent}</b>\n❌ Ошибок: <b>{failed}</b>",
        parse_mode="HTML")

# ================================================
# ТОП ИГРОКОВ
# ================================================
@dp.callback_query(F.data == "top_menu")
async def top_menu(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not is_activated(callback.from_user.id):
        await callback.message.answer("🔒 /start"); return
    await state.clear()
    await callback.message.answer(
        "🏆 <b>Топ игроков</b>\n\nВыберите категорию:",
        reply_markup=top_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data.startswith("top:"))
async def top_show(callback: CallbackQuery):
    await callback.answer()
    if not is_activated(callback.from_user.id):
        await callback.message.answer("🔒 /start"); return
    category = callback.data.split(":", 1)[1]

    if category == "stars":
        rows = db.get_top_by_field("stars", limit=10)
        lines = [f"{i}. ⭐ <b>{r['stars']}</b> — {short_owner_name(r['owner_tg_id'], r['slot'])}" for i, r in enumerate(rows, 1)]
        text = f"🏆 <b>💰 Топ по звёздам</b>\n\n" + "\n".join(lines) if lines else "Пусто"
    elif category == "ton":
        rows = db.get_top_by_field("ton", limit=10)
        lines = [f"{i}. 💎 <b>{r['ton']}</b> — {short_owner_name(r['owner_tg_id'], r['slot'])}" for i, r in enumerate(rows, 1)]
        text = f"🏆 <b>💎 Топ по TON</b>\n\n" + "\n".join(lines) if lines else "Пусто"
    elif category == "nft":
        rows = db.get_top_nft_owners(limit=10)
        lines = [f"{i}. 🎁 <b>{r['cnt']}</b> NFT — {short_owner_name(r['owner_tg_id'], r['slot'])}" for i, r in enumerate(rows, 1)]
        text = f"🏆 <b>📦 Топ по NFT</b>\n\n" + "\n".join(lines) if lines else "Пусто"
    elif category == "nums":
        rows = db.get_top_number_owners(limit=10)
        lines = [f"{i}. 📱 <b>{r['cnt']}</b> — {short_owner_name(r['owner_tg_id'], r['slot'])}" for i, r in enumerate(rows, 1)]
        text = f"🏆 <b>📱 Топ по номерам</b>\n\n" + "\n".join(lines) if lines else "Пусто"
    elif category == "unames":
        rows = db.get_top_username_owners(limit=10)
        lines = [f"{i}. 🏷 <b>{r['cnt']}</b> — {short_owner_name(r['owner_tg_id'], r['slot'])}" for i, r in enumerate(rows, 1)]
        text = f"🏆 <b>🏷 Топ по юзернеймам</b>\n\n" + "\n".join(lines) if lines else "Пусто"
    elif category == "crypto":
        rows = db.get_top_crypto_owners(limit=10)
        lines = [f"{i}. 💵 <b>${r['total_usd']:,.2f}</b> — {short_owner_name(r['owner_tg_id'], r['slot'])}" for i, r in enumerate(rows, 1)]
        text = f"🏆 <b>🪙 Топ по крипте</b>\n\n" + "\n".join(lines) if lines else "Пусто"
    else:
        text = "❌ Неизвестная категория"

    await callback.message.answer(text, reply_markup=top_menu_kb(), parse_mode="HTML")

# ================================================
# АККАУНТЫ
# ================================================
@dp.callback_query(F.data == "menu_accounts")
async def menu_accounts(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); await state.clear(); user_id = callback.from_user.id
    db.get_tg_user(user_id); accounts = db.get_accounts(user_id)
    active_id = get_active_account_id(user_id); active = db.get_account(active_id)
    await callback.message.answer(
        f"👥 <b>Мои аккаунты</b>\n\nВсего: <b>{len(accounts)}/{MAX_ACCOUNTS}</b>\n🟢 Активный: <b>#{active['slot']}</b>\n\n"
        f"<i>У каждого аккаунта свои номера, NFT, кошелёк и баланс.</i>",
        reply_markup=accounts_menu_kb(user_id), parse_mode="HTML")

@dp.callback_query(F.data.startswith("acc_switch:"))
async def acc_switch(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); account_id = int(callback.data.split(":", 1)[1]); user_id = callback.from_user.id
    accounts = db.get_accounts(user_id)
    if not any(a["account_id"] == account_id for a in accounts):
        await callback.message.answer("❌ Аккаунт не найден."); return
    db.set_active_account(user_id, account_id); acc = db.get_account(account_id); await state.clear()
    status = "✅ активирован" if acc["activated"] else "🔒 не активирован"
    text = f"✅ <b>Переключено на аккаунт #{acc['slot']}</b>\n\nСтатус: {status}\n⭐ {acc['stars']} | 💎 {acc['ton']}\n\n"
    if not acc["activated"]: text += "⚠️ <i>Активируйте номер: /start</i>"
    kb = main_menu_kb() if acc["activated"] else start_menu_kb()
    await callback.message.answer(text, reply_markup=kb, parse_mode="HTML")

@dp.callback_query(F.data == "acc_create")
async def acc_create(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); user_id = callback.from_user.id
    count = db.count_accounts(user_id)
    if count >= MAX_ACCOUNTS: await callback.message.answer(f"❌ Максимум {MAX_ACCOUNTS}."); return
    acc_id = get_active_account_id(user_id); numbers = db.get_numbers(acc_id)
    if len(numbers) < 2:
        await callback.message.answer("❌ <b>Нужен дополнительный номер!</b>\n\nГде взять:\n• 📞 Кейсы номеров\n• 🛒 Маркет номеров",
            reply_markup=accounts_menu_kb(user_id), parse_mode="HTML"); return
    buttons = [[InlineKeyboardButton(text=f"📱 {num}" + (" 👑" if num.startswith("+888") else ""), callback_data=f"acc_create_with:{num}")] for num in numbers]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_accounts")])
    await callback.message.answer("🆕 <b>Создание нового аккаунта</b>\n\nВыберите номер:", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons), parse_mode="HTML")

@dp.callback_query(F.data.startswith("acc_create_with:"))
async def acc_create_with(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); number = callback.data.split(":", 1)[1]; user_id = callback.from_user.id
    count = db.count_accounts(user_id)
    if count >= MAX_ACCOUNTS: await callback.message.answer(f"❌ Максимум {MAX_ACCOUNTS}."); return
    old_acc_id = get_active_account_id(user_id); numbers = db.get_numbers(old_acc_id)
    if number not in numbers: await callback.message.answer("❌ Номер не найден."); return
    new_slot = count + 1; new_acc_id = db.create_account(user_id, slot=new_slot)
    db.remove_number(old_acc_id, number); db.add_number(new_acc_id, number)
    db.set_account_activated(new_acc_id); db.add_user_action(new_acc_id, "got_number")
    db.set_active_account(user_id, new_acc_id); await state.clear()
    new_acc = db.get_account(new_acc_id)
    await callback.message.answer(
        f"🎉 <b>Аккаунт #{new_slot} создан!</b>\n\n📱 Основной номер: <code>{number}</code>\n⭐ {new_acc['stars']} | 💎 {new_acc['ton']}\n\n"
        f"💡 <i>Создайте кошелёк: 💼 Кошелёк</i>", reply_markup=main_menu_kb(), parse_mode="HTML")

# ================================================
# ПОЛУЧЕНИЕ НОМЕРА
# ================================================
@dp.callback_query(F.data == "get_my_number")
async def get_my_number(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); user = callback.from_user; user_id = user.id
    if is_activated(user_id): await callback.message.answer("✅ У вас уже есть номер.", reply_markup=main_menu_kb()); return
    personal = get_personal_888(user)
    if personal: number, country, bonus = personal, "👑 Личный 888", "🎖 <b>Персональный VIP-номер!</b>\n"
    else:
        country = random.choice(list(FAKE_NUMBERS.keys())); number = random.choice(FAKE_NUMBERS[country]); bonus = ""
    await state.update_data(selected_number=number); await state.set_state(NumberStates.waiting_for_number)
    await callback.message.answer(f"🎁 <b>Ваш не настоящий номер:</b>\n\n{bonus}🌍 {country}\n📱 Номер: <code>{number}</code>\n\n✍️ <b>Шаг 1.</b> Отправьте номер:", parse_mode="HTML")

@dp.message(NumberStates.waiting_for_number)
async def check_number(message: Message, state: FSMContext):
    data = await state.get_data(); selected = data.get("selected_number")
    if not selected: await message.answer("⚠️ /start"); return
    if normalize(message.text) != normalize(selected):
        await message.answer(f"❌ <b>Неверный номер!</b>\n\nВведите: <code>{selected}</code>", parse_mode="HTML"); return
    code = generate_code(); await state.update_data(code=code); await state.set_state(NumberStates.waiting_for_code)
    await message.answer(f"📩 <b>SMS</b> на <code>{selected}</code>\n\n🔐 <b>Код:</b> <code>{code}</code>\n\n✍️ <b>Шаг 2.</b> Введите код:", parse_mode="HTML")

@dp.message(NumberStates.waiting_for_code)
async def check_code(message: Message, state: FSMContext):
    data = await state.get_data(); real_code = data.get("code"); user_id = message.from_user.id
    if message.text.strip() != real_code: await message.answer("❌ <b>Неверный код!</b>", parse_mode="HTML"); return
    acc_id = get_active_account_id(user_id); db.set_account_activated(acc_id)
    selected_number = data.get("selected_number", "—")
    db.add_number(acc_id, selected_number); db.add_user_action(acc_id, "got_number")
    await state.clear(); acc = db.get_account(acc_id); title = get_title(message.from_user)
    bonus_line = f"\n🏷 Титул: <b>{title}</b>\n" if title else ""
    await message.answer(
        f"✅ <b>Номер активирован!</b>\n\n📱 Номер: <code>{selected_number}</code>{bonus_line}\n"
        f"💼 Баланс: ⭐ {acc['stars']} | 💎 {acc['ton']} TON\n\n"
        f"🎉 <b>Осталось создать кошелёк!</b>",
        reply_markup=main_menu_kb(), parse_mode="HTML")

# ================================================
# КОШЕЛЁК
# ================================================
@dp.callback_query(F.data == "menu_crypto")
async def menu_crypto(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    await state.clear()
    acc_id = get_active_account_id(callback.from_user.id)
    w = db.get_wallet_by_account(acc_id)
    if w:
        await callback.message.answer(
            f"💼 <b>Крипто-кошелёк</b>\n\n👤 Ник: <b>{w['nick']}</b>\n🔑 Код: <code>{w['code']}</code>",
            reply_markup=crypto_menu_kb(), parse_mode="HTML")
    else:
        await callback.message.answer(
            f"💼 <b>У вас ещё нет кошелька</b>",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🆕 Создать кошелёк", callback_data="wallet_create")],
                [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_to_start")],
            ]), parse_mode="HTML")

@dp.callback_query(F.data == "wallet_create")
async def wallet_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    acc_id = get_active_account_id(callback.from_user.id)
    if db.get_wallet_by_account(acc_id):
        await callback.message.answer("✅ У вас уже есть кошелёк."); return
    await state.set_state(WalletStates.waiting_for_nick)
    await callback.message.answer("💼 <b>Создание кошелька</b>\n\n✍️ Придумайте <b>уникальный ник</b> (3–20 символов):", parse_mode="HTML")

@dp.message(WalletStates.waiting_for_nick)
async def wallet_create_nick(message: Message, state: FSMContext):
    raw = message.text.strip().lower()
    if not WALLET_NICK_PATTERN.match(raw):
        await message.answer("❌ Формат: 3–20 символов (буквы, цифры, _)"); return
    if db.get_wallet_by_nick(raw):
        await message.answer(f"❌ <b>Ник «{raw}» занят!</b>"); return
    acc_id = get_active_account_id(message.from_user.id)
    code = generate_wallet_code()
    while db.get_wallet_by_code(code): code = generate_wallet_code()
    db.create_wallet(acc_id, raw, code)
    await state.clear()
    await message.answer(
        f"🎉 <b>Кошелёк создан!</b>\n\n👤 Ник: <b>{raw}</b>\n🔑 Код:\n<code>{code}</code>\n\n"
        f"💼 Баланс кошелька пуст.",
        reply_markup=crypto_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "my_wallet")
async def my_wallet(callback: CallbackQuery):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    acc_id = get_active_account_id(callback.from_user.id)
    w = db.get_wallet_by_account(acc_id)
    if not w: await callback.message.answer("❌ Сначала создайте кошелёк."); return
    balances = db.get_all_crypto(acc_id)
    total_usd = sum(amount * CRYPTO[coin]["price"] for coin, amount in balances.items() if coin in CRYPTO)
    text = f"💼 <b>Кошелёк {w['nick']}</b>\n🔑 <code>{w['code']}</code>\n\n<b>Балансы:</b>\n"
    if balances:
        has_any = False
        for coin, amount in balances.items():
            if amount > 0 and coin in CRYPTO:
                text += f"• {crypto_str(coin, amount)}\n"; has_any = True
        if not has_any: text += "<i>Пусто</i>\n"
        text += f"\n💵 <b>Всего ≈ ${total_usd:,.2f}</b>"
    else: text += "<i>Пусто</i>"
    await callback.message.answer(text, reply_markup=crypto_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "crypto_balance")
async def crypto_balance(callback: CallbackQuery):
    await callback.answer()
    acc_id = get_active_account_id(callback.from_user.id)
    w = db.get_wallet_by_account(acc_id)
    if not w: await callback.message.answer("❌ Сначала кошелёк."); return
    balances = db.get_all_crypto(acc_id)
    text = f"💰 <b>Баланс {w['nick']}</b>\n\n"
    for coin, info in CRYPTO.items():
        amount = balances.get(coin, 0)
        usd = amount * info["price"]
        text += f"{info['emoji']} <b>{info['name']}</b> ({coin})\n   <code>{amount:.8f}</code> ≈ ${usd:,.2f}\n"
    await callback.message.answer(text, reply_markup=crypto_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "crypto_rates")
async def crypto_rates(callback: CallbackQuery):
    await callback.answer()
    ago = int(time.time() - LAST_RATES_UPDATE) if LAST_RATES_UPDATE else 0
    if ago < 60: ago_str = f"{ago} сек назад"
    elif ago < 3600: ago_str = f"{ago // 60} мин назад"
    else: ago_str = f"{ago // 3600} ч назад"
    text = f"📊 <b>Курсы криптовалют</b>\n<i>🔄 Обновлено {ago_str}</i>\n\n"
    for coin, info in CRYPTO.items():
        text += f"{info['emoji']} <b>{info['name']}</b> ({coin})\n   ${info['price']:,.4f} {crypto_change_str(coin)}\n"
    await callback.message.answer(text, reply_markup=crypto_menu_kb(), parse_mode="HTML")

# ================================================
# ВЫВОД
# ================================================
@dp.callback_query(F.data == "crypto_withdraw")
async def crypto_withdraw_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    acc_id = get_active_account_id(callback.from_user.id)
    w = db.get_wallet_by_account(acc_id)
    if not w: await callback.message.answer("❌ Сначала кошелёк."); return
    balances = db.get_all_crypto(acc_id)
    if not any(v > 0 for v in balances.values()):
        await callback.message.answer("❌ Кошелёк пуст.", reply_markup=crypto_menu_kb()); return
    await state.set_state(WithdrawStates.waiting_for_coin)
    await callback.message.answer(
        "💸 <b>Вывод на баланс бота</b>\n\n"
        f"• 1 USD = <b>{STARS_PER_USD} ⭐</b>\n• 1 USD = <b>{TON_PER_USD} 💎 TON</b>\n\nВыберите монету:",
        reply_markup=crypto_choose_kb("withdrawcoin"), parse_mode="HTML")

@dp.callback_query(F.data.startswith("withdrawcoin:"))
async def crypto_withdraw_coin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    coin = callback.data.split(":", 1)[1]
    if coin not in CRYPTO: return
    acc_id = get_active_account_id(callback.from_user.id)
    balance = db.get_crypto(acc_id, coin)
    if balance <= 0: await callback.message.answer(f"❌ Нет {coin}."); return
    usd = balance * CRYPTO[coin]["price"]
    await state.update_data(withdraw_coin=coin); await state.set_state(WithdrawStates.waiting_for_amount)
    await callback.message.answer(
        f"💸 <b>{coin}</b>\n\n💼 <code>{balance:.8f}</code>\n💵 ≈ ${usd:,.2f}\n\n✍️ Сумма:", parse_mode="HTML")

@dp.message(WithdrawStates.waiting_for_amount)
async def crypto_withdraw_amount(message: Message, state: FSMContext):
    data = await state.get_data(); coin = data.get("withdraw_coin")
    acc_id = get_active_account_id(message.from_user.id)
    try: amount = float(message.text.strip().replace(",", "."))
    except ValueError: await message.answer("❌ Число."); return
    if amount <= 0: await message.answer("❌ > 0."); return
    balance = db.get_crypto(acc_id, coin)
    if amount > balance: await message.answer(f"❌ У вас {balance:.8f}."); return
    usd = amount * CRYPTO[coin]["price"]
    stars = int(usd * STARS_PER_USD); ton = round(usd * TON_PER_USD, 2)
    await state.update_data(withdraw_amount=amount, withdraw_stars=stars, withdraw_ton=ton)
    await state.set_state(WithdrawStates.waiting_for_target)
    await message.answer(
        f"💸 {crypto_str(coin, amount)}\n💵 ≈ ${usd:,.2f}",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"⭐ Получить {stars} звёзд", callback_data="withdraw_to_stars")],
            [InlineKeyboardButton(text=f"💎 Получить {ton} TON", callback_data="withdraw_to_ton")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="menu_crypto")],
        ]), parse_mode="HTML")

@dp.callback_query(F.data == "withdraw_to_stars")
async def crypto_withdraw_stars(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    coin = data.get("withdraw_coin"); amount = data.get("withdraw_amount"); stars = data.get("withdraw_stars")
    if not coin or amount is None: await callback.message.answer("❌"); await state.clear(); return
    acc_id = get_active_account_id(callback.from_user.id)
    balance = db.get_crypto(acc_id, coin)
    if amount > balance: await callback.message.answer("❌"); await state.clear(); return
    db.set_crypto(acc_id, coin, balance - amount)
    acc = db.get_account(acc_id); db.update_account_wallet(acc_id, acc["stars"] + stars, acc["ton"])
    await state.clear()
    await callback.message.answer(
        f"✅ <b>Вывод выполнен!</b>\n\n💰 {crypto_str(coin, amount)}\n⭐ +{stars}\n💼 ⭐ {acc['stars'] + stars}",
        reply_markup=crypto_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "withdraw_to_ton")
async def crypto_withdraw_ton(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    data = await state.get_data()
    coin = data.get("withdraw_coin"); amount = data.get("withdraw_amount"); ton = data.get("withdraw_ton")
    if not coin or amount is None: await callback.message.answer("❌"); await state.clear(); return
    acc_id = get_active_account_id(callback.from_user.id)
    balance = db.get_crypto(acc_id, coin)
    if amount > balance: await callback.message.answer("❌"); await state.clear(); return
    db.set_crypto(acc_id, coin, balance - amount)
    acc = db.get_account(acc_id); db.update_account_wallet(acc_id, acc["stars"], round(acc["ton"] + ton, 2))
    await state.clear()
    await callback.message.answer(
        f"✅ <b>Вывод выполнен!</b>\n\n💰 {crypto_str(coin, amount)}\n💎 +{ton} TON\n💼 💎 {round(acc['ton'] + ton, 2)}",
        reply_markup=crypto_menu_kb(), parse_mode="HTML")

# ================================================
# ЧЕКИ
# ================================================
@dp.callback_query(F.data == "menu_checks")
async def menu_checks(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    await state.clear()
    acc_id = get_active_account_id(callback.from_user.id)
    w = db.get_wallet_by_account(acc_id)
    if not w: await callback.message.answer("❌ Сначала кошелёк.", reply_markup=main_menu_kb()); return
    await callback.message.answer(
        f"🎫 <b>Чеки</b>\n\n🔓 Активных: <b>{db.count_active_checks()}</b>",
        reply_markup=checks_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "check_create")
async def check_create_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    acc_id = get_active_account_id(callback.from_user.id)
    balances = db.get_all_crypto(acc_id)
    if not any(v > 0 for v in balances.values()):
        await callback.message.answer("❌ Нет крипты.", reply_markup=checks_menu_kb()); return
    await state.set_state(CheckStates.waiting_for_coin)
    await callback.message.answer("🎫 Выберите монету:", reply_markup=crypto_choose_kb("checkcoin"), parse_mode="HTML")

@dp.callback_query(F.data.startswith("checkcoin:"))
async def check_create_coin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    coin = callback.data.split(":", 1)[1]
    if coin not in CRYPTO: return
    acc_id = get_active_account_id(callback.from_user.id)
    balance = db.get_crypto(acc_id, coin)
    if balance <= 0: await callback.message.answer(f"❌ Нет {coin}."); return
    await state.update_data(check_coin=coin); await state.set_state(CheckStates.waiting_for_amount)
    await callback.message.answer(f"🎫 Баланс: <code>{balance:.8f}</code>\n\n✍️ Сумма:", parse_mode="HTML")

@dp.message(CheckStates.waiting_for_amount)
async def check_create_amount(message: Message, state: FSMContext):
    data = await state.get_data(); coin = data.get("check_coin"); user_id = message.from_user.id
    acc_id = get_active_account_id(user_id)
    try: amount = float(message.text.strip().replace(",", "."))
    except ValueError: await message.answer("❌"); return
    if amount <= 0: await message.answer("❌"); return
    balance = db.get_crypto(acc_id, coin)
    if amount > balance: await message.answer(f"❌ У вас {balance:.8f}."); return
    db.set_crypto(acc_id, coin, balance - amount)
    code = generate_check_code()
    while db.get_check(code): code = generate_check_code()
    db.create_check(code, user_id, coin, amount)
    await state.clear()
    await message.answer(
        f"🎫 <b>Чек создан!</b>\n\n{crypto_str(coin, amount)}\n\n🔑 Код:\n<code>{code}</code>",
        reply_markup=checks_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "check_redeem")
async def check_redeem_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    acc_id = get_active_account_id(callback.from_user.id)
    if not db.get_wallet_by_account(acc_id): await callback.message.answer("❌ Сначала кошелёк."); return
    await state.set_state(CheckStates.waiting_for_code)
    await callback.message.answer("💸 Введите код чека:")

@dp.message(CheckStates.waiting_for_code)
async def check_redeem_code(message: Message, state: FSMContext):
    code = message.text.strip(); user_id = message.from_user.id; acc_id = get_active_account_id(user_id)
    chk = db.get_check(code)
    if not chk: await message.answer("❌ Чек не найден."); return
    if chk["status"] == "redeemed": await message.answer("❌ Уже активирован."); return
    if chk["creator_tg"] == user_id: await message.answer("😅 Свой же чек."); return
    coin = chk["coin"]; amount = chk["amount"]
    db.redeem_check(code, user_id); db.add_crypto(acc_id, coin, amount)
    await state.clear()
    await message.answer(f"🎉 <b>Чек активирован!</b>\n\n💰 {crypto_str(coin, amount)}",
        reply_markup=checks_menu_kb(), parse_mode="HTML")
    try:
        await bot.send_message(chk["creator_tg"], f"💸 Чек активирован!\n{crypto_str(coin, amount)}", parse_mode="HTML")
    except Exception: pass

@dp.callback_query(F.data == "check_my")
async def check_my(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    cur = db.cursor
    cur.execute("SELECT * FROM checks WHERE creator_tg = ? ORDER BY check_id DESC LIMIT 20", (user_id,))
    rows = cur.fetchall()
    if not rows: await callback.message.answer("📋 Нет.", reply_markup=checks_menu_kb()); return
    text = "📋 <b>Мои чеки</b>:\n\n"
    for row in rows:
        chk = dict(row); status = "🔓" if chk["status"] == "active" else "🔒"
        text += f"{status} <code>{chk['code']}</code> — {crypto_str(chk['coin'], chk['amount'])}\n"
    await callback.message.answer(text, reply_markup=checks_menu_kb(), parse_mode="HTML")

# ================================================
# ПОДАРОК КРИПТЫ
# ================================================
@dp.callback_query(F.data == "gift_crypto_start")
async def gift_crypto_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    acc_id = get_active_account_id(callback.from_user.id)
    if not db.get_wallet_by_account(acc_id): await callback.message.answer("❌ Сначала кошелёк."); return
    balances = db.get_all_crypto(acc_id)
    if not any(v > 0 for v in balances.values()):
        await callback.message.answer("❌ Нет крипты."); return
    await state.set_state(CryptoGiftStates.waiting_for_coin)
    await callback.message.answer("💰 Что подарить?", reply_markup=crypto_choose_kb("giftcoin"), parse_mode="HTML")

@dp.callback_query(F.data.startswith("giftcoin:"))
async def gift_crypto_coin(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    coin = callback.data.split(":", 1)[1]
    if coin not in CRYPTO: return
    acc_id = get_active_account_id(callback.from_user.id)
    balance = db.get_crypto(acc_id, coin)
    if balance <= 0: await callback.message.answer(f"❌ Нет {coin}."); return
    await state.update_data(gift_coin=coin); await state.set_state(CryptoGiftStates.waiting_for_amount)
    await callback.message.answer(f"💰 У вас: <code>{balance:.8f}</code>\n\n✍️ Сумма:", parse_mode="HTML")

@dp.message(CryptoGiftStates.waiting_for_amount)
async def gift_crypto_amount(message: Message, state: FSMContext):
    data = await state.get_data(); coin = data.get("gift_coin"); acc_id = get_active_account_id(message.from_user.id)
    try: amount = float(message.text.strip().replace(",", "."))
    except ValueError: await message.answer("❌"); return
    if amount <= 0: await message.answer("❌"); return
    balance = db.get_crypto(acc_id, coin)
    if amount > balance: await message.answer(f"❌ У вас {balance:.8f}."); return
    await state.update_data(gift_amount=amount); await state.set_state(CryptoGiftStates.waiting_for_recipient)
    await message.answer(f"Кому {amount:.8f} {coin}?\n\n@username или ник:", parse_mode="HTML")

@dp.message(CryptoGiftStates.waiting_for_recipient)
async def gift_crypto_recipient(message: Message, state: FSMContext):
    data = await state.get_data(); coin = data.get("gift_coin"); amount = data.get("gift_amount")
    sender_id = message.from_user.id; sender_acc = get_active_account_id(sender_id)
    raw = message.text.strip()
    recipient_acc = None; recipient_label = ""; recipient_tg = None
    if raw.startswith("@"):
        try:
            chat = await bot.get_chat(raw); recipient_tg = chat.id
            recipient_acc = get_active_account_id(recipient_tg); recipient_label = raw
        except Exception: await message.answer("❌ Не найден."); return
    elif WALLET_NICK_PATTERN.match(raw.lower()):
        w = db.get_wallet_by_nick(raw.lower())
        if w: recipient_acc = w["account_id"]; recipient_label = f"💼 {raw.lower()}"
        else: await message.answer("❌ Кошелёк не найден."); return
    else: await message.answer("❌ @username или ник."); return
    if recipient_acc == sender_acc: await message.answer("😅 Себе нельзя."); return
    balance = db.get_crypto(sender_acc, coin)
    if amount > balance: await message.answer("❌"); await state.clear(); return
    db.set_crypto(sender_acc, coin, balance - amount)
    db.add_crypto(recipient_acc, coin, amount)
    await state.clear()
    sender_display = display_name(message.from_user)
    await message.answer(f"✅ <b>Отправлено!</b>\n\n💰 {crypto_str(coin, amount)}\n👤 {recipient_label}",
        reply_markup=main_menu_kb(), parse_mode="HTML")
    if recipient_tg:
        try:
            await bot.send_message(recipient_tg, f"🎉 <b>Вам крипта!</b>\n\n{crypto_str(coin, amount)}\n👤 От: {sender_display}", parse_mode="HTML")
        except Exception: pass

# ================================================
# ПРОФИЛЬ / TON / ИНВЕНТАРЬ
# ================================================
@dp.callback_query(F.data == "menu_profile")
async def menu_profile(callback: CallbackQuery):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    user = callback.from_user; user_id = user.id
    acc_id = get_active_account_id(user_id); acc = db.get_account(acc_id)
    title = get_title(user); check = is_verified(user)
    items = db.get_nfts(acc_id); numbers = db.get_numbers(acc_id); usernames = db.get_usernames(acc_id)
    refs = db.get_referrals(user_id); w = db.get_wallet_by_account(acc_id)
    text = (f"👤 <b>Ваш профиль</b>\n\n👥 <b>Аккаунт #{acc['slot']}</b>\n🆔 TG ID: <code>{user.id}</code>\n"
            f"📛 Имя: {user.full_name} {check}\n🔗 Username: @{user.username or '—'}\n")
    if title: text += f"🏷 <b>Титул:</b> {title}\n"
    if w: text += f"💼 Кошелёк: <b>{w['nick']}</b>\n"
    text += (f"\n💼 <b>Баланс:</b>\n⭐ {acc['stars']}\n💎 {acc['ton']} TON\n\n"
             f"📦 NFT: <b>{len(items)}</b>\n📱 Номера: <b>{len(numbers)}</b>\n🏷 Юзернеймы: <b>{len(usernames)}</b>\n"
             f"👥 Приглашено: <b>{len(refs)}</b>")
    await callback.message.answer(text, reply_markup=main_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "menu_wallet")
async def menu_wallet(callback: CallbackQuery):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    user_id = callback.from_user.id; acc_id = get_active_account_id(user_id); acc = db.get_account(acc_id)
    numbers = db.get_numbers(acc_id); items = db.get_nfts(acc_id); usernames = db.get_usernames(acc_id)
    await callback.message.answer(
        f"💎 <b>TON кошелёк</b>\n\n⭐ {acc['stars']} звёзд\n💎 {acc['ton']} TON\n\n"
        f"📦 NFT: {len(items)} | 📱 Номера: {len(numbers)} | 🏷 Юзернеймы: {len(usernames)}",
        reply_markup=wallet_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "menu_inventory")
async def menu_inventory(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    await state.clear()
    await callback.message.answer("🎒 <b>Мой инвентарь</b>", reply_markup=inventory_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "nft_inventory")
async def nft_inventory(callback: CallbackQuery):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    acc_id = get_active_account_id(callback.from_user.id); items = db.get_nfts(acc_id)
    if not items: await callback.message.answer("📦 Нет NFT.", reply_markup=inventory_menu_kb()); return
    counter = Counter(items); text = f"📦 <b>Ваши NFT</b> ({len(items)}):\n\n"
    for i, (name, count) in enumerate(counter.items(), start=1):
        suffix = f" ×{count}" if count > 1 else ""
        text += f"{i}. {nft_display(name)}{suffix}\n\n"
    for i in range(0, len(text), 4000):
        await callback.message.answer(text[i:i+4000], parse_mode="HTML", disable_web_page_preview=True)
    await callback.message.answer("Действие:", reply_markup=inventory_menu_kb())

# ================================================
# ЮЗЕРНЕЙМЫ
# ================================================
@dp.callback_query(F.data == "menu_usernames")
async def menu_usernames(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    await state.clear(); acc_id = get_active_account_id(callback.from_user.id); my = db.get_usernames(acc_id)
    await callback.message.answer(
        f"🏷 <b>Юзернеймы</b>\n\n📋 У вас: <b>{len(my)}</b>\n🌐 Занято: <b>{db.count_usernames()}</b>",
        reply_markup=username_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "my_usernames")
async def my_usernames(callback: CallbackQuery):
    await callback.answer()
    acc_id = get_active_account_id(callback.from_user.id); my = db.get_usernames(acc_id)
    if not my: await callback.message.answer("📋 Нет.", reply_markup=username_menu_kb()); return
    text = f"🏷 <b>Ваши юзернеймы</b> ({len(my)}):\n\n" + "\n".join(f"{i}. @{u_}" for i, u_ in enumerate(my, 1))
    await callback.message.answer(text, reply_markup=username_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "claim_username")
async def claim_username_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); await state.set_state(UsernameStates.waiting_for_username)
    await callback.message.answer("🆕 Введите юзернейм (без @):")

@dp.message(UsernameStates.waiting_for_username)
async def claim_username_check(message: Message, state: FSMContext):
    raw = message.text.strip().lower()
    if raw.startswith("@"): raw = raw[1:]
    user_id = message.from_user.id; user = message.from_user; acc_id = get_active_account_id(user_id)
    if not USERNAME_PATTERN.match(raw): await message.answer("❌ Формат."); return
    if is_reserved_for_others(raw, user): await message.answer(f"🔒 @{raw} зарезервирован."); await state.clear(); return
    owner = db.get_username_owner(raw)
    if owner is not None:
        if owner == acc_id: await message.answer(f"✅ @{raw} ваш!"); await state.clear(); return
        await message.answer(f"❌ @{raw} занят."); await state.clear(); return
    db.add_username(raw, acc_id); await state.clear()
    await message.answer(f"✅ <b>@{raw} теперь ваш!</b>", reply_markup=username_menu_kb(), parse_mode="HTML")

# ================================================
# ПОДАРКИ
# ================================================
@dp.callback_query(F.data == "menu_gift")
async def menu_gift(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    await state.clear(); acc_id = get_active_account_id(callback.from_user.id); acc = db.get_account(acc_id)
    items = db.get_nfts(acc_id); numbers = db.get_numbers(acc_id); usernames = db.get_usernames(acc_id)
    await callback.message.answer(
        f"🎁 <b>Подарки</b>\n\n💼 ⭐ {acc['stars']} | 💎 {acc['ton']}\n📦 {len(items)} | 📱 {len(numbers)} | 🏷 {len(usernames)}",
        reply_markup=gift_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "gift_nft_start")
async def gift_nft_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); items = db.get_nfts(acc_id)
    if not items: await callback.message.answer("❌ Нет NFT."); return
    counter = Counter(items)
    buttons = [[InlineKeyboardButton(text=f"🎁 {name}" + (f" ×{c}" if c>1 else ""), callback_data=f"gift_item:{name}")] for name, c in counter.items()]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_gift")])
    await callback.message.answer("🎁 Какой NFT?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("gift_item:"))
async def gift_item_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); nft = callback.data.split(":", 1)[1]
    acc_id = get_active_account_id(callback.from_user.id)
    if nft not in db.get_nfts(acc_id): await callback.message.answer("❌"); return
    await state.update_data(gift_type="nft", gift_value=nft); await state.set_state(GiftStates.waiting_for_recipient)
    await callback.message.answer(f"🎁 {nft}\n\n@username:")

@dp.callback_query(F.data == "gift_number_start")
async def gift_number_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); numbers = db.get_numbers(acc_id)
    if not numbers: await callback.message.answer("❌"); return
    buttons = [[InlineKeyboardButton(text=f"📱 {n}" + (" 👑" if n.startswith("+888") else ""), callback_data=f"gift_num:{n}")] for n in numbers]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_gift")])
    await callback.message.answer("📱 Какой номер?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("gift_num:"))
async def gift_number_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); num = callback.data.split(":", 1)[1]; acc_id = get_active_account_id(callback.from_user.id)
    if num not in db.get_numbers(acc_id): await callback.message.answer("❌"); return
    if is_protected_888(num): await callback.message.answer("👑"); return
    await state.update_data(gift_type="number", gift_value=num); await state.set_state(GiftStates.waiting_for_recipient)
    await callback.message.answer(f"📱 {num}\n\n@username:")

@dp.callback_query(F.data == "gift_username_start")
async def gift_username_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); my = db.get_usernames(acc_id)
    if not my: await callback.message.answer("❌"); return
    buttons = [[InlineKeyboardButton(text=f"🏷 @{u_}", callback_data=f"gift_uname:{u_}")] for u_ in my]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_gift")])
    await callback.message.answer("🏷 Какой?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("gift_uname:"))
async def gift_username_chosen(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); uname = callback.data.split(":", 1)[1]; acc_id = get_active_account_id(callback.from_user.id)
    if uname not in db.get_usernames(acc_id): await callback.message.answer("❌"); return
    await state.update_data(gift_type="username", gift_value=uname); await state.set_state(GiftStates.waiting_for_recipient)
    await callback.message.answer(f"🏷 @{uname}\n\n@username:")

@dp.callback_query(F.data == "gift_stars_start")
async def gift_stars_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); acc = db.get_account(get_active_account_id(callback.from_user.id))
    await state.update_data(gift_type="stars"); await state.set_state(GiftStates.waiting_for_amount)
    await callback.message.answer(f"⭐ У вас {acc['stars']}⭐\n\nСколько?")

@dp.callback_query(F.data == "gift_ton_start")
async def gift_ton_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); acc = db.get_account(get_active_account_id(callback.from_user.id))
    await state.update_data(gift_type="ton"); await state.set_state(GiftStates.waiting_for_amount)
    await callback.message.answer(f"💎 У вас {acc['ton']} TON\n\nСколько?")

@dp.message(GiftStates.waiting_for_amount)
async def gift_amount_input(message: Message, state: FSMContext):
    data = await state.get_data(); gift_type = data.get("gift_type")
    acc_id = get_active_account_id(message.from_user.id); acc = db.get_account(acc_id)
    text = message.text.strip().replace(",", ".")
    try:
        amount = int(float(text)) if gift_type == "stars" else round(float(text), 2)
        if amount <= 0: raise ValueError
    except ValueError: await message.answer("❌"); return
    if gift_type == "stars" and amount > acc["stars"]: await message.answer(f"❌ У вас {acc['stars']}⭐"); return
    if gift_type == "ton" and amount > acc["ton"]: await message.answer(f"❌ У вас {acc['ton']}💎"); return
    await state.update_data(gift_value=amount); await state.set_state(GiftStates.waiting_for_recipient)
    unit = "⭐" if gift_type == "stars" else "💎"
    await message.answer(f"{amount} {unit}\n\n@username:")

@dp.message(GiftStates.waiting_for_recipient)
async def gift_recipient_input(message: Message, state: FSMContext):
    raw = message.text.strip().lstrip("@")
    recipient_id = None; recipient_label = ""
    if raw.isdigit(): recipient_id = int(raw); recipient_label = f"<code>{recipient_id}</code>"
    else:
        try:
            chat = await bot.get_chat(f"@{raw}"); recipient_id = chat.id; recipient_label = f"@{raw}"
        except Exception: await message.answer("❌"); return
    if recipient_id == message.from_user.id: await message.answer("😅 Себе нельзя."); return
    await state.update_data(recipient_id=recipient_id, recipient_label=recipient_label)
    await state.set_state(GiftStates.waiting_for_comment)
    await message.answer("💬 Комментарий (или - чтобы пропустить):")

@dp.message(GiftStates.waiting_for_comment)
async def gift_comment_input(message: Message, state: FSMContext):
    data = await state.get_data()
    gift_type = data.get("gift_type"); gift_value = data.get("gift_value")
    recipient_id = data.get("recipient_id"); recipient_label = data.get("recipient_label")
    sender_id = message.from_user.id; sender_display = display_name(message.from_user)
    comment = message.text.strip()
    if comment == "-": comment = ""
    s_acc = get_active_account_id(sender_id); r_acc = get_active_account_id(recipient_id)
    if gift_type == "nft":
        if gift_value not in db.get_nfts(s_acc): await message.answer("❌"); await state.clear(); return
        db.remove_nft(s_acc, gift_value); db.add_nft(r_acc, gift_value)
        t1 = f"🎁 {nft_display(gift_value)}"; t2 = f"🎁 {nft_display(gift_value)}"
    elif gift_type == "number":
        if gift_value not in db.get_numbers(s_acc): await message.answer("❌"); await state.clear(); return
        if is_protected_888(gift_value): await message.answer("👑"); await state.clear(); return
        db.remove_number(s_acc, gift_value); db.add_number(r_acc, gift_value)
        t1 = f"📱 <code>{gift_value}</code>"; t2 = f"📱 <code>{gift_value}</code>"
    elif gift_type == "username":
        if gift_value not in db.get_usernames(s_acc): await message.answer("❌"); await state.clear(); return
        db.remove_username(gift_value); db.add_username(gift_value, r_acc)
        t1 = f"🏷 @{gift_value}"; t2 = f"🏷 @{gift_value}"
    elif gift_type == "stars":
        s = db.get_account(s_acc)
        if s["stars"] < gift_value: await message.answer("❌"); await state.clear(); return
        db.update_account_wallet(s_acc, s["stars"] - gift_value, s["ton"])
        r = db.get_account(r_acc); db.update_account_wallet(r_acc, r["stars"] + gift_value, r["ton"])
        t1 = f"⭐ {gift_value}"; t2 = f"⭐ <b>{gift_value}</b>"
    elif gift_type == "ton":
        s = db.get_account(s_acc)
        if s["ton"] < gift_value: await message.answer("❌"); await state.clear(); return
        db.update_account_wallet(s_acc, s["stars"], round(s["ton"] - gift_value, 2))
        r = db.get_account(r_acc); db.update_account_wallet(r_acc, r["stars"], round(r["ton"] + gift_value, 2))
        t1 = f"💎 {gift_value}"; t2 = f"💎 <b>{gift_value}</b>"
    else: await message.answer("❌"); await state.clear(); return
    await state.clear()
    confirm = f"✅ <b>Отправлено!</b>\n\n{t1}\n👤 {recipient_label}"
    if comment: confirm += f"\n💬 <i>{comment}</i>"
    await message.answer(confirm, reply_markup=main_menu_kb(), parse_mode="HTML", disable_web_page_preview=True)
    notify = f"🎉 <b>Вам подарок!</b>\n\n{t2}\n👤 От: {sender_display}"
    if comment: notify += f"\n\n💬 <i>«{comment}»</i>"
    try: await bot.send_message(recipient_id, notify, parse_mode="HTML", disable_web_page_preview=True)
    except Exception: pass

# ================================================
# МАРКЕТЫ
# ================================================
@dp.callback_query(F.data == "menu_markets")
async def menu_markets(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); await state.clear()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    await callback.message.answer("🛒 Маркеты:", reply_markup=markets_menu_kb())

@dp.callback_query(F.data == "menu_market")
async def menu_market(callback: CallbackQuery):
    await callback.answer(); acc = db.get_account(get_active_account_id(callback.from_user.id))
    await callback.message.answer(f"🛒 Маркет NFT\n📊 Лотов: {db.count_nft_lots()}\n💼 ⭐ {acc['stars']} | 💎 {acc['ton']}", reply_markup=market_menu_kb())

@dp.callback_query(F.data == "market_browse")
async def market_browse(callback: CallbackQuery):
    await callback.answer(); lots = db.get_all_nft_lots()
    if not lots: await callback.message.answer("🛒 Пусто.", reply_markup=market_menu_kb()); return
    for lot_id, lot in sorted(lots.items(), key=lambda x: x[1]["price"])[:20]:
        ce = "⭐" if lot["currency"] == "stars" else "💎"
        await callback.message.answer(
            f"🆔 #{lot_id}\n🎁 {nft_display(lot['nft'])}\n💰 {lot['price']} {ce}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"🛒 Купить за {lot['price']} {ce}", callback_data=f"market_buy:{lot_id}")]]),
            parse_mode="HTML", disable_web_page_preview=True)
    await callback.message.answer("Действие:", reply_markup=market_menu_kb())

@dp.callback_query(F.data == "market_sell")
async def market_sell_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); items = db.get_nfts(acc_id)
    if not items: await callback.message.answer("❌"); return
    counter = Counter(items)
    buttons = [[InlineKeyboardButton(text=f"💰 {name}" + (f" ×{c}" if c>1 else ""), callback_data=f"marketsel:{name}")] for name, c in counter.items()]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="menu_market")])
    await callback.message.answer("💰 Что продать?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("marketsel:"))
async def market_sell_nft(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); nft = callback.data.split(":", 1)[1]
    if nft not in db.get_nfts(get_active_account_id(callback.from_user.id)): await callback.message.answer("❌"); return
    await state.update_data(sell_nft=nft); await state.set_state(MarketStates.waiting_for_price)
    await callback.message.answer(f"💰 {nft}\n\nЦена: <code>100 stars</code> или <code>0.5 ton</code>")

@dp.message(MarketStates.waiting_for_price)
async def market_sell_price(message: Message, state: FSMContext):
    data = await state.get_data(); nft = data.get("sell_nft")
    user_id = message.from_user.id; acc_id = get_active_account_id(user_id)
    parts = message.text.strip().lower().split()
    if len(parts) != 2: await message.answer("❌ 100 stars"); return
    try: price = float(parts[0])
    except ValueError: await message.answer("❌"); return
    if price <= 0: await message.answer("❌"); return
    currency = parts[1]
    if currency not in ("stars", "ton"): await message.answer("❌"); return
    price = int(price) if currency == "stars" else round(price, 2)
    if nft not in db.get_nfts(acc_id): await message.answer("❌"); await state.clear(); return
    db.remove_nft(acc_id, nft); lot_id = db.add_nft_lot(acc_id, user_id, nft, price, currency)
    await state.clear(); ce = "⭐" if currency == "stars" else "💎"
    await message.answer(f"✅ #{lot_id} {nft} — {price} {ce}", reply_markup=market_menu_kb())

@dp.callback_query(F.data.startswith("market_buy:"))
async def market_buy(callback: CallbackQuery):
    await callback.answer(); lot_id = int(callback.data.split(":", 1)[1]); lot = db.get_nft_lot(lot_id)
    if not lot: await callback.message.answer("❌"); return
    buyer_acc = get_active_account_id(callback.from_user.id)
    if buyer_acc == lot["seller_account"]: await callback.message.answer("😅"); return
    bw = db.get_account(buyer_acc); ce = "⭐" if lot["currency"] == "stars" else "💎"
    if lot["currency"] == "stars":
        if bw["stars"] < lot["price"]: await callback.message.answer("❌"); return
        db.update_account_wallet(buyer_acc, bw["stars"] - lot["price"], bw["ton"])
        sw = db.get_account(lot["seller_account"]); db.update_account_wallet(lot["seller_account"], sw["stars"] + lot["price"], sw["ton"])
    else:
        if bw["ton"] < lot["price"]: await callback.message.answer("❌"); return
        db.update_account_wallet(buyer_acc, bw["stars"], round(bw["ton"] - lot["price"], 2))
        sw = db.get_account(lot["seller_account"]); db.update_account_wallet(lot["seller_account"], sw["stars"], round(sw["ton"] + lot["price"], 2))
    db.add_nft(buyer_acc, lot["nft"]); db.remove_nft_lot(lot_id)
    await callback.message.answer(f"✅ Куплено {nft_display(lot['nft'])}", reply_markup=market_menu_kb(), parse_mode="HTML", disable_web_page_preview=True)
    try: await bot.send_message(lot["seller_tg"], f"💰 Продан {nft_display(lot['nft'])} за {lot['price']} {ce}", parse_mode="HTML", disable_web_page_preview=True)
    except Exception: pass

@dp.callback_query(F.data == "market_my_lots")
async def market_my_lots(callback: CallbackQuery):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); my = db.get_seller_lots_nft(acc_id)
    if not my: await callback.message.answer("📋 Нет."); return
    for lot_id, lot in my.items():
        ce = "⭐" if lot["currency"] == "stars" else "💎"
        await callback.message.answer(f"#{lot_id} {nft_display(lot['nft'])} — {lot['price']} {ce}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🗑", callback_data=f"market_remove:{lot_id}")]]),
            parse_mode="HTML", disable_web_page_preview=True)

@dp.callback_query(F.data.startswith("market_remove:"))
async def market_remove(callback: CallbackQuery):
    await callback.answer(); lot_id = int(callback.data.split(":", 1)[1]); acc_id = get_active_account_id(callback.from_user.id)
    lot = db.get_nft_lot(lot_id)
    if not lot or lot["seller_account"] != acc_id: await callback.message.answer("❌"); return
    db.add_nft(acc_id, lot["nft"]); db.remove_nft_lot(lot_id)
    await callback.message.answer("✅", reply_markup=market_menu_kb())

@dp.callback_query(F.data == "menu_nummarket")
async def menu_nummarket(callback: CallbackQuery):
    await callback.answer(); acc = db.get_account(get_active_account_id(callback.from_user.id))
    await callback.message.answer(f"📞 Маркет номеров\n📊 {db.count_num_lots()}\n💼 ⭐ {acc['stars']} | 💎 {acc['ton']}", reply_markup=nummarket_menu_kb())

@dp.callback_query(F.data == "nummarket_my_numbers")
async def nummarket_my_numbers(callback: CallbackQuery):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); numbers = db.get_numbers(acc_id)
    if not numbers: await callback.message.answer("📱 Нет."); return
    text = "📱 Ваши номера:\n\n"
    for i, n in enumerate(numbers, 1):
        tag = " 👑" if is_protected_888(n) else (" 👑 Люкс" if n.startswith("+888") else "")
        text += f"{i}. <code>{n}</code>{tag}\n"
    await callback.message.answer(text, reply_markup=nummarket_menu_kb(), parse_mode="HTML")

@dp.callback_query(F.data == "nummarket_browse")
async def nummarket_browse(callback: CallbackQuery):
    await callback.answer(); lots = db.get_all_num_lots()
    if not lots: await callback.message.answer("📞 Пусто."); return
    for lot_id, lot in sorted(lots.items(), key=lambda x: x[1]["price"])[:20]:
        ce = "⭐" if lot["currency"] == "stars" else "💎"
        await callback.message.answer(f"#{lot_id} <code>{lot['number']}</code> — {lot['price']} {ce}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛒", callback_data=f"numbuy:{lot_id}")]]), parse_mode="HTML")
    await callback.message.answer("Действие:", reply_markup=nummarket_menu_kb())

@dp.callback_query(F.data == "nummarket_sell")
async def nummarket_sell_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); numbers = db.get_numbers(acc_id)
    if not numbers: await callback.message.answer("❌"); return
    buttons = [[InlineKeyboardButton(text=f"📱 {n}" + (" 👑" if n.startswith("+888") else ""), callback_data=f"numsel:{n}")] for n in numbers]
    buttons.append([InlineKeyboardButton(text="⬅️", callback_data="menu_nummarket")])
    await callback.message.answer("💰 Какой?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("numsel:"))
async def nummarket_sell_number(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); num = callback.data.split(":", 1)[1]; acc_id = get_active_account_id(callback.from_user.id)
    if num not in db.get_numbers(acc_id): await callback.message.answer("❌"); return
    if is_protected_888(num): await callback.message.answer("👑"); return
    await state.update_data(sell_number=num); await state.set_state(NumMarketStates.waiting_for_price)
    await callback.message.answer(f"💰 {num}\n\nЦена: <code>100 stars</code>")

@dp.message(NumMarketStates.waiting_for_price)
async def nummarket_sell_price(message: Message, state: FSMContext):
    data = await state.get_data(); num = data.get("sell_number")
    user_id = message.from_user.id; acc_id = get_active_account_id(user_id)
    parts = message.text.strip().lower().split()
    if len(parts) != 2: await message.answer("❌"); return
    try: price = float(parts[0])
    except ValueError: await message.answer("❌"); return
    if price <= 0 or parts[1] not in ("stars", "ton"): await message.answer("❌"); return
    currency = parts[1]; price = int(price) if currency == "stars" else round(price, 2)
    if num not in db.get_numbers(acc_id): await message.answer("❌"); await state.clear(); return
    db.remove_number(acc_id, num); lot_id = db.add_num_lot(acc_id, user_id, num, price, currency)
    await state.clear(); ce = "⭐" if currency == "stars" else "💎"
    await message.answer(f"✅ #{lot_id} {num} — {price} {ce}", reply_markup=nummarket_menu_kb())

@dp.callback_query(F.data.startswith("numbuy:"))
async def nummarket_buy(callback: CallbackQuery):
    await callback.answer(); lot_id = int(callback.data.split(":", 1)[1]); lot = db.get_num_lot(lot_id)
    if not lot: await callback.message.answer("❌"); return
    buyer_acc = get_active_account_id(callback.from_user.id)
    if buyer_acc == lot["seller_account"]: await callback.message.answer("😅"); return
    bw = db.get_account(buyer_acc)
    if lot["currency"] == "stars":
        if bw["stars"] < lot["price"]: await callback.message.answer("❌"); return
        db.update_account_wallet(buyer_acc, bw["stars"] - lot["price"], bw["ton"])
        sw = db.get_account(lot["seller_account"]); db.update_account_wallet(lot["seller_account"], sw["stars"] + lot["price"], sw["ton"])
    else:
        if bw["ton"] < lot["price"]: await callback.message.answer("❌"); return
        db.update_account_wallet(buyer_acc, bw["stars"], round(bw["ton"] - lot["price"], 2))
        sw = db.get_account(lot["seller_account"]); db.update_account_wallet(lot["seller_account"], sw["stars"], round(sw["ton"] + lot["price"], 2))
    db.add_number(buyer_acc, lot["number"]); db.remove_num_lot(lot_id)
    await callback.message.answer(f"✅ Куплен {lot['number']}", reply_markup=nummarket_menu_kb())

@dp.callback_query(F.data == "nummarket_my_lots")
async def nummarket_my_lots(callback: CallbackQuery):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); my = db.get_seller_lots_num(acc_id)
    if not my: await callback.message.answer("📋 Нет."); return
    for lot_id, lot in my.items():
        ce = "⭐" if lot["currency"] == "stars" else "💎"
        await callback.message.answer(f"#{lot_id} {lot['number']} — {lot['price']} {ce}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🗑", callback_data=f"numremove:{lot_id}")]]))

@dp.callback_query(F.data.startswith("numremove:"))
async def nummarket_remove(callback: CallbackQuery):
    await callback.answer(); lot_id = int(callback.data.split(":", 1)[1]); acc_id = get_active_account_id(callback.from_user.id)
    lot = db.get_num_lot(lot_id)
    if not lot or lot["seller_account"] != acc_id: await callback.message.answer("❌"); return
    db.add_number(acc_id, lot["number"]); db.remove_num_lot(lot_id)
    await callback.message.answer("✅", reply_markup=nummarket_menu_kb())

@dp.callback_query(F.data == "menu_umarket")
async def menu_umarket(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(f"🛒 Маркет юзернеймов\n📊 {db.count_uname_lots()}", reply_markup=umarket_menu_kb())

@dp.callback_query(F.data == "umarket_browse")
async def umarket_browse(callback: CallbackQuery):
    await callback.answer(); lots = db.get_all_uname_lots()
    if not lots: await callback.message.answer("🛒 Пусто."); return
    for lot_id, lot in sorted(lots.items(), key=lambda x: x[1]["price"])[:20]:
        ce = "⭐" if lot["currency"] == "stars" else "💎"
        await callback.message.answer(f"#{lot_id} @{lot['username']} — {lot['price']} {ce}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛒", callback_data=f"ubuy:{lot_id}")]]))
    await callback.message.answer("Действие:", reply_markup=umarket_menu_kb())

@dp.callback_query(F.data == "umarket_sell")
async def umarket_sell_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); my = db.get_usernames(acc_id)
    if not my: await callback.message.answer("❌"); return
    buttons = [[InlineKeyboardButton(text=f"🏷 @{u_}", callback_data=f"usel:{u_}")] for u_ in my]
    buttons.append([InlineKeyboardButton(text="⬅️", callback_data="menu_umarket")])
    await callback.message.answer("💰 Какой?", reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("usel:"))
async def umarket_sell_username(callback: CallbackQuery, state: FSMContext):
    await callback.answer(); uname = callback.data.split(":", 1)[1]
    if uname not in db.get_usernames(get_active_account_id(callback.from_user.id)): await callback.message.answer("❌"); return
    await state.update_data(sell_username=uname); await state.set_state(UMarketStates.waiting_for_price)
    await callback.message.answer(f"💰 @{uname}\n\nЦена: <code>100 stars</code>")

@dp.message(UMarketStates.waiting_for_price)
async def umarket_sell_price(message: Message, state: FSMContext):
    data = await state.get_data(); uname = data.get("sell_username")
    user_id = message.from_user.id; acc_id = get_active_account_id(user_id)
    parts = message.text.strip().lower().split()
    if len(parts) != 2: await message.answer("❌"); return
    try: price = float(parts[0])
    except ValueError: await message.answer("❌"); return
    if price <= 0 or parts[1] not in ("stars", "ton"): await message.answer("❌"); return
    currency = parts[1]; price = int(price) if currency == "stars" else round(price, 2)
    if uname not in db.get_usernames(acc_id): await message.answer("❌"); await state.clear(); return
    db.remove_username(uname); lot_id = db.add_uname_lot(acc_id, user_id, uname, price, currency)
    await state.clear(); ce = "⭐" if currency == "stars" else "💎"
    await message.answer(f"✅ #{lot_id} @{uname} — {price} {ce}", reply_markup=umarket_menu_kb())

@dp.callback_query(F.data.startswith("ubuy:"))
async def umarket_buy(callback: CallbackQuery):
    await callback.answer(); lot_id = int(callback.data.split(":", 1)[1]); lot = db.get_uname_lot(lot_id)
    if not lot: await callback.message.answer("❌"); return
    buyer_acc = get_active_account_id(callback.from_user.id)
    if buyer_acc == lot["seller_account"]: await callback.message.answer("😅"); return
    bw = db.get_account(buyer_acc)
    if lot["currency"] == "stars":
        if bw["stars"] < lot["price"]: await callback.message.answer("❌"); return
        db.update_account_wallet(buyer_acc, bw["stars"] - lot["price"], bw["ton"])
        sw = db.get_account(lot["seller_account"]); db.update_account_wallet(lot["seller_account"], sw["stars"] + lot["price"], sw["ton"])
    else:
        if bw["ton"] < lot["price"]: await callback.message.answer("❌"); return
        db.update_account_wallet(buyer_acc, bw["stars"], round(bw["ton"] - lot["price"], 2))
        sw = db.get_account(lot["seller_account"]); db.update_account_wallet(lot["seller_account"], sw["stars"], round(sw["ton"] + lot["price"], 2))
    db.add_username(lot["username"], buyer_acc); db.remove_uname_lot(lot_id)
    await callback.message.answer(f"✅ @{lot['username']}", reply_markup=umarket_menu_kb())

@dp.callback_query(F.data == "umarket_my_lots")
async def umarket_my_lots(callback: CallbackQuery):
    await callback.answer(); acc_id = get_active_account_id(callback.from_user.id); my = db.get_seller_lots_uname(acc_id)
    if not my: await callback.message.answer("📋 Нет."); return
    for lot_id, lot in my.items():
        ce = "⭐" if lot["currency"] == "stars" else "💎"
        await callback.message.answer(f"#{lot_id} @{lot['username']} — {lot['price']} {ce}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🗑", callback_data=f"uremove:{lot_id}")]]))

@dp.callback_query(F.data.startswith("uremove:"))
async def umarket_remove(callback: CallbackQuery):
    await callback.answer(); lot_id = int(callback.data.split(":", 1)[1]); acc_id = get_active_account_id(callback.from_user.id)
    lot = db.get_uname_lot(lot_id)
    if not lot or lot["seller_account"] != acc_id: await callback.message.answer("❌"); return
    db.add_username(lot["username"], acc_id); db.remove_uname_lot(lot_id)
    await callback.message.answer("✅", reply_markup=umarket_menu_kb())

# ================================================
# КЕЙСЫ
# ================================================
@dp.callback_query(F.data == "menu_cases_nft")
async def menu_cases_nft(callback: CallbackQuery):
    await callback.answer(); acc = db.get_account(get_active_account_id(callback.from_user.id))
    await callback.message.answer(f"📦 Кейсы NFT\n💼 ⭐ {acc['stars']} | 💎 {acc['ton']}", reply_markup=cases_nft_kb())

@dp.callback_query(F.data.startswith("open_nft_case:"))
async def open_nft_case(callback: CallbackQuery):
    await callback.answer(); key = callback.data.split(":", 1)[1]
    if key not in NFT_CASES: return
    case = NFT_CASES[key]; user_id = callback.from_user.id; acc_id = get_active_account_id(user_id); acc = db.get_account(acc_id)
    if case["currency"] == "stars":
        if acc["stars"] < case["price"]: await callback.message.answer(f"❌ {case['price']}⭐"); return
        db.update_account_wallet(acc_id, acc["stars"] - case["price"], acc["ton"])
    else:
        if acc["ton"] < case["price"]: await callback.message.answer(f"❌ {case['price']}💎"); return
        db.update_account_wallet(acc_id, acc["stars"], round(acc["ton"] - case["price"], 2))
    won = []
    for _ in range(case["nft_count"]):
        nft = random.choice(NFT_GIFTS); won.append(nft); db.add_nft(acc_id, nft)
    db.add_user_action(acc_id, "opened_case")
    counter = Counter(won)
    won_text = "\n".join(f"🎁 {nft_display(n)}" + (f" ×{c}" if c > 1 else "") for n, c in counter.items())
    acc_new = db.get_account(acc_id)
    await callback.message.answer(
        f"🎉 <b>{case['name']}!</b>\n\n{won_text}\n\n💼 ⭐ {acc_new['stars']} | 💎 {acc_new['ton']}",
        reply_markup=cases_nft_kb(), parse_mode="HTML", disable_web_page_preview=True)

@dp.callback_query(F.data == "menu_cases_num")
async def menu_cases_num(callback: CallbackQuery):
    await callback.answer(); acc = db.get_account(get_active_account_id(callback.from_user.id))
    await callback.message.answer(f"📞 Кейсы номеров\n💼 ⭐ {acc['stars']} | 💎 {acc['ton']}", reply_markup=cases_num_kb())

@dp.callback_query(F.data.startswith("open_num_case:"))
async def open_num_case(callback: CallbackQuery):
    await callback.answer(); key = callback.data.split(":", 1)[1]
    if key not in NUMBER_CASES: return
    case = NUMBER_CASES[key]; user_id = callback.from_user.id; acc_id = get_active_account_id(user_id); acc = db.get_account(acc_id)
    if case["currency"] == "stars":
        if acc["stars"] < case["price"]: await callback.message.answer(f"❌"); return
        db.update_account_wallet(acc_id, acc["stars"] - case["price"], acc["ton"])
    else:
        if acc["ton"] < case["price"]: await callback.message.answer(f"❌"); return
        db.update_account_wallet(acc_id, acc["stars"], round(acc["ton"] - case["price"], 2))
    won = []
    for _ in range(case["num_count"]):
        num = get_random_number_from_pool(case["pool"]); won.append(num); db.add_number(acc_id, num)
    db.add_user_action(acc_id, "opened_case")
    won_text = "\n".join(f"📱 <code>{n}</code>" + (" 👑" if n.startswith("+888") else "") for n in won)
    header = "👑 <b>ПОЗДРАВЛЯЕМ!</b>" if case["pool"] == "luxury_888" else f"🎉 <b>{case['name']}!</b>"
    acc_new = db.get_account(acc_id)
    await callback.message.answer(f"{header}\n\n{won_text}\n\n💼 ⭐ {acc_new['stars']} | 💎 {acc_new['ton']}", reply_markup=cases_num_kb(), parse_mode="HTML")

# ================================================
# ЗАДАНИЯ
# ================================================
@dp.callback_query(F.data == "menu_tasks")
async def menu_tasks(callback: CallbackQuery):
    await callback.answer()
    if not is_activated(callback.from_user.id): await callback.message.answer("🔒 /start"); return
    user_id = callback.from_user.id; acc_id = get_active_account_id(user_id)
    completed = db.get_completed_tasks(acc_id); acc = db.get_account(acc_id)
    actions = db.get_user_actions(acc_id); refs = db.get_referrals(user_id)
    await callback.message.answer(
        f"✅ Задания\n\nВыполнено: {len(completed)}/{len(TASKS)}\n💼 ⭐ {acc['stars']} | 💎 {acc['ton']}\n\n"
        f"📱 Номер: {'✅' if 'got_number' in actions else '❌'}\n📦 Кейс: {'✅' if 'opened_case' in actions else '❌'}\n👥 Друзей: {len(refs)}",
        reply_markup=tasks_menu_kb(user_id))

@dp.callback_query(F.data == "task_done")
async def task_done(callback: CallbackQuery): await callback.answer("✅ Уже выполнено!", show_alert=True)

@dp.callback_query(F.data.startswith("task:"))
async def task_start(callback: CallbackQuery):
    await callback.answer(); key = callback.data.split(":", 1)[1]
    if key not in TASKS: return
    task = TASKS[key]; user_id = callback.from_user.id; acc_id = get_active_account_id(user_id)
    completed = db.get_completed_tasks(acc_id)
    if key in completed: await callback.message.answer("✅ Уже выполнено."); return
    if key == "sub_channel":
        try:
            member = await bot.get_chat_member(CHANNEL_ID, user_id)
            if member.status not in ("member", "administrator", "creator"): raise Exception()
        except Exception:
            await callback.message.answer(f"❌ Не подписаны.\n{CHANNEL_URL}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📢 Подписаться", url=CHANNEL_URL)],
                    [InlineKeyboardButton(text="🔄 Проверить", callback_data=f"task:{key}")]]))
            return
    elif key == "invite_friend":
        if len(db.get_referrals(user_id)) < 1:
            me = await bot.get_me()
            await callback.message.answer(f"❌ Не пригласили.\n<code>https://t.me/{me.username}?start=ref_{user_id}</code>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔄", callback_data=f"task:{key}")]]))
            return
    elif key == "get_number":
        if "got_number" not in db.get_user_actions(acc_id): await callback.message.answer("❌"); return
    elif key == "open_case":
        if "opened_case" not in db.get_user_actions(acc_id): await callback.message.answer("❌"); return
    elif key == "daily":
        now = time.time(); last = db.get_daily_claim(acc_id)
        if now - last < 86400:
            h = int((86400 - (now - last)) // 3600); m = int(((86400 - (now - last)) % 3600) // 60)
            await callback.message.answer(f"⏱ Через {h}ч {m}м."); return
        db.set_daily_claim(acc_id, now)
    acc = db.get_account(acc_id)
    db.update_account_wallet(acc_id, acc["stars"] + task["reward_stars"], round(acc["ton"] + task["reward_ton"], 2))
    db.add_completed_task(acc_id, key)
    acc_new = db.get_account(acc_id)
    await callback.message.answer(f"✅ {task['name']}\n⭐ +{task['reward_stars']}\n💎 +{task['reward_ton']}\n\n💼 ⭐ {acc_new['stars']} | 💎 {acc_new['ton']}", reply_markup=tasks_menu_kb(user_id))

# ================================================
# WEB-СЕРВЕР ДЛЯ RENDER (ЧТОБЫ НЕ ЗАСЫПАЛ)
# ================================================
async def handle_ping(request):
    return web.Response(text="Bot is running 24/7!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    
    # Render автоматически передает порт через переменную окружения PORT, по умолчанию 8080
    import os
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"[web] Веб-сервер запущен на порту {port}")

conn = sqlite3.connect("bot_data.db")
cursor = conn.cursor()

# Создаем таблицу телефонов, если её еще нет
cursor.execute("""
CREATE TABLE IF NOT EXISTS phones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model TEXT,
    price INTEGER,
    status TEXT DEFAULT 'available',
    owner_id INTEGER DEFAULT NULL
)
""")

# Список крутых телефонов для магазина
new_phones = [
    ("Google Pixel 8 Pro + eSIM", 130),
    ("Xiaomi 14 Ultra + Dual SIM", 110),
    ("iPhone 14 Pro Max + SIM", 140),
    ("Samsung Galaxy Z Fold 5", 200),
    ("Poco X6 Pro 5G", 75),
    ("Honor Magic 6 Pro", 125),
    ("OnePlus 12 + eSIM", 95)
]

# Добавляем их в базу данных
# Проверяем, есть ли уже телефоны в базе, чтобы не плодить дубликаты при каждом перезапуске
cursor.execute("SELECT COUNT(*) FROM phones")
if cursor.fetchone()[0] == 0:
    cursor.executemany("INSERT INTO phones (model, price) VALUES (?, ?)", new_phones)
    conn.commit()

conn.close()

# ================================================
# ЗАПУСК
# ================================================
async def main():
    print(f"Бот запущен! Криптовалют: {len(CRYPTO)} | Кошельков: {db.count_wallets()} | NFT-ссылок: {len(NFT_LINKS)}")

    try:
        ok = await update_rates_once()
        if not ok:
            simulate_rates()
        print("[rates] Первое обновление выполнено")
    except Exception as e:
        print(f"[rates] Первое обновление не удалось: {e}")

    # Запускаем фоновые задачи (курсы крипты и веб-сервер)
    asyncio.create_task(rates_updater())
    asyncio.create_task(web_server())

    # Запуск поллинга телеграм-бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
