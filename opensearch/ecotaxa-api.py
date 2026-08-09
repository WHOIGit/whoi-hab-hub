import requests

BASE = "https://ecotaxa.obs-vlfr.fr/api"

username = "eandrews@whoi.edu"
password = "AV131ion!"
project_id = 20825

# 1) Login
token = requests.post(
    f"{BASE}/login",
    json={"username": username, "password": password},
).json()
print(token)
headers = {"Authorization": f"Bearer {token}"}

# 2) Start general export
payload = {
    "request": {
        "project_id": project_id,
        "split_by": "sample",
        "with_images": "none",
        "with_internal_ids": False,
        "with_types_row": True,
        "only_annotations": False,
        "out_to_ftp": False
    },
    "filters": {}
}

r = requests.post(
    f"{BASE}/object_set/export/general",
    headers=headers,
    json=payload,
)
r.raise_for_status()
job = r.json()
print(job)
output_filename = "job_237221.zip"

headers["accept"] = "application/json"

# 3) Poll job, then:
#file_response = requests.get(f"{BASE}/jobs/{job['job_id']}/file", headers=headers)
# Use stream=True to download the file in pieces
with requests.get(f"{BASE}/jobs/249011/file", headers=headers, stream=True) as response:
    response.raise_for_status()  # Throws an error if the download fails
    
    with open(output_filename, "wb") as file:
        # Read the file 8KB at a time
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)

print(f"File downloaded successfully as: {output_filename}")