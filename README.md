# AgriSwitch–MASI — Four-page research website

This is a newly written, self-contained Streamlit website based on the supplied AgriSwitch-MASI CSV exports. It contains exactly **four pages**:

1. Overview Dashboard
2. Crop Pattern Analysis
3. Climate Analysis
4. Market Arrivals & MASI

The Model Evaluation, Historical Classification and Data & Methodology pages have deliberately been excluded. This package does **not** load or distribute the `.pkl` classifier. All included CSVs were provided by the user.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Run in Google Colab

Upload the ZIP and execute:

```python
from google.colab import files
uploaded = files.upload()
import zipfile, os
zip_name = next(name for name in uploaded if name.endswith('.zip'))
with zipfile.ZipFile(zip_name) as archive:
    archive.extractall('/content')
%cd /content/AgriSwitch_Four_Page_Website
!pip install -q -r requirements.txt
!streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true > /content/agriswitch_streamlit.log 2>&1 &
```

To get a temporary external link, use a trusted tunneling service. For stable presentation access deploy the folder to a hosting provider such as Streamlit Community Cloud. Keep an internet connection available when presenting.

## Data assumptions and limits

- Crop data cover selected Maharashtra districts, 2017–18 through 2022–23.
- Climate summaries span 2017–18 through 2024–25 and anomalies are calculated against the within-study-period district means.
- MASI uses the supplied four-year scores (2021–22 through 2024–25); it is historical variability, not forecast risk.
- Market-arrival reporting coverage/market identifiers and source rainfall units remain subject to verification.
- Crop-area changes at a district level cannot establish that individual farmers switched crops.
