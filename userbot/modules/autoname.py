"""Auto Profile Updation Commands
.autoname"""
from telethon import events
import asyncio
import time
from telethon.tl import functions
from telethon.errors import FloodWaitError
#from userbot.utils import admin_cmd
from userbot import CMD_HELP
from userbot import ALIVE_NAME


DEL_TIME_OUT = 60
DEFAULTUSER = str(ALIVE_NAME) if ALIVE_NAME else "FridayUserbot"


#@borg.on(admin_cmd(pattern="autoname"))  # pylint:disable=E0602
@register(outgoing=True, pattern="^.autoname (.*)")
async def _(event):
    if event.fwd_from:
        return
    while True:
       
        HM = time.strftime("%H:%M")
        name = f"🕒{HM} ⚡HeManT◡̈⃝ /teamretard/⚡"
        logger.info(name)
        try:
            await borg(functions.account.UpdateProfileRequest(  # pylint:disable=E0602
                first_name=name
            ))
        except FloodWaitError as ex:
            logger.warning(str(e))
            await asyncio.sleep(ex.seconds)
    
        # else:
            # logger.info(r.stringify())
            # await borg.send_message(  # pylint:disable=E0602
            #     Config.PRIVATE_GROUP_BOT_API_ID,  # pylint:disable=E0602
            #     "Successfully Changed Profile Name"
            # )
        await asyncio.sleep(DEL_TIME_OUT)
    await event.edit(f"Auto Name has been started Master") 
