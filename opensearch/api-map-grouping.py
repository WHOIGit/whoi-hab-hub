"""
Query HABhub V2 classifier scores endpoint and return results as a DataFrame.

Parameters mirror the documented REST API filters:
- start_date: 'YYYY-MM-DD'
- end_date:   'YYYY-MM-DD'
- species:    species ID string or comma-separated list
- model_id:   classifier model ID string
- score_gte:  float threshold for score >= score_gte
- dataset_id: optional, comma-separated dataset IDs
- bbox_sw:    optional, 'lon,lat' for southwest corner
- bbox_ne:    optional, 'lon,lat' for northeast corner
- save_csv:   if provided, write results to CSV at this path

Returns:
    pandas.DataFrame with one row per result.
"""

import requests
import pandas as pd

HABHUB_API_URL = "https://habhub-api.whoi.edu/api/v2/ifcb-species-scores/"


def fetch_paginated_results(api_url: str, params=None) -> list[dict]:
    """
    Fetch paginated results from an API and combine them into a single list.

    This follows the pattern in the HABhub V2 classifier API docs.

    Args:
        api_url: base URL of the API endpoint.
        params: dict of query parameters.

    Returns:
        List of result dicts from all pages.
    """
    if params is None:
        params = {}

    all_results: list[dict] = []
    page_idx = 1
    total_hits = None

    while True:
        resp = requests.get(api_url, params=params)
        resp.raise_for_status()

        data = resp.json()
        if total_hits is None and "totalHits" in data:
            total_hits = data["totalHits"]
            print(f"totalHits reported by API: {total_hits}")

        results = data.get("results", [])
        all_results.extend(results)

        print(
            f"Fetched page {page_idx}: {len(results)} results "
            f"(running total = {len(all_results)})"
        )

        links = data.get("links", {})
        next_url = links.get("next")

        if not next_url:
            break

        # For subsequent pages, HABhub encodes params in the 'next' URL already
        api_url = next_url
        params = {}  # avoid double-passing params
        page_idx += 1

    print(f"Done. Total results fetched: {len(all_results)}")
    if total_hits is not None:
        print(f"API totalHits: {total_hits}")
    return all_results


def fetch_habhub_concentrations(
    start_date: str,
    end_date: str,
    species: str,
    model_id: str,
    score_gte: float = 0.0,
    dataset_id=None,
    bbox_sw=None,
    bbox_ne=None,
    save_csv_raw=None,
    save_csv_bins=None,
) -> pd.DataFrame:
    """
    Query HABhub classifier scores and aggregate to per-binPid concentrations.

    Returns a DataFrame with one row per bin, including:
        - binPid
        - lon, lat
        - mlAnalyzed
        - n_hits (ROIs >= score_gte)
        - conc_per_ml = n_hits / mlAnalyzed
    """
    params: dict[str, str] = {
        "start_date": start_date,
        "end_date": end_date,
        "species": species,
        "model_id": model_id,
        "score_gte": str(score_gte),
    }
    if dataset_id:
        params["dataset_id"] = dataset_id
    if bbox_sw:
        params["bbox_sw"] = bbox_sw
    if bbox_ne:
        params["bbox_ne"] = bbox_ne

    all_results = fetch_paginated_results(HABHUB_API_URL, params=params)
    if not all_results:
        print("No HABhub classifier results returned for this query.")
        return pd.DataFrame()

    df_raw = pd.DataFrame(all_results)

    # Flatten the nested 'Source' dict into top-level columns
    source_df = pd.json_normalize(df_raw["Source"])
    df_flat = pd.concat([df_raw.drop(columns=["Source"]), source_df], axis=1)

    # Optional: save flattened raw rows
    if save_csv_raw:
        df_flat.to_csv(save_csv_raw, index=False)
        print(f"Saved raw HABhub results (flattened) to {save_csv_raw}")

    # Extract lon/lat from the 'point' field: [lon, lat]
    df_flat["lon"] = df_flat["point"].str[0]
    df_flat["lat"] = df_flat["point"].str[1]

    # ---- Aggregate per bin ----
    # Count of ROIs per bin = number of classifier hits for that bin (since score_gte filter is already applied)
    grouped = (
        df_flat.groupby("binPid")
        .agg(
            n_hits=("score", "size"),  # number of rows per bin
            mlAnalyzed=("mlAnalyzed", "first"),  # ml per bin (assumed constant)
            lon=("lon", "first"),
            lat=("lat", "first"),
        )
        .reset_index()
    )

    # Compute concentration as hits per ml
    grouped["conc_per_ml"] = grouped["n_hits"] / grouped["mlAnalyzed"]

    if save_csv_bins:
        grouped.to_csv(save_csv_bins, index=False)
        print(f"Saved binned HABhub concentrations to {save_csv_bins}")

    print(grouped)
    return grouped


if __name__ == "__main__":
    """
    PARAMS = {
        "start_date": "2024-10-1",
        "end_date": "2024-11-22",
        "species": "Pseudo-nitzschia",
        # "dataset_id": dataset_id,
        "model_id": "HABLAB_20240110_Tripos2",
        "score_gte": "0.0",
        # "bbox_sw": bbox_sw,
        # "bbox_ne": bbox_ne,
    }  # Adjust parameters as needed
    fetch_paginated_results(HABHUB_API_URL, PARAMS)
    """
    fetch_habhub_concentrations(
        "2024-10-1",
        "2024-11-22",
        "Pseudo-nitzschia",
        model_id="HABLAB_20240110_Tripos2",
        save_csv_bins="grouped.csv",
    )
