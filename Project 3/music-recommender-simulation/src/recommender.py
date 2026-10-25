"""Core scoring and ranking logic for the music recommender simulation."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


SongRecord = dict[str, Any]
UserPreferences = dict[str, Any]
Recommendation = tuple[SongRecord, float, str]


SCORING_MODES = {
    "balanced": {"genre": 2.0, "mood": 1.5, "energy": 1.5},
    "genre_first": {"genre": 3.0, "mood": 1.0, "energy": 1.0},
    "mood_first": {"genre": 1.0, "mood": 3.0, "energy": 1.0},
    "energy_focused": {"genre": 1.0, "mood": 1.0, "energy": 3.0},
}

NUMERIC_FLOAT_FIELDS = ("energy", "valence", "danceability", "acousticness")


@dataclass(frozen=True)
class Song:
    """Represent one song and the content features used for ranking."""

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass(frozen=True)
class UserProfile:
    """Represent a listener's main taste preferences."""

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """Provide an object-oriented interface to the functional scoring engine."""

    def __init__(self, songs: list[Song], mode: str = "balanced"):
        if mode not in SCORING_MODES:
            raise ValueError(f"Unknown scoring mode: {mode}")
        self.songs = songs
        self.mode = mode

    @staticmethod
    def _preferences(user: UserProfile) -> UserPreferences:
        """Convert a user profile into the scoring engine's dictionary shape."""
        return {
            "genre": user.favorite_genre,
            "mood": user.favorite_mood,
            "energy": user.target_energy,
            "acousticness": 0.8 if user.likes_acoustic else 0.2,
        }

    def recommend(self, user: UserProfile, k: int = 5) -> list[Song]:
        """Return up to k songs ordered from best to worst match."""
        song_lookup = {song.id: song for song in self.songs}
        records = [asdict(song) for song in self.songs]
        ranked = recommend_songs(self._preferences(user), records, k, self.mode)
        return [song_lookup[record["id"]] for record, _, _ in ranked]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Explain the feature matches that contributed to a song's score."""
        _, reasons = score_song(self._preferences(user), asdict(song), self.mode)
        return "; ".join(reasons)


def load_songs(csv_path: str | Path) -> list[SongRecord]:
    """Load song dictionaries from CSV and convert numeric fields to numbers."""
    path = Path(csv_path)
    songs: list[SongRecord] = []
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        required = {
            "id",
            "title",
            "artist",
            "genre",
            "mood",
            "energy",
            "tempo_bpm",
            "valence",
            "danceability",
            "acousticness",
        }
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(sorted(missing))}")

        for line_number, row in enumerate(reader, start=2):
            try:
                converted: SongRecord = dict(row)
                converted["id"] = int(row["id"])
                converted["tempo_bpm"] = float(row["tempo_bpm"])
                for field in NUMERIC_FLOAT_FIELDS:
                    converted[field] = float(row[field])
            except (TypeError, ValueError) as error:
                raise ValueError(f"Invalid numeric value on CSV line {line_number}") from error
            songs.append(converted)
    return songs


def _similarity(target: float, actual: float, maximum_gap: float = 1.0) -> float:
    """Return a zero-to-one similarity based on normalized distance."""
    return max(0.0, 1.0 - abs(target - actual) / maximum_gap)


def score_song(
    user_prefs: UserPreferences,
    song: SongRecord,
    mode: str = "balanced",
) -> tuple[float, list[str]]:
    """Score one song and return both its numeric score and plain-language reasons."""
    if mode not in SCORING_MODES:
        raise ValueError(f"Unknown scoring mode: {mode}")

    weights = SCORING_MODES[mode]
    score = 0.0
    reasons: list[str] = []

    if str(song["genre"]).casefold() == str(user_prefs.get("genre", "")).casefold():
        score += weights["genre"]
        reasons.append(f"genre match (+{weights['genre']:.2f})")

    if str(song["mood"]).casefold() == str(user_prefs.get("mood", "")).casefold():
        score += weights["mood"]
        reasons.append(f"mood match (+{weights['mood']:.2f})")

    target_energy = float(user_prefs.get("energy", 0.5))
    energy_points = weights["energy"] * _similarity(target_energy, float(song["energy"]))
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.2f})")

    optional_features = {
        "tempo_bpm": (0.50, 160.0, "tempo"),
        "valence": (0.50, 1.0, "valence"),
        "danceability": (0.50, 1.0, "danceability"),
        "acousticness": (0.50, 1.0, "acousticness"),
    }
    for feature, (weight, maximum_gap, label) in optional_features.items():
        if feature not in user_prefs:
            continue
        points = weight * _similarity(
            float(user_prefs[feature]), float(song[feature]), maximum_gap
        )
        score += points
        reasons.append(f"{label} similarity (+{points:.2f})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: UserPreferences,
    songs: list[SongRecord],
    k: int = 5,
    mode: str = "balanced",
) -> list[Recommendation]:
    """Score the catalog and return the top k explainable recommendations."""
    if k < 0:
        raise ValueError("k must be zero or greater")

    scored: list[tuple[SongRecord, float, list[str]]] = []
    for song in songs:
        score, reasons = score_song(user_prefs, song, mode)
        scored.append((song, score, reasons))

    scored.sort(
        key=lambda result: (
            -result[1],
            str(result[0]["title"]).casefold(),
            int(result[0]["id"]),
        )
    )
    return [
        (song, score, "; ".join(reasons))
        for song, score, reasons in scored[:k]
    ]
