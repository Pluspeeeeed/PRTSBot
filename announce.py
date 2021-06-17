import json

import httpx


def announce_decode():
    url = 'https://ak-fs.hypergryph.com/announce/Android/announcement.meta.json'
    with httpx.AsyncClient() as client:
        r = await client.get(url)
        announce_raw = r.json()
        for announce in announce_raw:
            page_data = await client.get(announce['webUrl'])
            print(str(page_data))
            print(announce['announceId'])