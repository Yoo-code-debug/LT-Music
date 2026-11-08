# LT-Music

LT-Music is a simple offline Android music-player starter made with Python and Kivy. Its dark interface is inspired by common music-player layouts, but it uses original LT-Music branding and does not copy Spotify's logo or assets.

## Features
- Scans the app's bundled `songs/` folder
- Search tracks by filename
- Switch between a light-blue dark theme and a pure-black theme
- Play, pause, previous, next
- Seek bar (audio-backend support may vary)

## Add your own audio
Put audio files you own or have permission to use in `songs/`.
Supported extensions in this starter: `.mp3`, `.wav`, `.ogg`, `.m4a`.
Audio format support can vary by Android device and Kivy audio provider.

The `songs/` folder includes a `.gitkeep` placeholder. Add your own licensed audio files before building if you want tracks included in the APK.

## Build APK on GitHub
1. Create a GitHub repository named `LT-Music`.
2. Upload all files and folders from this project to the repository.
3. Open the repository's **Actions** tab.
4. Select **Build LT-Music APK** and click **Run workflow**, or push a commit to the `main` branch.
5. Wait for the workflow to finish.
6. Open the completed workflow run and download the **LT-Music-APK** artifact.

The first build can take several minutes. GitHub Actions builds the APK in the cloud; you do not need to compile it on your Android phone.

## Build locally
Buildozer is intended for Linux/macOS; on Windows, use WSL. See the official Kivy packaging guide:
https://kivy.org/doc/stable/guide/packaging-android.html

Typical Linux commands:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install buildozer cython
buildozer android debug
```

## Project files
- `main.py` — app interface and playback code
- `buildozer.spec` — Android packaging settings
- `.github/workflows/build.yml` — GitHub Actions APK build
- `songs/` — add your own audio files here

## Spotify note
This is not a Spotify client and does not stream Spotify tracks. Spotify's developer platform has its own authorization, playback, and policy requirements. Do not copy Spotify branding, scrape its app, or redistribute copyrighted tracks. If you later integrate Spotify, use official Spotify developer documentation and comply with its current terms.


## Online song search
The app searches Apple's public iTunes Search API for song metadata (title, artist, album) and opens the official store page. It requires internet access. The online catalog is not every song ever released, and availability varies by country. This app does not stream full copyrighted songs from the API. Apple preview assets are subject to Apple's promotional-use terms.

The Android manifest includes the INTERNET permission. The app uses Kivy's `UrlRequest`, so no extra `requests` package is needed.
