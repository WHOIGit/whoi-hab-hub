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
        "split_by": "none",
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
headers["accept"] = "application/json"
print(headers)
# 3) Poll job, then:
#file_response = requests.get(f"{BASE}/jobs/{job['job_id']}/file", headers=headers)
file_response = requests.get(f"{BASE}/jobs/249011/file", headers=headers)
print(file_response.url)
data = file_response.json()
print(data)
#open("ecotaxa_export.zip", "wb").write(file_response.content)