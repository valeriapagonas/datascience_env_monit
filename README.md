# Environmental Monitoring and Data Analysis

## About this repository

This repository documents my coursework for the Environmental Monitoring
and Data Analysis module at the University of Freiburg during the winter
semester 2026/2027, as part of the M.Sc. Environmental Sciences,
majoring in Climate Change Ecology.

The project focuses on environmental data acquisition, processing,
quality control, integration, visualization and statistical analysis
to investigate ecosystem functioning and environmental drivers of
ecosystem productivity.

The analyses combine FLUXNET eddy covariance measurements with
complementary environmental datasets across five study sites.

This repository is a personal fork of the
[original course repository](https://github.com/negin-katal/datascience_env_monit)
and is updated throughout the semester.

## Study sites

| Site ID | Country | Ecosystem |
|---|---|---|
| JP-Api | Japan | Deciduous broadleaf forest (DBF) |
| CA-Ca1 | Canada | Evergreen needleleaf forest (ENF) |
| CH-Rtb | Switzerland | Grassland (GRA) |
| CZ-KrP | Czech Republic | Cropland (CRO) |
| US-Elm | United States | Wetland (WET) |

## Repository structure

| Folder or file | Description |
|---|---|
| `assignments/` | Original course assignment instructions |
| `scripts/` | Data acquisition, processing and analysis scripts |
| `scripts/block5/` | Complementary environmental data scripts |
| `reports/` | Quarto source files, HTML reports and references |
| `jobs/` | Slurm job submission scripts |
| `docs/` | Notes and templates |
| `data/raw/` | Original FLUXNET datasets (local only) |
| `data/external/` | Complementary datasets (local only) |
| `data/processed/` | Merged environmental datasets (local only) |
| `tower_sets_block4.csv` | FLUXNET tower assignments |

## Software and computational environment

- R
- Python
- Positron IDE
- Quarto
- Git and GitHub
- bwUniCluster and Slurm

Block 5 analyses were performed locally on macOS because
bwUniCluster was temporarily unavailable.

## Coursework and reproducibility

### Block 2 – Git, GitHub and cluster computing

Introduction to version control, repository management,
remote computing and reproducible scientific workflows.

The initial exercise bootstraps a synthetic GPP time series
and prints a 95% interval.

To reproduce the exercise, run from the repository root:

```bash
Rscript scripts/cluster_hello.R 200
```

This block also included working with Git commits, remote
repositories, SSH connections and Slurm job scripts.

### Block 4 – FLUXNET data summary

This assignment explores FLUXNET eddy covariance observations
across five study sites, focusing on ecosystem carbon fluxes,
meteorological variables, temporal coverage, data availability
and data quality.

The original FLUXNET datasets were downloaded using the
FLUXNET Shuttle and stored locally in `data/raw/`.

Report files:

- [Quarto source](reports/block4_data_summary.qmd)
- [Rendered HTML report](reports/block4_data_summary.html)

With the required FLUXNET data available locally,
render the report from the repository root:

```bash
quarto render reports/block4_data_summary.qmd --to html
```

### Block 5 – Complementary environmental data

This assignment integrates FLUXNET observations with
complementary environmental datasets to investigate
ecosystem functioning and productivity.

The preliminary exploratory analysis considered the
following datasets:

| Dataset | Environmental information |
|---|---|
| ERA5-Land | Air temperature, soil temperature and soil moisture |
| WorldClim | Long-term bioclimatic conditions |
| DHEED | Compound dry and hot events |
| SoilGrids | Soil physical and chemical properties |
| PlantTraits | Community-weighted plant functional traits |
| DeadTrees | Tree cover and standing deadwood |
| iNaturalist | Biodiversity observations |
| MODIS MOD13Q1 | Satellite-derived vegetation indices |

#### Final research question

How does the relationship between MODIS vegetation greenness
(NDVI/EVI) and FLUXNET gross primary productivity (GPP)
vary across five ecosystems, and can ERA5-Land soil moisture
help explain differences in this relationship?

The final analysis focuses on three data sources:

- FLUXNET gross primary productivity
- MODIS NDVI and EVI
- ERA5-Land volumetric soil water content (7–28 cm depth)

Report files:

- [Preliminary exploratory report](reports/block5_preliminary_report.html)
- [Preliminary Quarto source](reports/block5_preliminary_report.qmd)
- [Final HTML report](reports/block5_question.html)
- [Final Quarto source](reports/block5_question.qmd)

## Reproducing the Block 5 analysis

### 1. Clone the repository

```bash
git clone https://github.com/valeriapagonas/datascience_env_monit.git
cd datascience_env_monit
```

All subsequent terminal commands should be executed from
the repository root.

### 2. Install software dependencies

Install the required R packages in the R console:

```r
install.packages(c(
  "dplyr",
  "tidyr",
  "readr",
  "ggplot2",
  "lubridate",
  "knitr",
  "patchwork",
  "httr2",
  "jsonlite",
  "terra",
  "geodata",
  "MODISTools",
  "ecmwfr"
))
```

Install Python dependencies in the terminal:

```bash
python3 -m pip install pandas numpy requests rasterio pyproj cdsapi
```

Further information on dataset acquisition and dependencies
is provided in the
[Block 5 scripts documentation](scripts/block5/README.md).

### 3. Prepare the input data

Obtain the five assigned FLUXNET datasets using the FLUXNET
Shuttle and extract them into `data/raw/`, preserving the
directory structure described in the Block 4 assignment.

Keep `tower_sets_block4.csv` in the repository root.

Configure the correct student number in `block5_sites.R`
and `block5_sites.py` before running the complementary
data acquisition scripts.

### 4. Obtain the complementary datasets

Download ERA5-Land data:

```bash
Rscript scripts/block5/01_era5land.R
```

This step requires a Copernicus Climate Data Store (CDS)
account, accepted dataset licence and configured API
credentials.

Download MODIS vegetation indices:

```bash
python3 scripts/block5/08_modis_ndvi_evi.py
```

Only MODIS observations with pixel reliability flags
0 (good quality) and 1 (marginal quality) are retained.

The MODIS validation script is available at:

`scripts/block5/08_modis_validation.py`

### 5. Merge the datasets

After downloading the required complementary datasets,
run the merging script:

```bash
Rscript scripts/block5/09_merge.R
```

This generates the processed datasets:

- `data/processed/site_static.csv`
- `data/processed/site_daily.csv`

The final report uses the merged daily dataset together
with the original MODIS composite observations:

- `data/processed/site_daily.csv`
- `data/external/modis/modis_vi_my_sites.csv`

The original MODIS observations are retained to preserve
their temporal resolution and avoid treating interpolated
daily vegetation indices as independent observations.

### 6. Render the final report

Once the required input datasets are available, run:

```bash
quarto render reports/block5_question.qmd --to html
```

The Quarto document contains the additional data processing,
quality filtering, temporal matching, statistical analysis,
tables and figures.

The rendered output is saved as:

`reports/block5_question.html`

## Data availability and quality control

Raw, external and processed environmental datasets are
stored locally and are not committed to GitHub.

Missing observations are retained as NA, and no additional
gap-filling is performed in Block 5.

Dataset provenance, spatial and temporal resolution,
download dates, quality-control procedures and methodological
limitations are documented in the corresponding reports.

Scientific references are maintained in
[references.bib](reports/references.bib).

## Updating the repository

New course materials are obtained from the upstream repository
after committing or stashing local changes:

```bash
git status
git pull --no-rebase upstream main
git push origin main
```

If a merge conflict occurs in `README.md`, the personal
README is retained in accordance with the course instructions.

## Author

**Valeria Pagonas**

M.Sc. Environmental Sciences – Climate Change Ecology  
University of Freiburg  
Winter semester 2026/2027

## Acknowledgements

The original teaching materials and complementary data
acquisition scripts were provided through the Environmental
Monitoring and Data Analysis course repository.

FLUXNET site investigators and the providers of complementary
environmental datasets are acknowledged and cited in the
individual reports.

Last updated: 25 November 2026.