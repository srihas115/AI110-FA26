# VibeMap Music Recommender

VibeMap is a CLI-first, content-based music recommender. It compares a listener's stated taste with an 18-song catalog, gives every song a weighted score, and returns a ranked top five with a plain-language explanation for every result.

## How the System Works

Large streaming platforms can combine content-based filtering with collaborative filtering. Content-based filtering compares attributes such as genre, mood, tempo, and energy. Collaborative filtering instead learns from behavior shared across people, such as likes, skips, replays, and playlist additions. VibeMap focuses on the content-based side so every decision remains visible and easy to inspect.

Each song has an ID, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness. A profile always supplies a preferred genre, mood, and target energy. It can also supply targets for tempo, valence, danceability, or acousticness.

The balanced scoring recipe is:

- Add `2.0` points for an exact genre match.
- Add `1.5` points for an exact mood match.
- Add up to `1.5` points for energy similarity: `1.5 × (1 - absolute energy gap)`.
- For each optional numeric preference, add up to `0.5` similarity points.
- Rank every song from highest to lowest score. Break ties by title and then ID, so output is deterministic.

This separates the scoring rule (judge one song) from the ranking rule (order the whole catalog):

```text
User preferences + songs.csv
            |
            v
 score every individual song
            |
            v
 sort by score, title, and ID
            |
            v
 top K songs + score explanations
```

The implementation also includes `genre_first`, `mood_first`, and `energy_focused` strategies. These modes use the same pipeline with different feature weights, making sensitivity experiments reproducible without editing source code.

## Project Structure

```text
music-recommender-simulation/
├── data/
│   └── songs.csv
├── src/
│   ├── main.py
│   └── recommender.py
├── tests/
│   └── test_recommender.py
├── ai_interactions.md
├── model_card.md
├── README.md
└── requirements.txt
```

## Setup and Run

From this directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m src.main
```

The path to `songs.csv` is resolved relative to the source file, so the CLI does not depend on the shell's current directory.

## Sample Recommendation Output

The CLI evaluates four intentionally different profiles. The final one is an adversarial profile that asks for the conflicting combination of sad, very energetic EDM.

```text
Loaded songs: 18
Scoring mode: balanced

High-Energy Pop (genre=pop, mood=happy, energy=0.85, danceability=0.85)
----------------------------------------------------------------------------------------
1. Sunrise City — Neon Echo                      Score: 5.42
   Because: genre match (+2.00); mood match (+1.50); energy similarity (+1.46); danceability similarity (+0.47)
2. Gym Hero — Max Pulse                          Score: 3.87
   Because: genre match (+2.00); energy similarity (+1.38); danceability similarity (+0.48)
3. Rooftop Lights — Indigo Parade                Score: 3.35
   Because: mood match (+1.50); energy similarity (+1.36); danceability similarity (+0.48)
4. Golden Hour Drive — Sol Rivera                Score: 1.93
   Because: energy similarity (+1.46); danceability similarity (+0.47)
5. Static Hearts — Glass Avenue                  Score: 1.84
   Because: energy similarity (+1.48); danceability similarity (+0.36)

Chill Lofi (genre=lofi, mood=chill, energy=0.35, acousticness=0.8)
----------------------------------------------------------------------------------------
1. Library Rain — Paper Lanterns                 Score: 5.47
   Because: genre match (+2.00); mood match (+1.50); energy similarity (+1.50); acousticness similarity (+0.47)
2. Midnight Coding — LoRoom                      Score: 5.35
   Because: genre match (+2.00); mood match (+1.50); energy similarity (+1.40); acousticness similarity (+0.45)
3. Focus Flow — LoRoom                           Score: 3.92
   Because: genre match (+2.00); energy similarity (+1.42); acousticness similarity (+0.49)
4. Spacewalk Thoughts — Orbit Bloom              Score: 3.33
   Because: mood match (+1.50); energy similarity (+1.40); acousticness similarity (+0.44)
5. Coffee Shop Stories — Slow Stereo             Score: 1.93
   Because: energy similarity (+1.47); acousticness similarity (+0.46)

Deep Intense Rock (genre=rock, mood=intense, energy=0.92, tempo_bpm=145)
----------------------------------------------------------------------------------------
1. Storm Runner — Voltline                       Score: 5.46
   Because: genre match (+2.00); mood match (+1.50); energy similarity (+1.48); tempo similarity (+0.48)
2. Static Hearts — Glass Avenue                  Score: 3.86
   Because: genre match (+2.00); energy similarity (+1.38); tempo similarity (+0.48)
3. Gym Hero — Max Pulse                          Score: 3.44
   Because: mood match (+1.50); energy similarity (+1.48); tempo similarity (+0.46)
4. Iron Horizon — Ember Crown                    Score: 3.33
   Because: mood match (+1.50); energy similarity (+1.41); tempo similarity (+0.42)
5. Electric Bloom — Nova Circuit                 Score: 1.94
   Because: energy similarity (+1.44); tempo similarity (+0.50)

Conflicted Sad Workout (genre=edm, mood=sad, energy=0.95, valence=0.2)
----------------------------------------------------------------------------------------
1. Electric Bloom — Nova Circuit                 Score: 3.65
   Because: genre match (+2.00); energy similarity (+1.48); valence similarity (+0.17)
2. Static Hearts — Glass Avenue                  Score: 3.31
   Because: mood match (+1.50); energy similarity (+1.33); valence similarity (+0.48)
3. Iron Horizon — Ember Crown                    Score: 1.90
   Because: energy similarity (+1.46); valence similarity (+0.45)
4. Storm Runner — Voltline                       Score: 1.80
   Because: energy similarity (+1.44); valence similarity (+0.36)
5. Gym Hero — Max Pulse                          Score: 1.69
   Because: energy similarity (+1.47); valence similarity (+0.21)
```

## Evaluation and Experiment

The top results match the intended profiles: `Sunrise City` wins for happy pop, `Library Rain` for chill lofi, and `Storm Runner` for intense rock. The edge case exposes a tradeoff: `Electric Bloom` wins through its EDM genre and energy even though its euphoric mood and high valence conflict with the request for sad music.

I ran a weight-shift experiment using the built-in `energy_focused` mode. It reduces genre and mood to `1.0` point each and doubles energy's balanced weight from `1.5` to `3.0`.

| Profile | Balanced top two | Energy-focused top two | Observation |
|---|---|---|---|
| High-Energy Pop | Sunrise City, Gym Hero | Sunrise City, Gym Hero | The winners stayed stable, but high-energy non-pop tracks moved closer. |
| Chill Lofi | Library Rain, Midnight Coding | Library Rain, Midnight Coding | Exact lofi/chill matches remained strong; ambient and jazz alternatives gained points. |
| Deep Intense Rock | Storm Runner, Static Hearts | Storm Runner, Gym Hero | Energy moved Gym Hero above the second rock song. |
| Conflicted Sad Workout | Electric Bloom, Static Hearts | Static Hearts, Electric Bloom | The sad rock song narrowly passed EDM when energy became dominant, showing that a weight change can make results different without making them unambiguously better. |

The model card contains the full profile comparisons, bias analysis, and evaluation conclusions.

## Testing

Run the automated tests with:

```bash
python -m pytest -q
```

The suite covers typed CSV conversion, invalid data, exact and case-insensitive matching, optional features, strategy weights, deterministic sorting, boundary values for `k`, explanations, and both functional and object-oriented APIs.

```text
..............                                                           [100%]
14 passed in 0.02s
```

## Limitations and Risks

The catalog is tiny and synthetic, and several genres or moods have only one example. Exact text matching cannot understand related labels such as `happy` and `euphoric`. The system has no listening history, skips, lyrics, cultural context, or collaborative signals. Fixed weights can form a filter bubble by repeatedly rewarding the categories a user already selected, and high energy can overpower an emotionally conflicting result.

## Reflection

My biggest learning moment was seeing that recommendation quality depends as much on representation and weighting as on sorting. The ranking code is short, but choices such as whether genre is worth more than mood change what the system appears to understand. Adding explanations made those choices much easier to audit.

AI helped translate the assignment into an implementation plan, propose edge cases, and generate a first pass at code and tests. I still needed to check the scoring math, execute each profile, compare the output with intuition, and confirm the written claims against the actual terminal results. I was surprised that a few weighted additions can feel personalized even though the program knows nothing about listening history. Next, I would collect explicit likes and skips, learn weights per user, and add a diversity step so the top results explore outside one genre.

See the complete [Model Card](model_card.md) and [AI Interactions Log](ai_interactions.md).
