import asyncio
import threading
import requests
from datetime import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
import re
from flask import Flask, jsonify, render_template_string, request

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

# Flask uygulaması
app = Flask(__name__)

# Durum bilgilerini tutacak
durum = {
    "son_kontrol": "Hiç çalışmadı",
    "son_gonderilen": "Henüz yok",
    "toplam_gonderilen": 0,
    "calisiyor": False,
    "hata": None
}

# ────────────────────────────────────────────────
#          TAM ÜLKE HARİTASI (neredeyse tüm ülkeler)
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
    # NANP örnekleri (isteğe bağlı detay)
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
    chars = r'_*[]()\\\~`>#+-=|{}.!'
    return ''.join('\\' + c if c in chars else c for c in str(text))


def api_den_cek():
    try:
        r = requests.get(API_URL, params=API_PARAMS, timeout=15)
        r.raise_for_status()
        if not r.text.strip():
            print("API boş cevap döndü")
            return []
        try:
            veri = r.json()
            return veri if isinstance(veri, list) else []
        except:
            print("JSON parse edilemedi, düz metin işleniyor...")
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
        # Genel OTP desenleri
        r'(?:code|kod|kodu|رمز|كود|验证码|codice|code is|your code|kodunuz)[\s:=-]{0,4}(\d{4,7})',
        r'(?:WhatsApp|Telegram|imo|Facebook|Google|Instagram)[\w\s]*(?:code|kod|verify)[\s:=]{0,4}(\d{4,7})',
        r'\b(\d{4,7})\b',

        # WhatsApp özel (çok yaygın formatlar)
        r'(?:Your\s+WhatsApp\s+code|WhatsApp\s+code|Mã\s+WhatsApp\s+của\s+bạn)[:\s]*(\d{6})',
        r'WhatsApp\s+code:\s*(\d{3}[- ]?\d{3})',
        r'(?:code|Mã|kod|Your code)[:\s-]*(\d{6})',
        r'(?:Mã xác nhận|Mã WhatsApp)[:\s]*(\d{6})',
        r'\b(\d{6})\b',  # son çare 6 haneli
    ]

    mesaj_lower = mesaj.lower()

    for pat in desenler:
        eslesme = re.search(pat, mesaj, re.IGNORECASE)
        if eslesme:
            kod = re.sub(r'[^0-9]', '', eslesme.group(1))
            if 4 <= len(kod) <= 7:
                return kod

    # Ekstra son çare: herhangi 6 haneli rakam grubu
    son_care = re.findall(r'\b\d{6}\b', mesaj)
    if son_care:
        return son_care[0]

    return "Bulunamadı"


# ────────────────────────────────────────────────
#              ASYNC GÖNDERİM
# ────────────────────────────────────────────────

async def telegram_gonder(mesaj, tuslar):
    try:
        await bot.send_message(
            chat_id=TELEGRAM_GROUP_ID,
            text=mesaj,
            parse_mode="MarkdownV2",
            reply_markup=InlineKeyboardMarkup(tuslar),
            disable_web_page_preview=True,
            disable_notification=False
        )
        return True
    except Exception as e:
        print(f"Telegram gönderim hatası: {e}")
        return False


# ────────────────────────────────────────────────
#         ARKA PLAN OTP KONTROL DÖNGÜSÜ
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
                print(f"→ {len(yeni_kayitlar)} yeni OTP tespit edildi")

                for satir in yeni_kayitlar[::-1]:
                    uygulama = satir[0]
                    numara   = satir[1]
                    icerik   = satir[2].replace('\n', ' ').replace('  ', ' ')
                    zaman    = satir[3]

                    ulke_adi, bayrak = ulke_bul(numara)
                    maskeli = numara[:4] + "••••" + numara[-4:] if len(numara) >= 10 else numara
                    otp = otp_cikar(icerik)

                    # Debug için mesajı konsola yaz
                    print(f"DEBUG MESAJ: {icerik}")
                    print(f"Çıkarılan OTP: {otp}")

                    mesaj = (
                        f"📨 *VEXORP Yeni OTP Geldi*\n"
                        f"────────────────────────────\n"
                        f"🕒 *Zaman* → {md_escape(zaman)}\n"
                        f"🌍 *Ülke* → {md_escape(ulke_adi)} {bayrak}\n"
                        f"📱 *Numara* → `{md_escape(maskeli)}`\n"
                        f"🛠️ *Uygulama* → {md_escape(uygulama)}\n"
                        f"🔐 *OTP Kodu* → ```{md_escape(otp)}```\n"
                        f"────────────────────────────\n"
                        f"📝 *Orijinal Mesaj:*\n{md_escape(icerik[:380])}{' …' if len(icerik) > 380 else ''}\n"
                        f"────────────────────────────"
                    )

                    tuslar = [
                        [
                            InlineKeyboardButton("👤 Owner: @Vexorp", url="https://t.me/Vexorp"),
                            InlineKeyboardButton("📢 Kanal", url="https://t.me/+wdMrCqP5yDM2OWJk")
                        ]
                    ]

                    if await telegram_gonder(mesaj, tuslar):
                        durum["son_gonderilen"] = f"{zaman} - {maskeli} ({otp})"
                        durum["toplam_gonderilen"] += 1
                        print(f"  ✔ Gönderildi → {maskeli} ({otp})")
                    else:
                        print(f"  ✘ Gönderilemedi")

        except Exception as e:
            durum["hata"] = str(e)
            print(f"Döngü hatası: {e}")

        await asyncio.sleep(KONTROL_ARALIGI_SN)


# ────────────────────────────────────────────────
#         FLASK ROUTE'LAR
# ────────────────────────────────────────────────

@app.route("/")
def ana_sayfa():
    html = """
    <html>
    <head><title>VEXORP OTP İzleyici</title>
    <meta charset="utf-8">
    <style>
        body { font-family: monospace; background:#0d1117; color:#c9d1d9; padding:20px; }
        h1 { color:#58a6ff; }
        .status { background:#161b22; padding:20px; border-radius:10px; border:1px solid #30363d; }
        button { padding:12px 24px; font-size:1.1em; margin:10px; background:#238636; color:white; border:none; border-radius:6px; cursor:pointer; }
        button[name="stop"] { background:#da3633; }
        button:hover { opacity:0.9; }
    </style>
    </head>
    <body>
        <h1>VEXORP OTP Otomatik İletici</h1>
        <div class="status">
            <p>Durum ..............: <b style="color:{% if calisiyor %}#3fb950{% else %}#f85149{% endif %};">{{ 'ÇALIŞIYOR' if calisiyor else 'DURDURULDU' }}</b></p>
            <p>Son kontrol ........: {{ son_kontrol }}</p>
            <p>Son gönderilen .....: {{ son_gonderilen }}</p>
            <p>Toplam gönderilen ..: {{ toplam_gonderilen }}</p>
            {% if hata %}
            <p style="color:#f85149;">Son hata ...........: {{ hata }}</p>
            {% endif %}
        </div>

        <form method="post" action="/kontrol">
            <button type="submit" name="action" value="start">Başlat ▶</button>
            <button type="submit" name="action" value="stop">Durdur ■</button>
            <button type="submit" name="action" value="status">Yenile</button>
        </form>
    </body>
    </html>
    """
    return render_template_string(html, **durum)


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
        print("→ Durdurma sinyali gönderildi (döngü bir sonraki kontrolde duracak)")

    return ana_sayfa()


if __name__ == "__main__":
    print("╔════════════════════════════════════════════╗")
    print("║      VEXORP OTP İLETİCİ + FLASK            ║")
    print("║  Web: http://127.0.0.1:5000                ║")
    print("╚════════════════════════════════════════════╝\n")

    # Otomatik başlatmak istersen aşağıdaki satırları aç
    # durum["calisiyor"] = True
    # loop_thread = threading.Thread(target=lambda: asyncio.run(otp_kontrol_loop()), daemon=True)
    # loop_thread.start()

    app.run(host="0.0.0.0", port=5000, debug=False)