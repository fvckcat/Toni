#Written By Ayush Chatterjee And Avishek Bhattacharjee
#By Eviral (github.com/TeamEviral ; t.me/Eviral)
#Don't forget to give credit and make your source public.

from Harita.events import register
from os import remove, execle, path, environ
import asyncio
import sys
from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError
from Harita import OWNER_ID, tbot, UPSTREAM_REPO_URL

async def gen_chlog(repo, diff):
    ch_log = ""
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += (
            f"•[{c.committed_datetime.strftime(d_form)}]: {c.summary} by <{c.author}>\n"
        )
    return ch_log

@register(pattern="^/update(?: |$)(.*)")
async def upstream(ups):
    check = ups.message.sender_id
    if int(check) != int(OWNER_ID):
        return
    lol = await ups.reply("`Mengecek update, mohon tunggu....`")
    conf = ups.pattern_match.group(1)
    off_repo = UPSTREAM_REPO_URL
    force_update = False

    try:
        txt = "`Uups.. Update tidak bisa dilanjutkan "
        repo = Repo()
    except NoSuchPathError as error:
        await lol.edit(f"{txt}\n`direktori {error} tidak ditemukan`")
        repo.__del__()
        return
    except GitCommandError as error:
        await lol.edit(f"{txt}\n`Kegagalan awal! {error}`")
        repo.__del__()
        return
    except InvalidGitRepositoryError as error:
        if conf != "now":
            await lol.edit(
                f"**Waduh, direktori {error} sepertinya tidak ada untuk repository.\
            \nTapi saya dapat memperbaiki ini, ketik** `/update now`"
            )
            return
        repo = Repo.init()
        origin = repo.create_remote("upstream", off_repo)
        origin.fetch()        
        force_update = True
        repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)

    ac_br = repo.active_branch.name
    if ac_br != "master":
        await lol.edit(
            f"**[UPDATER]:**` Sepertinya anda menggunakan repo costum ({ac_br}). "
            "dalam hal ini, update tidak dapat dilakukan "
            "branch mana yang akan digabungkan. "
            "tolong cek di official branch`"
        )
        repo.__del__()
        return

    try:
        repo.create_remote("upstream", off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote("upstream")
    ups_rem.fetch(ac_br)

    changelog = await gen_chlog(repo, f"HEAD..upstream/{ac_br}")

    if not changelog and not force_update:
        await lol.edit("\n`Bot kamu sudah`  **up-to-date**  \n")
        repo.__del__()
        return

    if conf != "now" and not force_update:
        changelog_str = (
            f"**UPDATE baru tersedia untuk {ac_br}\n\nCHANGELOG:**\n`{changelog}`"
        )
        if len(changelog_str) > 4096:
            await lol.edit("`Changelog terlalu besar, unduh untuk melihatnya.`")
            file = open("output.txt", "w+")
            file.write(changelog_str)
            file.close()
            await tbot.send_file(
                ups.chat_id,
                "output.txt",
                reply_to=ups.id,
            )
            remove("output.txt")
        else:
            await lol.edit(changelog_str)
        await ups.respond("**ketik** `/update now` **untuk update**")
        return

    if force_update:
        await lol.edit("`Tutup-Sinkronisasi ke versi terbaru, mohon tunggu...`")
    else:
        await lol.edit("`Masih berjalan ....`")

    try:
        ups_rem.pull(ac_br)
    except GitCommandError:
        repo.git.reset("--hard", "FETCH_HEAD")
    
    await lol.edit("`Update berhasil!\n" "restarting......`")
    args = [sys.executable, "-m", "Evie"]
    execle(sys.executable, *args, environ)
    return
