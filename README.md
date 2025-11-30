
# Food Shelf-Life Estimator (Rule-based)

This project is a Streamlit app that estimates food shelf life using a conservative, rule-based dataset.

## Files

- `app.py` — Streamlit frontend + backend logic.
- `rules.json` — Rules dataset with 263 foods, global modifiers and sensory flags.
- `README.md` — This file.
- `LICENSE` — MIT license.

## How to run

1. Install dependencies:

   ```bash
   pip install streamlit
   ```

2. Run the app:

   ```bash
   streamlit run app.py
   ```

3. Open the URL shown in the terminal (usually http://localhost:8501) in a browser.

The rules dataset can be previewed and downloaded from within the app in the sidebar section named **"Rules dataset (rules.json)"**.
