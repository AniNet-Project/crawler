# -*- coding: utf-8 -*-

"""
crawl bgm.tv, gen json file.
"""

import sys
import os
import json
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
from itertools import repeat
from datetime import datetime

import fire
import requests
from requests import RequestException, Timeout
from lxml import etree


def get_page(url, timeout=10):
    """ download html according to an url """
    print(f"Fetch page {url}", file=sys.stderr)
    headers = {
        "Referer": url,
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36",
    }
    rsp = requests.get(url, headers=headers, timeout=timeout)
    if rsp.status_code != 200:
        raise RequestException("request failed.")
    html = rsp.content
    return html.decode("utf-8")


def parse_subjects(html):
    tree = etree.HTML(html)
    item_list = tree.xpath('//*[@id="browserItemList"]')[0]
    subs = [
        (li.attrib['id'].split('_')[1], parse_name(li))
        for li in item_list
    ]
    return subs


def parse_name(li):
    return li.xpath('div/h3/a')[0].text


def parse_charaters(html):
    tree = etree.HTML(html)
    elm = tree.xpath('//*[@id="columnInSubjectA"]')[0] 
    elms_a = list( filter(lambda e: e.tag == 'a', elm.getchildren()) )
    ids = [a.attrib['name'].split('_')[1] for a in elms_a]
    return ids


def parse_item(html, id_, url):
    tree = etree.HTML(html)
    name = get_name(tree)
    img_url = get_img_url(tree)
    info = get_detail(tree)
    return {
        'id': id_,
        'label': name,
        'info': info or "",
        'image': 'https:' + img_url,
        'link': url,
        'categorie': 'person',
    }

def get_name(tree):
    elm = tree.xpath('//*[@id="headerSubject"]/h1/small')
    if len(elm) > 0:
        return elm[0].text
    elm = tree.xpath('//*[@id="headerSubject"]/h1/a')[0]
    return elm.text

def get_img_url(tree):
    elm = tree.xpath('//*[@id="columnCrtA"]/div[1]/div/a/img')
    if len(elm) > 0:
        return elm[0].attrib['src']
    else:
        return ''

def get_detail(tree):
    elm = tree.xpath('//*[@id="columnCrtB"]/div[2]')
    if len(elm) > 0:
        return elm[0].text
    else:
        return ''


json_temp = {
    "categories": {
        "person": {
            "label": "人物",
            "color": "#66ccff",
        }
    },
    "data": {
        "nodes": [],
        "edges": [],
    }
}


def process_pid(pid, out_dir):
    url = f"https://bgm.tv/anime/browser?sort=rank&page={pid}"
    while True:
        infos = []
        try:
            html = get_page(url)
            subs = parse_subjects(html)
            for id_, name in subs:
                process_subject(id_, name, out_dir)
                infos.append( (id_, name) )
            return infos
        except Exception as e:
            print(e, file=sys.stderr)


def process_subject(id_, name, out_dir):
    out = f"{out_dir}/{id_}.json"
    if os.path.exists(out):
        print(out, "exists.", file=sys.stderr)
        return id_, name
    json_ = deepcopy(json_temp)
    url = f"https://bgm.tv/subject/{id_}/characters"
    html = get_page(url)
    ch_ids = parse_charaters(html)
    for cid in ch_ids:
        url = f"https://bgm.tv/character/{cid}"
        html = get_page(url)
        item = parse_item(html, cid, url)
        json_['data']['nodes'].append(item)
    with open(out, 'w') as f:
        json.dump(json_, f, ensure_ascii=False, indent=2)
    print(id_, name, sep='\t')
    return id_, name


def main(pages=[1,2,3,4,5,6,7,8,9,10],
         out_dir="./data/json",
         index_json_path="./data/bgm.json",
         workers=20):

    index_json = {
        "data": []
    }
    with ThreadPoolExecutor(max_workers=workers) as e:
        if workers == 1:
            map_ = map
        else:
            map_ = e.map
        for infos in map_(process_pid, pages, repeat(out_dir)):
            for id_, name in infos:
                data_url = f"https://raw.githubusercontent.com/AniNet-Project/crawler/master/data/json/{id_}.json"
                index_json['data'].append({
                    'id': id_, 
                    'name': name,
                    'data': data_url,
                })
    
    index_json['date'] = str(datetime.utcnow())

    with open(index_json_path, 'w') as f:
        json.dump(index_json, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    fire.Fire(main)
