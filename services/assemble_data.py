import json
import aiohttp
import asyncio

from bs4 import BeautifulSoup, Tag

from repositories.cache import Cache


base_url = "https://whatrocks.github.io"


async def request_speech(client: aiohttp.ClientSession, speech_url: str):
    async with client.get(speech_url) as response:
        speech_text = await response.text()
        return speech_text


async def parse_speech(raw_speech: str) -> str:
    soup = BeautifulSoup(raw_speech)
    speech = soup.select_one(".blog-post-content").text
    return soup.select("h2")[1].text, speech


async def get_speech(client: aiohttp.ClientSession, speech: Tag) -> str:
    speech_url = speech.a.attrs["href"]
    cache_key = ":".join(("speech", speech_url)).replace("/", "-")
    if not (raw_speech := await Cache.get(cache_key)):
        raw_speech = await request_speech(client, base_url+speech_url)
        await Cache.set(cache_key, raw_speech)
    speech_text = await parse_speech(raw_speech)
    return speech_text


async def request_speeches():
    async with aiohttp.ClientSession() as session:
        if not (home_site := await Cache.get("speech:home")):
            home_site = await request_speech(session, base_url+"/commencement-db/")
            await Cache.set("speech:home", home_site)
        soup = BeautifulSoup(home_site)
        speeches_wrappers = soup.div.div.select_one("div:nth-of-type(2)").div.div.children
        speeches_futures = (get_speech(session, speech) for speech in speeches_wrappers)
        speeches = await asyncio.gather(*speeches_futures)
        return {title: speech for title, speech in speeches}


async def get_speeches():
    cache_key = "speeches.json"
    if not (speeches := await Cache.get(cache_key)):
        speeches = await request_speeches()
        await Cache.set(cache_key, json.dumps(speeches))
    else:
        speeches = json.loads(speeches)
    return speeches
