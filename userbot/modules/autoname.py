import asyncio
import time
import datetime
from datetime import datetime
from datetime import datetime, timezone
import pytz
from telethon.tl import functions
from telethon.tl.functions.account import UpdateUsernameRequest 
from telethon.errors import FloodWaitError


DEL_TIME_OUT = 60


@register(outgoing=True, pattern="^.autotime$")
async def _(event):
    if event.fwd_from:
        return
    while True:
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        berlin_time_now = now.strftime("%H:%M")
        firstname =  f"HeManT◡̈⃝ /teamretard/ ⏳ {berlin_time_now}"
        logger.info(firstname)
        try:
            await borg(functions.account.UpdateProfileRequest(  # pylint:disable=E0602
                first_name=firstname

            ))
        except FloodWaitError as ex:
            logger.warning(str(e))
            await asyncio.sleep(ex.seconds)
        # else:
            # logger.info(r.stringify())
            # await borg.send_message(  # pylint:disable=E0602
            #     Config.PRIVATE_GROUP_BOT_API_ID,  # pylint:disable=E0602
            #     "Changed Profile Picture"
            # )
        await asyncio.sleep(DEL_TIME_OUT)

