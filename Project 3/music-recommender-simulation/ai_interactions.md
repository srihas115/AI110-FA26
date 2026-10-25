# AI Interactions Log

## Agentic Workflow

**What task did you give the agent?**

I asked Codex to finish Project 3 from the saved CodePath assignment page, use the official Music Recommender Simulation starter, make meaningful commits, verify the result, and prepare the repository subfolder for submission.

**Prompts used**

- Finish Project 3 using the saved CodePath Project 3 instructions.
- Delete the downloaded assignment HTML and companion files only after the implementation is complete, and never commit them.

**What did the agent generate or change?**

- Imported the official starter into `Project 3/music-recommender-simulation` without its Git history.
- Expanded the catalog from 10 to 18 fictional songs across more genres and moods.
- Implemented typed CSV loading, weighted scoring, per-feature reasons, deterministic top-k ranking, and an object-oriented wrapper.
- Added balanced, genre-first, mood-first, and energy-focused scoring strategies.
- Added a CLI evaluation for four profiles, including one conflicting edge case.
- Replaced the starter tests with 14 tests covering loading, scoring, ranking, explanations, modes, invalid inputs, and edge cases.
- Completed the README, model card, experiment, bias analysis, and personal reflection.

**What did you verify or fix manually?**

I checked that every displayed score equals the sum of its explanation, that numeric CSV fields are converted before math, and that ties have deterministic ordering. I ran all four profiles, compared balanced and energy-focused rankings, reviewed the adversarial profile's surprising result, and ran the full automated suite plus Python compilation. I also verified that the downloaded course page remained untracked throughout development.

## Design Pattern

**Which design pattern did you use?**

A lightweight Strategy pattern for scoring modes.

**How did AI help you brainstorm or implement it?**

AI proposed keeping one scoring pipeline and storing named weight dictionaries instead of duplicating separate ranking functions. This makes the experiment repeatable and keeps explanations consistent across modes.

**How does the pattern appear in the final code?**

`SCORING_MODES` defines each strategy. `score_song()` and `recommend_songs()` accept a mode name, and the `Recommender` class stores the selected mode. The same catalog can therefore be ranked with different priorities while using one tested implementation.
