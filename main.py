import asyncio, requests, re, threading
from datetime import datetime
from flask import Flask, render_template_string
from telegram import Bot

# ================== AYARLAR ==================
API_URL = "http://147.135.212.197/crapi/st/viewstats"
API_TOKEN = "RFdUREJBUzR9T4dVc49ndmFra1NYV5CIhpGVcnaOYmqHhJZXfYGJSQ=="

TELEGRAM_BOT_TOKEN = "8450988435:AAFbbzEg_CDHnuIwsn6RE9C--sUT7rOUxw8"
TELEGRAM_GROUP_ID = -1003744838706

CHECK_INTERVAL = 35
MAX_RECORDS = 8

bot = Bot(token=TELEGRAM_BOT_TOKEN)

# ================== FULL COUNTRY MAP ==================
COUNTRY_MAP = {
"1":("ABD/Kanada","🇺🇸"),"7":("Rusya","🇷🇺"),"20":("Mısır","🇪🇬"),"27":("Güney Afrika","🇿🇦"),
"30":("Yunanistan","🇬🇷"),"31":("Hollanda","🇳🇱"),"32":("Belçika","🇧🇪"),"33":("Fransa","🇫🇷"),
"34":("İspanya","🇪🇸"),"36":("Macaristan","🇭🇺"),"39":("İtalya","🇮🇹"),"40":("Romanya","🇷🇴"),
"41":("İsviçre","🇨🇭"),"43":("Avusturya","🇦🇹"),"44":("İngiltere","🇬🇧"),"45":("Danimarka","🇩🇰"),
"46":("İsveç","🇸🇪"),"47":("Norveç","🇳🇴"),"48":("Polonya","🇵🇱"),"49":("Almanya","🇩🇪"),
"51":("Peru","🇵🇪"),"52":("Meksika","🇲🇽"),"53":("Küba","🇨🇺"),"54":("Arjantin","🇦🇷"),
"55":("Brezilya","🇧🇷"),"56":("Şili","🇨🇱"),"57":("Kolombiya","🇨🇴"),"58":("Venezuela","🇻🇪"),
"60":("Malezya","🇲🇾"),"61":("Avustralya","🇦🇺"),"62":("Endonezya","🇮🇩"),
"63":("Filipinler","🇵🇭"),"64":("Yeni Zelanda","🇳🇿"),"65":("Singapur","🇸🇬"),
"66":("Tayland","🇹🇭"),"81":("Japonya","🇯🇵"),"82":("Güney Kore","🇰🇷"),
"84":("Vietnam","🇻🇳"),"86":("Çin","🇨🇳"),"90":("Türkiye","🇹🇷"),
"91":("Hindistan","🇮🇳"),"92":("Pakistan","🇵🇰"),"93":("Afganistan","🇦🇫"),
"94":("Sri Lanka","🇱🇰"),"95":("Myanmar","🇲🇲"),"98":("İran","🇮🇷"),
"211":("Güney Sudan","🇸🇸"),"212":("Fas","🇲🇦"),"213":("Cezayir","🇩🇿"),
"216":("Tunus","🇹🇳"),"218":("Libya","🇱🇾"),"220":("Gambiya","🇬🇲"),
"221":("Senegal","🇸🇳"),"222":("Moritanya","🇲🇷"),"223":("Mali","🇲🇱"),
"224":("Gine","🇬🇳"),"225":("Fildişi Sahili","🇨🇮"),"226":("Burkina Faso","🇧🇫"),
"227":("Nijer","🇳🇪"),"228":("Togo","🇹🇬"),"229":("Benin","🇧🇯"),
"230":("Mauritius","🇲🇺"),"231":("Liberya","🇱🇷"),"232":("Sierra Leone","🇸🇱"),
"233":("Gana","🇬🇭"),"234":("Nijerya","🇳🇬"),"235":("Çad","🇹🇩"),
"236":("Orta Afrika","🇨🇫"),"237":("Kamerun","🇨🇲"),"238":("Cape Verde","🇨🇻"),
"239":("Sao Tome","🇸🇹"),"240":("Ekvator Ginesi","🇬🇶"),"241":("Gabon","🇬🇦"),
"242":("Kongo","🇨🇬"),"243":("Demokratik Kongo","🇨🇩"),"244":("Angola","🇦🇴"),
"248":("Seyşeller","🇸🇨"),"249":("Sudan","🇸🇩"),"250":("Ruanda","🇷🇼"),
"251":("Etiyopya","🇪🇹"),"252":("Somali","🇸🇴"),"253":("Cibuti","🇩🇯"),
"254":("Kenya","🇰🇪"),"255":("Tanzanya","🇹🇿"),"256":("Uganda","🇺🇬"),
"257":("Burundi","🇧🇮"),"258":("Mozambik","🇲🇿"),"260":("Zambiya","🇿🇲"),
"261":("Madagaskar","🇲🇬"),"263":("Zimbabve","🇿🇼"),"264":("Namibya","🇳🇦"),
"265":("Malavi","🇲🇼"),"266":("Lesotho","🇱🇸"),"267":("Botsvana","🇧🇼"),
"268":("Eswatini","🇸🇿"),"269":("Komorlar","🇰🇲"),
"350":("Cebelitarık","🇬🇮"),"351":("Portekiz","🇵🇹"),"352":("Lüksemburg","🇱🇺"),
"353":("İrlanda","🇮🇪"),"354":("İzlanda","🇮🇸"),"355":("Arnavutluk","🇦🇱"),
"356":("Malta","🇲🇹"),"357":("Kıbrıs","🇨🇾"),"358":("Finlandiya","🇫🇮"),
"359":("Bulgaristan","🇧🇬"),"370":("Litvanya","🇱🇹"),"371":("Letonya","🇱🇻"),
"372":("Estonya","🇪🇪"),"373":("Moldova","🇲🇩"),"374":("Ermenistan","🇦🇲"),
"375":("Belarus","🇧🇾"),"376":("Andorra","🇦🇩"),"377":("Monako","🇲🇨"),
"378":("San Marino","🇸🇲"),"379":("Vatikan","🇻🇦"),"380":("Ukrayna","🇺🇦"),
"381":("Sırbistan","🇷🇸"),"382":("Karadağ","🇲🇪"),"383":("Kosova","🇽🇰"),
"385":("Hırvatistan","🇭🇷"),"386":("Slovenya","🇸🇮"),"387":("Bosna","🇧🇦"),
"389":("Kuzey Makedonya","🇲🇰"),
"420":("Çekya","🇨🇿"),"421":("Slovakya","🇸🇰"),
"500":("Falkland","🇫🇰"),"501":("Belize","🇧🇿"),"502":("Guatemala","🇬🇹"),
"503":("El Salvador","🇸🇻"),"504":("Honduras","🇭🇳"),"505":("Nikaragua","🇳🇮"),
"506":("Kosta Rika","🇨🇷"),"507":("Panama","🇵🇦"),"509":("Haiti","🇭🇹"),
"591":("Bolivya","🇧🇴"),"592":("Guyana","🇬🇾"),"593":("Ekvador","🇪🇨"),
"595":("Paraguay","🇵🇾"),"598":("Uruguay","🇺🇾"),
"670":("Doğu Timor","🇹🇱"),"673":("Brunei","🇧🇳"),"675":("Papua Yeni Gine","🇵🇬"),
"676":("Tonga","🇹🇴"),"679":("Fiji","🇫🇯"),
"852":("Hong Kong","🇭🇰"),"853":("Makao","🇲🇴"),
"880":("Bangladeş","🇧🇩"),"960":("Maldivler","🇲🇻"),
"966":("Suudi Arabistan","🇸🇦"),"971":("BAE","🇦🇪"),"972":("İsrail","🇮🇱"),
"974":("Katar","🇶🇦"),"977":("Nepal","🇳🇵"),"992":("Tacikistan","🇹🇯"),
"993":("Türkmenistan","🇹🇲"),"994":("Azerbaycan","🇦🇿"),
"995":("Gürcistan","🇬🇪"),"996":("Kırgızistan","🇰🇬"),"998":("Özbekistan","🇺🇿")
}

# ================== FLASK ==================
app = Flask(__name__)
otp_logs = []
country_stats = {}

HTML = """
<h1>VEXORP ADMIN DASHBOARD</h1>
<h3>Ülke İstatistikleri</h3>
<ul>
{% for k,v in stats.items() %}
<li>{{k}} : {{v}}</li>
{% endfor %}
</ul>

<table border=1>
<tr><th>Zaman</th><th>Ülke</th><th>Numara</th><th>Uygulama</th><th>OTP</th></tr>
{% for l in logs %}
<tr>
<td>{{l["time"]}}</td>
<td>{{l["country"]}}</td>
<td>{{l["number"]}}</td>
<td>{{l["app"]}}</td>
<td>{{l["otp"]}}</td>
</tr>
{% endfor %}
</table>
"""

@app.route("/")
def home():
    return "BOT AKTİF"

@app.route("/admin")
def admin():
    return render_template_string(HTML, logs=otp_logs[::-1], stats=country_stats)

def run_flask():
    app.run(host="0.0.0.0", port=8080)

threading.Thread(target=run_flask).start()

# ================== BOT ==================
def get_country(phone):
    p = phone.lstrip("+")
    for k in sorted(COUNTRY_MAP, key=len, reverse=True):
        if p.startswith(k):
            return COUNTRY_MAP[k]
    return ("Bilinmeyen","🌍")

def extract_otp(msg):
    m = re.search(r"\b\d{4,7}\b", msg)
    return m.group() if m else "?"

def get_api():
    try:
        r = requests.get(API_URL, params={"token":API_TOKEN}, timeout=10)
        return r.json()
    except:
        return []

last_time = None

async def loop():
    global last_time
    while True:
        data = get_api()
        if not data:
            await asyncio.sleep(CHECK_INTERVAL)
            continue

        for d in data[:MAX_RECORDS]:
            app_name, number, msg, time = d
            ts = datetime.strptime(time,"%Y-%m-%d %H:%M:%S")

            if last_time and ts <= last_time:
                continue
            last_time = ts

            country, flag = get_country(number)
            otp = extract_otp(msg)

            otp_logs.append({"time":time,"country":country,"number":number,"app":app_name,"otp":otp})
            country_stats[country] = country_stats.get(country,0)+1

            text = f"Yeni OTP\nÜlke: {country} {flag}\nNumara: {number}\nApp: {app_name}\nOTP: {otp}"
            await bot.send_message(chat_id=TELEGRAM_GROUP_ID,text=text)

        await asyncio.sleep(CHECK_INTERVAL)

asyncio.run(loop())