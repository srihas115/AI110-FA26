"""Tests for CSV loading, explainable scoring, and recommendation ranking."""

from pathlib import Path

import pytest

from src.recommender import (
    Recommender,
    Song,
    UserProfile,
    load_songs,
    recommend_songs,
    score_song,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def sample_songs() -> list[dict]:
    return [
        {
            "id": 1,
            "title": "Test Pop Track",
            "artist": "Test Artist",
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120.0,
            "valence": 0.9,
            "danceability": 0.8,
            "acousticness": 0.2,
        },
        {
            "id": 2,
            "title": "Chill Lofi Loop",
            "artist": "Second Artist",
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.4,
            "tempo_bpm": 80.0,
            "valence": 0.6,
            "danceability": 0.5,
            "acousticness": 0.9,
        },
    ]


def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Second Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_load_songs_converts_numeric_fields() -> None:
    songs = load_songs(PROJECT_ROOT / "data" / "songs.csv")

    assert len(songs) == 18
    assert isinstance(songs[0]["id"], int)
    assert isinstance(songs[0]["energy"], float)
    assert isinstance(songs[0]["tempo_bpm"], float)


def test_load_songs_reports_missing_columns(tmp_path: Path) -> None:
    incomplete_csv = tmp_path / "incomplete.csv"
    incomplete_csv.write_text("id,title\n1,Example\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required columns"):
        load_songs(incomplete_csv)


def test_load_songs_reports_invalid_numeric_data(tmp_path: Path) -> None:
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text(
        "id,title,artist,genre,mood,energy,tempo_bpm,valence,danceability,acousticness\n"
        "one,Example,Artist,pop,happy,high,fast,good,yes,no\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="CSV line 2"):
        load_songs(invalid_csv)


def test_exact_match_receives_genre_mood_and_energy_points(sample_songs: list[dict]) -> None:
    score, reasons = score_song(
        {"genre": "pop", "mood": "happy", "energy": 0.8}, sample_songs[0]
    )

    assert score == pytest.approx(5.0)
    assert reasons == [
        "genre match (+2.00)",
        "mood match (+1.50)",
        "energy similarity (+1.50)",
    ]


def test_text_matches_are_case_insensitive(sample_songs: list[dict]) -> None:
    score, _ = score_song(
        {"genre": "POP", "mood": "HAPPY", "energy": 0.8}, sample_songs[0]
    )

    assert score == pytest.approx(5.0)


def test_optional_preferences_contribute_explanations(sample_songs: list[dict]) -> None:
    score, reasons = score_song(
        {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "tempo_bpm": 120,
            "valence": 0.9,
            "danceability": 0.8,
            "acousticness": 0.2,
        },
        sample_songs[0],
    )

    assert score == pytest.approx(7.0)
    assert reasons[-1] == "acousticness similarity (+0.50)"


def test_scoring_modes_change_feature_priorities(sample_songs: list[dict]) -> None:
    preferences = {"genre": "pop", "mood": "chill", "energy": 0.4}

    genre_score, _ = score_song(preferences, sample_songs[0], "genre_first")
    mood_score, _ = score_song(preferences, sample_songs[1], "mood_first")

    assert genre_score == pytest.approx(3.6)
    assert mood_score == pytest.approx(4.0)


def test_unknown_scoring_mode_is_rejected(sample_songs: list[dict]) -> None:
    with pytest.raises(ValueError, match="Unknown scoring mode"):
        score_song({}, sample_songs[0], "mystery")


def test_recommendations_are_sorted_and_explained(sample_songs: list[dict]) -> None:
    results = recommend_songs(
        {"genre": "pop", "mood": "happy", "energy": 0.8}, sample_songs, k=2
    )

    assert [result[0]["id"] for result in results] == [1, 2]
    assert results[0][1] > results[1][1]
    assert "genre match" in results[0][2]


def test_recommendations_are_deterministic_when_scores_tie(sample_songs: list[dict]) -> None:
    for song in sample_songs:
        song["genre"] = "other"
        song["mood"] = "other"
        song["energy"] = 0.5
    sample_songs[0]["title"] = "Zulu"
    sample_songs[1]["title"] = "Alpha"

    results = recommend_songs({"energy": 0.5}, sample_songs, k=2)

    assert [result[0]["title"] for result in results] == ["Alpha", "Zulu"]


def test_k_larger_than_catalog_returns_every_song(sample_songs: list[dict]) -> None:
    results = recommend_songs({"energy": 0.5}, sample_songs, k=99)

    assert len(results) == 2


def test_negative_k_is_rejected(sample_songs: list[dict]) -> None:
    with pytest.raises(ValueError, match="zero or greater"):
        recommend_songs({"energy": 0.5}, sample_songs, k=-1)


def test_object_oriented_api_returns_ranked_songs() -> None:
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    recommender = make_small_recommender()

    results = recommender.recommend(user, k=2)

    assert len(results) == 2
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_object_oriented_api_explanation_is_non_empty() -> None:
    user = UserProfile("pop", "happy", 0.8, False)
    recommender = make_small_recommender()

    explanation = recommender.explain_recommendation(user, recommender.songs[0])

    assert "genre match" in explanation
    assert explanation.strip()
