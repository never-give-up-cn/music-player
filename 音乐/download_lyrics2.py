"""
Second pass: download lyrics for failed songs with better keywords
"""
import os, re, json, urllib.request, urllib.parse, time, sys
sys.stdout.reconfigure(encoding='utf-8')
H = {"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"}

MUSIC_DIR = r"C:\Users\CYH\Desktop\音乐"
os.chdir(MUSIC_DIR)

with open('songs.js','r',encoding='utf-8') as f: content = f.read()
pattern = re.compile(r"\{\s*title:\s*'([^']+)',\s*artist:\s*'([^']+)',\s*file:\s*'([^']+)'\s*\}")
songs = pattern.findall(content)

def fetch(url, hdrs=None):
    h = H.copy()
    if hdrs: h.update(hdrs)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode('utf-8','replace')

def netease_search(keyword):
    url = "https://music.163.com/api/search/get/web?csrf_token=&s=" + urllib.parse.quote(keyword) + "&type=1&offset=0&limit=5"
    try:
        d = json.loads(fetch(url))
        return d.get('result',{}).get('songs',[])
    except: return []

def get_netease_lyric(sid):
    url = f"https://music.163.com/api/song/lyric?id={sid}&lv=1&kv=1&tv=-1"
    try:
        d = json.loads(fetch(url))
        lrc = d.get('lrc',{}).get('lyric','')
        return lrc if lrc.strip() else None
    except: return None

total, ok = 0, 0
for title, artist, filename in songs:
    base = os.path.splitext(filename)[0]
    lrc_path = base + '.lrc'
    if os.path.exists(lrc_path) and os.path.getsize(lrc_path) > 50:
        continue

    # Generate alternative search keywords
    kws = []
    bare = re.sub(r'\(.*?\)', '', title).strip()
    if bare: kws.append(bare)
    kws.append(title)
    kws.append(artist)
    if ' ' in title: kws.append(title.split(' ')[0])
    kws = list(set(k for k in kws if k and len(k) > 1))

    done = False
    for kw in kws:
        songs_data = netease_search(kw)
        if not songs_data: continue
        for s in songs_data:
            lrc = get_netease_lyric(s['id'])
            if lrc:
                lines = []
                for line in lrc.split('\n'):
                    clean = re.sub(r'^\s*\[(ti|ar|al|by|offset):.*?\]\s*', '', line)
                    if clean.strip(): lines.append(clean)
                if lines:
                    with open(lrc_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    print(f"OK {filename}: {len(lines)} lines")
                    done = True; ok += 1; break
        if done: break
    if not done:
        print(f"FAIL {filename}")
    total += 1
    time.sleep(0.5)

print(f"\nSecond pass: {ok}/{total}")
