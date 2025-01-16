import requests
import json
from pprint import pprint
from datetime import datetime as dt
from bs4 import BeautifulSoup
import re
import glob 
from itertools import chain 
from collections import OrderedDict

archive = requests.get('https://a.4cdn.org/pol/archive.json')
archivethread = archive.json()

with open ("archivethread.json", "w") as f: 
    json.dump(archivethread, f)

def archthreadcontent (thread_no):
    try: 
        url = f"https://a.4cdn.org/pol/thread/{thread_no}.json"
        v = requests.get(url) 
        vr = v.json()
        with open (f"{thread_no}_thread.json", "w") as file: 
            json.dump(vr, file)
        status = f"{len(vr)} posts saved for {thread_no}"
        return status 
    except: 
        status = "SOMETHING WENT WRONG NOOOOOOOO"
        return status   
def relpostinfo (a_post): 
    relevant_keys = ["no", "resto", "now", "time", "name", "id", "sub", "com", "ext", "replies", "images", "unique_ips", "archived_on"]
    filtered_dict = {key: a_post[key] for key in relevant_keys if key in (list(a_post.keys()))}
    return filtered_dict
def string_cleaning (string_pun): 
    new = re.sub(r"https?:[^\s]+", "", string_pun)
    return new 
def text_key(a_dict): 
    try: 
        soup = BeautifulSoup(a_dict['com'], 'html.parser')
        meow = soup.get_text(separator=' ').strip()
        a_dict['text'] = string_cleaning(meow)
        # try to find the 'quotelink' and extract the ID if it exists
        id_link = soup.find('a', class_='quotelink')
        if id_link and id_link.get('href'):
            id_number = id_link['href'].lstrip('#p')
            a_dict['id'] = id_number
        return a_dict
    except: 
        return 'no com founds?'
def transform_dict(data):
    if "text" in data:  # Check if 'text' key exists
        match = re.search(r'>>(\d+)', data["text"])  # Find pattern >>numbers
        if match:
            data["replyto"] = match.group(1)  # Add 'replyto' key with extracted number
            data["text"] = re.sub(r'>>\d+', '', data["text"]).strip()  # Remove >>numbers from 'text'
    return data

def build_all_threads(posts):
    no_to_post = {str(post['no']): post for post in posts if isinstance(post, dict) and 'no' in post}
    threads = []
    processed = set()
    def follow_chain(post):
        chain = []
        current = post
        while current:
            chain.append(current['no'])  # Add the 'no' value to the chain
            processed.add(current['no'])
            replyto = str(current.get('replyto')) if current.get('replyto') else None  
            if replyto is None or replyto in processed: 
                break
            if replyto in no_to_post:
                current = no_to_post[replyto]
            else:  
                current = None  # End the chain
        return chain
    for post in posts:
        if isinstance(post, dict) and str(post['no']) not in processed:      
            chain = follow_chain(post)      
            threads.append(chain)
    return threads


omg = [archthreadcontent(m) for m in archivethread]
combined = []
for json_file in glob.glob("*.json"):
    with open (json_file, "rb") as infile: 
        combined.append(json.load(infile))

letsgo = [[relpostinfo(m) for m in l['posts']] for l in combined]
final = [[text_key(a) for a in m] for m in letsgo]

# output the archive here
with open ("sets\cleanarchive.json", "w") as f: 
    json.dump(final, f)

with open ('sets/cleanarchive.json', 'r') as file: 
    data = json.load(file)
v = list(chain.from_iterable(data)) 
f = [m['text'] for m in v if isinstance(m, dict)] #f is the dict with sentences only 
va = [x for x in v if isinstance(x, dict)]
vb = [[x for x in y if isinstance(x, dict)] for y in data]
a = [transform_dict(x) for x in v]
a1 = [[transform_dict(x) for x in y] for y in vb]
me = [build_all_threads(x) for x in a1]

with open('nested_list.txt', 'w') as f:
    json.dump(me, f)

