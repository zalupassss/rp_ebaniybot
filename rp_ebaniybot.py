import os
import random
import threading
import time
import telebot
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask

# Глобальный список, куда мы скачаем слова из интернета
ONLINE_WORDS = []

# 🔑 Токен бота
TOKEN = "8892392566:AAE0rSE7QW21zfgZsKhIpf9NrU4OjxR52HY"
bot = telebot.TeleBot(TOKEN)

# Веб-сервер для хостинга (Render)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is active!"

# 📚 База стандартных РП-команд
RP_COMMANDS = {
    "поцеловать": {
        "aliases": ["поцеловать", "/kiss", "!поцеловать", "поцелуй"],
        "target_text": "💋 <b>{sender}</b> целует <b>{target}</b>!",
        "solo_text": "💋 <b>{sender}</b> целует воздух... Кого-то явно не хватает!",
        "gifs": ["https://media1.tenor.com/m/GAr1rMm39pcAAAAC/anime-hug.gif"],
    },
    "обнять": {
        "aliases": ["обнять", "/hug", "!обнять"],
        "target_text": "🫂 <b>{sender}</b> крепко-крепко обнимает <b>{target}</b>!",
        "solo_text": "🤗 <b>{sender}</b> обнимает весь чат!",
        "gifs": ["https://media1.tenor.com/m/I1v_9vYjxyEAAAAC/hibike-euphonium.gif"],
    },
    "погладить": {
        "aliases": ["погладить", "/pat", "!погладить"],
        "target_text": "🫳 <b>{sender}</b> нежно гладит <b>{target}</b> по голове!",
        "solo_text": "🫳 <b>{sender}</b> гладит сам себя...",
        "gifs": ["https://media1.tenor.com/m/PkWttKcH1xMAAAAC/kobayashi-dragon.gif"],
    },
    "укусить": {
        "aliases": ["укусить", "/bite", "!укусить", "куснуть"],
        "target_text": "🦷 <b>{sender}</b> делает аккуратный «кусь» <b>{target}</b>!",
        "solo_text": "😬 <b>{sender}</b> делает «кусь» воздуха!",
        "gifs": ["https://media1.tenor.com/m/5mVQ3ffWUTgAAAAC/anime-bite.gif"],
    },
    "покормить": {
        "aliases": ["покормить", "/feed", "!покормить", "накормить"],
        "target_text": "🍲 <b>{sender}</b> вкусно кормит <b>{target}</b>! Теперь кто-то сыт и доволен 😊",
        "solo_text": "🍲 <b>{sender}</b> вкусно кушает! Приятного аппетита 😋",
        "gifs": ["https://media.tenor.com/gIbE9pZ7raYAAAAC/wataten-watashi-ni-tenshi-ga-maiorita.gif"],
    },
    "оставить засос": {
        "aliases": ["оставить засос", "оставить_засос", "!оставить засос"],
        "target_text": "💋 <b>{sender}</b> оставляет страстный засос на шее <b>{target}</b>!",
        "solo_text": "💋 <b>{sender}</b> пытается оставить засос... но на ком?",
        "gifs": ["https://media1.tenor.com/m/5FOgNEcoaYMAAAAC/neck-kisses.gif"],
    },
    "флиртовать": {
        "aliases": ["флиртовать", "флирт", "/flirt", "!флирт"],
        "target_text": "😏 <b>{sender}</b> игриво флиртует с <b>{target}</b>~",
        "solo_text": "😏 <b>{sender}</b> тренирует навыки флирта перед зеркалом!",
        "gifs": ["https://media.tenor.com/TlFyVb6dRqkAAAAC/anime-horusultra.gif"],
    },
    "трахнуть": {
        "aliases": ["трахнуть", "выебать", "/sex", "!трахнуть"],
        "target_text": "🔥 <b>{sender}</b> нежно трахнул <b>{target}</b>!",
        "solo_text": "🔥 <b>{sender}</b> но член не встал...",
        "gifs": ["https://media.tenor.com/SiL8iSajNNQAAAAi/hi.gif"],
    },
    "засосать": {
        "aliases": ["засосать", "!засосать", "/засосать"],
        "target_text": "🔥 <b>{sender}</b> нежно засосал <b>{target}</b>!",
        "solo_text": "🔥 <b>{sender}</b> засосал подушку...",
        "gifs": ["https://media.tenor.com/xYUjLVz6rJoAAAAC/mhel.gif"],
    },
}

# 🛠 Базы данных в памяти
CHAT_CUSTOM_RP = {}        # {chat_id: {command_name: data_dict}}
USER_ADDING_STATE = {}     # {user_id: chat_id}
USERS_ECONOMY = {}         # {user_id: data_dict}
CROCODILE_GAMES = {}       # {chat_id: {"mode": "classic/games", "display_word": "...", "answers": [...], "host_id": 123, "host_name": "..."}}

# 🐊 Классическая база слов
CROCODILE_WORDS = [
    "яблоко", "банан", "собака", "кошка", "слон", "жираф", "медведь", "лиса", "волк", "заяц",
    "тигр", "лев", "акула", "дельфин", "кит", "пингвин", "страус", "крокодил", "змея", "черепаха",
    "лягушка", "бабочка", "паук", "муха", "комар", "врач", "учитель", "повар", "строитель", "космонавт",
    "пилот", "полицейский", "пожарный", "художник", "музыкант", "актер", "певец", "программист", "журналист", "фотограф",
    "пицца", "суши", "бургер", "пельмени", "борщ", "шоколад", "мороженое", "арбуз", "шаурма", "торт",
    "сыр", "хлеб", "молоко", "кофе", "чай", "телевизор", "компьютер", "ноутбук", "телефон", "наушники",
    "микрофон", "часы", "очки", "рюкзак", "зеркало", "кровать", "диван", "стол", "стул", "лампа",
    "автомобиль", "самолет", "вертолет", "корабль", "велосипед", "самокат", "мотоцикл", "трактор", "поезд", "автобус",
    "любовь", "дружба", "магия", "интернет", "нейросеть", "мем", "аниме", "стрим", "донат", "вайб",
    "кринж", "праздник", "подарок", "сюрприз", "космос", "планета", "звезда", "солнце", "луна", "облако"
]

# 🎮 База из 150 видеоигр
GAME_WORDS = [
    # 1 - 20
    {"display": "League of Legends", "answers": ["league of legends", "лига легенд", "лол", "lol"]},
    {"display": "Zenless Zone Zero", "answers": ["zenless zone zero", "zzz", "ззз"]},
    {"display": "Minecraft", "answers": ["minecraft", "майнкрафт", "майн"]},
    {"display": "Dota 2", "answers": ["dota 2", "дота 2", "дота", "dota"]},
    {"display": "Counter-Strike", "answers": ["counter-strike", "counter strike", "cs:go", "cs2", "cs", "кс", "ксго"]},
    {"display": "Genshin Impact", "answers": ["genshin impact", "геншин", "геншин импакт"]},
    {"display": "Honkai: Star Rail", "answers": ["honkai star rail", "хср", "hsr", "хонкай стар рейл", "стар рейл"]},
    {"display": "Brawl Stars", "answers": ["brawl stars", "бравл старс", "бравл"]},
    {"display": "Roblox", "answers": ["roblox", "роблокс"]},
    {"display": "The Witcher 3: Wild Hunt", "answers": ["ведьмак 3", "ведьмак", "witcher 3", "witcher", "ведьмак 3 дикая охота"]},
    {"display": "GTA 5", "answers": ["gta 5", "гта 5", "gta", "гта", "gta v", "гта в"]},
    {"display": "Cyberpunk 2077", "answers": ["cyberpunk 2077", "киберпанк 2077", "cyberpunk", "киберпанк"]},
    {"display": "Undertale", "answers": ["undertale", "андертейл"]},
    {"display": "Deltarune", "answers": ["deltarune", "дельтарун"]},
    {"display": "S.T.A.L.K.E.R.: Shadow of Chernobyl", "answers": ["stalker", "сталкер", "s.t.a.l.k.e.r.", "сталкер тень чернобыля"]},
    {"display": "Terraria", "answers": ["terraria", "террария"]},
    {"display": "Five Nights at Freddy's", "answers": ["fnaf", "фнаф", "five nights at freddy's", "пять ночей с фредди"]},
    {"display": "Valorant", "answers": ["valorant", "валорант"]},
    {"display": "Overwatch", "answers": ["overwatch", "овервотч", "овер"]},
    {"display": "Fallout 4", "answers": ["fallout 4", "фоллаут 4", "fallout", "фоллаут"]},

    # 21 - 40
    {"display": "The Elder Scrolls V: Skyrim", "answers": ["skyrim", "скарим", "скайрим", "tes 5", "tes v"]},
    {"display": "Red Dead Redemption 2", "answers": ["red dead redemption 2", "rdr 2", "рдр 2", "rdr2", "рдр2"]},
    {"display": "Dark Souls", "answers": ["dark souls", "дарк соулс", "ДС", "ds"]},
    {"display": "Elden Ring", "answers": ["elden ring", "елден ринг", "эSubн ринг", "эльден ринг"]},
    {"display": "Bloodborne", "answers": ["bloodborne", "бладборн"]},
    {"display": "Sekiro: Shadows Die Twice", "answers": ["sekiro", "секиро"]},
    {"display": "Hollow Knight", "answers": ["hollow knight", "холоу найт", "холлоу найт"]},
    {"display": "Portal 2", "answers": ["portal 2", "портал 2", "portal", "портал"]},
    {"display": "Half-Life 2", "answers": ["half-life 2", "half life 2", "халф лайф 2", "халфа 2", "half life", "халфа"]},
    {"display": "Apex Legends", "answers": ["apex legends", "апекс легендс", "апекс", "apex"]},
    {"display": "PUBG", "answers": ["pubg", "пабг", "пубг"]},
    {"display": "Rust", "answers": ["rust", "раст"]},
    {"display": "Dead by Daylight", "answers": ["dead by daylight", "dbd", "дбд"]},
    {"display": "Geometry Dash", "answers": ["geometry dash", "геометри даш", "гд", "gd"]},
    {"display": "Phasmophobia", "answers": ["phasmophobia", "фазмофобия", "фазма"]},
    {"display": "Lethal Company", "answers": ["lethal company", "летал компани"]},
    {"display": "Cuphead", "answers": ["cuphead", "капхед"]},
    {"display": "Dead Cells", "answers": ["dead cells", "дед селлс", "дед селс"]},
    {"display": "Hotline Miami", "answers": ["hotline miami", "хотлайн майами", "хотлайн"]},
    {"display": "The Binding of Isaac", "answers": ["the binding of isaac", "binding of isaac", "айзек", "isaac"]},

    # 41 - 60
    {"display": "Subnautica", "answers": ["subnautica", "сабнатика", "субнатика"]},
    {"display": "Outlast", "answers": ["outlast", "аутласт"]},
    {"display": "Amnesia: The Dark Descent", "answers": ["amnesia", "амнезия"]},
    {"display": "Resident Evil 4", "answers": ["resident evil 4", "обитель зла 4", "резидент ивил 4", "re4", "re 4"]},
    {"display": "Silent Hill 2", "answers": ["silent hill 2", "сайлент хилл 2", "silent hill", "сайлент хилл"]},
    {"display": "Detroit: Become Human", "answers": ["detroit become human", "детройт бикам хьюман", "детройт"]},
    {"display": "Life is Strange", "answers": ["life is strange", "лайф из стрендж", "лис"]},
    {"display": "The Last of Us", "answers": ["the last of us", "одну из нас", "одни из нас", "tlou", "тлоу"]},
    {"display": "God of War", "answers": ["god of war", "год оф вор", "бог войны", "gow"]},
    {"display": "Assassin's Creed", "answers": ["assassin's creed", "assassins creed", "ассасин крид", "ассасин"]},
    {"display": "Far Cry 3", "answers": ["far cry 3", "фар край 3", "far cry", "фар край"]},
    {"display": "Mafia 2", "answers": ["mafia 2", "мафия 2", "mafia", "мафия"]},
    {"display": "Mass Effect", "answers": ["mass effect", "масс эффект"]},
    {"display": "S.T.A.L.K.E.R. 2: Heart of Chornobyl", "answers": ["stalker 2", "сталкер 2", "s.t.a.l.k.e.r. 2"]},
    {"display": "Metro 2033", "answers": ["metro 2033", "метро 2033", "метро"]},
    {"display": "World of Tanks", "answers": ["world of tanks", "мир танков", "танки", "wot", "вот"]},
    {"display": "War Thunder", "answers": ["war thunder", "вар тандер", "тундра"]},
    {"display": "Clash Royale", "answers": ["clash royale", "клеш рояль", "клешрояль"]},
    {"display": "Clash of Clans", "answers": ["clash of clans", "клеш оф кленс", "кок"]},
    {"display": "Standoff 2", "answers": ["standoff 2", "стандофф 2", "стандофф", "стандоф"]},

    # 61 - 80
    {"display": "Mobile Legends: Bang Bang", "answers": ["mobile legends", "млбб", "mlbb", "мобил легендс"]},
    {"display": "Garry's Mod", "answers": ["garry's mod", "garrys mod", "гаррис мод", "гмод", "gmod"]},
    {"display": "Left 4 Dead 2", "answers": ["left 4 dead 2", "лефт 4 дед 2", "л4д2", "l4d2", "left 4 dead"]},
    {"display": "Team Fortress 2", "answers": ["team fortress 2", "тим фортресс 2", "тф2", "tf2"]},
    {"display": "Payday 2", "answers": ["payday 2", "пейдей 2", "пайдей 2", "payday"]},
    {"display": "Among Us", "answers": ["among us", "амонг ас", "амонгас"]},
    {"display": "Fall Guys", "answers": ["fall guys", "фол гайс"]},
    {"display": "Rocket League", "answers": ["rocket league", "рокет лига", "рокет лиг"]},
    {"display": "Sea of Thieves", "answers": ["sea of thieves", "си оф сивс", "море воров"]},
    {"display": "Monster Hunter: World", "answers": ["monster hunter world", "монстер хантер"]},
    {"display": "Devil May Cry 5", "answers": ["devil may cry 5", "девил май край 5", "dmc 5", "дмк 5", "dmc"]},
    {"display": "Bayonetta", "answers": ["bayonetta", "байонетта"]},
    {"display": "Nier: Automata", "answers": ["nier automata", "нир автомата", "ниер автомата"]},
    {"display": "Persona 5", "answers": ["persona 5", "персона 5", "persona", "персона"]},
    {"display": "Yakuza 0", "answers": ["yakuza 0", "якудза 0", "yakuza", "якудза"]},
    {"display": "Death Stranding", "answers": ["death stranding", "дет стрендинг", "симулятор курьера"]},
    {"display": "Control", "answers": ["control", "контрол"]},
    {"display": "Alan Wake", "answers": ["alan wake", "алан вейк"]},
    {"display": "Quantum Break", "answers": ["quantum break", "квантум брейк"]},
    {"display": "Dishonored", "answers": ["dishonored", "дисхоноред"]},

    # 81 - 100
    {"display": "Bioshock", "answers": ["bioshock", "биошок"]},
    {"display": "Hitman", "answers": ["hitman", "хитман"]},
    {"display": "Tomb Raider", "answers": ["tomb raider", "томб райдер", "лара крофт"]},
    {"display": "Uncharted", "answers": ["uncharted", "анчартед"]},
    {"display": "Heavy Rain", "answers": ["heavy rain", "хеви рейн"]},
    {"display": "Beyond: Two Souls", "answers": ["beyond two souls", "за гранью две души"]},
    {"display": "Until Dawn", "answers": ["until dawn", "доживи до рассвета", "антил дон"]},
    {"display": "The Quarry", "answers": ["the quarry", "куорри", "кворри"]},
    {"display": "Poppy Playtime", "answers": ["poppy playtime", "поппи плейтайм", "хаги ваги"]},
    {"display": "Bendy and the Ink Machine", "answers": ["bendy and the ink machine", "бенди", "bendy"]},
    {"display": "Slender: The Eight Pages", "answers": ["slender", "слендер", "слендермен"]},
    {"display": "Hello Neighbor", "answers": ["hello neighbor", "привет сосед", "сосед"]},
    {"display": "Little Nightmares", "answers": ["little nightmares", "литл найтмерс", "маленькие кошмары"]},
    {"display": "Limbo", "answers": ["limbo", "лимбо"]},
    {"display": "Inside", "answers": ["inside", "инсайд"]},
    {"display": "Celeste", "answers": ["celeste", "селеста"]},
    {"display": "Hades", "answers": ["hades", "хадес", "аид"]},
    {"display": "Katana Zero", "answers": ["katana zero", "катана зеро"]},
    {"display": "Omori", "answers": ["omori", "омори"]},
    {"display": "Slay the Spire", "answers": ["slay the spire", "слей зе спайр"]},

    # 101 - 120
    {"display": "Palworld", "answers": ["palworld", "палворлд", "палы"]},
    {"display": "Helldivers 2", "answers": ["helldivers 2", "хеллдайверс 2", "хелдайверс 2"]},
    {"display": "Escape from Tarkov", "answers": ["escape from tarkov", "тарков", "eft"]},
    {"display": "Warframe", "answers": ["warframe", "варфрейм"]},
    {"display": "Crossout", "answers": ["crossout", "кроссаут"]},
    {"display": "Point Blank", "answers": ["point blank", "поинт бланк", "пб"]},
    {"display": "Warface", "answers": ["warface", "варфейс", "варфак"]},
    {"display": "Tom Clancy's Rainbow Six Siege", "answers": ["rainbow six siege", "радуга", "сидж", "r6s", "rainbow six"]},
    {"display": "Don't Starve", "answers": ["don't starve", "dont starve", "донт старв"]},
    {"display": "Factorio", "answers": ["factorio", "факторио"]},
    {"display": "RimWorld", "answers": ["rimworld", "римворлд"]},
    {"display": "The Sims 4", "answers": ["the sims 4", "симс 4", "sims 4", "симс"]},
    {"display": "Heroes of Might and Magic III", "answers": ["герои 3", "heroes 3", "герои меча и магии 3", "homm 3"]},
    {"display": "Sid Meier's Civilization VI", "answers": ["civilization 6", "цивилизация 6", "цива 6", "цива"]},
    {"display": "Hearts of Iron IV", "answers": ["hearts of iron 4", "hoi4", "хои4", "день победы 4"]},
    {"display": "Europa Universalis IV", "answers": ["europa universalis 4", "европа 4", "eu4"]},
    {"display": "Stellaris", "answers": ["stellaris", "стелларис"]},
    {"display": "Crusader Kings III", "answers": ["crusader kings 3", "крестоносцы 3", "ck3"]},
    {"display": "Mount & Blade II: Bannerlord", "answers": ["mount and blade", "баннерлорд", "баннерлорд 2", "маунт и блейд"]},

    # 121 - 140
    {"display": "Stardew Valley", "answers": ["stardew valley", "стардью валли", "стардью"]},
    {"display": "Animal Crossing: New Horizons", "answers": ["animal crossing", "энимал кроссинг"]},
    {"display": "Cities: Skylines", "answers": ["cities skylines", "ситис скайлайнс"]},
    {"display": "Euro Truck Simulator 2", "answers": ["euro truck simulator 2", "ets 2", "етс 2", "евро трек симулятор"]},
    {"display": "Spore", "answers": ["spore", "спор"]},
    {"display": "Slime Rancher", "answers": ["slime rancher", "слайм ранчер"]},
    {"display": "Untitled Goose Game", "answers": ["untitled goose game", "игра про гуся", "гусь"]},
    {"display": "Goat Simulator", "answers": ["goat simulator", "симулятор козла"]},
    {"display": "Plague Inc.", "answers": ["plague inc", "плаг инк", "чума"]},
    {"display": "Flappy Bird", "answers": ["flappy bird", "флеппи берд"]},
    {"display": "Subway Surfers", "answers": ["subway surfers", "сабвей сёрф", "сабвей сурф", "сабвей"]},
    {"display": "Fruit Ninja", "answers": ["fruit ninja", "фрут ниндзя"]},
    {"display": "Angry Birds", "answers": ["angry birds", "энгри бердс", "злые птички"]},
    {"display": "Plants vs. Zombies", "answers": ["plants vs zombies", "растения против зомби", "pvz", "пвз"]},
    {"display": "Pou", "answers": ["pou", "поу"]},
    {"display": "Talking Tom", "answers": ["talking tom", "говорящий том", "том"]},
    {"display": "Shadow Fight 2", "answers": ["shadow fight 2", "шедоу файт 2", "бой с тенью 2"]},
    {"display": "Hill Climb Racing", "answers": ["hill climb racing", "хилл клаймб ресинг", "машинки"]},
    {"display": "Doodle Jump", "answers": ["doodle jump", "дудл джамп"]},
    {"display": "Pac-Man", "answers": ["pac-man", "pacman", "пакман"]},

    # 141 - 150
    {"display": "Tetris", "answers": ["tetris", "тетрис"]},
    {"display": "Sonic the Hedgehog", "answers": ["sonic", "соник"]},
    {"display": "Super Mario Bros.", "answers": ["super mario", "mario", "марио", "супер марио"]},
    {"display": "The Legend of Zelda: Breath of the Wild", "answers": ["zelda", "зельда", "botw"]},
    {"display": "Overcooked!", "answers": ["overcooked", "оверкукед"]},
    {"display": "Keep Talking and Nobody Explodes", "answers": ["keep talking and nobody explodes", "бомба"]},
    {"display": "Satisfactory", "answers": ["satisfactory", "сатисфактори"]},
    {"display": "Deep Rock Galactic", "answers": ["deep rock galactic", "дип рок галактик", "дрг", "drg"]},
    {"display": "Crossy Road", "answers": ["crossy road", "кросси роуд"]},
    {"display": "Vampire Survivors", "answers": ["vampire survivors", "вампир сурвайворс"]}
]

SHOP_ITEMS = {
    "ears": {"name": "🐾 Кошачьи ушки", "price": 100, "desc": "Эффект 'Милота': мурр..~ и x3 некокойна."},
    "ramen": {"name": "🍜 Рамен", "price": 50, "desc": "Эффект 'Даттебаё жгучесть': пассивный фарм на 1 час."},
    "rose": {"name": "🌹 Алая роза", "price": 150, "desc": "Эффект 'Романтика': романтичный префикс."},
    "crown": {"name": "👑 Корона", "price": 500, "desc": "Эффект 'Император': префикс 'Господин,'."}
}

def get_user_data(user_id):
    if user_id not in USERS_ECONOMY:
        USERS_ECONOMY[user_id] = {
            "coins": 100,
            "inventory": [],
            "active_effects": [],
            "purchase_cooldowns": {},
            "ramen_expires_at": 0,
            "last_passive_check": time.time(),
            "stats": {"hugs": 0, "kisses": 0, "actions": 0},
            "last_daily": 0
        }
    return USERS_ECONOMY[user_id]

def update_passive_coins(u_data):
    now = time.time()
    if u_data["ramen_expires_at"] > now:
        elapsed = now - u_data["last_passive_check"]
        earned = int(elapsed // 30)
        if earned > 0:
            u_data["coins"] += earned
            u_data["last_passive_check"] += earned * 30
    else:
        u_data["last_passive_check"] = now


# ==========================================
# ЛОГИКА И МЕНЮ ИГРЫ КРОКОДИЛ
# ==========================================

# 1. Объявляем пустой список заранее
ONLINE_WORDS = []

def load_words_from_internet():
    global ONLINE_WORDS
    try:
        print("Скачиваю базу слов из интернета...")
        # 👇 СЮДА ВСТАВЬ ССЫЛКУ RAW ИЗ PASTEBIN ИЛИ GITHUB GIST 👇
        url = "https://pastebin.com/raw/5KQM0sHA" 
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            ONLINE_WORDS = [word.strip().lower() for word in response.text.splitlines() if word.strip()]
            print(f"Успешно загружено {len(ONLINE_WORDS)} легких слов из интернета!")
        else:
            print("Сайт со словами недоступен, будем использовать стандартную базу.")
    except Exception as e:
        print(f"Ошибка при скачивании слов: {e}")

# Загружаем слова при запуске
load_words_from_internet()

def send_croc_round_message(chat_id, host_id, host_name, mode, prefix_text=""):
    display_word, answers = generate_word(mode)
    
    CROCODILE_GAMES[chat_id] = {
        "mode": mode,
        "display_word": display_word,
        "answers": answers,
        "host_id": host_id,
        "host_name": host_name
    }

    mode_title = "🐊 Классический Крокодил" if mode == "classic" else "🎮 Отгадай игру"

    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("👀 Загаданное слово", callback_data="croc_show_word"),
        InlineKeyboardButton("🔄 Поменять слово", callback_data="croc_skip_word"),
        InlineKeyboardButton("🔀 Сменить режим", callback_data="croc_change_mode")
    )

    msg_text = (
        f"{prefix_text}"
        f"🎯 **Новый раунд ({mode_title})!**\n\n"
        f"👑 Ведущий: **{host_name}**\n\n"
        f"Ведущий, жми на кнопку ниже, смотри слово и объясняй его чату!\n"
        f"Чтобы остановить игру, напишите `стоп` или `сдаемся`."
    )

    bot.send_message(chat_id, msg_text, reply_markup=markup, parse_mode="Markdown")


@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["крокодил", "игры", "игра"])
def show_game_menu(message):
    chat_id = message.chat.id
    if chat_id in CROCODILE_GAMES:
        game = CROCODILE_GAMES[chat_id]
        bot.send_message(chat_id, f"🐊 Игра уже идет! Ведущий: **{game['host_name']}**.\nЧтобы закончить, напишите `стоп`.", parse_mode="Markdown")
        return

    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("🐊 Классический Крокодил", callback_data="start_mode_classic"),
        InlineKeyboardButton(f"🎮 Отгадай игру ({len(GAME_WORDS)} тайтлов!)", callback_data="start_mode_games")
    )

    bot.send_message(
        chat_id,
        "🎮 **Выбери режим игры:**\n\n"
        "• **Классический** — обычные предметы, животные и слова.\n"
        f"• **Отгадай игру** — {len(GAME_WORDS)} популярных ПК и мобильных видеоигр!",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("start_mode_"))
def start_selected_game_mode(call):
    chat_id = call.message.chat.id
    user = call.from_user
    mode = call.data.replace("start_mode_", "", 1)

    if chat_id in CROCODILE_GAMES:
        bot.answer_callback_query(call.id, "Игра уже запущена!", show_alert=True)
        return

    bot.delete_message(chat_id, call.message.message_id)
    send_croc_round_message(chat_id, user.id, user.first_name, mode, "🎉 **Игра запущенa!**\n\n")

@bot.callback_query_handler(func=lambda call: call.data == "croc_show_word")
def croc_show_word(call):
    chat_id = call.message.chat.id
    if chat_id not in CROCODILE_GAMES:
        bot.answer_callback_query(call.id, "Эта игра уже закончилась!", show_alert=True)
        return
        
    game = CROCODILE_GAMES[chat_id]
    if call.from_user.id != game["host_id"]:
        bot.answer_callback_query(call.id, f"Эй! Ты не ведущий, тебе смотреть нельзя! Ведущий: {game['host_name']} 😡", show_alert=True)
        return
        
    bot.answer_callback_query(call.id, f"Твоя цель:\n\n{game['display_word'].upper()}\n\nОбъясни это остальным!", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "croc_skip_word")
def croc_skip_word(call):
    chat_id = call.message.chat.id
    if chat_id not in CROCODILE_GAMES:
        bot.answer_callback_query(call.id, "Игра не активна!", show_alert=True)
        return

    game = CROCODILE_GAMES[chat_id]
    if call.from_user.id != game["host_id"]:
        bot.answer_callback_query(call.id, "Только ведущий может менять слово!", show_alert=True)
        return

    display_word, answers = generate_word(game["mode"])
    game["display_word"] = display_word
    game["answers"] = answers
    
    bot.answer_callback_query(call.id, f"Новое слово выбрано! Нажми 'Загаданное слово', чтобы узнать его.", show_alert=True)
    bot.send_message(chat_id, f"🔄 **{game['host_name']}** поменял(а) слово! Отгадываем заново!", parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "croc_change_mode")
def croc_change_mode(call):
    chat_id = call.message.chat.id
    if chat_id not in CROCODILE_GAMES:
        bot.answer_callback_query(call.id, "Игра не активна!", show_alert=True)
        return

    game = CROCODILE_GAMES[chat_id]
    if call.from_user.id != game["host_id"]:
        bot.answer_callback_query(call.id, "Только ведущий может сменить режим!", show_alert=True)
        return

    new_mode = "games" if game["mode"] == "classic" else "classic"
    display_word, answers = generate_word(new_mode)
    game["mode"] = new_mode
    game["display_word"] = display_word
    game["answers"] = answers

    mode_title = "🎮 Отгадай игру" if new_mode == "games" else "🐊 Классический Крокодил"
    bot.answer_callback_query(call.id, f"Режим изменен на: {mode_title}", show_alert=True)
    bot.send_message(chat_id, f"🔀 **{game['host_name']}** сменил(а) режим на **{mode_title}**! Слово обновлено.", parse_mode="Markdown")

def generate_word(mode):
    if mode == "classic":
        # Если слова скачались — берем оттуда, иначе из локальной подстраховки
        if ONLINE_WORDS:
            selected_word = random.choice(ONLINE_WORDS)
        else:
            selected_word = random.choice(CROCODILE_WORDS)
            
        return selected_word.capitalize(), [selected_word.lower()]
    else:
        game_item = random.choice(GAME_WORDS)
        return game_item["display"], game_item["answers"]

# ==========================================
# ЭКОНОМИКА, МАГАЗИН И РП
# ==========================================

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["баланс", "монеты", "коинс"])
def show_balance(message):
    u_data = get_user_data(message.from_user.id)
    update_passive_coins(u_data)
    bot.send_message(
        message.chat.id,
        f"🪙 Баланс пользователя **{message.from_user.first_name}**: `{u_data['coins']} некокойнов`",
        parse_mode="Markdown",
        reply_to_message_id=message.message_id
    )

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() == "профиль")
def show_profile(message):
    user = message.from_user
    u_data = get_user_data(user.id)
    update_passive_coins(u_data)
    
    inv = ", ".join([SHOP_ITEMS[item]["name"] for item in u_data["inventory"]]) or "Пусто"
    
    text = (
        f"👤 **Профиль: {user.first_name}**\n\n"
        f"🪙 Баланс: `{u_data['coins']} некокойнов`\n"
        f"🎒 Инвентарь: {inv}\n"
    )
    
    now = time.time()
    if u_data["ramen_expires_at"] > now:
        rem_min = int((u_data["ramen_expires_at"] - now) // 60)
        text += f"🍜 Рамен активен еще: `{rem_min} мин.`\n"
        
    text += (
        f"\n📊 Статистика РП:\n"
        f" • Всего действий: `{u_data['stats']['actions']}`\n"
        f" • Объятий: `{u_data['stats']['hugs']}`\n"
        f" • Поцелуев: `{u_data['stats']['kisses']}`\n\n"
        "🛠 **Управление эффектами:**\nнажимай на кнопки ниже, чтобы включить или выключить их:"
    )
    
    markup = InlineKeyboardMarkup(row_width=1)
    for item_key in u_data["inventory"]:
        item_name = SHOP_ITEMS[item_key]["name"]
        is_active = item_key in u_data["active_effects"]
        status_icon = "🟢 ВКЛ" if is_active else "🔴 ВЫКЛ"
        markup.add(InlineKeyboardButton(f"{item_name} [{status_icon}]", callback_data=f"toggle_{item_key}"))
        
    if not u_data["inventory"]:
        markup.add(InlineKeyboardButton("🛍 В магазин", callback_data="goto_shop"))

    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=markup, reply_to_message_id=message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith("toggle_"))
def toggle_effect(call):
    user_id = call.from_user.id
    item_key = call.data.replace("toggle_", "", 1)
    u_data = get_user_data(user_id)
    
    if item_key not in u_data["inventory"]:
        bot.answer_callback_query(call.id, "У тебя нет этого предмета!", show_alert=True)
        return
        
    if item_key in u_data["active_effects"]:
        u_data["active_effects"].remove(item_key)
        bot.answer_callback_query(call.id, "Эффект выключен!")
    else:
        u_data["active_effects"].append(item_key)
        bot.answer_callback_query(call.id, "Эффект успешно активирован!")
        
    try:
        show_profile_edited(call.message, user_id)
    except:
        pass

def show_profile_edited(message, user_id):
    u_data = get_user_data(user_id)
    inv = ", ".join([SHOP_ITEMS[item]["name"] for item in u_data["inventory"]]) or "Пусто"
    
    text = (
        f"👤 **Профиль**\n\n"
        f"🪙 Баланс: `{u_data['coins']} некокойнов`\n"
        f"🎒 Инвентарь: {inv}\n"
    )
    now = time.time()
    if u_data["ramen_expires_at"] > now:
        rem_min = int((u_data["ramen_expires_at"] - now) // 60)
        text += f"🍜 Рамен активен еще: `{rem_min} мин.`\n"
        
    text += "\n🛠 **Управление эффектами:**"
    
    markup = InlineKeyboardMarkup(row_width=1)
    for item_key in u_data["inventory"]:
        item_name = SHOP_ITEMS[item_key]["name"]
        is_active = item_key in u_data["active_effects"]
        status_icon = "🟢 ВКЛ" if is_active else "🔴 ВЫКЛ"
        markup.add(InlineKeyboardButton(f"{item_name} [{status_icon}]", callback_data=f"toggle_{item_key}"))
        
    bot.edit_message_text(text, message.chat.id, message.message_id, parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() == "магазин")
def show_shop(message):
    markup = InlineKeyboardMarkup(row_width=1)
    for key, item in SHOP_ITEMS.items():
        markup.add(InlineKeyboardButton(f"{item['name']} — {item['price']} 🪙", callback_data=f"buy_{key}"))
    
    bot.send_message(
        message.chat.id,
        "🛍 **Неко-Магазин товаров**\n\n(Купить каждый товар можно 1 раз в сутки):\nВыбирай позицию:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "goto_shop")
def callback_goto_shop(call):
    show_shop(call.message)

@bot.callback_query_handler(func=lambda call: call.data.startswith("buy_"))
def buy_item(call):
    user_id = call.from_user.id
    item_key = call.data.replace("buy_", "", 1)
    u_data = get_user_data(user_id)
    
    if item_key not in SHOP_ITEMS:
        bot.answer_callback_query(call.id, "Товар не найден!")
        return
        
    item = SHOP_ITEMS[item_key]
    
    now = time.time()
    last_buy = u_data["purchase_cooldowns"].get(item_key, 0)
    if now - last_buy < 86400:
        hours_left = int((86400 - (now - last_buy)) // 3600)
        bot.answer_callback_query(call.id, f"Купить этот товар можно будет через {hours_left} ч. (кулдаун 1 день)", show_alert=True)
        return
        
    if u_data["coins"] < item["price"]:
        bot.answer_callback_query(call.id, f"Не хватает некокойнов! Нужно {item['price']} 🪙", show_alert=True)
        return
        
    u_data["coins"] -= item["price"]
    u_data["purchase_cooldowns"][item_key] = now
    
    if item_key == "ramen":
        u_data["ramen_expires_at"] = now + 3600
        if "ramen" not in u_data["inventory"]:
            u_data["inventory"].append("ramen")
        if "ramen" not in u_data["active_effects"]:
            u_data["active_effects"].append("ramen")
        bot.answer_callback_query(call.id, "🍜 Ты съел Рамен! Эффект 'Даттебаё' активирован на 1 час!", show_alert=True)
    else:
        if item_key not in u_data["inventory"]:
            u_data["inventory"].append(item_key)
        bot.answer_callback_query(call.id, f"Успешная покупка: {item['name']}!", show_alert=True)
        
    bot.edit_message_text(
        f"✅ Вы успешно приобрели **{item['name']}**!\nПроверить инвентарь и включить эффект можно написав слово `профиль`.",
        call.message.chat.id,
        call.message.message_id,
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["награда", "/daily"])
def daily_reward(message):
    user_id = message.from_user.id
    u_data = get_user_data(user_id)
    update_passive_coins(u_data)
    now = time.time()
    
    if now - u_data["last_daily"] < 86400:
        left = int((86400 - (now - u_data["last_daily"])) // 3600)
        bot.send_message(message.chat.id, f"⏳ Ты уже забирал награду. Следующая будет доступна через {left} ч.", reply_to_message_id=message.message_id)
        return
        
    u_data["last_daily"] = now
    reward = 50
    u_data["coins"] += reward
    bot.send_message(message.chat.id, f"🎁 Ежедневная награда получена! Тебе начислено `{reward} некокойнов` 🪙", parse_mode="Markdown", reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["кастомрп", "кастом", "рппанель"])
def rp_panel_word(message):
    chat_id = message.chat.id
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("➕ Добавить РП-команду", callback_data="rp_menu_add"),
        InlineKeyboardButton("📜 Список кастомных команд", callback_data="rp_menu_list"),
        InlineKeyboardButton("🗑 Удалить кастомную команду", callback_data="rp_menu_del")
    )
    bot.send_message(
        chat_id,
        "🛠 **Панель кастомных РП-команд**\n\nВыбирай нужное действие:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith("rp_menu_"))
def rp_menu_callback(call):
    chat_id = call.message.chat.id
    user_id = call.from_user.id
    data = call.data
    
    if data == "rp_menu_add":
        USER_ADDING_STATE[user_id] = chat_id
        bot.answer_callback_query(call.id)
        bot.send_message(
            chat_id,
            "✍️ **Создание новой РП-команды**\n\n"
            "Отправь в чат данные в формате:\n"
            "`название | текст_для_двоих | текст_одного | ссылка_на_гифку`",
            parse_mode="Markdown"
        )
    elif data == "rp_menu_list":
        bot.answer_callback_query(call.id)
        customs = CHAT_CUSTOM_RP.get(chat_id, {})
        if not customs:
            bot.send_message(chat_id, "📜 В этом чате нет кастомных команд.")
        else:
            lst = "\n".join([f"🔹 `{name}`" for name in customs.keys()])
            bot.send_message(chat_id, f"📜 **Кастомные команды:**\n\n{lst}", parse_mode="Markdown")
    elif data == "rp_menu_del":
        bot.answer_callback_query(call.id)
        customs = CHAT_CUSTOM_RP.get(chat_id, {})
        if not customs:
            bot.send_message(chat_id, "🗑 Удалять нечего.")
            return
        markup = InlineKeyboardMarkup(row_width=2)
        buttons = [InlineKeyboardButton(name, callback_data=f"rp_del_{name}") for name in customs.keys()]
        markup.add(*buttons)
        bot.send_message(chat_id, "🗑 **Выбери команду для удаления:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("rp_del_"))
def rp_delete_callback(call):
    chat_id = call.message.chat.id
    cmd_name = call.data.replace("rp_del_", "", 1)
    if chat_id in CHAT_CUSTOM_RP and cmd_name in CHAT_CUSTOM_RP[chat_id]:
        del CHAT_CUSTOM_RP[chat_id][cmd_name]
        bot.answer_callback_query(call.id, f"Команда '{cmd_name}' удалена!")
        bot.edit_message_text(f"🗑 Команда **{cmd_name}** удалена!", chat_id, call.message.message_id, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.from_user.id in USER_ADDING_STATE)
def process_new_rp(message):
    user_id = message.from_user.id
    chat_id = USER_ADDING_STATE.pop(user_id, None)
    if not chat_id or message.chat.id != chat_id or not message.text:
        return
    parts = message.text.split("|")
    if len(parts) < 4:
        bot.send_message(chat_id, "❌ Ошибка формата! Нужно 4 части через `|`.", parse_mode="Markdown")
        return
    name = parts[0].strip().lower()
    CHAT_CUSTOM_RP.setdefault(chat_id, {})[name] = {
        "aliases": [name],
        "target_text": parts[1].strip(),
        "solo_text": parts[2].strip(),
        "gifs": [parts[3].strip()]
    }
    bot.send_message(chat_id, f"✅ Кастомная команда `{name}` добавлена!", parse_mode="Markdown", reply_to_message_id=message.message_id)

@bot.message_handler(func=lambda m: m.text and m.text.lower().strip() in ["команды", "помощь", "/help"])
def show_all_commands(message):
    text = (
        "📜 **Список всех команд:**\n\n"
        "🎭 **РП-команды:** поцеловать, обнять, погладить, укусить, покормить, оставить засос, флиртовать, трахнуть\n"
        "🪙 **Экономика:** баланс, профиль, магазин, награда\n"
        "🎮 **Игры:** крокодил, игры\n"
        "🛠 **Кастом:** кастомрп (панель создания)"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_to_message_id=message.message_id)

def get_rp_action(message_text, chat_id):
    if not message_text:
        return None
    text_low = message_text.lower().strip()
    if chat_id in CHAT_CUSTOM_RP:
        for action_key, data in CHAT_CUSTOM_RP[chat_id].items():
            for alias in data["aliases"]:
                if text_low.startswith(alias):
                    return data
    for action_key, data in RP_COMMANDS.items():
        for alias in data["aliases"]:
            if text_low.startswith(alias):
                return data
    return None

@bot.message_handler(func=lambda m: get_rp_action(m.text, m.chat.id) is not None)
def handle_rp(message):
    user = message.from_user
    u_data = get_user_data(user.id)
    update_passive_coins(u_data)
    
    gain = 3 if "ears" in u_data["active_effects"] else 1
    u_data["coins"] += gain
    u_data["stats"]["actions"] += 1
    if "обнять" in message.text.lower():
        u_data["stats"]["hugs"] += 1
    elif "поцеловать" in message.text.lower() or "поцелуй" in message.text.lower():
        u_data["stats"]["kisses"] += 1

    action_data = get_rp_action(message.text, message.chat.id)
    sender = user.first_name

    if message.reply_to_message:
        target = message.reply_to_message.from_user.first_name
        text = action_data["target_text"].format(sender=sender, target=target)
    else:
        text = action_data["solo_text"].format(sender=sender)

    prefix = ""
    if "ears" in u_data["active_effects"]:
        prefix += "мурр..~ "
    if "rose" in u_data["active_effects"]:
        prefix += "🌹 *с нежным трепетом* — "
    if "crown" in u_data["active_effects"]:
        prefix += "👑 Господин, "

    text = prefix + text

    gifs = action_data["gifs"]
    if gifs:
        gif_to_send = random.choice(gifs)
        formatted_text = f"{text}\n<a href='{gif_to_send}'>&#8204;</a>"
        bot.send_message(message.chat.id, text=formatted_text, parse_mode="HTML", reply_to_message_id=message.message_id)
    else:   
        bot.send_message(message.chat.id, text=text, parse_mode="HTML", reply_to_message_id=message.message_id)

# ==========================================
# ОБЩИЙ ОБРАБОТЧИК (Проверка ответов в игре + Авто-смена ведущего)
# ==========================================
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    if not message.text:
        return
        
    chat_id = message.chat.id
    user_id = message.from_user.id
    text = message.text.lower().strip()
    
    # Пассивный фарм от рамена
    u_data = get_user_data(user_id)
    update_passive_coins(u_data)

    # 🐊 Логика проверки победы и авто-передачи очереди
    if chat_id in CROCODILE_GAMES:
        game = CROCODILE_GAMES[chat_id]
        
        if text in ["сдаемся", "стоп крокодил", "стоп"]:
            bot.send_message(
                chat_id, 
                f"🛑 **Игра остановлена!**\nЗагаданное было: **{game['display_word'].upper()}**", 
                parse_mode="Markdown"
            )
            del CROCODILE_GAMES[chat_id]
        elif text in game["answers"]:
            if user_id == game["host_id"]:
                bot.send_message(chat_id, "Эй, ведущий, нельзя угадывать свое же слово! 😅", reply_to_message_id=message.message_id)
            else:
                reward = 100
                u_data["coins"] += reward
                current_mode = game["mode"]
                
                win_text = (
                    f"🎉 **{message.from_user.first_name}** угадал(а) **{game['display_word'].upper()}**!\n"
                    f"Награда: `{reward} некокойнов` 🪙\n"
                    f"🏆 Теперь **{message.from_user.first_name}** становится новым ведущим!\n\n"
                )

                # Удаляем старый раунд и мгновенно запускаем новый для угадавшего
                del CROCODILE_GAMES[chat_id]
                send_croc_round_message(chat_id, user_id, message.from_user.first_name, current_mode, prefix_text=win_text)

# ==========================================
# ЗАПУСК БОТА И ВЕБ-СЕРВЕРА
# ==========================================
def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    
    print("Бот запущен и работает!")
    while True:
        try:
            bot.infinity_polling(timeout=10, long_polling_timeout=5)
        except Exception as e:
            print(f"Ошибка бота: {e}")
            time.sleep(5)
            
            