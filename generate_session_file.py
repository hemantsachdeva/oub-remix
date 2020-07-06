from telethon import TelegramClient
from telethon.sessions import StringSession

print("""Aa gaye Betichod string generate karne. 
lodu use ==>> my.telegram.com (vpn use karna) <<==
Apna Telegram Account login kar btc
Click on API Development Tools Blah Blah Maa ki chu
Create a new application, by entering the required details of teri Maa ka bhosda""")


APP_API_ID = int(input("Madarchod APP API ID Daal Behen Ke Lawde: "))
APP_API_HASH = input("Gandu Khush Matt Ho Ab APP API HASH daal: ")
with TelegramClient(StringSession(), APP_API_ID, APP_API_HASH) as client:
    print(client.session.save())
