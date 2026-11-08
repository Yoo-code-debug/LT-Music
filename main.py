import json
import threading
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

from kivy.app import App
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.network.urlrequest import UrlRequest
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex


THEMES = {
    "blue": {
        "bg": "#07131F", "panel": "#102536", "panel2": "#173348",
        "accent": "#8EDBFF", "text": "#F2FAFF", "muted": "#9CB8C8",
        "field": "#102536",
    },
    "black": {
        "bg": "#050505", "panel": "#151515", "panel2": "#242424",
        "accent": "#F4F7FA", "text": "#FFFFFF", "muted": "#A5A5A5",
        "field": "#171717",
    },
}


class LTMusicApp(App):
    def build(self):
        self.title = "LT-Music"
        self.song_dir = Path(__file__).parent / "songs"
        self.song_dir.mkdir(exist_ok=True)
        self.tracks = []
        self.current_index = -1
        self.sound = None
        self.is_paused = False
        self.duration = 0
        self.paused_position = 0
        self.theme_name = "blue"
        self.theme = THEMES[self.theme_name]
        self.search_event = None
        self.active_request = None

        self.root_layout = BoxLayout(
            orientation="vertical", padding=dp(16), spacing=dp(9)
        )

        header = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        brand = Label(
            text="[b]LT-Music[/b]", markup=True, color=self.color("accent"),
            font_size="27sp", halign="left", valign="middle"
        )
        brand.bind(size=lambda w, s: setattr(w, "text_size", s))
        header.add_widget(brand)

        self.theme_button = Button(
            text="●  BLUE THEME", size_hint_x=None, width=dp(132),
            background_normal="", background_color=self.color("panel2"),
            color=self.color("accent"), bold=True, font_size="11sp"
        )
        self.theme_button.bind(on_release=self.toggle_theme)
        header.add_widget(self.theme_button)
        self.root_layout.add_widget(header)

        self.subtitle = Label(
            text="DISCOVER MUSIC FROM AROUND THE WORLD",
            color=self.color("muted"), size_hint_y=None,
            height=dp(22), halign="left", font_size="10sp", bold=True
        )
        self.subtitle.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.root_layout.add_widget(self.subtitle)

        self.search = TextInput(
            hint_text="Search songs, artists or albums...",
            multiline=False, size_hint_y=None, height=dp(48),
            background_normal="", background_active="",
            background_color=self.color("field"),
            foreground_color=self.color("text"),
            hint_text_color=self.color("muted"),
            cursor_color=self.color("accent"),
            padding=[dp(14), dp(12), dp(14), dp(12)]
        )
        self.search.bind(text=self.on_search)
        self.root_layout.add_widget(self.search)

        self.status = Label(
            text="Search online to discover music",
            color=self.color("muted"), size_hint_y=None,
            height=dp(24), halign="left", font_size="11sp"
        )
        self.status.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.root_layout.add_widget(self.status)

        self.results_box = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(7)
        )
        self.results_box.bind(minimum_height=self.results_box.setter("height"))
        scroll = ScrollView()
        scroll.add_widget(self.results_box)
        self.root_layout.add_widget(scroll)

        self.player_panel = BoxLayout(
            orientation="vertical", size_hint_y=None,
            height=dp(176), padding=dp(12), spacing=dp(5)
        )
        self.player_panel.background_color = self.color("panel")

        self.track_label = Label(
            text="LT-Music Player", color=self.color("text"),
            bold=True, halign="left", size_hint_y=None,
            height=dp(25), font_size="15sp"
        )
        self.track_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.artist_label = Label(
            text="Local songs appear here when added to songs/",
            color=self.color("muted"), halign="left",
            size_hint_y=None, height=dp(20), font_size="10sp"
        )
        self.artist_label.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.player_panel.add_widget(self.track_label)
        self.player_panel.add_widget(self.artist_label)

        self.progress = Slider(min=0, max=100, value=0, size_hint_y=None,
                               height=dp(25))
        self.player_panel.add_widget(self.progress)

        controls = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(12))
        self.previous_button = self.make_control("⏮", self.previous_track)
        self.play_button = self.make_control("▶", self.toggle_play, primary=True)
        self.next_button = self.make_control("⏭", self.next_track)
        controls.add_widget(self.previous_button)
        controls.add_widget(self.play_button)
        controls.add_widget(self.next_button)
        self.player_panel.add_widget(controls)
        self.root_layout.add_widget(self.player_panel)

        Window.clearcolor = self.color("bg")
        self.load_local_songs()
        self.show_message("Search for a song, artist or album above.")
        Clock.schedule_interval(self.update_progress, 0.5)
        return self.root_layout

    def color(self, key):
        return get_color_from_hex(self.theme[key])

    def make_control(self, text, callback, primary=False):
        btn = Button(
            text=text, bold=True, font_size="19sp",
            background_normal="", background_down="",
            background_color=self.color("accent") if primary else self.color("panel2"),
            color=self.color("bg") if primary else self.color("text")
        )
        btn.bind(on_release=lambda *_: callback())
        return btn

    def toggle_theme(self, *_):
        self.theme_name = "black" if self.theme_name == "blue" else "blue"
        self.theme = THEMES[self.theme_name]
        self.apply_theme()

    def apply_theme(self):
        Window.clearcolor = self.color("bg")
        self.theme_button.text = "●  " + self.theme_name.upper() + " THEME"
        self.theme_button.background_color = self.color("panel2")
        self.theme_button.color = self.color("accent")
        self.subtitle.color = self.color("muted")
        self.search.background_color = self.color("field")
        self.search.foreground_color = self.color("text")
        self.search.hint_text_color = self.color("muted")
        self.search.cursor_color = self.color("accent")
        self.status.color = self.color("muted")
        self.player_panel.background_color = self.color("panel")
        self.track_label.color = self.color("text")
        self.artist_label.color = self.color("muted")
        self.play_button.background_color = self.color("accent")
        self.play_button.color = self.color("bg")
        for btn in (self.previous_button, self.next_button):
            btn.background_color = self.color("panel2")
            btn.color = self.color("text")
        # Re-render current results in the selected theme.
        self.on_search(self.search, self.search.text)

    def load_local_songs(self):
        extensions = {".mp3", ".wav", ".ogg", ".m4a"}
        self.tracks = sorted(
            [f for f in self.song_dir.iterdir()
             if f.is_file() and f.suffix.lower() in extensions],
            key=lambda f: f.name.lower()
        )

    def show_message(self, message):
        self.results_box.clear_widgets()
        label = Label(
            text=message, color=self.color("muted"), halign="left",
            valign="middle", size_hint_y=None, height=dp(76)
        )
        label.bind(size=lambda w, s: setattr(w, "text_size", s))
        self.results_box.add_widget(label)

    def on_search(self, _instance, query):
        if self.search_event:
            self.search_event.cancel()
        query = query.strip()
        if len(query) < 2:
            self.show_message("Type at least 2 characters to search the online catalog.")
            self.status.text = "ONLINE MUSIC SEARCH"
            return
        self.status.text = "Searching online..."
        self.show_message("Connecting to the music catalog...")
        self.search_event = Clock.schedule_once(
            lambda _dt, q=query: self.search_catalog(q), 0.65
        )

    def search_catalog(self, query):
        # Apple iTunes Search API: public catalog metadata, no API key required.
        params = urllib.parse.urlencode({
            "term": query,
            "media": "music",
            "entity": "song",
            "limit": "35",
            "country": "US"
        })
        url = "https://itunes.apple.com/search?" + params
        try:
            self.active_request = UrlRequest(
                url, on_success=self.on_search_success,
                on_failure=self.on_search_failure,
                on_error=self.on_search_error,
                timeout=20, req_headers={"User-Agent": "LT-Music/1.0"}
            )
        except Exception as exc:
            self.show_message("Could not start online search: " + str(exc))
            self.status.text = "SEARCH ERROR"

    def on_search_success(self, _request, data):
        results = data.get("results", []) if isinstance(data, dict) else []
        self.results_box.clear_widgets()
        if not results:
            self.status.text = "NO RESULTS"
            self.show_message("No matches found. Try another song or artist.")
            return

        self.status.text = "FOUND {} RESULTS  •  APPLE MUSIC CATALOG".format(len(results))
        for item in results:
            title = item.get("trackName", "Unknown title")
            artist = item.get("artistName", "Unknown artist")
            album = item.get("collectionName", "Unknown album")
            store_url = item.get("trackViewUrl") or item.get("collectionViewUrl")
            row = BoxLayout(
                orientation="horizontal", size_hint_y=None,
                height=dp(72), spacing=dp(8), padding=[dp(5), dp(4)]
            )
            text_col = BoxLayout(orientation="vertical", spacing=dp(2))
            title_label = Label(
                text=title, color=self.color("text"), bold=True,
                halign="left", valign="middle", font_size="13sp"
            )
            title_label.bind(size=lambda w, s: setattr(w, "text_size", s))
            artist_label = Label(
                text=artist + "  •  " + album,
                color=self.color("muted"), halign="left",
                valign="middle", font_size="10sp"
            )
            artist_label.bind(size=lambda w, s: setattr(w, "text_size", s))
            text_col.add_widget(title_label)
            text_col.add_widget(artist_label)
            row.add_widget(text_col)

            open_btn = Button(
                text="OPEN", size_hint_x=None, width=dp(66),
                background_normal="", background_color=self.color("panel2"),
                color=self.color("accent"), bold=True, font_size="10sp"
            )
            open_btn.disabled = not bool(store_url)
            open_btn.bind(
                on_release=lambda _btn, u=store_url: self.open_store(u)
            )
            row.add_widget(open_btn)
            self.results_box.add_widget(row)

    def on_search_failure(self, _request, _result):
        self.status.text = "SEARCH FAILED"
        self.show_message("The music catalog could not complete the search. Check your internet connection and try again.")

    def on_search_error(self, _request, error):
        self.status.text = "CONNECTION ERROR"
        self.show_message("Could not connect. Check your internet connection and try again.")

    def open_store(self, url):
        if url:
            webbrowser.open(url)

    def play_path(self, path):
        self.stop_current()
        sound = SoundLoader.load(str(path))
        if sound is None:
            self.track_label.text = "Unable to play this local audio"
            self.artist_label.text = path.name
            return
        self.sound = sound
        self.sound.play()
        self.is_paused = False
        self.current_index = self.tracks.index(path) if path in self.tracks else -1
        self.track_label.text = path.stem.replace("_", " ")
        self.artist_label.text = "LOCAL FILE  •  LT-MUSIC"
        self.play_button.text = "Ⅱ"
        self.duration = sound.length or 0
        self.paused_position = 0
        self.progress.max = max(1, self.duration)
        self.progress.value = 0

    def stop_current(self):
        if self.sound:
            try:
                self.sound.stop()
            except Exception:
                pass
        self.sound = None
        self.is_paused = False
        self.play_button.text = "▶"

    def toggle_play(self):
        if not self.sound:
            if self.tracks:
                self.play_path(self.tracks[0])
            else:
                self.track_label.text = "No local songs added"
                self.artist_label.text = "Online results open in the official store"
            return
        if self.is_paused:
            self.sound.play()
            try:
                self.sound.seek(self.paused_position)
            except Exception:
                pass
            self.is_paused = False
            self.play_button.text = "Ⅱ"
        else:
            try:
                self.paused_position = self.sound.get_pos()
            except Exception:
                self.paused_position = 0
            self.sound.stop()
            self.is_paused = True
            self.play_button.text = "▶"

    def previous_track(self):
        if self.tracks:
            index = self.current_index if self.current_index >= 0 else 0
            self.play_path(self.tracks[(index - 1) % len(self.tracks)])

    def next_track(self):
        if self.tracks:
            index = self.current_index if self.current_index >= 0 else -1
            self.play_path(self.tracks[(index + 1) % len(self.tracks)])

    def update_progress(self, _dt):
        if self.sound and not self.is_paused:
            try:
                pos = self.sound.get_pos()
                if self.duration > 0:
                    self.progress.value = min(pos, self.duration)
                    if pos >= self.duration - 0.4:
                        self.next_track()
            except Exception:
                pass

    def on_stop(self):
        self.stop_current()


if __name__ == "__main__":
    LTMusicApp().run()
