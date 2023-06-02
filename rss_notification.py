import feedparser
from tinydb import TinyDB, Query
import requests
import logging
from bs4 import BeautifulSoup

rss_url_list = ["https://rss.zaqai.com/ssdut",
                "https://rss.zaqai.com/xjtu/se/sxxx",
                "https://rss.zaqai.com/xjtu/se/tzgg",
                "https://rss.zaqai.com/xjtu/se/xwxx",
                "https://rss.zaqai.com/xjtu/se/yjsjw"]
map_key_list = ["ssdut", "xjtu_sxxx", "xjtu_tzgg", "xjtu_xwxx", "xjtu_yjsjw"]
db = TinyDB('db.json')
info = Query()
logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S", level=logging.INFO)


# !!! only execute once for init tinydb(a little ugly)
# db.insert({'key': 'ssdut', 'title': "","link":""})
# db.insert({'key': 'xjtu_sxxx', 'title': "","link":""})
# db.insert({'key': 'xjtu_tzgg', 'title': "","link":""})
# db.insert({'key': 'xjtu_xwxx', 'title': "","link":""})
# db.insert({'key': 'xjtu_yjsjw', 'title': "","link":""})


def push(entry):
    headers = {
        'Content-Type': 'application/json',
    }
    # push server see https://github.com/songquanpeng/message-pusher
    res = requests.post("$PUSH_URL", json={
        "title": entry.title,
        "description": BeautifulSoup(d.entries[0].summary, features="lxml").get_text(),
        "content": entry.summary,
        "channel": "qiyeweixin",
        "url": entry.link
    })
    res = res.json()
    if res["success"]:
        logging.info(f"pushed {entry.title}")
    else:
        logging.warning(res["message"])


for map_key, rss_url in zip(map_key_list, rss_url_list):
    d = feedparser.parse(rss_url)
    entry = d.entries[0]
    res = db.search(info.key == map_key)[0]
    if not (res["title"] == entry.title and res["link"] == entry.link):
        push(entry)
        db.update({'title': entry.title, "link": entry.link},
                  info.key == map_key)
