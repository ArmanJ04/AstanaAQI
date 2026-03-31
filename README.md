# AstanaAQI

This repository contains the dataset, modeling notebook, generated article materials, and supporting files for the study:

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

## Repository contents

This repository currently contains the following files and folders:

```text
AstanaAQI/
├── astana_emb_dataset.csv
├── astanaUS.csv
├── final_improved.ipynb
├── modelDATA.py
├── figures1/
└── tables1/
