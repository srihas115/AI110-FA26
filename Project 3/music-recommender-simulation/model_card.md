# Model Card: VibeMap 1.0

## 1. Model Name

**VibeMap 1.0**

## 2. Goal, Intended Use, and Non-Intended Use

VibeMap predicts which songs in a small catalog best match a stated taste profile. It is designed for students exploring how content-based ranking turns features into recommendations. It assumes the listener can describe a preferred genre, mood, and energy level, with optional numeric preferences.

This is a classroom simulation, not a production model. It should not be used to make high-stakes decisions, infer sensitive traits, judge artists, or claim to represent a person's full taste. Scores are relative matches inside this catalog, not universal quality ratings.

## 3. Data Used

The local CSV contains 18 fictional songs. Ten came from the starter catalog and eight were added to improve variety. Its columns are ID, title, artist, genre, mood, energy, tempo, valence, danceability, and acousticness.

The expanded rows add Latin, classical, hip hop, folk, EDM, R&B, and metal examples. The data is still small: most categories contain only one or two tracks, labels are subjective, and it contains no lyrics, language, release date, popularity, listening behavior, or real user feedback. It is not a representative sample of music or listeners.

## 4. Algorithm Summary

VibeMap uses content-based filtering. In balanced mode, an exact genre match earns 2 points and an exact mood match earns 1.5 points. Energy earns up to 1.5 points based on how close the song is to the target. Optional tempo, valence, danceability, and acousticness preferences each earn up to 0.5 similarity points.

Every song is scored independently. The program sorts the catalog by total score and returns the top five. Each result lists the factors that added points. Ties use title and ID so repeated runs are stable.

Three additional strategies change the feature weights: genre-first, mood-first, and energy-focused. They reuse the same scoring pipeline. This strategy-style design makes experiments easy to repeat without changing the algorithm by hand.

## 5. Strengths and Observed Behavior

VibeMap works best when the requested genre and mood both exist in the catalog. It gave intuitive first choices for three focused profiles: `Sunrise City` for high-energy happy pop, `Library Rain` for chill lofi, and `Storm Runner` for intense rock. The explanations correctly reveal which exact matches and numeric similarities produced those rankings.

It also handles a profile with no perfect song instead of failing. For the conflicted sad-workout profile, it presents the tradeoff between an energetic EDM match and a sad mood match. The deterministic rules and tests make every result reproducible.

## 6. Limitations and Bias

The biggest weakness is sparse representation. A category with one song can appear to be the only valid expression of that genre, while lofi and pop have several chances to rank. That can over-favor represented genres and make unfamiliar preferences collapse into energy-only matches.

Exact labels also create artificial boundaries: the system treats `happy` and `euphoric` as unrelated even though a listener may view them as similar. Fixed weights can create a filter bubble because a selected genre receives a large bonus on every run. Numeric similarity ignores context, so a high-energy euphoric track can rank for a sad workout request. The catalog and weights reflect their creator's choices, not ground truth about musical taste.

## 7. Evaluation Process

I ran the top-five ranking for four profiles:

- **High-Energy Pop:** pop, happy, energy 0.85, danceability 0.85.
- **Chill Lofi:** lofi, chill, energy 0.35, acousticness 0.80.
- **Deep Intense Rock:** rock, intense, energy 0.92, tempo 145 BPM.
- **Conflicted Sad Workout:** EDM, sad, energy 0.95, valence 0.20.

The first three test clear, internally consistent tastes. The fourth is adversarial because the small catalog has no sad EDM track. I checked whether top songs matched my intuition, whether the explanation added up to the displayed score, and whether profiles produced meaningfully different rankings.

Pairwise comparisons:

- Pop versus lofi: pop favors energetic, danceable songs; lofi moves low-energy acoustic tracks to the top.
- Pop versus rock: both favor energy, but genre and mood send one toward happy pop and the other toward intense guitars.
- Pop versus conflicted: `Sunrise City` loses its exact matches, while high-energy EDM and sad rock become stronger.
- Lofi versus rock: their target energies are almost opposites, so calm acoustic tracks give way to fast, intense tracks.
- Lofi versus conflicted: the low-energy/acoustic targets reverse into very high energy and low valence, producing almost entirely different top fives.
- Rock versus conflicted: both like high energy, so several songs overlap, but rock/intense puts `Storm Runner` first while EDM/sad splits its top two between `Electric Bloom` and `Static Hearts`.

The biggest surprise was the conflicted profile. Balanced mode ranked `Electric Bloom` first because genre and energy outweighed its emotional mismatch. This demonstrates why a high score is not the same as a correct recommendation.

### Weight-Shift Experiment

I changed the ranking to energy-focused mode: energy increased from 1.5 to 3 points while genre and mood became 1 point each. `Gym Hero` passed `Static Hearts` for the rock profile even though it is pop, and `Static Hearts` narrowly passed `Electric Bloom` for the conflicted profile. The change increased cross-genre similarity but weakened categorical intent. It made the output different, not consistently more accurate, so balanced mode remains the default.

The automated suite contains 14 tests for loading, scoring, explanations, modes, sorting, error handling, and API behavior. All tests pass.

## 8. Ideas for Improvement

1. Gather likes, skips, replays, and explicit ratings so each listener's weights can adapt over time.
2. Expand and rebalance the catalog, allow multiple mood tags, and represent related terms with embeddings instead of exact text matches.
3. Add a diversity reranker that limits repeated artists or genres and occasionally explores outside the user's existing profile.

## 9. Personal Reflection

My biggest learning moment was realizing that the feature choices are the model. The final sorting step is simple; the difficult part is deciding how a human idea such as a musical vibe becomes fields and weights. Explanations made it clear when a result succeeded for the intended reason and when it only benefited from energy.

AI helped me turn the requirements into modules, brainstorm an adversarial profile, and draft code and tests. I had to double-check its work by recomputing expected scores, running the CLI, and comparing every documentation claim to real output. Simple weighted rules still felt surprisingly personal when several features lined up. If I continued, I would learn preferences from feedback and deliberately balance relevance with discovery.
