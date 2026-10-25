"""Command-line demonstration for the music recommender simulation."""

from pathlib import Path
from typing import Any

from .recommender import load_songs, recommend_songs


PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROFILES: dict[str, dict[str, Any]] = {
    "High-Energy Pop": {
        "genre": "pop",
        "mood": "happy",
        "energy": 0.85,
        "danceability": 0.85,
    },
    "Chill Lofi": {
        "genre": "lofi",
        "mood": "chill",
        "energy": 0.35,
        "acousticness": 0.80,
    },
    "Deep Intense Rock": {
        "genre": "rock",
        "mood": "intense",
        "energy": 0.92,
        "tempo_bpm": 145,
    },
    "Conflicted Sad Workout": {
        "genre": "edm",
        "mood": "sad",
        "energy": 0.95,
        "valence": 0.20,
    },
}


def print_recommendations(
    profile_name: str,
    preferences: dict[str, Any],
    songs: list[dict[str, Any]],
    k: int = 5,
    mode: str = "balanced",
) -> None:
    """Print one user profile and its ranked recommendations as a table."""
    preference_text = ", ".join(f"{key}={value}" for key, value in preferences.items())
    print(f"\n{profile_name} ({preference_text})")
    print("-" * 88)
    for rank, (song, score, explanation) in enumerate(
        recommend_songs(preferences, songs, k, mode), start=1
    ):
        label = f"{rank}. {song['title']} — {song['artist']}"
        print(f"{label:<48} Score: {score:.2f}")
        print(f"   Because: {explanation}")


def main() -> None:
    """Load the catalog and show recommendations for four evaluation profiles."""
    songs = load_songs(PROJECT_ROOT / "data" / "songs.csv")
    print(f"Loaded songs: {len(songs)}")
    print("Scoring mode: balanced")
    for profile_name, preferences in PROFILES.items():
        print_recommendations(profile_name, preferences, songs)


if __name__ == "__main__":
    main()
