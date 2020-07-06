# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.b (the "License");
# you may not use this file except in compliance with the License.
#
# This script wont run your bot, it just generates a session.

from telethon import TelegramClient
from dotenv import load_dotenv
import os

print("""Aa gaye Betichod string generate karne. 
lodu use ==>> my.telegram.com (vpn use karna) <<==
Apna Telegram Account login kar btc
Click on API Development Tools Blah Blah Maa ki chu
Create a new application, by entering the required details Maa ka bhosda""")

load_dotenv("config.env")

API_KEY = int(input("Madarchod APP ID Daal Behen Ke Lawde: "))
API_HASH = input("Gandu Khush Matt Ho Ab API HASH daal: ")

bot = TelegramClient('userbot', API_KEY, API_HASH)
bot.start()
