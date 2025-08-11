# CBM Calculator (Streamlit)

This Streamlit app calculates CBM (m³) from bin dimensions given in centimeters. The app supports column mapping, visual summaries, usage breakdowns, and file download.

## Features
- Upload Excel (.xlsx/.xls) or CSV
- Map columns for BinID, Height, Width, Depth (cm)
- Optional: Map a "Usage" column (e.g., drawer / non-drawer) to get breakdowns
- Calculate CBM (m³) and round to configurable decimals
- Download results as an updated Excel with CBM and a small-bins sheet
- Visualizations: histogram, boxplot, breakdown bar chart

## Quickstart
1. Create a GitHub repo and push the files from this project.
2. Add a sample CSV (see `sample_templates`).
3. On Streamlit Cloud (app.streamlit.io), connect your GitHub repo and deploy the app.

## Deployment notes
- Make sure `requirements.txt` is present.
- Streamlit Cloud will install dependencies and run `streamlit run app.py`.
