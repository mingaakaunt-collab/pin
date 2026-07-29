import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import json
import os
import random
from datetime import datetime, timedelta, timezone
import urllib.parse
import requests
import time
import fragment_api
import keep_alive
from keep_alive import server as app

BOT_TOKEN = "8337116890:AAGETZWBZVVNnUtQFIHAtZ_h8lxHu6cuuG4"
ADMIN_ID = 5866652107
CHANNEL_ID = -1003791438142

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

def get_internal_user_id(telegram_id):
    filename = 'users.json'
    if not os.path.exists(filename):
        data = {"users": {}, "next_id": 1000}
    else:
        with open(filename, 'r') as f:
            data = json.load(f)
            
    tg_id_str = str(telegram_id)
    if tg_id_str not in data["users"]:
        data["users"][tg_id_str] = data["next_id"]
        data["next_id"] += 1
        with open(filename, 'w') as f:
            json.dump(data, f)
            
    return data["users"][tg_id_str]

# func.php dagi inlinekey funksiyasining analogi
def inlinekey(text, cb_data, icon_id="0", style="default", url=None):
    if url:
        btn = InlineKeyboardButton(text=text, url=url)  # type: ignore
    else:
        btn = InlineKeyboardButton(text=text, callback_data=cb_data)  # type: ignore
        
    # Rasmiy Telegram API da tugma rangi yo'q bo'lsa-da, 
    # ba'zi maxsus mijozlar (client) o'qishi uchun xuddi PHP dagi kabi JSON ga qo'shamiz:
    orig_to_dict = btn.to_dict
    def custom_to_dict():
        d = orig_to_dict()
        d['icon_custom_emoji_id'] = icon_id
        d['style'] = style
        return d
    
    btn.to_dict = custom_to_dict
    return btn


@bot.message_handler(commands=['start'])
def start_handler(message):
    markup = InlineKeyboardMarkup()
    
    # 1-qator
    markup.row(
        inlinekey("Xisob toldirish", "xisob_toldirish", "5443127283898405358", "primary"), 
        inlinekey("Xisobim", "xisobim", "4972482444025398275", "primary")
    )
    # 2-qator
    markup.row(
        inlinekey("Stars olish", "stars_olish", "5951810621887484519", "success"), 
        inlinekey("Gift olish", "gift_olish", "6021710505960281699", "success")
    )
    # 4-qator
    markup.row(
        inlinekey("NFT gift olish", "nft_olish", "5312361253610475399", "success"), 
        inlinekey("NFT gift sotish", "nft_sotish", "5150158575271674966", "success")
    )
    # 5-qator
    markup.row(
        inlinekey("USDT olish", "usdt_olish", "5287231198098117669", "success"), 
        inlinekey("USDT sotish", "usdt_sotish", "6014655953457123498", "success")
    )
    # 6-qator
    markup.row(
        inlinekey("Premium olish", "premium_olish", "6298821774423361023", "success"), 
        inlinekey("Kanal,gr sotish", "kanal_sotish", "5316847419965579451", "success")
    )
    # 7-qator
    markup.row(
        inlinekey("SMM xizmatlari", "smm_xizmatlari", "5460689598445273231", "danger")
    )
    # 8-qator
    markup.row(
        inlinekey("Statistika", "stat", "5231200819986047254", "primary"), 
        inlinekey("Admin", None, "5444965061749644170", "primary", url="https://t.me/raxmatullayevic")
    )
    
    user = message.from_user
    username_text = f"@{user.username}" if user.username else user.first_name
    
    # Yangi foydalanuvchiga 1000 dan boshlanuvchi ID beramiz
    internal_id = get_internal_user_id(user.id)
    
    caption_text = f"""<tg-emoji emoji-id="5458603043203327669">👋</tg-emoji> Xush kelibsiz, {username_text}

<tg-emoji emoji-id="5456140674028019486">⚡️</tg-emoji> Qulay interfeys
<tg-emoji emoji-id="5456140674028019486">⚡️</tg-emoji> Qulay to'lov
<tg-emoji emoji-id="5456140674028019486">⚡️</tg-emoji> To'liq avtomatlashtirilgan xizmat

User ID: {internal_id}

Pastdagi tugmani bosing va hoziroq boshlang <tg-emoji emoji-id="5406745015365943482">⬇️</tg-emoji>"""
    
    # Rasmni yuborish (rasm fayli kod turgan papkada 'logo.jpg' nomida bo'lishi kerak)
    try:
        with open('logo.jpg', 'rb') as photo:
            bot.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=caption_text,
                reply_markup=markup
            )
    except FileNotFoundError:
        # Agar rasm topilmasa, oddiy xabar yuboradi
        bot.send_message(
            chat_id=message.chat.id,
            text=caption_text + "\n\n<i>(Rasm topilmadi, iltimos papkaga 'logo.jpg' faylini tashlang)</i>",
            reply_markup=markup
        )

@bot.message_handler(commands=['sendphoto'])
def sendphoto_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(inlinekey("🏠", "1"))
    
    bot.send_photo(
        chat_id=message.chat.id,
        photo="https://t.me/photoaibeck/10",
        caption="<b>Salom</b>",
        reply_markup=markup
    )

@bot.message_handler(commands=['da'])
def da_handler(message):
    markup = InlineKeyboardMarkup()
    markup.add(inlinekey("🏠", "ans"))
    
    bot.send_message(
        chat_id=CHANNEL_ID,
        text="<b>Salom</b>",
        reply_markup=markup
    )

def check_ton_transactions():
    import threading
    ton_address = "UQC_y72lZIrk5l3b_NpyzrAGt6wSk284BkXnP8Z5gNKAERhn"
    while True:
        try:
            if not os.path.exists('users.json'):
                time.sleep(60)
                continue
                
            with open('users.json', 'r') as f:
                data = json.load(f)
                
            if "pending_ton" not in data or not data["pending_ton"]:
                time.sleep(60)
                continue
                
            # Fetch transactions
            res = requests.get(f"https://toncenter.com/api/v2/getTransactions?address={ton_address}&limit=20").json()
            if res.get("ok"):
                txs = res["result"]
                for tx in txs:
                    in_msg = tx.get("in_msg", {})
                    if not in_msg:
                        continue
                    value_nano = int(in_msg.get("value", 0))
                    value_ton = value_nano / 1e9
                    msg_data = in_msg.get("message", "")
                    
                    matched_uid = None
                    for uid, p in data["pending_ton"].items():
                        if p["memo"] == msg_data and value_ton >= p["ton_amount"] * 0.99:
                            matched_uid = uid
                            break
                            
                    if matched_uid:
                        # Success! Add balance
                        p = data["pending_ton"][matched_uid]
                        uzs_amount = p["uzs_amount"]
                        
                        if "balances" not in data:
                            data["balances"] = {}
                        if matched_uid not in data["balances"]:
                            data["balances"][matched_uid] = 0
                        data["balances"][matched_uid] += uzs_amount
                        
                        del data["pending_ton"][matched_uid]
                        
                        with open('users.json', 'w') as f:
                            json.dump(data, f)
                            
                        admin_msg_id = p.get("admin_msg_id")
                        if admin_msg_id:
                            try:
                                bot.edit_message_text(f"🔄 TON avto-to'lov qabul qilindi!\nID: {matched_uid}\nSumma: {uzs_amount} so'm ({p['ton_amount']} TON)\n\n✅ Avtomatik tasdiqlandi", ADMIN_ID, admin_msg_id, reply_markup=None)
                            except:
                                pass
                        else:
                            try:
                                bot.send_message(ADMIN_ID, f"🔄 TON avto-to'lov qabul qilindi!\nID: {matched_uid}\nSumma: {uzs_amount} so'm ({p['ton_amount']} TON)")
                            except:
                                pass
                                
                        # Send success message
                        try:
                            formatted = f"{uzs_amount:,}".replace(",", " ")
                            bot.send_message(int(matched_uid), f"<tg-emoji emoji-id=\"5222174276198609679\">✅</tg-emoji> To'lovingiz admin tomonidan tasdiqlandi!\nHisobingizga {formatted} so'm qo'shildi.")
                        except:
                            pass
                            
        except Exception as e:
            pass
            
        time.sleep(60)

def get_ton_to_uzs_rate():
    try:
        # CoinGecko for TON to USD
        cg_res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=the-open-network&vs_currencies=usd").json()
        ton_usd = cg_res['the-open-network']['usd']
        
        # Exchangerate for USD to UZS
        er_res = requests.get("https://api.exchangerate-api.com/v4/latest/USD").json()
        usd_uzs = er_res['rates']['UZS']
        
        return ton_usd * usd_uzs
    except Exception as e:
        # Fallback rate if API fails
        return 5 * 12600

def process_ton_amount(message):
    try:
        amount = float(message.text.replace(" ", "").replace(",", "."))
        if amount <= 0:
            bot.send_message(message.chat.id, "Iltimos, 0 dan katta miqdor kiriting.")
            return
            
        rate = get_ton_to_uzs_rate()
        total_uzs = int(amount * rate)
        final_uzs = int(total_uzs * 0.9)  # 10% ushlab qolinadi
        
        if final_uzs <= 0:
            bot.send_message(message.chat.id, "Kiritilgan TON miqdori juda kam.")
            return
            
        # Generate MEMO: user_id + timestamp last 4 digits
        memo = f"{message.from_user.id}{str(int(time.time()))[-4:]}"
            
        # Adminga boshlang'ich xabar
        formatted_amount = f"{final_uzs:,}".replace(",", " ")
        admin_text = f"Yangi to'lov so'rovi!\nTizim: TON\nFoydalanuvchi: {message.from_user.first_name} (ID: {message.from_user.id})\nSumma: {formatted_amount} so'm ({amount} TON)\nHolat: ⏳ Kutilmoqda"
        admin_markup = InlineKeyboardMarkup()
        admin_markup.row(inlinekey("✅ Tasdiqlash", f"admin_approve_ton_{message.from_user.id}_{final_uzs}", "0", "success"))
        admin_markup.row(inlinekey("❌ Bekor qilish", f"admin_reject_ton_{message.from_user.id}", "0", "danger"))
        try:
            admin_msg = bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_markup)
            admin_msg_id = admin_msg.message_id
        except:
            admin_msg_id = None

        # Save pending transaction
        user_id_str = str(message.from_user.id)
        with open('users.json', 'r') as f:
            data = json.load(f)
        
        if "pending_ton" not in data:
            data["pending_ton"] = {}
            
        data["pending_ton"][user_id_str] = {
            "memo": memo,
            "ton_amount": amount,
            "uzs_amount": final_uzs,
            "time": time.time(),
            "admin_msg_id": admin_msg_id
        }
        
        with open('users.json', 'w') as f:
            json.dump(data, f)
            
        formatted_amount = f"{final_uzs:,}".replace(",", " ")
        ton_address = "UQC_y72lZIrk5l3b_NpyzrAGt6wSk284BkXnP8Z5gNKAERhn"
        
        text = f"""✅ TON To'lov so'rovi yaratildi!

🛒 Kiritilgan miqdor: {amount} TON
💸 Hisobingizga tushadigan summa: {formatted_amount} so'm

Quyidagi manzilga aniq {amount} TON yuboring:
<code>{ton_address}</code>

‼️ DIQQAT: To'lovni yuborayotganda Comment (MEMO) qismiga quyidagi kodni yozishingiz SHART, aks holda to'lov topilmaydi:
<code>{memo}</code>

⏰ To'lov amalga oshirilgach, bot avtomatik aniqlaydi (odatda 1-2 daqiqa oladi)."""
        
        markup = InlineKeyboardMarkup()
        markup.row(inlinekey("To'lovni bekor qilish", "cancel_payment", "5222214769150276151", "danger"))
        markup.row(inlinekey("Bosh menyu", "main_menu", "0", "default"))
        
        bot.send_message(message.chat.id, text, reply_markup=markup)
        
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri TON miqdorini kiriting (masalan, 1 yoki 1.5).")

def receive_receipt(message, amount):
    if not message.photo:
        msg = bot.send_message(message.chat.id, "Iltimos, chekni rasm shaklida yuboring! Yoki bekor qilish uchun Bosh menyu /start tugmasini bosing.")
        bot.register_next_step_handler(msg, receive_receipt, amount)
        return
        
    photo_id = message.photo[-1].file_id
    user_info = f"{message.from_user.first_name} (ID: {message.from_user.id})"
    caption = f"Yangi to'lov!\nFoydalanuvchi: {user_info}\nSumma: {amount} so'm"
    
    clean_amount = amount.replace(" ", "")
    markup = InlineKeyboardMarkup()
    markup.row(inlinekey("✅ Tasdiqlash", f"admin_approve_karta_{message.from_user.id}_{clean_amount}", "0", "success"))
    markup.row(inlinekey("❌ Bekor qilish", f"admin_reject_karta_{message.from_user.id}", "0", "danger"))
    
    uid = str(message.from_user.id)
    with open('users.json', 'r') as f:
        data = json.load(f)
    if "pending_karta" in data and uid in data["pending_karta"]:
        old_msg_id = data["pending_karta"][uid].get("admin_msg_id")
        if old_msg_id:
            try: bot.delete_message(ADMIN_ID, old_msg_id)
            except: pass
            
    admin_msg = bot.send_photo(ADMIN_ID, photo_id, caption=caption, reply_markup=markup)
    
    if "pending_karta" in data and uid in data["pending_karta"]:
        data["pending_karta"][uid]["admin_msg_id"] = admin_msg.message_id
        with open('users.json', 'w') as f:
            json.dump(data, f)
    
    bot.send_message(message.chat.id, "To'lov chekingiz adminga yuborildi. Tasdiqlanishi bilan hisobingizga pul tushadi.")

def process_payment_amount(message):
    try:
        # Bo'shliqlarni olib tashlab, raqamga o'girmiz
        amount = int(message.text.replace(" ", ""))
        if amount < 1000 or amount > 2500000:
            bot.send_message(message.chat.id, "Iltimos, 1 000 so'mdan 2 500 000 so'mgacha bo'lgan summani kiriting.")
            return
            
        # 1 dan 99 gacha tasodifiy son qoshamiz (bekor qilindi, foydalanuvchi so'roviga ko'ra)
        unique_amount = amount
        formatted_amount = f"{unique_amount:,}".replace(",", " ")
        
        # Adminga boshlang'ich xabar
        admin_text = f"Yangi to'lov so'rovi!\nTizim: Karta\nFoydalanuvchi: {message.from_user.first_name} (ID: {message.from_user.id})\nSumma: {formatted_amount} so'm\nHolat: ⏳ Kutilmoqda (Chek kutilmoqda)"
        admin_markup = InlineKeyboardMarkup()
        admin_markup.row(inlinekey("✅ Tasdiqlash", f"admin_approve_karta_{message.from_user.id}_{unique_amount}", "0", "success"))
        admin_markup.row(inlinekey("❌ Bekor qilish", f"admin_reject_karta_{message.from_user.id}", "0", "danger"))
        try:
            admin_msg = bot.send_message(ADMIN_ID, admin_text, reply_markup=admin_markup)
            admin_msg_id = admin_msg.message_id
        except:
            admin_msg_id = None
            
        with open('users.json', 'r') as f: data = json.load(f)
        if "pending_karta" not in data: data["pending_karta"] = {}
        data["pending_karta"][str(message.from_user.id)] = {"amount": unique_amount, "admin_msg_id": admin_msg_id}
        with open('users.json', 'w') as f: json.dump(data, f)
        
        # Vaqtni hisoblash (Toshkent vaqti bilan)
        tz = timezone(timedelta(hours=5))
        now = datetime.now(tz)
        end_time = now + timedelta(minutes=5)
        
        time_format = "%H:%M:%S"
        start_str = now.strftime(time_format)
        end_str = end_time.strftime(time_format)
        
        text = f"""✅ To'lov so'rovi yaratildi!

➕ To'lov uchun karta: <code>9860196600861393</code>

🛒 Aniq shu miqdorni yuboring:
↪️ <code>{formatted_amount}</code> so'm

‼️ DIQQAT: Faqat aynan {formatted_amount} so'm o'tkazing. Kam yoki ko'p yuborsangiz, to'lov avtomatik tan olinmaydi va pul balansingizga tushmay qoladi!

⏰ To'lov amalga oshirilgach, bot avtomatik aniqlaydi.
⚠️ Muddat: {start_str} — {end_str} (Toshkent)
Aniq 5 daqiqa. Undan keyin avtomatik bekor qilinadi!"""

        markup = InlineKeyboardMarkup()
        markup.row(inlinekey("To'lov qildim", f"paid_{formatted_amount}", "5222174276198609679", "success"))
        markup.row(inlinekey("To'lovni bekor qilish", "cancel_payment", "5222214769150276151", "danger"))
        markup.row(inlinekey("Bosh menyu", "main_menu", "0", "default"))
        
        bot.send_message(message.chat.id, text, reply_markup=markup)
        
    except ValueError:
        bot.send_message(message.chat.id, "Iltimos, to'g'ri summa kiriting (faqat sonlar).")


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "xisob_toldirish":
        text = "To'lov usulini tanlang:"
        markup = InlineKeyboardMarkup()
        markup.row(inlinekey("Karta orqali", "pay_karta", "5445353829304387411", "success"))
        markup.row(inlinekey("Gram (ton) orqali", "pay_ton", "5377620962390857342", "success"))
        markup.row(inlinekey("Stars orqali", "pay_stars", "4983746717313664194", "success"))
        markup.row(inlinekey("Bosh menyu", "main_menu", "0", "default"))
        
        bot.send_message(call.message.chat.id, text, reply_markup=markup)
        bot.answer_callback_query(call.id)
        
    elif call.data == "pay_karta":
        text = """<tg-emoji emoji-id="5287231198098117669">💰</tg-emoji> Xisob to'ldirish

Quyidagi miqdorni kiriting:
🔻 Minimal: 1 000 so'm
🔺 Maksimal: 2 500 000 so'm"""
        
        markup = InlineKeyboardMarkup()
        markup.add(inlinekey("Bekor qilish", "cancel_action", "5222214769150276151", "danger"))
        
        msg = bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.register_next_step_handler(msg, process_payment_amount)
        bot.answer_callback_query(call.id)
        
    elif call.data == "xisobim":
        with open('users.json', 'r') as f: data = json.load(f)
        uid_str = str(call.from_user.id)
        
        balance = 0
        if "balances" in data and uid_str in data["balances"]:
            balance = data["balances"][uid_str]
            
        formatted_balance = f"{balance:,}".replace(",", " ")
        
        safe_name = call.from_user.first_name.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        text = f"""<tg-emoji emoji-id="5224450179368767019">💎</tg-emoji> <b>SHAXSIY KABINET</b>
        
<tg-emoji emoji-id="5456140674028019486">👤</tg-emoji> <b>Ism:</b> {safe_name}
<tg-emoji emoji-id="5334890573281114250">🆔</tg-emoji> <b>ID raqamingiz:</b> {get_internal_user_id(call.from_user.id)}

<tg-emoji emoji-id="5278467510604160626">💰</tg-emoji> <b>Joriy balansingiz:</b> 
<tg-emoji emoji-id="5444856076954520455">💸</tg-emoji> <code>{formatted_balance}</code> <b>so'm</b>

<i>Xizmatlarimizdan foydalanish uchun balansingizni to'ldiring!</i>"""
        
        markup = InlineKeyboardMarkup()
        markup.row(inlinekey("Xisobni to'ldirish", "xisob_toldirish", "5443127283898405358", "success"))
        markup.row(inlinekey("Bosh menyu", "main_menu", "0", "primary"))
        
        try:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except Exception as e:
            import traceback
            with open("stars_error.log", "w") as f:
                f.write(traceback.format_exc())
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            try: bot.send_message(call.message.chat.id, text, reply_markup=markup)
            except: pass
            
        bot.answer_callback_query(call.id)
        
    elif call.data == "stars_olish":
        text = """<tg-emoji emoji-id="5951810621887484519">⭐️</tg-emoji> <b>Telegram Stars buyurtma</b>
        
<tg-emoji emoji-id="5350713563512052787">📉</tg-emoji> Minimal: 50
<tg-emoji emoji-id="5350305691942788490">📈</tg-emoji> Maksimal: 10000

<tg-emoji emoji-id="5951810621887484519">⭐️</tg-emoji> Kerakli miqdorni tanlang yoki raqam bilan yuboring <tg-emoji emoji-id="5438525681707278534">👇</tg-emoji>"""
        
        markup = InlineKeyboardMarkup()
        # Row 1
        markup.row(
            inlinekey("50 — 9 450 so'm", "buy_stars_50", "5951810621887484519", "success"),
            inlinekey("75 — 14 175 so'm", "buy_stars_75", "5951810621887484519", "success")
        )
        # Row 2
        markup.row(
            inlinekey("100 — 18 900 so'm", "buy_stars_100", "5951810621887484519", "success"),
            inlinekey("150 — 28 350 so'm", "buy_stars_150", "5951810621887484519", "success")
        )
        # Row 3
        markup.row(
            inlinekey("250 — 47 250 so'm", "buy_stars_250", "5951810621887484519", "success"),
            inlinekey("350 — 66 150 so'm", "buy_stars_350", "5951810621887484519", "success")
        )
        # Row 4
        markup.row(
            inlinekey("500 — 94 500 so'm", "buy_stars_500", "5951810621887484519", "success"),
            inlinekey("750 — 141 750 so'm", "buy_stars_750", "5951810621887484519", "success")
        )
        # Row 5
        markup.row(
            inlinekey("1000 — 189 000 so'm", "buy_stars_1000", "5951810621887484519", "success"),
            inlinekey("1500 — 283 500 so'm", "buy_stars_1500", "5951810621887484519", "success")
        )
        # Row 6
        markup.row(
            inlinekey("2500 — 472 500 so'm", "buy_stars_2500", "5951810621887484519", "success"),
            inlinekey("5000 — 945 000 so'm", "buy_stars_5000", "5951810621887484519", "success")
        )
        # Row 7
        markup.row(
            inlinekey("10000 — 1 890 000 so'm", "buy_stars_10000", "5951810621887484519", "success")
        )
        # Row 8
        markup.row(
            inlinekey("Boshqa miqdor", "buy_stars_custom", "5373007621416568211", "primary")
        )
        # Row 9
        markup.row(
            inlinekey("Bosh menyu", "main_menu", "0", "danger")
        )
        
        try:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except Exception as e:
            import traceback
            with open("stars_error.log", "w") as f:
                f.write(traceback.format_exc())
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            try: bot.send_message(call.message.chat.id, text, reply_markup=markup)
            except: pass
            
        bot.answer_callback_query(call.id)
        
    elif call.data.startswith("buy_stars_self_"):
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        amount = int(call.data.replace("buy_stars_self_", ""))
        price = amount * 189
        
        username = call.from_user.username
        if username:
            username = "@" + username
            class DummyMessage: pass
            msg = DummyMessage()
            msg.text = username
            msg.chat = call.message.chat
            msg.from_user = call.from_user
            
            process_stars_username(msg, amount, price)
        else:
            bot.send_message(call.message.chat.id, "❌ Sizning Telegram akkauntingizda @username yo'q! Iltimos, o'z profilinngizga kirib username o'rnating yoki shunchaki yozma ravishda botga yuboring.")
            
        bot.answer_callback_query(call.id)

    elif call.data.startswith("buy_stars_"):
        bot.delete_message(call.message.chat.id, call.message.message_id)
        action = call.data.replace("buy_stars_", "")
        
        if action == "custom":
            text = "Yuborilishi kerak bo'lgan Stars miqdorini kiriting (Minimal: 50, Maksimal: 10000):"
            markup = InlineKeyboardMarkup()
            markup.add(inlinekey("Bekor qilish", "cancel_action", "5222214769150276151", "danger"))
            msg = bot.send_message(call.message.chat.id, text, reply_markup=markup)
            bot.register_next_step_handler(msg, process_custom_stars)
        else:
            amount = int(action)
            price = amount * 189
            text = f"""<tg-emoji emoji-id="5951810621887484519">⭐️</tg-emoji> <b>{amount} yulduz</b>
<tg-emoji emoji-id="5444856076954520455">💸</tg-emoji> Narxi: {price:,} so'm

<tg-emoji emoji-id="4965219701572503640">💼</tg-emoji> Yulduz yuboriladigan username ni yuboring (masalan: durov):

<tg-emoji emoji-id="5312536423851630001">💡</tg-emoji> Yoki o'zingizga olish uchun quyidagi tugmani bosing <tg-emoji emoji-id="5438525681707278534">👇</tg-emoji>"""
            markup = InlineKeyboardMarkup()
            markup.row(inlinekey("O'zim uchun", f"buy_stars_self_{amount}", "4965219701572503640", "primary"))
            markup.row(inlinekey("Bosh menyu", "main_menu", "0", "danger"))
            msg = bot.send_message(call.message.chat.id, text, reply_markup=markup)
            bot.register_next_step_handler(msg, process_stars_username, amount, price)
            
        bot.answer_callback_query(call.id)
        
    elif call.data == "nft_olish":
        text = """<tg-emoji emoji-id='5312361253610475399'>🎁</tg-emoji> <b>NFT Gift tanlang:</b>"""
        
        markup = InlineKeyboardMarkup()
        markup.row(inlinekey("Star Notepad", "buy_nft_star_notepad", "5357053450637045218", "primary"))
        markup.row(inlinekey("Jack-in-the-box", "buy_nft_jack_box", "5431821190513583006", "primary"))
        markup.row(inlinekey("Money Pot", "buy_nft_money_pot", "5386516410891526768", "primary"))
        markup.row(inlinekey("Stellar Rocket", "buy_nft_stellar_rocket", "5465184436339372102", "primary"))
        markup.row(inlinekey("Mood Pack", "buy_nft_mood_pack", "5309980110856685304", "primary"))
        markup.row(inlinekey("Bosh menyu", "main_menu", "0", "danger"))
        
        try:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except:
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
        
        bot.answer_callback_query(call.id)
        
    elif call.data == "buy_nft_star_notepad":
        price = 100000
        uid = str(call.from_user.id)
        with open('users.json', 'r') as f: data = json.load(f)
        balance = data.get("balances", {}).get(uid, 0)
        
        text = f"""<tg-emoji emoji-id='5357053450637045218'>⭐</tg-emoji> <b>Star Notepad</b>

<tg-emoji emoji-id='5312536423851630001'>💡</tg-emoji> NFTni ko'rish: <a href='https://t.me/nft/StarNotepad-70876'>https://t.me/nft/StarNotepad-70876</a>

💸 Narxi: {price:,} so'm
💰 Balansingiz: {balance:,} so'm"""
        
        markup = InlineKeyboardMarkup()
        markup.row(inlinekey("✅ Sotib olish", "confirm_nft_star_notepad", "5357053450637045218", "primary"))
        markup.row(inlinekey("⬅️ Orqaga", "nft_olish", "0", "primary"))
        markup.row(inlinekey("Bosh menyu", "main_menu", "0", "danger"))
        
        try:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except:
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
        
        bot.answer_callback_query(call.id)

    elif call.data == "confirm_nft_star_notepad":
        price = 100000
        uid = str(call.from_user.id)
        with open('users.json', 'r') as f: data = json.load(f)
        balance = data.get("balances", {}).get(uid, 0)
        
        if balance < price:
            bot.answer_callback_query(call.id, f"❌ Hisobingizda mablag' yetarli emas! Kerak: {price:,} so'm", show_alert=True)
            return
        
        data["balances"][uid] = balance - price
        if "spent" not in data: data["spent"] = {}
        data["spent"][uid] = data["spent"].get(uid, 0) + price
        with open('users.json', 'w') as f: json.dump(data, f)
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"<tg-emoji emoji-id='5222174276198609679'>✅</tg-emoji> <b>To'lov qabul qilindi!</b>\n\n<tg-emoji emoji-id='5357053450637045218'>⭐</tg-emoji> Star Notepad buyurtmangiz qabul qilindi.\n💸 Yechildi: {price:,} so'm"
            )
        except:
            bot.send_message(call.message.chat.id, f"<tg-emoji emoji-id='5222174276198609679'>✅</tg-emoji> <b>To'lov qabul qilindi!</b>\n\n<tg-emoji emoji-id='5357053450637045218'>⭐</tg-emoji> Star Notepad buyurtmangiz qabul qilindi.\n💸 Yechildi: {price:,} so'm")
        
        bot.send_message(ADMIN_ID, f"🛒 <b>NFT Buyurtma</b>\n\n👤 Xaridor: {call.from_user.first_name} (ID: <code>{uid}</code>)\n🎁 NFT: Star Notepad\n🔗 https://t.me/nft/StarNotepad-70876\n💸 Summa: {price:,} so'm")
        bot.answer_callback_query(call.id)
        
    elif call.data == "premium_olish":
        text = """<tg-emoji emoji-id='6298821774423361023'>💎</tg-emoji> <b>Premium muddatini tanlang:</b>"""
        
        markup = InlineKeyboardMarkup()
        markup.row(inlinekey("3 oylik", "buy_premium_3", "6298821774423361023", "primary"))
        markup.row(inlinekey("6 oylik", "buy_premium_6", "6298821774423361023", "primary"))
        markup.row(inlinekey("12 oylik", "buy_premium_12", "6298821774423361023", "primary"))
        markup.row(inlinekey("Bosh menyu", "main_menu", "0", "danger"))
        
        try:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except:
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_message(call.message.chat.id, text, reply_markup=markup)
        
        bot.answer_callback_query(call.id)
        
    elif call.data == "gift_olish":
        text = """🎁 Telegram Gift yuborish

👇 Giftni tanlang:"""
        
        markup = InlineKeyboardMarkup()
        
        # Row 1
        markup.row(
            inlinekey("💗 15 ⭐️ — 2 880 so'm", "buy_gift_heart_15", "0", "primary"),
            inlinekey("15 ⭐️ — 2 880 so'm", "buy_gift_bear_15", "5280598054901145762", "primary")
        )
        # Row 2
        markup.row(
            inlinekey("25 ⭐️ — 4 800 so'm", "buy_gift_box_25", "5280615440928758599", "primary"),
            inlinekey("25 ⭐️ — 4 800 so'm", "buy_gift_rose_25", "5280947338821524402", "primary")
        )
        # Row 3
        markup.row(
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_bearmech_50", "5447213743417105726", "primary"),
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_cake_50", "5280659198055572187", "primary")
        )
        # Row 4
        markup.row(
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_bouquet_50", "5280774333243873175", "primary"),
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_rocket_50", "5283080528818360566", "primary")
        )
        # Row 5
        markup.row(
            inlinekey("🍾 50 ⭐️ — 9 600 so'm", "buy_gift_champagne_50", "0", "primary"),
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_bunny_50", "5393309541620291208", "primary")
        )
        # Row 6
        markup.row(
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_bearballoon_50", "5359736160224586485", "primary"),
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_bearlep_50", "5317000922096769303", "primary")
        )
        # Row 7
        markup.row(
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_bearpink_50", "5289761157173775507", "primary"),
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_heartribbon_50", "5224628072619216265", "primary")
        )
        # Row 8
        markup.row(
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_bearwhite_50", "5226661632259691727", "primary"),
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_tree_50", "5345935030143196497", "primary")
        )
        # Row 9
        markup.row(
            inlinekey("50 ⭐️ — 9 600 so'm", "buy_gift_bearsanta_50", "5379850840691476775", "primary"),
            inlinekey("100 ⭐️ — 19 200 so'm", "buy_gift_ring_100", "5280651583078556009", "primary")
        )
        # Row 10
        markup.row(
            inlinekey("100 ⭐️ — 19 200 so'm", "buy_gift_diamond_100", "5280922999241859582", "primary"),
            inlinekey("100 ⭐️ — 19 200 so'm", "buy_gift_trophy_100", "5280769763398671636", "primary")
        )
        # Row 11
        markup.row(
            inlinekey("Bosh menyu", "main_menu", "0", "danger")
        )
        
        try:
            if call.message.content_type == 'photo':
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            else:
                bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
        except Exception as e:
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            try: bot.send_message(call.message.chat.id, text, reply_markup=markup)
            except: pass
            
        bot.answer_callback_query(call.id)
        
    elif call.data == "pay_ton":
        text = "Qancha TON kiritmoqchisiz? (Masalan: 1 yoki 0.5)"
        markup = InlineKeyboardMarkup()
        markup.add(inlinekey("Bekor qilish", "cancel_action", "5222214769150276151", "danger"))
        
        msg = bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.register_next_step_handler(msg, process_ton_amount)
        bot.answer_callback_query(call.id)
        
    elif call.data == "pay_stars":
        text = "Hozir stars avto tolov ishlamayabdi. Stars orqali to'lov qilmoqchi bo'lsangiz adminga murojaat qiling."
        markup = InlineKeyboardMarkup()
        markup.add(inlinekey("Admin", None, "5444965061749644170", "primary", url="https://t.me/raxmatullayevic"))
        markup.add(inlinekey("Bosh menyu", "main_menu", "0", "default"))
        
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id)
        
    elif call.data in ["cancel_action", "cancel_payment", "main_menu"]:
        bot.delete_message(call.message.chat.id, call.message.message_id)
        uid = str(call.message.chat.id)
        
        if call.data in ["cancel_action", "cancel_payment"]:
            with open('users.json', 'r') as f: data = json.load(f)
            updated = False
            for ptype in ["pending_karta", "pending_ton"]:
                if ptype in data and uid in data[ptype]:
                    msg_id = data[ptype][uid].get("admin_msg_id")
                    if msg_id:
                        try: bot.edit_message_text(f"Holat: ❌ Mijoz bekor qildi (ID: {uid})", ADMIN_ID, msg_id, reply_markup=None)
                        except: pass
                    del data[ptype][uid]
                    updated = True
            if updated:
                with open('users.json', 'w') as f: json.dump(data, f)
        
        if call.data == "main_menu":
            start_handler(call.message)
            bot.answer_callback_query(call.id, "Bosh menyu")
        else:
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.answer_callback_query(call.id, "Bekor qilindi")
            
    elif call.data.startswith("paid_"):
        # "paid_1 000" dan summani ajratib olamiz
        amount = call.data.split("_")[1]
        text = "Iltimos, to'lov cheki (skrinshot yoki rasm) nusxasini shu yerga yuboring:"
        
        markup = InlineKeyboardMarkup()
        markup.add(inlinekey("Bekor qilish", "cancel_action", "5222214769150276151", "danger"))
        
        msg = bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=markup)
        bot.register_next_step_handler(msg, receive_receipt, amount)
        bot.answer_callback_query(call.id)
        
    elif call.data.startswith("admin_approve_"):
        parts = call.data.split("_")
        pay_type = parts[2]
        uid_str = parts[3]
        amount = int(parts[4])
        
        with open('users.json', 'r') as f: data = json.load(f)
        
        pkey = f"pending_{pay_type}"
        if pkey not in data or uid_str not in data[pkey]:
            bot.answer_callback_query(call.id, "Bu to'lov allaqachon bajarilgan yoki bekor qilingan!", show_alert=True)
            return
            
        del data[pkey][uid_str]
        
        if "balances" not in data: data["balances"] = {}
        if uid_str not in data["balances"]: data["balances"][uid_str] = 0
        data["balances"][uid_str] += amount
        
        with open('users.json', 'w') as f: json.dump(data, f)
            
        if call.message.photo:
            bot.edit_message_caption(f"{call.message.caption}\n\n✅ Tasdiqlandi!", call.message.chat.id, call.message.message_id, reply_markup=None)
        else:
            bot.edit_message_text(f"{call.message.text}\n\n✅ Tasdiqlandi!", call.message.chat.id, call.message.message_id, reply_markup=None)
            
        formatted = f"{amount:,}".replace(",", " ")
        try: bot.send_message(int(uid_str), f"<tg-emoji emoji-id=\"5222174276198609679\">✅</tg-emoji> To'lovingiz admin tomonidan tasdiqlandi!\nHisobingizga {formatted} so'm qo'shildi.")
        except: pass
        bot.answer_callback_query(call.id, "Tasdiqlandi!")
            
    elif call.data.startswith("admin_reject_"):
        parts = call.data.split("_")
        pay_type = parts[2]
        uid_str = parts[3]
        
        with open('users.json', 'r') as f: data = json.load(f)
        pkey = f"pending_{pay_type}"
        if pkey in data and uid_str in data[pkey]:
            del data[pkey][uid_str]
            with open('users.json', 'w') as f: json.dump(data, f)
            
        if call.message.photo:
            bot.edit_message_caption(f"{call.message.caption}\n\n❌ Bekor qilindi!", call.message.chat.id, call.message.message_id, reply_markup=None)
        else:
            bot.edit_message_text(f"{call.message.text}\n\n❌ Bekor qilindi!", call.message.chat.id, call.message.message_id, reply_markup=None)
            
        try: bot.send_message(int(uid_str), "❌ To'lovingiz admin tomonidan bekor qilindi.")
        except: pass
        bot.answer_callback_query(call.id, "Bekor qilindi")
        
    elif call.data == "1":
        # Foydalanuvchini kanaldagi holatini tekshiramiz
        try:
            member = bot.get_chat_member(CHANNEL_ID, call.from_user.id)
            status = member.status
            
            if status in ['creator', 'administrator', 'member']:
                bot.answer_callback_query(call.id, text="Salom ey", show_alert=True)
            else:
                bot.answer_callback_query(
                    call.id, 
                    text="❌ Xato\n\nKerakli ma'lumotni olish uchun avval kanalga obuna bo‘ling", 
                    show_alert=True
                )
        except telebot.apihelper.ApiTelegramException:
            # Agar botning kanalda adminlik huquqi bo'lmasa xato beradi
            bot.answer_callback_query(call.id, text="Bot kanalda admin emas!", show_alert=True)

def process_custom_stars(message):
    try:
        amount = int(message.text.strip())
        if amount < 50 or amount > 10000:
            bot.send_message(message.chat.id, "❌ Noto'g'ri miqdor! Minimal 50, Maksimal 10000 bo'lishi kerak.")
            return
            
        price = amount * 189
        text = f"""<tg-emoji emoji-id="5951810621887484519">⭐️</tg-emoji> <b>{amount} yulduz</b>
<tg-emoji emoji-id="5444856076954520455">💸</tg-emoji> Narxi: {price:,} so'm

<tg-emoji emoji-id="4965219701572503640">💼</tg-emoji> Yulduz yuboriladigan username ni yuboring (masalan: durov):

<tg-emoji emoji-id="5312536423851630001">💡</tg-emoji> Yoki o'zingizga olish uchun quyidagi tugmani bosing <tg-emoji emoji-id="5438525681707278534">👇</tg-emoji>"""
        markup = InlineKeyboardMarkup()
        markup.row(inlinekey("O'zim uchun", f"buy_stars_self_{amount}", "4965219701572503640", "primary"))
        markup.row(inlinekey("Bosh menyu", "main_menu", "0", "danger"))
        msg = bot.send_message(message.chat.id, text, reply_markup=markup)
        bot.register_next_step_handler(msg, process_stars_username, amount, price)
    except ValueError:
        bot.send_message(message.chat.id, "❌ Iltimos, faqat raqam kiriting!")

def process_stars_username(message, amount, price):
    username = message.text.strip()
    if not username:
        bot.send_message(message.chat.id, "❌ Noto'g'ri username kiritildi.")
        return
        
    uid = str(message.chat.id)
    with open('users.json', 'r') as f: data = json.load(f)
    
    balance = data.get("balances", {}).get(uid, 0)
    
    if balance < price:
        bot.send_message(message.chat.id, f"<tg-emoji emoji-id='5222214769150276151'>❌</tg-emoji> <b>Hisobingizda mablag' yetarli emas!</b>\n\nKerakli summa: {price:,} so'm\nBalansingiz: {balance:,} so'm")
        return
        
    # Pulni yechish
    data["balances"][uid] = balance - price
    
    if "spent" not in data:
        data["spent"] = {}
    data["spent"][uid] = data["spent"].get(uid, 0) + price
    
    with open('users.json', 'w') as f: json.dump(data, f)
    
    # Kutish xabari
    wait_msg = bot.send_message(
        message.chat.id, 
        f"<tg-emoji emoji-id='5395622806710934862'>⏳</tg-emoji> <b>Stars yuborilmoqda...</b>"
    )
    
    try:
        import fragment_api
        res = fragment_api.call_fragment_api(username, amount, "stars")
        # Determine success: accept True, or dict with ok=True / status='success'
        success = False
        if isinstance(res, dict):
            if res.get('ok') or res.get('status') == 'success' or res.get('result'):
                success = True
        elif res is True:
            success = True
        if not success:
            raise Exception("API xatosi")

        # Success: inform user that Stars have been delivered and recorded in DB
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=wait_msg.message_id,
            text=f"<tg-emoji emoji-id='5222174276198609679'>✅</tg-emoji> <b>To'lov qabul qilindi!</b>\n\n👤 Qabul qiluvchi: {username}\n⭐️ Miqdor: {amount}\n💸 Summasi: {price:,} so'm"
        )

        # Admin notification
        admin_text = f"✅ <b>Yangi xarid (Stars)</b>\n\n👤 Xaridor: {message.from_user.first_name} (ID: <code>{uid}</code>)\n🎯 Qabul qiluvchi: {username}\n⭐️ Miqdor: {amount} Stars\n💸 Yechilgan summa: {price:,} so'm"
        bot.send_message(ADMIN_ID, admin_text)
        
    except Exception as e:
        # Pulni qaytarish (Refund)
        with open('users.json', 'r') as f: ref_data = json.load(f)
        ref_data["balances"][uid] = ref_data.get("balances", {}).get(uid, 0) + price
        ref_data["spent"][uid] = ref_data.get("spent", {}).get(uid, 0) - price
        with open('users.json', 'w') as f: json.dump(ref_data, f)
        
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=wait_msg.message_id,
            text=f"<tg-emoji emoji-id='5222214769150276151'>❌</tg-emoji> <b>Stars yuborilmadi</b>\n\n({price:,} so'm) 100% qaytarildi."
        )
        bot.send_message(ADMIN_ID, f"❌ Fragment API xatosi (Summa egasiga qaytarildi):\n{str(e)}")

def start_bot():
    """Bot ishga tushirishni boshlaydi"""
    bot.set_my_commands([
        BotCommand("start", "Botni yangilash")
    ])
    
    # TON to'lovlarini avtomatik tekshiruvchi fon jarayoni
    import threading
    t = threading.Thread(target=check_ton_transactions, daemon=True)
    t.start()
    
    WEBHOOK_URL = os.environ.get('WEBHOOK_URL', '')
    
    if WEBHOOK_URL:
        # Render.com: webhook rejimi
        keep_alive.init_webhook(bot, WEBHOOK_URL)
        port = int(os.environ.get('PORT', 8080))
        keep_alive.server.run(host='0.0.0.0', port=port)
    else:
        # Lokal: polling rejimi
        bot.remove_webhook()
        bot.polling(none_stop=True, interval=0)

if __name__ == '__main__':
    start_bot()
