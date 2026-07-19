"""
蝰蛇音乐播放器 - Desktop Edition
真正的 10 段均衡器音效（基于 ffmpeg）+ 进度条 + 歌词
"""
import tkinter as tk
from tkinter import ttk
import pygame
import os, json, time, subprocess, threading, re, glob, random

MUSIC_DIR = os.path.dirname(os.path.abspath(__file__))
TEMP_DIR = os.path.join(MUSIC_DIR, '.viper_cache')
os.makedirs(TEMP_DIR, exist_ok=True)

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
        self.root.geometry("950x680+50+50")
        self.root.configure(bg='#0d0d12')
        self.root.minsize(800, 600)

        pygame.mixer.init(frequency=44100, size=-16, channels=2)

        self.playlist = []
        self.current_idx = -1
        self.playing = False
        self.current_effect = 'flat'
        self.intensity = 70
        self.processed_file = None
        self.current_src_path = None  # original filepath (for lyrics lookup)
        self.length_cache = {}  # filepath -> duration seconds
        self.seek_offset = 0.0  # for pygame.get_pos() correction after seek

        # Song length tracking (pygame can't always get_length reliably)
        self.song_length = 0  # seconds
        self.song_start_time = 0  # time.time() when playback started

        # Lyrics
        self.lyrics_data = []  # [(timestamp_sec, text), ...]
        self.lyric_idx = -1

        self.load_playlist()
        self.build_ui()
        self.poll_progress()
        self.poll_song_end()

    # ==================== Playlist ====================
    def load_playlist(self):
        songs_js = os.path.join(MUSIC_DIR, 'songs.js')
        if os.path.exists(songs_js):
            self.playlist = self.parse_songs_js(songs_js)
        if not self.playlist:
            self.playlist = self.scan_mp3s()
        # Pre-cache song lengths in background
        threading.Thread(target=self._precache_lengths, daemon=True).start()

    def _precache_lengths(self):
        for _, _, fpath in self.playlist:
            if fpath not in self.length_cache:
                try:
                    dur = self.get_song_length(fpath)
                    self.length_cache[fpath] = dur
                except: pass

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

    # ==================== Lyrics ====================
    def load_lyrics(self, mp3_path):
        """Load .lrc file matching the mp3"""
        self.lyrics_data = []
        self.lyric_idx = -1
        self.lyric_text.config(state='normal')
        self.lyric_text.delete(1.0, 'end')

        lrc_path = os.path.splitext(mp3_path)[0] + '.lrc'
        if not os.path.exists(lrc_path):
            lrc_path = os.path.join(MUSIC_DIR, 'lyrics', os.path.splitext(os.path.basename(mp3_path))[0] + '.lrc')

        if os.path.exists(lrc_path):
            self.parse_lrc(lrc_path)

        if self.lyrics_data:
            self.lyric_text.insert('end', '\n'.join([''] * 3))
            self.lyric_text.insert('end', '\n'.join([t for _, t in self.lyrics_data]))
        else:
            self.lyric_text.insert('end', '暂无歌词')
        self.lyric_text.config(state='disabled')

    def parse_lrc(self, path):
        """Parse .lrc file into [(time_sec, text), ...]"""
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        pattern = re.compile(r'\[(\d+):(\d+(?:\.\d+)?)\](.*)')
        for line in lines:
            m = pattern.match(line.strip())
            if m:
                minutes = int(m.group(1))
                seconds = float(m.group(2))
                text = m.group(3).strip()
                if text:
                    self.lyrics_data.append((minutes * 60 + seconds, text))

        self.lyrics_data.sort(key=lambda x: x[0])

    def update_lyrics(self, pos_sec):
        """Scroll lyrics to match current position"""
        if not self.lyrics_data:
            return
        idx = -1
        for i, (ts, _) in enumerate(self.lyrics_data):
            if ts <= pos_sec:
                idx = i
            else:
                break
        if idx != self.lyric_idx and idx >= 0:
            self.lyric_idx = idx
            # Highlight current line by scrolling to it
            line_start = 4 + idx  # +4 for initial blank lines
            self.lyric_text.tag_remove('current', 1.0, 'end')
            self.lyric_text.tag_add('current', f'{line_start}.0', f'{line_start}.end')
            self.lyric_text.tag_configure('current', foreground='#f0b429', font=('Microsoft YaHei', 12, 'bold'))
            # Make sure it's visible
            self.lyric_text.see(f'{line_start}.0')

    # ==================== EQ Processing ====================
    def apply_eq(self, src_path, effect, intensity=70):
        gains = PRESETS.get(effect, PRESETS['flat'])
        intensity_scale = intensity / 70.0
        filters = []
        for i, gain in enumerate(gains):
            db = gain * intensity_scale
            if abs(db) < 0.5:
                continue
            q = 0.7 + (i * 0.05)
            filters.append(f"equalizer=f={EQ_BANDS[i]}:t=q:w={q}:g={db:.1f}")
        if not filters:
            return src_path
        filter_str = ','.join(filters)
        base = os.path.splitext(os.path.basename(src_path))[0]
        safe = re.sub(r'[^\w\-]', '_', f"{base}_{effect}_{int(intensity)}")
        out_path = os.path.join(TEMP_DIR, f"{safe}.mp3")
        if os.path.exists(out_path):
            return out_path
        cmd = ['ffmpeg', '-i', src_path, '-af', filter_str,
               '-b:a', '192k', '-q:a', '2', '-y', out_path, '-loglevel', 'error']
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=30)
            return out_path
        except:
            return src_path

    def clear_cache(self):
        if os.path.exists(TEMP_DIR):
            for f in glob.glob(os.path.join(TEMP_DIR, '*.mp3')):
                try: os.remove(f)
                except: pass

    def get_song_length(self, filepath):
        """Get song length in seconds (cached after first call)"""
        if filepath in self.length_cache:
            return self.length_cache[filepath]
        try:
            result = subprocess.run(
                ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', filepath],
                capture_output=True, text=True, timeout=5
            )
            dur = float(result.stdout.strip())
            self.length_cache[filepath] = dur
            return dur
        except:
            return 0

    # ==================== Playback ====================
    def play_file(self, filepath):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.seek_offset = 0.0
        time.sleep(0.02)
        try:
            pygame.mixer.music.load(filepath)
            pygame.mixer.music.play()
            self.song_start_time = time.time()
            self.song_length = self.get_song_length(filepath)
            src = self.current_src_path or filepath
            self.load_lyrics(src)
        except Exception as e:
            print(f"Play error: {e}")

    def play_song(self, idx=None):
        if idx is not None:
            self.current_idx = idx
        if self.current_idx < 0 or self.current_idx >= len(self.playlist):
            return
        title, artist, filepath = self.playlist[self.current_idx]
        self.current_src_path = filepath  # store original for lyrics
        self.update_song_info()
        self.update_progress_display(0, 0)

        if self.current_effect != 'flat':
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
            self.song_start_time = time.time() - (pygame.mixer.music.get_pos() / 1000)
        self.update_ui()

    def next_song(self):
        if self.playlist:
            self.play_song((self.current_idx + 1) % len(self.playlist))

    def prev_song(self):
        if self.playlist:
            self.play_song((self.current_idx - 1) % len(self.playlist))

    def seek_to(self, pct):
        """Seek to percentage (0-100) of song"""
        if self.song_length <= 0 or not self.playing:
            return
        target_sec = self.song_length * (pct / 100.0)
        try:
            pygame.mixer.music.play(start=target_sec)
            self.seek_offset = target_sec
            self.song_start_time = time.time() - target_sec
        except:
            pass

    def change_effect(self, effect):
        if effect == self.current_effect:
            return
        self.current_effect = effect
        self.update_effect_ui()
        if self.playing and self.current_idx >= 0:
            _, _, filepath = self.playlist[self.current_idx]
            if effect == 'flat':
                self.processed_file = None
                pos = self.get_pos_sec()
                self.play_file(filepath)
                self.seek_to_sec(pos)
                self.status_var.set("")
            else:
                self.status_var.set(f"切换音效: {effect}...")
                threading.Thread(target=self._process_and_play, args=(filepath,), daemon=True).start()

    def change_intensity(self, val):
        self.intensity = int(val)
        if self.current_effect != 'flat' and self.playing and self.current_idx >= 0:
            _, _, filepath = self.playlist[self.current_idx]
            self.status_var.set(f"调整强度: {self.intensity}%...")
            threading.Thread(target=self._process_and_play, args=(filepath,), daemon=True).start()

    def get_pos_sec(self):
        try:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                return (pos_ms / 1000.0) + self.seek_offset
        except:
            pass
        return 0

    def seek_to_sec(self, sec):
        try:
            pygame.mixer.music.play(start=sec)
            self.song_start_time = time.time() - sec
        except:
            pass

    def poll_progress(self):
        """Update progress bar and time display every 200ms"""
        if self.playing:
            pos = self.get_pos_sec()
            if self.song_length > 0:
                pct = min(100, (pos / self.song_length) * 100)
                self.progress_bar['value'] = pct
                self.update_progress_display(pos, self.song_length)
                # Update lyrics
                self.update_lyrics(pos)
        self.root.after(200, self.poll_progress)

    def poll_song_end(self):
        """Auto-advance when song ends"""
        if self.playing and not pygame.mixer.music.get_busy() and self.get_pos_sec() > 0:
            self.next_song()
        self.root.after(500, self.poll_song_end)

    # ==================== UI ====================
    def build_ui(self):
        bg, surface, card, gold, text, textdim = '#0d0d12', '#1a1a24', '#222233', '#f0b429', '#eee', '#888'

        self.root.configure(bg=bg)
        main = tk.Frame(self.root, bg=bg)
        main.pack(fill='both', expand=True, padx=10, pady=10)

        # ====== Left: Playlist ======
        left = tk.Frame(main, bg=surface, width=260)
        left.pack(side='left', fill='y', padx=(0,8))
        left.pack_propagate(False)

        tk.Label(left, text="播放列表", bg=surface, fg=text,
                 font=('Microsoft YaHei', 13, 'bold')).pack(pady=(8,3), padx=8, anchor='w')
        tk.Label(left, text=f"{len(self.playlist)} 首", bg=surface, fg=textdim,
                 font=('Microsoft YaHei', 9)).pack(pady=(0,5), padx=8, anchor='w')

        list_frame = tk.Frame(left, bg=surface)
        list_frame.pack(fill='both', expand=True, padx=5)
        self.listbox = tk.Listbox(list_frame, bg=card, fg=text, selectbackground=gold,
                                  selectforeground='#000', font=('Microsoft YaHei', 10),
                                  borderwidth=0, highlightthickness=0, width=28)
        self.listbox.pack(side='left', fill='both', expand=True)
        self.listbox.bind('<<ListboxSelect>>', lambda e: self._on_select())
        scroll = tk.Scrollbar(list_frame, orient='vertical', command=self.listbox.yview)
        scroll.pack(side='right', fill='y')
        self.listbox.config(yscrollcommand=scroll.set)
        self.populate_playlist()

        # ====== Right: Main content ======
        right = tk.Frame(main, bg=bg)
        right.pack(side='right', fill='both', expand=True)

        # --- Song Info & Progress ---
        info_bar = tk.Frame(right, bg=bg)
        info_bar.pack(fill='x', pady=(0,5))

        self.title_var = tk.StringVar(value="🎵 选择歌曲")
        self.artist_var = tk.StringVar(value="")
        tk.Label(info_bar, textvariable=self.title_var, bg=bg, fg=text,
                 font=('Microsoft YaHei', 16, 'bold')).pack(anchor='w')
        tk.Label(info_bar, textvariable=self.artist_var, bg=bg, fg=textdim,
                 font=('Microsoft YaHei', 11)).pack(anchor='w')

        # Progress bar + time
        prog_frame = tk.Frame(right, bg=bg)
        prog_frame.pack(fill='x', pady=3)

        self.time_current = tk.StringVar(value="0:00")
        self.time_total = tk.StringVar(value="0:00")
        tk.Label(prog_frame, textvariable=self.time_current, bg=bg, fg=textdim,
                 font=('Consolas', 9)).pack(side='left')
        self.progress_bar = ttk.Progressbar(prog_frame, orient='horizontal',
                                             length=400, mode='determinate',
                                             style='gold.Horizontal.TProgressbar')
        self.progress_bar.pack(side='left', fill='x', expand=True, padx=5)
        tk.Label(prog_frame, textvariable=self.time_total, bg=bg, fg=textdim,
                 font=('Consolas', 9)).pack(side='right')

        # Click-to-seek on progress bar
        self.progress_bar.bind('<Button-1>', self._on_progress_click)

        # Controls
        ctrl = tk.Frame(right, bg=bg)
        ctrl.pack(fill='x', pady=3)
        self.btn_play = tk.Button(ctrl, text="▶ 播放", command=self.toggle_play,
                                  bg=gold, fg='#000', font=('Microsoft YaHei', 10, 'bold'),
                                  width=8, borderwidth=0, padx=10, pady=3)
        self.btn_play.pack(side='left', padx=2)
        tk.Button(ctrl, text="⏮", command=self.prev_song,
                  bg=surface, fg=text, font=('Arial', 13), width=2, borderwidth=0).pack(side='left', padx=1)
        tk.Button(ctrl, text="⏭", command=self.next_song,
                  bg=surface, fg=text, font=('Arial', 13), width=2, borderwidth=0).pack(side='left', padx=1)
        self.status_var = tk.StringVar(value="")
        tk.Label(ctrl, textvariable=self.status_var, bg=bg, fg=gold,
                 font=('Microsoft YaHei', 9)).pack(side='right', padx=5)

        # --- Split: EQ (left) + Lyrics (right) ---
        bot = tk.Frame(right, bg=bg)
        bot.pack(fill='both', expand=True, pady=(5,0))

        # EQ Panel
        eq_frame = tk.Frame(bot, bg=surface, bd=1, relief='solid', highlightbackground='#333')
        eq_frame.pack(side='left', fill='both', expand=True, padx=(0,4))

        eq_header = tk.Frame(eq_frame, bg=surface)
        eq_header.pack(fill='x', padx=8, pady=(5,2))
        tk.Label(eq_header, text="🐍 蝰蛇音效", bg=surface, fg=gold,
                 font=('Microsoft YaHei', 12, 'bold')).pack(side='left')

        self.eq_on = tk.BooleanVar(value=False)
        self.eq_toggle = tk.Checkbutton(eq_header, variable=self.eq_on,
                                         command=self._on_eq_toggle,
                                         bg=surface, selectcolor=surface,
                                         activebackground=surface)
        tk.Label(eq_header, text="开启", bg=surface, fg=textdim,
                 font=('Microsoft YaHei', 9)).pack(side='right')
        self.eq_toggle.pack(side='right')
        tk.Label(eq_header, text="关闭", bg=surface, fg=textdim,
                 font=('Microsoft YaHei', 9)).pack(side='right', padx=2)

        # Intensity
        int_frame = tk.Frame(eq_frame, bg=surface)
        int_frame.pack(fill='x', padx=8, pady=1)
        tk.Label(int_frame, text="强度", bg=surface, fg=textdim,
                 font=('Microsoft YaHei', 8)).pack(side='left')
        self.int_slider = tk.Scale(int_frame, from_=10, to=100, orient='horizontal',
                                    bg=surface, fg=text, troughcolor='#333',
                                    highlightbackground=surface, length=120,
                                    command=lambda v: self.change_intensity(v))
        self.int_slider.set(self.intensity)
        self.int_slider.pack(side='right')

        # Visualizer
        viz = tk.Frame(eq_frame, bg='#111', height=35)
        viz.pack(fill='x', padx=8, pady=2)
        self.viz_bars = []
        for _ in range(10):
            bar = tk.Frame(viz, bg='#333', width=15)
            bar.pack(side='left', expand=True, padx=1, pady=2)
            self.viz_bars.append(bar)

        # EQ Grid
        grid = tk.Frame(eq_frame, bg=surface)
        grid.pack(fill='both', expand=True, padx=8, pady=(2,8))
        presets = [k for k in PRESETS if k != 'flat']
        for i, name in enumerate(presets):
            r, c = divmod(i, 5)
            btn = tk.Button(grid, text=name,
                            command=lambda n=name: self._on_preset(n),
                            bg=card, fg=text, activebackground=gold, activeforeground='#000',
                            font=('Microsoft YaHei', 9), borderwidth=0, padx=4, pady=4)
            btn.grid(row=r, column=c, padx=2, pady=2, sticky='ew')
            grid.columnconfigure(c, weight=1)

        # --- Lyrics Panel ---
        lyric_frame = tk.Frame(bot, bg=surface, bd=1, relief='solid', highlightbackground='#333', width=300)
        lyric_frame.pack(side='right', fill='both', expand=True, padx=(4,0))
        lyric_frame.pack_propagate(False)

        tk.Label(lyric_frame, text="📃 歌词", bg=surface, fg=textdim,
                 font=('Microsoft YaHei', 10)).pack(pady=(5,2), padx=8, anchor='w')

        self.lyric_text = tk.Text(lyric_frame, bg='#111', fg=textdim,
                                   font=('Microsoft YaHei', 11), borderwidth=0,
                                   highlightthickness=0, wrap='word',
                                   padx=10, pady=5, spacing1=4, spacing2=2)
        self.lyric_text.pack(fill='both', expand=True, padx=4, pady=(0,8))
        self.lyric_text.insert('end', "暂无歌词")
        self.lyric_text.config(state='disabled')

        # --- Progress bar style ---
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('gold.Horizontal.Tprogressbar', troughcolor='#333',
                         background=gold, lightcolor=gold, darkcolor=gold, bordercolor=gold)

        # Bind close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def populate_playlist(self):
        self.listbox.delete(0, 'end')
        for title, artist, _ in self.playlist:
            display = title[:28] + ('..' if len(title) > 28 else '')
            self.listbox.insert('end', display)

    def update_song_info(self):
        if 0 <= self.current_idx < len(self.playlist):
            title, artist, _ = self.playlist[self.current_idx]
            self.title_var.set(f"🎵 {title}")
            self.artist_var.set(artist or '')

    def update_progress_display(self, pos_sec, total_sec):
        def fmt(s):
            if s <= 0: return "0:00"
            m = int(s // 60)
            s2 = int(s % 60)
            return f"{m}:{s2:02d}"
        self.time_current.set(fmt(pos_sec))
        self.time_total.set(fmt(total_sec))

    def update_ui(self):
        self.btn_play.config(text="⏸ 暂停" if self.playing else "▶ 播放")

    def update_effect_ui(self):
        gains = PRESETS.get(self.current_effect, PRESETS['flat'])
        intensity = self.intensity / 70.0
        max_gain = 12
        for i, bar in enumerate(self.viz_bars):
            g = (gains[i] if i < len(gains) else 0) * intensity
            pct = min(100, max(5, abs(g) / max_gain * 100))
            bar.configure(bg='#f0b429' if g >= 0 else '#555', height=int(pct))

    def _on_select(self):
        sel = self.listbox.curselection()
        if sel:
            self.play_song(sel[0])

    def _on_progress_click(self, event):
        """Handle click on progress bar to seek"""
        if self.song_length <= 0:
            return
        w = self.progress_bar.winfo_width()
        if w > 0:
            pct = (event.x / w) * 100
            self.seek_to(pct)

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
                pos = self.get_pos_sec()
                self.play_file(filepath)
                self.seek_to_sec(pos)
                self.status_var.set("")

    def _on_preset(self, name):
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
