# Copyright (C) 2019 The Raphielscape Company LLC.
#
# Licensed under the Raphielscape Public License, Version 1.d (the "License");
# you may not use this file except in compliance with the License.

from bs4 import BeautifulSoup as bs
import requests
import json
import os
import aria2p
import math
from asyncio import sleep
from subprocess import PIPE, Popen
from userbot import LOGS, CMD_HELP, TEMP_DOWNLOAD_DIRECTORY
from userbot.events import register
from userbot.utils import humanbytes
from requests import get


def subprocess_run(cmd):
    subproc = Popen(cmd, stdout=PIPE, stderr=PIPE,
                    shell=True, universal_newlines=True)
    talk = subproc.communicate()
    exitCode = subproc.returncode
    if exitCode != 0:
        return
    return talk


# Get best trackers for improved download speeds, thanks K-E-N-W-A-Y.
trackers_list = get(
    'https://raw.githubusercontent.com/ngosang/trackerslist/master/trackers_best.txt'
).text.replace('\n\n', ',')
trackers = f"[{trackers_list}]"

cmd = f"aria2c \
--enable-rpc \
--rpc-listen-all=false \
--rpc-listen-port 6800 \
--max-connection-per-server=10 \
--rpc-max-request-size=1024M \
--seed-time=0.01 \
--max-upload-limit=5K \
--max-concurrent-downloads=5 \
--min-split-size=10M \
--follow-torrent=mem \
--split=10 \
--bt-tracker={trackers} \
--daemon=true \
--allow-overwrite=true"

subprocess_run(cmd)
if not os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
    os.makedirs(TEMP_DOWNLOAD_DIRECTORY)
download_path = os.getcwd() + TEMP_DOWNLOAD_DIRECTORY.strip('.')

aria2 = aria2p.API(aria2p.Client(host="http://localhost", port=6800,
                                 secret=""))

aria2.set_global_options({'dir': download_path})


@register(outgoing=True, pattern="^.amag(?: |$)(.*)")
async def magnet_download(event):
    magnet_uri = event.pattern_match.group(1)
    # Add Magnet URI Into Queue
    try:
        download = aria2.add_magnet(magnet_uri)
    except Exception as e:
        LOGS.info(str(e))
        return await event.edit("Error:\n`" + str(e) + "`")
    gid = download.gid
    await check_progress_for_dl(gid=gid, event=event, previous=None)
    await sleep(5)
    new_gid = await check_metadata(gid)
    await check_progress_for_dl(gid=new_gid, event=event, previous=None)


@register(outgoing=True, pattern="^.ator(?: |$)(.*)")
async def torrent_download(event):
    torrent_file_path = event.pattern_match.group(1)
    # Add Torrent Into Queue
    try:
        download = aria2.add_torrent(torrent_file_path,
                                     uris=None,
                                     options=None,
                                     position=None)
    except Exception as e:
        return await event.edit(str(e))
    gid = download.gid
    await check_progress_for_dl(gid=gid, event=event, previous=None)


@register(outgoing=True, pattern="^.aurl(?: |$)(.*)")
async def aurl_download(event):
    uri = [event.pattern_match.group(1)]
    try:  # Add URL Into Queue
        download = aria2.add_uris(uri, options=None, position=None)
    except Exception as e:
        LOGS.info(str(e))
        return await event.edit("Error :\n`{}`".format(str(e)))
    gid = download.gid
    await check_progress_for_dl(gid=gid, event=event, previous=None)
    file = aria2.get_download(gid)
    if file.followed_by_ids:
        new_gid = await check_metadata(gid)
        await check_progress_for_dl(gid=new_gid, event=event, previous=None)


@register(outgoing=True, pattern="^.aclear(?: |$)(.*)")
async def remove_all(event):
    try:
        removed = aria2.remove_all(force=True)
        aria2.purge_all()
    except Exception:
        pass
    if not removed:  # If API returns False Try to Remove Through System Call.
        subprocess_run("aria2p remove-all")
    await event.edit("`Clearing on-going downloads... `")
    await sleep(2.5)
    await event.edit("`Successfully cleared all downloads.`")
    await sleep(2.5)


@register(outgoing=True, pattern="^.apause(?: |$)(.*)")
async def pause_all(event):
    # Pause ALL Currently Running Downloads.
    await event.edit("`Pausing downloads...`")
    aria2.pause_all(force=True)
    await sleep(2.5)
    await event.edit("`Successfully paused on-going downloads.`")
    await sleep(2.5)


@register(outgoing=True, pattern="^.aresume(?: |$)(.*)")
async def resume_all(event):
    await event.edit("`Resuming downloads...`")
    aria2.resume_all()
    await sleep(1)
    await event.edit("`Downloads resumed.`")
    await sleep(2.5)
    await event.delete()


@register(outgoing=True, pattern="^.ashow(?: |$)(.*)")
async def show_all(event):
    output = "output.txt"
    downloads = aria2.get_downloads()
    msg = ""
    for download in downloads:
        msg = msg + "File: `" + str(download.name) + "`\nSpeed: " + str(
            download.download_speed_string()) + "\nProgress: " + str(
                download.progress_string()) + "\nTotal Size: " + str(
                    download.total_length_string()) + "\nStatus: " + str(
                        download.status) + "\nETA:  " + str(
                            download.eta_string()) + "\n\n"
    if len(msg) <= 4096:
        await event.edit("`On-going Downloads: `\n" + msg)
        await sleep(5)
        await event.delete()
    else:
        await event.edit("`Output is too big, sending it as a file...`")
        with open(output, 'w') as f:
            f.write(msg)
        await sleep(2)
        await event.delete()
        await event.client.send_file(
            event.chat_id,
            output,
            force_document=True,
            supports_streaming=False,
            allow_cache=False,
            reply_to=event.message.id,
        )


async def check_metadata(gid):
    file = aria2.get_download(gid)
    new_gid = file.followed_by_ids[0]
    LOGS.info("Changing GID " + gid + " to" + new_gid)
    return new_gid


async def check_progress_for_dl(gid, event, previous):
    complete = None
    while not complete:
        file = aria2.get_download(gid)
        complete = file.is_complete
        try:
            if not complete and not file.error_message:
                percentage = int(file.progress)
                downloaded = percentage * int(file.total_length) / 100
                prog_str = "`Downloading` | [{0}{1}] `{2}`".format(
                    "".join(["■" for i in range(
                            math.floor(percentage / 10))]),
                    "".join(["▨" for i in range(
                            10 - math.floor(percentage / 10))]),
                    file.progress_string())
                msg = (
                    f"`Name`: `{file.name}`\n"
                    f"`Status` -> **{file.status.capitalize()}**\n"
                    f"{prog_str}\n"
                    f"`{humanbytes(downloaded)} of {file.total_length_string()}"
                    f" @ {file.download_speed_string()}`\n"
                    f"`ETA` -> {file.eta_string()}\n"
                )
                if msg != previous:
                    await event.edit(msg)
                    msg = previous
            else:
                await event.edit(f"`{msg}`")
            await sleep(5)
            await check_progress_for_dl(gid, event, previous)
            file = aria2.get_download(gid)
            complete = file.is_complete
            if complete:
                return await event.edit(
                    f"`Name`: `{file.name}`\n"
                    f"`Size`: `{file.total_length_string()}`\n"
                    f"`Path`: `{TEMP_DOWNLOAD_DIRECTORY + file.name}`\n"
                    "`Response`: **OK** - Successfully downloaded..."
                )
        except Exception as e:
            if " not found" in str(e) or "'file'" in str(e):
                await event.edit("Download Canceled :\n`{}`".format(file.name))
                await sleep(2.5)
                return await event.delete()
            elif " depth exceeded" in str(e):
                file.remove(force=True)
                await event.edit(
                    "Download Auto Canceled :\n`{}`\nYour Torrent/Link is Dead."
                    .format(file.name))
def dogbin(magnets):
	counter = 0
	urls = []
	while counter != len(magnets):
		message = magnets[counter]
		url = "https://del.dog/documents"
		r = requests.post(url, data=message.encode("UTF-8")).json()
		url = f"https://del.dog/{r['key']}"
		urls.append(url)
		counter = counter + 1
	return urls	
	
@register(outgoing=True, pattern="^.tsearch(?: |$)(.*)")
async def tor_search(event):
	if event.fwd_from:
		return 
	headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36'}

	search_str = event.pattern_match.group(1)

	print(search_str)
	await event.edit("Searching for "+search_str+".....")
	if " " in search_str:
		search_str = search_str.replace(" ","+")
		print(search_str)
		res = requests.get("https://www.torrentdownloads.me/search/?new=1&s_cat=0&search="+search_str,headers)

	else:
		res = requests.get("https://www.torrentdownloads.me/search/?search="+search_str,headers)

	source = bs(res.text,'lxml')
	urls = []
	magnets = []
	titles = []
	counter = 0
	for div in source.find_all('div',{'class':'grey_bar3 back_none'}):
		# print("https://www.torrentdownloads.me"+a['href'])
		try:
			title = div.p.a['title']
			title = title[20:]
			titles.append(title)
			urls.append("https://www.torrentdownloads.me"+div.p.a['href'])
		except KeyError:
			pass
		except TypeError:
			pass
		except AttributeError:
			pass	
		if counter == 11:
			break		
		counter = counter + 1
	if not urls:
		await event.edit("Either the Keyword was restricted or not found..")		
		return

	print("Found URLS...")
	for url in urls:
		res = requests.get(url,headers)
		# print("URl: "+url)
		source = bs(res.text,'lxml')
		for div in source.find_all('div',{'class':'grey_bar1 back_none'}):
			try:
				mg = div.p.a['href']
				magnets.append(mg)
			except Exception as e:
				pass	
	print("Found Magnets...")
	shorted_links = dogbin(magnets)
	print("Dogged Magnets to del.dog...")
	msg = ""
	try:
		search_str = search_str.replace("+"," ")
	except:
		pass	
	msg = "**Torrent Search Query**\n`{}`".format(search_str)+"\n**Results**\n"
	counter = 0
	while counter != len(titles):
		msg = msg + "⁍ [{}]".format(titles[counter])+"({})".format(shorted_links[counter])+"\n\n"
		counter = counter + 1


	await event.edit(msg,link_preview=False)
CMD_HELP.update({
    "aria":
    "`.aurl` [URL] (or) .amag [Magnet Link] (or) .ator [path to torrent file]\
    \nUsage: Downloads the file into your userbot server storage.\
    \n\n`.apause` (or) .aresume\
    \nUsage: Pauses/resumes on-going downloads.\
    \n\n`.aclear`\
    \nUsage: Clears the download queue, deleting all on-going downloads.\
    \n\n`.ashow`\
    \nUsage: Shows progress of the on-going downloads.\
    \n\n`.tsearch <query>`\
    \nUsage: Searches torrent."
})
