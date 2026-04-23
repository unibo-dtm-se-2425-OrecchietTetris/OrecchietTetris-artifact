import os

# Must be set before any Kivy import. On headless CI runners (no display/SDL2
# context), kivy.core.window's default SDL2 backend exits the process with
# code 102. The headless provider avoids all display/GL initialisation.
os.environ.setdefault("KIVY_NO_ENV_CONFIG", "1")
os.environ.setdefault("KIVY_WINDOW", "headless")
