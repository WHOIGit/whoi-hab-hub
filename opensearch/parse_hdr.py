from hdr import parse_hdr_file

file_path = "D20230729T001110_IFCB110.hdr"

resp = parse_hdr_file(file_path)
latitude = resp.get("gpsLatitude", None)
longitude = resp.get("gpsLongitude", None)

if latitude and longitude:
    print(latitude, longitude)
    # run the Dynamo update
else:
    print("No lat/long")
