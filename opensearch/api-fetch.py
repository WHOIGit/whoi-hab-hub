import requests

# set your filter parameters
# all parameters are optional, but unfiltered searches may return millions of results so use caution
start_date = "2023-06-01"
end_date = "2023-06-30"
species = "Alexandrium_catenella"
# dataset_id = ""
model_id = "HABLAB_20240110_Tripos2"
score_gte = ".9"
# bbox_sw = "lat,long"
# bbox_ne = "lat,long"


def fetch_paginated_results(api_url, params=None):
    """
    Fetch paginated results from an API and combine them into a single response.

    Args:
        api_url (str): The base URL of the API endpoint.
        params (dict, optional): Additional query parameters for the API request.

    Returns:
        list: A combined list of all results from all pages.
    """
    if params is None:
        params = {}

    all_results = []

    while True:
        # Update the parameters to
        # params.update({"page": page})

        # Make the API request
        response = requests.get(api_url, params=params)

        # Raise an error if the request failed
        response.raise_for_status()

        # Parse the JSON response
        data = response.json()

        # Get next/prev links
        links = data.get("links", None)
        # Check if there are more pages
        # Assuming the API provides a "next" field to indicate the next page
        if not links:
            break

        # Get the results
        results = data["results"]["hits"]["hits"]
        print(results, len(results))
        # Add the current page's results to the combined list
        all_results.extend(results)

        # Update the API URL to get next page of results
        api_url = links["next"]
        print("Next", api_url)

    return all_results


# Example usage
if __name__ == "__main__":
    API_URL = "https://habhub-api.whoi.edu/api/v2/ifcb-species-scores/"
    PARAMS = {
        "start_date": start_date,
        "end_date": end_date,
        "species": species,
        # "dataset_id": dataset_id,
        "model_id": model_id,
        "score_gte": score_gte,
        # "bbox_sw": bbox_sw,
        # "bbox_ne": bbox_ne,
    }  # Adjust parameters as needed

    try:
        combined_results = fetch_paginated_results(API_URL, params=PARAMS)
        print(f"Fetched {len(combined_results)} items.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
