import asyncio
import threading
import requests
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import re
from flask import Flask, render_template_string, request

app = Flask(__name__)

# ────────────────────────────────────────────────
#                  AYARLAR
# ────────────────────────────────────────────────

API_URL    = "http://147.135.212.197/crapi/st/viewstats"
API_TOKEN  = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="

TELEGRAM_BOT_TOKEN = "8450988435:AAFbbzEg_CDHnuIwsn6RE9C--sUT7rOUxw8"
TELEGRAM_GROUP_ID  = -1003744838706

API_PARAMS = {"token": API_TOKEN, "records": ""}

KONTROL_ARALIGI_SN = 35
SON_KAYIT_SINIR    = 8

bot = Bot(token=TELEGRAM_BOT_TOKEN)

durum = {
    "son_kontrol": "Hiç çalışmadı",
    "son_gonderilen": "Henüz yok",
    "toplam_gonderilen": 0,
    "calisiyor": False,
    "hata": None,
    "loglar": []
}

# ────────────────────────────────────────────────
#          TAM ÜLKE HARİTASI
# ────────────────────────────────────────────────

COUNTRY_MAP = {
    "1":     ("ABD / Kanada / Karayipler (çoğu)", "🇺🇸"),
    "7":     ("Rusya / Kazakistan", "🇷🇺"),
    "20":    ("Mısır", "🇪🇬"),
    "27":    ("Güney Afrika", "🇿🇦"),
    "30":    ("Yunanistan", "🇬🇷"),
    "31":    ("Hollanda", "🇳🇱"),
    "32":    ("Belçika", "🇧🇪"),
    "33":    ("Fransa", "🇫🇷"),
    "34":    ("İspanya", "🇪🇸"),
    "36":    ("Macaristan", "🇭🇺"),
    "39":    ("İtalya / Vatikan", "🇮🇹"),
    "40":    ("Romanya", "🇷🇴"),
    "41":    ("İsviçre", "🇨🇭"),
    "43":    ("Avusturya", "🇦🇹"),
    "44":    ("Birleşik Krallık", "🇬🇧"),
    "45":    ("Danimarka", "🇩🇰"),
    "46":    ("İsveç", "🇸🇪"),
    "47":    ("Norveç", "🇳🇴"),
    "48":    ("Polonya", "🇵🇱"),
    "49":    ("Almanya", "🇩🇪"),
    "51":    ("Peru", "🇵🇪"),
    "52":    ("Meksika", "🇲🇽"),
    "53":    ("Küba", "🇨🇺"),
    "54":    ("Arjantin", "🇦🇷"),
    "55":    ("Brezilya", "🇧🇷"),
    "56":    ("Şili", "🇨🇱"),
    "57":    ("Kolombiya", "🇨🇴"),
    "58":    ("Venezuela", "🇻🇪"),
    "60":    ("Malezya", "🇲🇾"),
    "61":    ("Avustralya", "🇦🇺"),
    "62":    ("Endonezya", "🇮🇩"),
    "63":    ("Filipinler", "🇵🇭"),
    "64":    ("Yeni Zelanda", "🇳🇿"),
    "65":    ("Singapur", "🇸🇬"),
    "66":    ("Tayland", "🇹🇭"),
    "81":    ("Japonya", "🇯🇵"),
    "82":    ("Güney Kore", "🇰🇷"),
    "84":    ("Vietnam", "🇻🇳"),
    "86":    ("Çin", "🇨🇳"),
    "90":    ("Türkiye", "🇹🇷"),
    "91":    ("Hindistan", "🇮🇳"),
    "92":    ("Pakistan", "🇵🇰"),
    "93":    ("Afganistan", "🇦🇫"),
    "94":    ("Sri Lanka", "🇱🇰"),
    "95":    ("Myanmar", "🇲🇲"),
    "98":    ("İran", "🇮🇷"),
    "211":   ("Güney Sudan", "🇸🇸"),
    "212":   ("Fas", "🇲🇦"),
    "213":   ("Cezayir", "🇩🇿"),
    "216":   ("Tunus", "🇹🇳"),
    "218":   ("Libya", "🇱🇾"),
    "220":   ("Gambiya", "🇬🇲"),
    "221":   ("Senegal", "🇸🇳"),
    "222":   ("Moritanya", "🇲🇷"),
    "223":   ("Mali", "🇲🇱"),
    "224":   ("Gine", "🇬🇳"),
    "225":   ("Fildişi Sahili", "🇨🇮"),
    "226":   ("Burkina Faso", "🇧🇫"),
    "227":   ("Nijer", "🇳🇪"),
    "228":   ("Togo", "🇹🇬"),
    "229":   ("Benin", "🇧🇯"),
    "230":   ("Mauritius", "🇲🇺"),
    "231":   ("Liberya", "🇱🇷"),
    "232":   ("Sierra Leone", "🇸🇱"),
    "233":   ("Gana", "🇬🇭"),
    "234":   ("Nijerya", "🇳🇬"),
    "235":   ("Çad", "🇹🇩"),
    "236":   ("Orta Afrika Cumhuriyeti", "🇨🇫"),
    "237":   ("Kamerun", "🇨🇲"),
    "238":   ("Cape Verde", "🇨🇻"),
    "239":   ("Sao Tome ve Principe", "🇸🇹"),
    "240":   ("Ekvator Ginesi", "🇬🇶"),
    "241":   ("Gabon", "🇬🇦"),
    "242":   ("Kongo", "🇨🇬"),
    "243":   ("Demokratik Kongo Cumhuriyeti", "🇨🇩"),
    "244":   ("Angola", "🇦🇴"),
    "248":   ("Seyşeller", "🇸🇨"),
    "249":   ("Sudan", "🇸🇩"),
    "250":   ("Ruanda", "🇷🇼"),
    "251":   ("Etiyopya", "🇪🇹"),
    "252":   ("Somali", "🇸🇴"),
    "253":   ("Cibuti", "🇩🇯"),
    "254":   ("Kenya", "🇰🇪"),
    "255":   ("Tanzanya", "🇹🇿"),
    "256":   ("Uganda", "🇺🇬"),
    "257":   ("Burundi", "🇧🇮"),
    "258":   ("Mozambik", "🇲🇿"),
    "260":   ("Zambiya", "🇿🇲"),
    "261":   ("Madagaskar", "🇲🇬"),
    "262":   ("Réunion / Mayotte", "🇷🇪"),
    "263":   ("Zimbabve", "🇿🇼"),
    "264":   ("Namibya", "🇳🇦"),
    "265":   ("Malavi", "🇲🇼"),
    "266":   ("Lesotho", "🇱🇸"),
    "267":   ("Botsvana", "🇧🇼"),
    "268":   ("Esvatini", "🇸🇿"),
    "269":   ("Komorlar", "🇰🇲"),
    "290":   ("Saint Helena", "🇸🇭"),
    "291":   ("Eritre", "🇪🇷"),
    "297":   ("Aruba", "🇦🇼"),
    "298":   ("Faroe Adaları", "🇫🇴"),
    "299":   ("Grönland", "🇬🇱"),
    "350":   ("Cebelitarık", "🇬🇮"),
    "351":   ("Portekiz", "🇵🇹"),
    "352":   ("Lüksemburg", "🇱🇺"),
    "353":   ("İrlanda", "🇮🇪"),
    "354":   ("İzlanda", "🇮🇸"),
    "355":   ("Arnavutluk", "🇦🇱"),
    "356":   ("Malta", "🇲🇹"),
    "357":   ("Kıbrıs", "🇨🇾"),
    "358":   ("Finlandiya", "🇫🇮"),
    "359":   ("Bulgaristan", "🇧🇬"),
    "370":   ("Litvanya", "🇱🇹"),
    "371":   ("Letonya", "🇱🇻"),
    "372":   ("Estonya", "🇪🇪"),
    "373":   ("Moldova", "🇲🇩"),
    "374":   ("Ermenistan", "🇦🇲"),
    "375":   ("Belarus", "🇧🇾"),
    "376":   ("Andorra", "🇦🇩"),
    "377":   ("Monako", "🇲🇨"),
    "378":   ("San Marino", "🇸🇲"),
    "379":   ("Vatikan", "🇻🇦"),
    "380":   ("Ukrayna", "🇺🇦"),
    "381":   ("Sırbistan", "🇷🇸"),
    "382":   ("Karadağ", "🇲🇪"),
    "383":   ("Kosova", "🇽🇰"),
    "385":   ("Hırvatistan", "🇭🇷"),
    "386":   ("Slovenya", "🇸🇮"),
    "387":   ("Bosna Hersek", "🇧🇦"),
    "389":   ("Kuzey Makedonya", "🇲🇰"),
    "420":   ("Çekya", "🇨🇿"),
    "421":   ("Slovakya", "🇸🇰"),
    "423":   ("Lihtenştayn", "🇱🇮"),
    "500":   ("Falkland Adaları", "🇫🇰"),
    "501":   ("Belize", "🇧🇿"),
    "502":   ("Guatemala", "🇬🇹"),
    "503":   ("El Salvador", "🇸🇻"),
    "504":   ("Honduras", "🇭🇳"),
    "505":   ("Nikaragua", "🇳🇮"),
    "506":   ("Kosta Rika", "🇨🇷"),
    "507":   ("Panama", "🇵🇦"),
    "509":   ("Haiti", "🇭🇹"),
    "590":   ("Guadeloupe", "🇬🇵"),
    "591":   ("Bolivya", "🇧🇴"),
    "592":   ("Guyana", "🇬🇾"),
    "593":   ("Ekvador", "🇪🇨"),
    "594":   ("Fransız Guyanası", "🇬🇫"),
    "595":   ("Paraguay", "🇵🇾"),
    "596":   ("Martinik", "🇲🇶"),
    "597":   ("Surinam", "🇸🇷"),
    "598":   ("Uruguay", "🇺🇾"),
    "670":   ("Doğu Timor", "🇹🇱"),
    "672":   ("Norfolk Adası", "🇳🇫"),
    "673":   ("Brunei", "🇧🇳"),
    "674":   ("Nauru", "🇳🇷"),
    "675":   ("Papua Yeni Gine", "🇵🇬"),
    "676":   ("Tonga", "🇹🇴"),
    "677":   ("Solomon Adaları", "🇸🇧"),
    "678":   ("Vanuatu", "🇻🇺"),
    "679":   ("Fiji", "🇫🇯"),
    "680":   ("Palau", "🇵🇼"),
    "681":   ("Wallis ve Futuna", "🇼🇫"),
    "682":   ("Cook Adaları", "🇨🇰"),
    "683":   ("Niue", "🇳🇺"),
    "685":   ("Samoa", "🇼🇸"),
    "686":   ("Kiribati", "🇰🇮"),
    "687":   ("Yeni Kaledonya", "🇳🇨"),
    "688":   ("Tuvalu", "🇹🇻"),
    "689":   ("Fransız Polinezyası", "🇵🇫"),
    "690":   ("Tokelau", "🇹🇰"),
    "691":   ("Mikronezya", "🇫🇲"),
    "692":   ("Marshall Adaları", "🇲🇭"),
    "850":   ("Kuzey Kore", "🇰🇵"),
    "852":   ("Hong Kong", "🇭🇰"),
    "853":   ("Makao", "🇲🇴"),
    "855":   ("Kamboçya", "🇰🇭"),
    "856":   ("Laos", "🇱🇦"),
    "880":   ("Bangladeş", "🇧🇩"),
    "886":   ("Tayvan", "🇹🇼"),
    "960":   ("Maldivler", "🇲🇻"),
    "961":   ("Lübnan", "🇱🇧"),
    "962":   ("Ürdün", "🇯🇴"),
    "963":   ("Suriye", "🇸🇾"),
    "964":   ("Irak", "🇮🇶"),
    "965":   ("Kuveyt", "🇰🇼"),
    "966":   ("Suudi Arabistan", "🇸🇦"),
    "967":   ("Yemen", "🇾🇪"),
    "968":   ("Umman", "🇴🇲"),
    "970":   ("Filistin", "🇵🇸"),
    "971":   ("Birleşik Arap Emirlikleri", "🇦🇪"),
    "972":   ("İsrail", "🇮🇱"),
    "973":   ("Bahreyn", "🇧🇭"),
    "974":   ("Katar", "🇶🇦"),
    "975":   ("Butan", "🇧🇹"),
    "976":   ("Moğolistan", "🇲🇳"),
    "977":   ("Nepal", "🇳🇵"),
    "992":   ("Tacikistan", "🇹🇯"),
    "993":   ("Türkmenistan", "🇹🇲"),
    "994":   ("Azerbaycan", "🇦🇿"),
    "995":   ("Gürcistan", "🇬🇪"),
    "996":   ("Kırgızistan", "🇰🇬"),
    "998":   ("Özbekistan", "🇺🇿"),
    "1242":  ("Bahamalar", "🇧🇸"),
    "1246":  ("Barbados", "🇧🇧"),
    "1264":  ("Anguilla", "🇦🇮"),
    "1268":  ("Antigua ve Barbuda", "🇦🇬"),
    "1473":  ("Grenada", "🇬🇩"),
}

# ────────────────────────────────────────────────
#              YARDIMCI FONKSİYONLAR
# ────────────────────────────────────────────────

def md_escape(text):
    chars = r'_*[]()\\\\~`>#+-=|{}.!'
    return ''.join('\\' + c if c in chars else c for c in str(text))

def api_den_cek():
    try:
        r = requests.get(API_URL, params=API_PARAMS, timeout=15)
        r.raise_for_status()
        if not r.text.strip():
            return []
        try:
            veri = r.json()
            return veri if isinstance(veri, list) else []
        except:
            satirlar = r.text.strip().split("\n")
            kayitlar = []
            for s in satirlar:
                parcalar = s.split("|")
                if len(parcalar) >= 4:
                    kayitlar.append([p.strip() for p in parcalar[:4]])
            return kayitlar
    except Exception as e:
        print(f"API hatası: {e}")
        return []

def zaman_coz(ts_str):
    try:
        return datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
    except:
        return None

def ulke_bul(phone):
    temiz = phone.lstrip('+0 ')
    for kod in sorted(COUNTRY_MAP.keys(), key=len, reverse=True):
        if temiz.startswith(kod):
            return COUNTRY_MAP[kod]
    return "Bilinmeyen Ülke", "🌍"

def otp_cikar(mesaj):
    desenler = [
        r'(?:code|kod|kodu|رمز|كود|验证码|codice|code is|your code|kodunuz)[\s:=-]{0,4}(\d{4,7})',
        r'\b(\d{4,7})\b',
        r'(?:Your\s+WhatsApp\s+code)[:\s]*(\d{6})',
        r'\b(\d{6})\b',
    ]
    for pat in desenler:
        eslesme = re.search(pat, mesaj, re.IGNORECASE)
        if eslesme:
            kod = re.sub(r'[^0-9]', '', eslesme.group(1))
            if 4 <= len(kod) <= 7:
                return kod
    return "Bulunamadı"

async def telegram_gonder(mesaj, tuslar):
    try:
        await bot.send_message(
            chat_id=TELEGRAM_GROUP_ID,
            text=mesaj,
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup(tuslar),
            disable_web_page_preview=True
        )
        return True
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")
        return False

# ────────────────────────────────────────────────
#         ARKA PLAN DÖNGÜSÜ
# ────────────────────────────────────────────────

son_gorulen_zaman = None

async def otp_kontrol_loop():
    global son_gorulen_zaman
    while durum["calisiyor"]:
        try:
            durum["son_kontrol"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            kayitlar = api_den_cek()
            if not kayitlar:
                await asyncio.sleep(KONTROL_ARALIGI_SN)
                continue

            yeni_kayitlar = []
            if son_gorulen_zaman is None:
                yeni_kayitlar = kayitlar[:SON_KAYIT_SINIR]
                if yeni_kayitlar:
                    son_gorulen_zaman = zaman_coz(yeni_kayitlar[0][3])
            else:
                for satir in kayitlar:
                    ts = zaman_coz(satir[3])
                    if ts and ts > son_gorulen_zaman:
                        yeni_kayitlar.append(satir)

            if yeni_kayitlar:
                son_gorulen_zaman = zaman_coz(yeni_kayitlar[0][3])
                print(f"→ {len(yeni_kayitlar)} yeni OTP")

                for satir in yeni_kayitlar[::-1]:
                    uygulama = satir[0]
                    numara   = satir[1]
                    icerik   = satir[2].replace('\n', ' ').replace('  ', ' ')
                    zaman    = satir[3]

                    ulke_adi, bayrak = ulke_bul(numara)
                    maskeli = numara[:4] + "••••" + numara[-4:] if len(numara) >= 10 else numara
                    otp = otp_cikar(icerik)

                    mesaj = (
                        f"📨 *Yeni OTP Geldi*\n"
                        f"────────────────────────────\n"
                        f"🕒 {md_escape(zaman)}\n"
                        f"🌍 {md_escape(ulke_adi)} {bayrak}\n"
                        f"📱 `{md_escape(maskeli)}`\n"
                        f"🛠️ {md_escape(uygulama)}\n"
                        f"🔐 ```{md_escape(otp)}```\n"
                        f"────────────────────────────\n"
                        f"{md_escape(icerik[:380])}{' …' if len(icerik) > 380 else ''}\n"
                    )

                    tuslar = [
                        [
                            InlineKeyboardButton("👤 @Vexorp", url="https://t.me/Vexorp"),
                            InlineKeyboardButton("📢 Kanal", url="https://t.me/+wdMrCqP5yDM2OWJk")
                        ]
                    ]

                    if await telegram_gonder(mesaj, tuslar):
                        durum["son_gonderilen"] = f"{zaman} - {maskeli} ({otp})"
                        durum["toplam_gonderilen"] += 1

                        yeni_log = {
                            "zaman": zaman,
                            "numara": maskeli,
                            "otp": otp,
                            "uygulama": uygulama,
                            "ulke": f"{ulke_adi} {bayrak}"
                        }
                        durum["loglar"].insert(0, yeni_log)
                        if len(durum["loglar"]) > 2000:
                            durum["loglar"] = durum["loglar"][:2000]

        except Exception as e:
            durum["hata"] = str(e)
            print(f"Döngü hatası: {e}")

        await asyncio.sleep(KONTROL_ARALIGI_SN)

# ────────────────────────────────────────────────
#         FLASK ROUTE'LAR
# ────────────────────────────────────────────────

@app.route("/")
def dashboard():
    try:
        html = r"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>VEXORP OTP Panel</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
            <style>
                :root { --bg:#0d1117; --surface:#161b22; --accent:#58a6ff; --green:#3fb950; --red:#f85149; --text:#c9d1d9; --dim:#8b949e; --border:#30363d; }
                body { font-family:system-ui,sans-serif; background:var(--bg); color:var(--text); margin:0; padding:2rem; min-height:100vh; }
                .container { max-width:900px; margin:0 auto; }
                h1 { color:var(--accent); text-align:center; margin-bottom:2rem; }
                .status { background:var(--surface); padding:1.5rem; border-radius:12px; border:1px solid var(--border); margin-bottom:2rem; }
                .status p { margin:0.8rem 0; font-size:1.1rem; }
                .value { font-weight:600; }
                .running { color:var(--green); }
                .stopped { color:var(--red); }
                .controls { text-align:center; margin:2rem 0; }
                .btn { padding:0.9rem 1.8rem; margin:0.5rem; font-size:1.05rem; border:none; border-radius:8px; cursor:pointer; color:white; transition:0.2s; }
                .btn-start { background:var(--green); }
                .btn-stop { background:var(--red); }
                .btn-refresh { background:#444c56; }
                .btn:hover { opacity:0.9; transform:scale(1.03); }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>VEXORP OTP Panel</h1>
                <div class="status">
                    <p>Durum ............ : <span class="value {% if calisiyor %}running{% else %}stopped{% endif %}">{{ 'ÇALIŞIYOR' if calisiyor else 'DURDURULDU' }}</span></p>
                    <p>Son kontrol ...... : <span class="value">{{ son_kontrol }}</span></p>
                    <p>Son gönderilen ... : <span class="value">{{ son_gonderilen }}</span></p>
                    <p>Toplam gönderilen : <span class="value">{{ toplam_gonderilen }}</span></p>
                    {% if hata %}
                    <p style="color:var(--red);">Hata ............. : {{ hata }}</p>
                    {% endif %}
                </div>
                <div class="controls">
                    <form method="post" action="/kontrol">
                        <button type="submit" name="action" value="start" class="btn btn-start">Başlat ▶</button>
                        <button type="submit" name="action" value="stop" class="btn btn-stop">Durdur ■</button>
                        <button type="submit" name="action" value="status" class="btn btn-refresh">Yenile</button>
                    </form>
                </div>
                <p style="text-align:center; margin-top:3rem;">
                    <a href="/loglar" style="color:var(--accent); text-decoration:none;">→ OTP Loglarını Görüntüle ←</a>
                </p>
            </div>
        </body>
        </html>
        """
        return render_template_string(html, **durum)
    except Exception as e:
        return f"<h1>500 Hatası</h1><pre>{str(e)}</pre>"

@app.route("/loglar")
def loglar_sayfasi():
    try:
        loglar = durum.get("loglar", [])
        html = r"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>OTP Logları - VEXORP</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css"/>
            <style>
                :root { --bg:#0d1117; --surface:#161b22; --accent:#58a6ff; --green:#3fb950; --text:#c9d1d9; --dim:#8b949e; --border:#30363d; }
                body { font-family:system-ui,sans-serif; background:var(--bg); color:var(--text); margin:0; padding:2rem; }
                .container { max-width:1100px; margin:0 auto; }
                h1 { color:var(--accent); text-align:center; margin-bottom:1.5rem; }
                .back { text-align:center; margin-bottom:1.5rem; }
                .back a { color:var(--accent); text-decoration:none; font-size:1.1rem; }
                .search { margin:1.5rem 0; text-align:center; }
                #searchInput { width:100%; max-width:500px; padding:0.8rem; background:#0d1117; border:1px solid var(--border); border-radius:8px; color:var(--text); font-size:1rem; }
                table { width:100%; border-collapse:collapse; background:var(--surface); border-radius:10px; overflow:hidden; box-shadow:0 4px 20px rgba(0,0,0,0.4); }
                th, td { padding:1rem; text-align:left; border-bottom:1px solid var(--border); }
                th { background:#0d1117; color:var(--accent); cursor:pointer; }
                tr:hover { background:#1f2937; }
                .otp-code { background:rgba(63,185,80,0.15); color:var(--green); padding:0.3rem 0.7rem; border-radius:6px; font-family:monospace; }
                .pagination { margin:2rem 0; text-align:center; }
                .page-btn { padding:0.6rem 1.2rem; margin:0.3rem; background:#21262d; border:1px solid var(--border); border-radius:6px; color:var(--text); cursor:pointer; }
                .page-btn.active { background:var(--accent); color:#0d1117; }
                .page-btn:disabled { opacity:0.4; cursor:not-allowed; }
                .empty { text-align:center; padding:4rem; color:var(--dim); font-size:1.2rem; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>OTP Logları</h1>
                <div class="back"><a href="/">← Dashboard'a dön</a></div>

                <div class="search">
                    <input type="text" id="searchInput" placeholder="Numara, OTP, ülke veya uygulama ara...">
                </div>

                <table id="logTable">
                    <thead>
                        <tr>
                            <th>Zaman</th>
                            <th>Numara</th>
                            <th>OTP</th>
                            <th>Uygulama</th>
                            <th>Ülke</th>
                        </tr>
                    </thead>
                    <tbody id="logBody"></tbody>
                </table>

                <div class="pagination" id="pagination"></div>
                <div class="empty" id="noResults" style="display:none;">Sonuç bulunamadı</div>
            </div>

            <script>
                const logs = {{ loglar | tojson | safe }};
                let filtered = [...logs];
                let currentPage = 1;
                const perPage = 15;

                function renderTable() {
                    const term = document.getElementById('searchInput').value.toLowerCase();
                    filtered = logs.filter(log => 
                        Object.values(log).some(v => String(v).toLowerCase().includes(term))
                    );

                    const start = (currentPage - 1) * perPage;
                    const items = filtered.slice(start, start + perPage);

                    const tbody = document.getElementById('logBody');
                    tbody.innerHTML = '';

                    if (items.length === 0) {
                        document.getElementById('logTable').style.display = 'none';
                        document.getElementById('noResults').style.display = 'block';
                    } else {
                        document.getElementById('logTable').style.display = 'table';
                        document.getElementById('noResults').style.display = 'none';

                        items.forEach(log => {
                            const tr = document.createElement('tr');
                            tr.innerHTML = `
                                <td>${log.zaman || '-'}</td>
                                <td>${log.numara || '-'}</td>
                                <td><span class="otp-code">${log.otp || '-'}</span></td>
                                <td>${log.uygulama || '-'}</td>
                                <td>${log.ulke || '-'}</td>
                            `;
                            tbody.appendChild(tr);
                        });
                    }

                    renderPagination();
                }

                function renderPagination() {
                    const pagination = document.getElementById('pagination');
                    pagination.innerHTML = '';
                    if (filtered.length <= perPage) return;

                    const totalPages = Math.ceil(filtered.length / perPage);

                    const prev = document.createElement('button');
                    prev.className = 'page-btn';
                    prev.textContent = 'Önceki';
                    prev.disabled = currentPage === 1;
                    prev.onclick = () => { if (currentPage > 1) currentPage--, renderTable(); };
                    pagination.appendChild(prev);

                    for (let i = 1; i <= totalPages; i++) {
                        if (i === 1 || i === totalPages || Math.abs(i - currentPage) <= 2) {
                            const btn = document.createElement('button');
                            btn.className = 'page-btn' + (i === currentPage ? ' active' : '');
                            btn.textContent = i;
                            btn.onclick = () => { currentPage = i; renderTable(); };
                            pagination.appendChild(btn);
                        }
                    }

                    const next = document.createElement('button');
                    next.className = 'page-btn';
                    next.textContent = 'Sonraki';
                    next.disabled = currentPage === totalPages;
                    next.onclick = () => { if (currentPage < totalPages) currentPage++, renderTable(); };
                    pagination.appendChild(next);
                }

                document.getElementById('searchInput').addEventListener('input', () => {
                    currentPage = 1;
                    renderTable();
                });

                renderTable();
            </script>
        </body>
        </html>
        """
        return render_template_string(html, loglar=loglar)
    except Exception as e:
        return f"<h1>500 Hatası (Loglar sayfası)</h1><pre>{str(e)}</pre>"

@app.route("/kontrol", methods=["POST"])
def kontrol():
    global loop_thread
    action = request.form.get("action")

    if action == "start" and not durum["calisiyor"]:
        durum["calisiyor"] = True
        durum["hata"] = None

        def baslat():
            asyncio.run(otp_kontrol_loop())

        loop_thread = threading.Thread(target=baslat, daemon=True)
        loop_thread.start()
        print("→ OTP izleme başlatıldı")

    elif action == "stop":
        durum["calisiyor"] = False
        print("→ Durdurma sinyali gönderildi")

    return dashboard()

if __name__ == "__main__":
    print("VEXORP OTP Paneli başlatılıyor...")
    print("→ http://127.0.0.1:5000/")
    print("→ Loglar: http://127.0.0.1:5000/loglar")
    app.run(host="0.0.0.0", port=5000, debug=True)  # ← debug=True önemli!