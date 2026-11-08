[app]
title = LT-Music
package.name = ltmusic
package.domain = com.ltmusic
source.dir = .
source.include_exts = py,kv,png,jpg,jpeg,atlas,mp3,wav,ogg,m4a,txt
source.exclude_dirs = .git,.github,.buildozer,bin,venv,__pycache__
version = 1.0.0
requirements = python3,kivy
orientation = portrait
fullscreen = 0

# This starter plays audio files packaged in the songs/ directory.
# No internet permission is needed for offline playback.

# Android permissions
android.permissions = INTERNET

# Android SDK configuration
android.api = 35
android.minapi = 24
android.archs = arm64-v8a

# Android settings
android.accept_sdk_license = True
android.allow_backup = True
android.enable_androidx = True


[buildozer]
log_level = 2
warn_on_root = 1
