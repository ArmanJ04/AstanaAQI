# AstanaAQI

This repository contains the data, modeling notebook, generated article materials, and supporting project files for the study:

**Leakage-Safe Next-Day PM2.5 AQI Forecasting in Astana Using Meteorological and Domain-Oriented Predictors**

## Overview

This project investigates **next-day daily PM2.5 Air Quality Index (AQI) forecasting** for the **US Embassy Astana station** using machine learning, meteorological variables, and domain-oriented predictors.

The forecasting task is defined as:

- predicting **PM2.5 AQI for day t+1**
- using information available on **day t**
- under the assumption that **same-day meteorological observations are already known at issue time**

A central methodological requirement of the project is that the PM2.5 AQI time series contains substantial missing intervals. Because of this, the AQI series is first **reindexed to a complete daily calendar** before lagged and rolling predictors are created. This avoids an incorrect compressed-series formulation and supports leakage-safe forecasting.

## Why this station was selected

The **US Embassy Astana station** was selected for three methodological reasons:

1. it provided the most usable long-run station-level PM2.5 AQI record for Astana within the data-collection workflow used in this study;
2. its temporal coverage was sufficient for calendar-consistent reindexing, leakage-safe lag construction, and multi-fold time-based validation;
3. focusing on a single station isolates **temporal predictability** and avoids mixing heterogeneous monitoring contexts across sites.

This repository therefore supports a **station-level forecasting study**, not a citywide spatial air-quality model for all of Astana.

## Repository structure

The current repository structure is:

```text
AstanaAQI/
├── astana_emb_dataset.csv
├── astanaUS.csv
├── final_improved.ipynb
├── modelDATA.py
├── figures1/
└── tables1/
```

## Repository contents

### 1. Main processed dataset

**File:** `astana_emb_dataset.csv`

This is the **final processed dataset** used for model development, cross-validation, holdout evaluation, and article results.

It contains:

- daily PM2.5 AQI observations for the **US Embassy Astana station**
- daily meteorological variables
- aligned calendar dates
- supplementary pollutant variables preserved for extension analyses

This is the **main dataset used in the article and notebook**.

### 2. Source AQI dataset

**File:** `astanaUS.csv`

This file contains the **source AQI data** used in the data-preparation workflow before the final merged dataset was assembled.

It is included in the repository to improve transparency and reproducibility.

### 3. Modeling notebook

**File:** `final_improved.ipynb`

This is the **main modeling notebook** for the project.

It includes:

1. dataset loading and validation
2. exploratory analysis
3. leakage-safe feature engineering
4. outer date-purged cross-validation
5. chronological holdout evaluation
6. comparison of regression models
7. polluted-day detection analysis for AQI > 100
8. feature-set ablation
9. permutation importance
10. supplementary co-pollutant experiments
11. predictive-interval analysis
12. final next-day inference example

The notebook is centered on:

- **next-day PM2.5 AQI regression**
- supplementary event-detection and interpretability analysis

### 4. Supporting Python script

**File:** `modelDATA.py`

This Python script is included as a supporting project file used in the workflow of the study. Depending on the exact working version, it may support parts of:

- data preparation
- weather-data processing
- feature generation
- modeling workflow support

### 5. Generated article figures

**Folder:** `figures1/`

This folder contains figures generated for the article and analysis workflow, such as:

- PM2.5 AQI time-series plots
- cross-validation performance plots
- holdout prediction plots
- event-detection plots
- feature-importance plots
- methodological pipeline figure

### 6. Generated article tables

**Folder:** `tables1/`

This folder contains generated result tables used in the article, including:

- cross-validation summaries
- holdout regression results
- event-detection metrics
- ablation results
- supplementary analysis outputs

## Target variable

The target variable in this project is:

- **daily PM2.5 AQI**

This project forecasts **AQI**, not PM2.5 concentration in micrograms per cubic meter.

All modeling, evaluation, and interpretation in the article refer to **AQI forecasting**.

## How the processed dataset was assembled

The final processed dataset `astana_emb_dataset.csv` was assembled through the following workflow:

1. manual collection of daily PM2.5 AQI values from AQICN historical records for the US Embassy Astana station;
2. chronological cleaning and normalization of the raw AQI series;
3. reindexing of the AQI record to a complete daily calendar;
4. retrieval of daily meteorological variables from the Open-Meteo historical archive;
5. merge by date between the AQI calendar and the meteorological data;
6. validation of duplicate dates, numeric consistency, and missing-value structure;
7. export of the final merged dataset as `astana_emb_dataset.csv`.

## Weather and climate variables

Meteorological variables were retrieved from:

- **Open-Meteo Historical Weather API**
- ERA5-based reanalysis products available through Open-Meteo

The modeling workflow uses daily aggregated weather variables such as:

- mean temperature
- minimum temperature
- maximum temperature
- mean humidity
- mean dew point
- mean wind speed
- maximum wind speed
- maximum wind gust
- mean pressure
- precipitation sum
- mean cloud cover
- mean radiation
- mean wind direction

The project also derives domain-oriented predictors such as:

- stagnant anticyclonic conditions
- cold-stagnant regimes
- heating-season indicators
- low-wind persistence
- high-pressure persistence
- circular wind-direction encoding

## Main modeling objective

The main objective of this repository is to evaluate whether a leakage-safe forecasting pipeline can produce useful **next-day PM2.5 AQI forecasts for Astana** under correct temporal validation.

The strongest overall result in the project is obtained for **next-day forecasting** using **Ridge regression with autoregressive and weather-domain predictors**.

The study shows that:

- useful predictive skill is concentrated mainly at the **one-day horizon**
- meteorological and domain-oriented predictors contribute strongly to performance
- predictive skill declines substantially as the forecast horizon increases
- rare severe pollution episodes remain difficult to detect reliably

## Reproducibility

To reproduce the main workflow:

### Step 1. Clone the repository

```bash
git clone https://github.com/ArmanJ04/AstanaAQI.git
cd AstanaAQI
```

### Step 2. Open the modeling notebook

Open:

- `final_improved.ipynb`

### Step 3. Run the notebook

Run the notebook from top to bottom.

The notebook uses:

- `astana_emb_dataset.csv` as the main processed dataset
- `figures1/` for generated figure outputs
- `tables1/` for generated table outputs

## Relationship to the article

This repository provides the public data and reproducibility materials for the article:

**Leakage-Safe Next-Day PM2.5 AQI Forecasting in Astana Using Meteorological and Domain-Oriented Predictors**

The article is based on:

- the processed dataset `astana_emb_dataset.csv`
- the source AQI file `astanaUS.csv`
- the modeling notebook `final_improved.ipynb`
- the supporting workflow file `modelDATA.py`
- generated figures in `figures1/`
- generated tables in `tables1/`

## Data availability

The dataset, modeling notebook, generated figures, generated tables, and supporting project files are publicly available in this repository:

- https://github.com/ArmanJ04/AstanaAQI

Primary processed dataset:

- `astana_emb_dataset.csv`

Source AQI dataset:

- `astanaUS.csv`

Main modeling notebook:

- `final_improved.ipynb`

Supporting script:

- `modelDATA.py`

## Limitations

This repository reflects a **station-level forecasting study** and should not be interpreted as a full spatial air-quality model for all of Astana.

Main limitations include:

- substantial missing intervals in the AQI series
- dependence of the best-performing setup on same-day observed meteorology
- weaker reliability for rare severe-pollution episodes
- rapidly declining performance at longer forecast horizons

## Suggested repository citation

If you use this repository, please cite both the associated article and the repository itself.

Suggested repository citation:

> Jansatov, A. Astana PM2.5 AQI forecasting dataset, notebook, and code repository. GitHub repository. Available at: https://github.com/ArmanJ04/AstanaAQI

## Contact

**Arman Jansatov**  
Astana IT University  
Astana, Kazakhstan  
Email: 255118@astanait.edu.kz
