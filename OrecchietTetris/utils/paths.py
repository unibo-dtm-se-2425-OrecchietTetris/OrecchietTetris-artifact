from pathlib import Path

from platformdirs import user_data_dir

ASSETS_DIR: Path = Path(__file__).parent.parent / "assets"
MUSIC_DIR: Path = Path(__file__).parent.parent / "assets" / "music"
LOCALES_DIR: Path = Path(__file__).parent.parent / "locales"

# Writable per-user location for runtime data (e.g. leaderboard).
USER_DATA_DIR: Path = Path(user_data_dir("OrecchietTetris"))
