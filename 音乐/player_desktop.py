"""
蝰蛇音乐播放器 - Desktop Edition
真正的 10 段均衡器音效（基于 ffmpeg）
"""
import tkinter as tk
from tkinter import ttk, font
import pygame
import os, json, time, subprocess, threading, re, shutil, glob
from pathlib import Path

MUSIC_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(MUSIC_DIR, '.viper_cache')
os.makedirs(TEMP_DIR, exist_ok=True)

# ============ EQ Presets (10 bands: 32, 64, 125, 250, 500, 1k, 2k, 4k, 8k, 16k Hz) ============
EQ_BANDS = [32, 64, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

PRESETS = {
    'flat':       [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    '3D丽音':      [2, 1, 0, -1, -1, 0, 2, 4, 6, 8],
    '环绕丽音':    [0, -1, -2, -2, 0, 2, 3, 5, 7, 9],
    'HiFi现场':    [3, 3, 2, 1, 1, 2, 3, 4, 5, 6],
    '演唱会':      [2, 2, 1, 1, 2, 3, 4, 5, 6, 7],
    '声乐古风':    [-2, -1, 1, 3, 4, 3, 2, 1, 0, -1],
    '纯净人声':    [-6, -4, -2, 0, 2, 5, 6, 4, 2, 1],
    '5.1全景':     [0, 0, -1, -1, 0, 2, 4, 6, 8, 10],
    '超重低音':    [12, 12, 8, 4, 2, 0, -2, -4, -6, -8],
    '清澈人声':    [-2, 0, 2, 3, 4, 5, 6, 7, 8, 9],
    '电子乐':      [8, 6, 4, 2, 1, 2, 4, 6, 8, 10],
    '爵士':        [4, 3, 2, 1, 2, 3, 4, 5, 4, 3],
    '古典':        [2, 2, 3, 3, 3, 4, 5, 6, 7, 8],
    '摇滚':        [6, 5, 4, 3, 2, 3, 4, 5, 6, 6],
    '流行':        [4, 4, 3, 2, 2, 3, 4, 5, 6, 7],
    'R&B':         [8, 7, 5, 3, 2, 3, 4, 5, 6, 6],
    '舞曲':        [10, 8, 6, 4, 3, 3, 4, 6, 8, 10],
    '民谣':        [2, 2, 3, 4, 4, 3, 2, 2, 1, 1],
}

class MusicPlayer:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("蝰蛇音乐播放器")
        self.root.geometry("900x650")
        self.root.configure(bg='#0d0d12')

        pygame.mixer.init(frequency=44100, size=-16, channels=2)

        self.playlist = []       # [(title, artist, filepath), ...]
        self.current_idx = -1
        self.playing = False
        self.current_effect = 'flat'
        self.intensity = 70
        self.processed_file = None  # path to current EQ-processed file
        self.song_end_event = threading.Event()

        self.load_playlist()
        self.build_ui()
        self.check_song_end()

    # ============ Playlist ============
    def load_playlist(self):
        """Load songs.js if exists, otherwise scan MP3 files"""
        songs_js = os.path.join(MUSIC_DIR, 'songs.js')
        if os.path.exists(songs_js):
            self.playlist = self.parse_songs_js(songs_js)
        if not self.playlist:
            self.playlist = self.scan_mp3s()

    def parse_songs_js(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        pattern = re.compile(r"\{\s*title:\s*'([^']+)',\s*artist:\s*'([^']+)',\s*file:\s*'([^']+)'\s*\}")
        result = []
        for t, a, fname in pattern.findall(content):
            fpath = os.path.join(MUSIC_DIR, fname)
            if os.path.exists(fpath):
                result.append((t, a, fpath))
        return result

    def scan_mp3s(self):
        result = []
        for f in sorted(glob.glob(os.path.join(MUSIC_DIR, '*.mp3'))):
            title = os.path.splitext(os.path.basename(f))[0]
            result.append((title, '', f))
        return result

    # ============ EQ Processing ============
    def apply_eq(self, src_path, effect, intensity=70):
        """Use ffmpeg to apply 10-band EQ, return path to processed file"""
        gains = PRESETS.get(effect, PRESETS['flat'])
        intensity_scale = intensity / 70.0

        # Build ffmpeg equalizer filter chain
        filters = []
        for i, gain in enumerate(gains):
            db = gain * intensity_scale
            if abs(db) < 0.5: continue  # skip negligible bands
            q = 0.7 + (i * 0.05)
            filters.append(f"equalizer=f={EQ_BANDS[i]}:t=q:w={q}:g={db:.1f}")

        if not filters:
            return src_path  # no processing needed

        filter_str = ','.join(filters)

        base = os.path.splitext(os.path.basename(src_path))[0]
        safe = re.sub(r'[^\w\-]', '_', f"{base}_{effect}_{int(intensity)}")
        out_path = os.path.join(TEMP_DIR, f"{safe}.mp3")

        if os.path.exists(out_path):
            return out_path  # already cached

        cmd = ['ffmpeg', '-i', src_path, '-af', filter_str,
               '-b:a', '192k', '-q:a', '2', '-y', out_path,
               '-loglevel', 'error']
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            return out_path
        except:
            return src_path  # fallback to original

    def clear_cache(self):
        if os.path.exists(TEMP_DIR):
            for f in glob.glob(os.path.join(TEMP_DIR, '*.mp3')):
                try: os.remove(f)
                except: pass

    # ============ Playback ============
    def play_file(self, filepath):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        time.sleep(0.05)
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Play error: {e}")

    def play_song(self, idx=None):
        if idx is not None:
            self.current_idx = idx
        if self.current_idx < 0 or self.current_idx >= len(self.playlist):
            return
        title, artist, filepath = self.playlist[self.current_idx]
        self.update_song_info()

        if self.current_effect != 'flat':
            # Process with EQ in background thread
            self.status_var.set(f"处理音效: {self.current_effect}...")
            self.root.update()
            threading.Thread(target=self._process_and_play, args=(filepath,), daemon=True).start()
        else:
            self.processed_file = None
            self.play_file(filepath)
            self.playing = True
            self.update_ui()
            self.status_var.set("")

    def _process_and_play(self, filepath):
        out = self.apply_eq(filepath, self.current_effect, self.intensity)
        self.processed_file = out
        self.root.after(0, self._play_processed, out)

    def _play_processed(self, out):
        self.play_file(out)
        self.playing = True
        self.update_ui()
        self.status_var.set(f"音效: {self.current_effect}")

    def toggle_play(self):
        if not self.playlist:
            return
        if self.playing and pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.playing = False
        elif not pygame.mixer.music.get_busy():
            self.play_song()
        else:
            pygame.mixer.music.unpause()
            self.playing = True
        self.update_ui()

    def next_song(self):
        if self.playlist:
            self.play_song((self.current_idx + 1) % len(self.playlist))

    def prev_song(self):
        if self.playlist:
            self.play_song((self.current_idx - 1) % len(self.playlist))

    def change_effect(self, effect):
        if effect == self.current_effect:
            return
        self.current_effect = effect
        self.update_effect_ui()

        if self.playing and self.current_idx >= 0:
            self.status_var.set(f"切换音效: {effect}...")
            _, _, filepath = self.playlist[self.current_idx]
            if effect == 'flat':
                self.processed_file = None
                # Restart with original
                pos = self.get_pos()
                self.play_file(filepath)
                self.set_pos(pos)
                self.status_var.set("")
            else:
                threading.Thread(target=self._process_and_play, args=(filepath,), daemon=True).start()

    def change_intensity(self, val):
        self.intensity = int(val)
        if self.current_effect != 'flat' and self.playing and self.current_idx >= 0:
            _, _, filepath = self.playlist[self.current_idx]
            self.status_var.set(f"调整强度: {self.intensity}%...")
            threading.Thread(target=self._process_and_play, args=(filepath,), daemon=True).start()

    def get_pos(self):
        try: return pygame.mixer.music.get_pos()
        except: return 0

    def set_pos(self, ms):
        try:
            pygame.mixer.music.rewind()
            time.sleep(0.05)
            pygame.mixer.music.play(start=ms//1000)
        except: pass

    def check_song_end(self):
        """Poll for song end and auto-advance"""
        if self.playing and not pygame.mixer.music.get_busy() and self.current_idx >= 0:
            self.next_song()
        self.root.after(500, self.check_song_end)

    # ============ UI ============
    def build_ui(self):
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # === Colors ===
        bg = '#0d0d12'
        surface = '#1a1a24'
        card = '#222233'
        gold = '#f0b429'
        text = '#eee'
        textdim = '#888'
        self.colors = {'bg': bg, 'surface': surface, 'card': card, 'gold': gold, 'text': text, 'textdim': textdim}
        self.root.configure(bg=bg)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TScale', background=bg, troughcolor='#333', slidercolor=gold)

        # === Main Frame ===
        main = tk.Frame(self.root, bg=bg)
        main.grid(row=0, column=0, sticky='nsew', padx=12, pady=12)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        # === Left Panel - Playlist ===
        left = tk.Frame(main, bg=surface, width=280)
        left.grid(row=0, column=0, sticky='nsw', padx=(0,8))
        left.rowconfigure(1, weight=1)

        tk.Label(left, text="播放列表", bg=surface, fg=text,
                 font=('Microsoft YaHei', 13, 'bold')).grid(row=0, column=0, pady=(10,5), padx=10, sticky='w')

        list_frame = tk.Frame(left, bg=surface)
        list_frame.grid(row=1, column=0, sticky='nsew', padx=5, pady=5)

        self.listbox = tk.Listbox(list_frame, bg=card, fg=text, selectbackground=gold,
                                  selectforeground='#000', font=('Microsoft YaHei', 11),
                                  borderwidth=0, highlightthickness=0, width=30, height=20)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', lambda e: self._on_playlist_select())

        scroll = tk.Scrollbar(list_frame, orient='vertical', command=self.listbox.yview)
        scroll.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scroll.set)

        self.populate_playlist()

        # === Right Panel ===
        right = tk.Frame(main, bg=bg)
        right.grid(row=0, column=1, sticky='nsew')
        right.columnconfigure(0, weight=1)

        # Song Info
        self.info_frame = tk.Frame(right, bg=bg, height=80)
        self.info_frame.pack(fill='x', pady=(5,10))
        self.title_var = tk.StringVar(value="选择歌曲")
        self.artist_var = tk.StringVar(value="")
        tk.Label(self.info_frame, textvariable=self.title_var, bg=bg, fg=text,
                 font=('Microsoft YaHei', 18, 'bold')).pack(anchor='w')
        tk.Label(self.info_frame, textvariable=self.artist_var, bg=bg, fg=textdim,
                 font=('Microsoft YaHei', 12)).pack(anchor='w')

        # Controls
        ctrl = tk.Frame(right, bg=bg)
        ctrl.pack(fill='x', pady=5)

        self.btn_play = tk.Button(ctrl, text="▶ 播放", command=self.toggle_play,
                                  bg=gold, fg='#000', font=('Microsoft YaHei', 11, 'bold'),
                                  width=10, borderwidth=0, padx=15, pady=5)
        self.btn_play.pack(side='left', padx=3)

        tk.Button(ctrl, text="⏮", command=self.prev_song,
                  bg=surface, fg=text, font=('Arial', 14), width=3, borderwidth=0).pack(side='left', padx=2)
        tk.Button(ctrl, text="⏭", command=self.next_song,
                  bg=surface, fg=text, font=('Arial', 14), width=3, borderwidth=0).pack(side='left', padx=2)

        # Status
        self.status_var = tk.StringVar(value="")
        tk.Label(ctrl, textvariable=self.status_var, bg=bg, fg=gold,
                 font=('Microsoft YaHei', 10)).pack(side='right', padx=10)

        # === EQ Section ===
        eq_frame = tk.Frame(right, bg=surface, bd=1, relief='solid', highlightbackground='#333')
        eq_frame.pack(fill='both', expand=True, pady=(5,0))

        # EQ Header
        eq_header = tk.Frame(eq_frame, bg=surface)
        eq_header.pack(fill='x', padx=10, pady=(8,5))

        tk.Label(eq_header, text="🐍 蝰蛇音效", bg=surface, fg=gold,
                 font=('Microsoft YaHei', 13, 'bold')).pack(side='left')

        self.eq_on = tk.BooleanVar(value=False)
        self.eq_toggle = tk.Checkbutton(eq_header, variable=self.eq_on,
                                         command=self._on_eq_toggle,
                                         bg=surface, fg=text, selectcolor=surface,
                                         activebackground=surface,
                                         font=('Microsoft YaHei', 10))
        tk.Label(eq_header, text="关闭", bg=surface, fg=textdim,
                 font=('Microsoft YaHei', 10)).pack(side='right', padx=2)
        self.eq_toggle.pack(side='right')
        tk.Label(eq_header, text="开启", bg=surface, fg=textdim,
                 font=('Microsoft YaHei', 10)).pack(side='right')

        # Intensity
        int_frame = tk.Frame(eq_frame, bg=surface)
        int_frame.pack(fill='x', padx=10, pady=2)
        tk.Label(int_frame, text="强度", bg=surface, fg=textdim,
                 font=('Microsoft YaHei', 9)).pack(side='left')
        self.int_slider = tk.Scale(int_frame, from_=10, to=100, orient='horizontal',
                                    bg=surface, fg=text, troughcolor='#333',
                                    highlightbackground=surface,
                                    command=lambda v: self.change_intensity(v))
        self.int_slider.set(self.intensity)
        self.int_slider.pack(side='right', fill='x', expand=True, padx=(5,0))

        # EQ Visualizer (placeholder)
        self.viz_frame = tk.Frame(eq_frame, bg='#111', height=50)
        self.viz_frame.pack(fill='x', padx=10, pady=3)
        self.viz_bars = []
        for _ in range(10):
            bar = tk.Frame(self.viz_frame, bg='#333', width=20)
            bar.pack(side='left', expand=True, padx=1, pady=3)
            self.viz_bars.append(bar)

        # EQ Grid
        grid_frame = tk.Frame(eq_frame, bg=surface)
        grid_frame.pack(fill='both', expand=True, padx=10, pady=(5,10))

        presets = list(PRESETS.keys())
        # Organize in rows of 4
        for i, name in enumerate(presets):
            if name == 'flat': continue  # hidden
            row, col = divmod(i, 4)
            btn = tk.Button(grid_frame, text=name,
                            command=lambda n=name: self._on_preset_click(n),
                            bg=card, fg=text, activebackground=gold, activeforeground='#000',
                            font=('Microsoft YaHei', 10),
                            borderwidth=0, padx=8, pady=6, width=10)
            btn.grid(row=row, column=col, padx=3, pady=3, sticky='ew')
            grid_frame.columnconfigure(col, weight=1)

        self.eq_buttons = {}  # will track for highlighting

        # === Binding ===
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def populate_playlist(self):
        self.listbox.delete(0, 'end')
        for title, artist, _ in self.playlist:
            display = title[:30] + ('..' if len(title) > 30 else '')
            self.listbox.insert('end', display)

    def update_song_info(self):
        if 0 <= self.current_idx < len(self.playlist):
            title, artist, _ = self.playlist[self.current_idx]
            self.title_var.set(title)
            self.artist_var.set(artist or '')

    def update_ui(self):
        self.btn_play.config(text="⏸ 暂停" if self.playing else "▶ 播放")

    def update_effect_ui(self):
        """Update EQ visualizer bars"""
        gains = PRESETS.get(self.current_effect, PRESETS['flat'])
        intensity = self.intensity / 70.0
        max_gain = 12
        for i, bar in enumerate(self.viz_bars):
            g = (gains[i] if i < len(gains) else 0) * intensity
            pct = min(100, max(5, abs(g) / max_gain * 100))
            color = '#f0b429' if g >= 0 else '#666'
            bar.configure(bg=color, height=int(pct))

    def _on_playlist_select(self):
        sel = self.listbox.curselection()
        if sel:
            self.play_song(sel[0])

    def _on_eq_toggle(self):
        if self.eq_on.get():
            self.current_effect = '3D丽音'
            self.update_effect_ui()
            if self.playing and self.current_idx >= 0:
                _, _, filepath = self.playlist[self.current_idx]
                self.status_var.set(f"处理音效: {self.current_effect}...")
                threading.Thread(target=self._process_and_play, args=(filepath,), daemon=True).start()
        else:
            self.current_effect = 'flat'
            self.update_effect_ui()
            if self.playing and self.current_idx >= 0:
                _, _, filepath = self.playlist[self.current_idx]
                pos = self.get_pos()
                self.play_file(filepath)
                self.set_pos(pos)
                self.status_var.set("")

    def _on_preset_click(self, name):
        self.eq_on.set(True)
        self.change_effect(name)

    def on_close(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.clear_cache()
        try: pygame.mixer.quit()
        except: pass
        self.root.destroy()

    def run(self):
        self.root.mainloop()

if __name__ == '__main__':
    app = MusicPlayer()
    app.run()
