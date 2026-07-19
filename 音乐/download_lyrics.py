"""
Download .lrc lyrics for all songs from Netease Cloud Music
"""
import os, re, json, urllib.request, urllib.parse, time, sys
sys.stdout.reconfigure(encoding='utf-8')
H = {"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"}

MUSIC_DIR = r"C:\Users\CYH\Desktop\音乐"
os.chdir(MUSIC_DIR)

with open('songs.js','r',encoding='utf-8') as f: content = f.read()
pattern = re.compile(r"\{\s*title:\s*'([^']+)',\s*artist:\s*'([^']+)',\s*file:\s*'([^']+)'\s*\}")
songs = pattern.findall(content)

def fetch(url):
    req = urllib.request.Request(url, headers=H)
    with urllib.request.urlopen(req, timeout=10) as r:
        return r.read().decode('utf-8','replace')

def search_id(keyword):
    url = "https://music.163.com/api/search/get/web?csrf_token=&s=" + urllib.parse.quote(keyword) + "&type=1&offset=0&limit=3"
    try:
        d = json.loads(fetch(url))
        songs_data = d.get('result',{}).get('songs',[])
        if songs_data:
            kw_lower = keyword.lower().split()[0] if keyword.split() else ''
            for s in songs_data:
                if kw_lower and kw_lower in s['name'].lower():
                    return s['id']
            return songs_data[0]['id']
    except: pass
    return None

def get_lyric(sid):
    url = f"https://music.163.com/api/song/lyric?id={sid}&lv=1&kv=1&tv=-1"
    try:
        d = json.loads(fetch(url))
        lrc = d.get('lrc',{}).get('lyric','')
        return lrc if lrc.strip() else None
    except: return None

total, ok, skip, fail = len(songs), 0, 0, 0
for i, (title, artist, filename) in enumerate(songs, 1):
    base = os.path.splitext(filename)[0]
    lrc_path = base + '.lrc'
    if os.path.exists(lrc_path):
        skip += 1; continue
    kw = f"{title} {artist}".strip()
    if not kw: kw = title
    print(f"[{i}/{total}] {title[:25]:25s}", end=' ')
    sid = search_id(kw)
    if not sid:
        print("FAIL no id"); fail += 1; continue
    lrc = get_lyric(sid)
    if lrc:
        lines = []
        for line in lrc.split('\n'):
            clean = re.sub(r'^\s*\[(ti|ar|al|by|offset):.*?\]\s*', '', line)
            if clean.strip(): lines.append(clean)
        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))
        print(f"OK {len(lines)} lines")
        ok += 1
    else:
        print("FAIL no lyrics")
        fail += 1
    time.sleep(0.8)

print(f"\nDone! Downloaded:{ok} Skipped:{skip} Failed:{fail}")
