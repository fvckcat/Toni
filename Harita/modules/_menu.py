from Harita import CMD_LIST, CMD_HELP, tbot
import io
import re
from math import ceil

from telethon import custom, events, Button

from Harita.events import register

from telethon import types
from telethon.tl import functions

from pymongo import MongoClient
from Harita import MONGO_DB_URI

client = MongoClient()
client = MongoClient(MONGO_DB_URI)
db = client["harita"]
pagenumber = db.pagenumber



about = "**Tentang Saya**\n\nNama saya Toni, Sebuah bot manajemen grup yang kuat, yang dapat membantu admin dengan mudah!\n\n**Versi Software:** 2.0.1\n**Versi Telethon:** 1.21.1\n\n**Pembuat Saya:**\nToni | Lebah @BluueBlueSky\n\nChannel Support: [Click Here](t.me/CandaAnda)\nChat Support: [Click Here](t.me/BluueBlueSky)\n\nDan terakhir, Terimakasih sudah mensupport saya🐝"
ad_caption = "Hay! Saya Toni, ditugaskan untuk membantu memanajemen grup! Saya bertindak seperti admin dan membuat perintah otomatis!\n\nJoin @CandaAnda untuk quotes.\n@BluueBlueSky untuk panduan dan bantuan\n\nKamu bisa mengecek lebih banyak tentang saya melalui tombol berikut."
pm_caption = "Hay! Nama saya Toni - Saya adalah bot untuk membantu memanajemen grup dengan mudah!\n\nKetik /help untuk mengetahui lebih lanjut tentang saya.\n\n"
pmt = "Hay! Saya Toni\nSaya adalah Telethon Based grup manajemen bot\n dengan banyak sekali fitur! Mari lihat\nbeberapa panduan dibawah ini.\n\nPerintah utama:\n/start : Memulai saya, digunakan untuk mengecek apakah saya aktif atau tidak\n/help : PM anda pesan ini.\nJelajahi Perintah Saya🐝."
@register(pattern="^/start$")
async def start(event):

    if not event.is_group:
        await tbot.send_message(
            event.chat_id,
            pm_caption,
            buttons=[
                [
                    Button.inline("🧰 Tutorial", data="soon"),
                    Button.inline("📚 Perintah", data="help_menu"),
                ],
                  [
                    Button.url(
                        "📌 Tambahkan Saya Ke Grup Kamu!", "t.me/TheToniBot?startgroup=true"
                    ),
                ],
            ],
        )
    else:
        await event.reply("Yuhu Toni disini!,\nada yang bisa saya bantu?")

@tbot.on(events.CallbackQuery(pattern=r"reopen_again"))
async def reopen_again(event):
    if not event.is_group:
        await event.edit(
            pm_caption,
            buttons=[
                [
                    Button.inline("🧰 Tutorial", data="soon"),
                    Button.inline("📚 Perintah", data="help_menu"),
                ],
                  [
                    Button.url(
                        "📌 Tambahkan Saya Ke Grup Kamu!", "t.me/TheToniBot$?startgroup=true"
                    ),
                ],
            ],
        )
    else:
        pass


@register(pattern="^/help$")
async def help(event):
    if not event.is_group:
        buttons = paginate_help(event, 0, CMD_LIST, "helpme")
        await event.reply(pmt, buttons=buttons)
    else:
        await event.reply(
            "Hubungi saya di Pc!",
            buttons=[[Button.url("Klik ini untuk bantuan!", "t.me/TheToniBot?start=help")]],
        )

@tbot.on(events.CallbackQuery(pattern=r"help_menu"))
async def help_menu(event):
    buttons = paginate_help(event, 0, CMD_LIST, "helpme")
    await event.edit(pmt, buttons=buttons)

@tbot.on(events.CallbackQuery(pattern=r"soon"))
async def soon(event):
    buttons=[[Button.inline("About Me", data="about_me"), Button.inline("Commands", data="help_menu"),],[Button.inline("Go Back", data="reopen_again"),],]
    await event.edit(ad_caption, buttons=buttons)

@tbot.on(events.CallbackQuery(pattern=r"about_me"))
async def soon(event):
    buttons=[Button.inline("Go Back", data="soon"),]
    await event.edit(about, buttons=buttons)

@tbot.on(events.callbackquery.CallbackQuery(data=re.compile(b"us_plugin_(.*)")))
async def on_plug_in_callback_query_handler(event):
    plugin_name = event.data_match.group(1).decode("UTF-8")
    help_string = ""
    # By @Eviral

    for i in CMD_LIST[plugin_name]:
        plugin = plugin_name.replace("_", " ")
        emoji = plugin_name.split("_")[0]
        output = str(CMD_HELP[plugin][1])
        help_string = f"Inilah bantuannya untuk **{emoji}**:\n" + output

    if help_string is None:
        pass  # stuck on click
    else:
        reply_pop_up_alert = help_string
    try:
        await event.edit(
            reply_pop_up_alert, buttons=[
                [Button.inline("Back", data="go_back")]]
        )
    except BaseException:
        pass

@tbot.on(events.CallbackQuery(pattern=r"go_back"))
async def go_back(event):
    c = pagenumber.find_one({"id": event.sender_id})
    number = c["page"]
    # print (number)
    buttons = paginate_help(event, number, CMD_LIST, "helpme")
    await event.edit(pm_caption, buttons=buttons)

def get_page(id):
    return pagenumber.find_one({"id": id})


def paginate_help(event, page_number, loaded_plugins, prefix):
    number_of_rows = 21
    number_of_cols = 3

    to_check = get_page(id=event.sender_id)

    if not to_check:
        pagenumber.insert_one({"id": event.sender_id, "page": page_number})

    else:
        pagenumber.update_one(
            {
                "_id": to_check["_id"],
                "id": to_check["id"],
                "page": to_check["page"],
            },
            {"$set": {"page": page_number}},
        )

    helpable_plugins = []
    for p in loaded_plugins:
        if not p.startswith("_"):
            helpable_plugins.append(p)
    helpable_plugins = sorted(helpable_plugins)
    modules = [
        custom.Button.inline(
            "{}".format(x.replace("_", " ")), data="us_plugin_{}".format(x)
        )
        for x in helpable_plugins
    ]
    pairs = list(zip(modules[::number_of_cols], modules[1::number_of_cols], modules[2::number_of_cols]))
    if len(modules) % number_of_cols == 1:
        pairs.append((modules[-1],))
    max_num_pages = ceil(len(pairs) / number_of_rows)
    modulo_page = page_number % max_num_pages
    pairs = pairs[
            modulo_page * number_of_rows: number_of_rows * (modulo_page + 1)
        ] + [
            (
                custom.Button.inline(
                    "Kembali 🔙", data="reopen_again"
               ),
                custom.Button.url(
                    "📱 Instagram Pemilik", "www.instagram.com/antoniprananda"
                ),
                
                
          )

        ]
    return pairs

def nood_page(event, page_number, loaded_plugins, prefix):
    number_of_rows = 21
    number_of_cols = 3

    to_check = get_page(id=event.sender_id)

    if not to_check:
        pagenumber.insert_one({"id": event.sender_id, "page": page_number})

    else:
        pagenumber.update_one(
            {
                "_id": to_check["_id"],
                "id": to_check["id"],
                "page": to_check["page"],
            },
            {"$set": {"page": page_number}},
        )

    helpable_plugins = []
    for p in loaded_plugins:
        if not p.startswith("_"):
            helpable_plugins.append(p)
    helpable_plugins = sorted(helpable_plugins)
    modules = [
        custom.Button.inline(
            "{}".format(x.replace("_", " ")), data="help_plugin_{}".format(x)
        )
        for x in helpable_plugins
    ]
    pairs = list(zip(modules[::number_of_cols], modules[1::number_of_cols], modules[2::number_of_cols]))
    if len(modules) % number_of_cols == 1:
        pairs.append((modules[-1],))
    max_num_pages = ceil(len(pairs) / number_of_rows)
    modulo_page = page_number % max_num_pages
    pairs = pairs[
            modulo_page * number_of_rows: number_of_rows * (modulo_page + 1)
        ] + [
            (
                custom.Button.inline(
                    "Kembali 🔙", data="help_menu"
                ),

            )
        ]
    return pairs
