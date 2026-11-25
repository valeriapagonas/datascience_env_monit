"""
08_modis_validation.py

Environmental Monitoring and Data Analysis - Block 5
University of Freiburg

Download official MODIS NDVI and EVI values for comparison
with vegetation indices calculated from reflectance data.

Product: MOD13Q1 Collection 6.1
Spatial resolution: 250 m
Temporal resolution: 16-day composites
Spatial window: 1 km around each FLUXNET tower

Existing raw files are NEVER overwritten.

Completed site/band downloads are saved separately.
The script can be run again after an interruption.

Data source:
ORNL DAAC MODIS/VIIRS Subset Web Service

References:
Didan (2021), MOD13Q1 V061
DOI: 10.5067/MODIS/MOD13Q1.061

ORNL DAAC (2018), MODIS Subsets Web Service
DOI: 10.3334/ORNLDAAC/1557
"""

from pathlib import Path
import time

import pandas as pd
import requests


# ============================================================
# 1. CONFIGURATION
# ============================================================

print("MODIS VALIDATION SCRIPT STARTED", flush=True)

DATA_DIR = Path("data/external/modis")

API = "https://modis.ornl.gov/rst/api/v1/MOD13Q1"

# Official MODIS vegetation index bands
BANDS = {
    "250m_16_days_NDVI": "ndvi_modis",
    "250m_16_days_EVI": "evi_modis",
}

# FLUXNET tower coordinates: latitude, longitude
SITES = {
    "CA-Ca1": (49.86730, -125.33360),
    "CH-Rtb": (47.38040, 8.99340),
    "CZ-KrP": (49.57326, 15.07877),
    "JP-Api": (40.00136, 140.93658),
    "US-Elm": (25.55190, -80.78260),
}

# Same spatial window as the original MODIS script
KM = 1

# Maximum dates requested per subset
CHUNK_SIZE = 10

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Freiburg Environmental Monitoring course",
}

# Separate folder for validation downloads
VALIDATION_DIR = DATA_DIR / "official_validation"

VALIDATION_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# 2. FUNCTION TO CONTACT THE MODIS API
# ============================================================

def get_json(url, params, tries=6):

    for attempt in range(1, tries + 1):

        try:
            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=120
            )

            response.raise_for_status()

            return response.json()

        except (requests.RequestException, ValueError) as error:

            print(
                f"Request failed ({attempt}/{tries}): {error}",
                flush=True
            )

            if attempt == tries:
                raise

            delay = 10 * attempt

            print(
                f"Retrying after {delay} seconds...",
                flush=True
            )

            time.sleep(delay)


# ============================================================
# 3. LOAD EXISTING MODIS DATES AND PIXELS
# ============================================================

def load_existing_pixels(site_id):

    file = DATA_DIR / f"{site_id}_mod13q1_pixels.csv"

    if not file.exists():
        raise FileNotFoundError(
            f"Original MODIS file missing: {file}"
        )

    original = pd.read_csv(
        file,
        usecols=["calendar_date", "pixel"]
    )

    original["calendar_date"] = (
        original["calendar_date"].astype(str)
    )

    original["pixel"] = (
        original["pixel"].astype(int)
    )

    # Each pixel/date appears multiple times in the
    # original file because multiple bands were downloaded.
    original = original.drop_duplicates()

    return original


# ============================================================
# 4. GET AVAILABLE MODIS DATES
# ============================================================

def get_date_lookup(lat, lon):

    result = get_json(
        f"{API}/dates",
        {
            "latitude": lat,
            "longitude": lon
        }
    )

    lookup = {
        item["calendar_date"]: item["modis_date"]
        for item in result["dates"]
    }

    return lookup


# ============================================================
# 5. DOWNLOAD ONE OFFICIAL MODIS BAND
# ============================================================

def download_band(
    site_id,
    lat,
    lon,
    band,
    name,
    wanted_dates,
    date_lookup,
    expected_pixels
):

    rows = []

    for start in range(
        0,
        len(wanted_dates),
        CHUNK_SIZE
    ):

        chunk = wanted_dates[
            start:start + CHUNK_SIZE
        ]

        first_date = chunk[0]
        last_date = chunk[-1]

        print(
            f"  {name}: {first_date} to {last_date}",
            flush=True
        )

        result = get_json(
            f"{API}/subset",
            {
                "latitude": lat,
                "longitude": lon,
                "band": band,
                "startDate": date_lookup[first_date],
                "endDate": date_lookup[last_date],
                "kmAboveBelow": KM,
                "kmLeftRight": KM,
            }
        )

        for subset in result["subset"]:

            date = subset["calendar_date"]

            # Retain only dates in original downloads
            if date not in chunk:
                continue

            for pixel, value in enumerate(subset["data"]):

                rows.append({
                    "site_id": site_id,
                    "date": date,
                    "pixel": pixel,
                    "band": name,
                    "value": value
                })

        time.sleep(1)

    output = pd.DataFrame(
        rows,
        columns=[
            "site_id", "date", "pixel", "band", "value"
        ]
    )

    # Check that every expected date/pixel was obtained.
    actual = output[
        ["date", "pixel"]
    ].rename(columns={"date": "calendar_date"})

    if actual.duplicated().any():
        raise ValueError(
            f"{site_id}, {name}: duplicate date/pixel records"
        )

    expected_keys = set(
        map(tuple, expected_pixels[
            ["calendar_date", "pixel"]
        ].itertuples(index=False, name=None))
    )

    actual_keys = set(
        map(tuple, actual.itertuples(
            index=False, name=None
        ))
    )

    if expected_keys != actual_keys:
        raise ValueError(
            f"{site_id}, {name}: downloaded pixel/date "
            "keys do not match the original data. "
            "Check the MODIS window and service response."
        )

    return output


# ============================================================
# 6. PROCESS ALL FIVE FLUXNET SITES
# ============================================================

def main():

    all_outputs = []

    for site_id, (lat, lon) in SITES.items():

        print(
            f"\nProcessing {site_id}",
            flush=True
        )

        original_pixels = load_existing_pixels(site_id)

        wanted_dates = sorted(
            original_pixels["calendar_date"].unique()
        )

        print(
            f"  Original dates: {len(wanted_dates)}",
            flush=True
        )

        # Avoid calling the API if both files exist.
        pending = [
            (band, name)
            for band, name in BANDS.items()
            if not (
                VALIDATION_DIR /
                f"{site_id}_{name}.csv"
            ).exists()
        ]

        date_lookup = None

        if pending:

            date_lookup = get_date_lookup(lat, lon)

            missing = [
                date for date in wanted_dates
                if date not in date_lookup
            ]

            if missing:
                raise ValueError(
                    f"{site_id}: unavailable MODIS dates: "
                    f"{missing}"
                )

        for band, name in BANDS.items():

            output_file = (
                VALIDATION_DIR /
                f"{site_id}_{name}.csv"
            )

            if output_file.exists():

                print(
                    f"  {name}: using saved file",
                    flush=True
                )

                band_data = pd.read_csv(output_file)

            else:

                print(
                    f"  Downloading {name}...",
                    flush=True
                )

                band_data = download_band(
                    site_id,
                    lat,
                    lon,
                    band,
                    name,
                    wanted_dates,
                    date_lookup,
                    original_pixels
                )

                # Write only after all pixel/date checks pass.
                temporary_file = output_file.with_suffix(
                    ".csv.tmp"
                )

                band_data.to_csv(
                    temporary_file,
                    index=False
                )

                temporary_file.replace(output_file)

                print(
                    f"  Saved {output_file}",
                    flush=True
                )

            # Validate cached files too.
            actual = band_data[
                ["date", "pixel"]
            ].rename(
                columns={"date": "calendar_date"}
            )

            expected_keys = set(map(
                tuple,
                original_pixels[
                    ["calendar_date", "pixel"]
                ].itertuples(index=False, name=None)
            ))

            actual_keys = set(map(
                tuple,
                actual.itertuples(index=False, name=None)
            ))

            if (
                expected_keys != actual_keys
                or len(actual) != len(expected_keys)
            ):
                raise ValueError(
                    f"Invalid saved data for {site_id}, {name}"
                )

            all_outputs.append(band_data)

        print(
            f"  {site_id}: completed",
            flush=True
        )

    # ========================================================
    # 7. COMBINE VALIDATION DATA
    # ========================================================

    combined = pd.concat(
        all_outputs,
        ignore_index=True
    )

    combined_file = (
        DATA_DIR / "modis_official_validation.csv"
    )

    combined.to_csv(
        combined_file,
        index=False
    )

    print(
        "\nMODIS VALIDATION DOWNLOAD COMPLETE",
        flush=True
    )

    print(
        f"\nSaved: {combined_file}",
        flush=True
    )

    print("\nRecords by site and band:")

    print(
        combined.groupby(
            ["site_id", "band"]
        ).size()
    )

    print(
        "\nRaw official values have not been scaled. "
        "Apply the 0.0001 scale factor and quality "
        "filter during validation in R."
    )


# ============================================================
# 8. EXECUTE SCRIPT
# ============================================================

if __name__ == "__main__":
    main()
