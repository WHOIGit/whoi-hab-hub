from hdr import parse_hdr_file

file_path = "D20230729T001110_IFCB110.hdr"

resp = parse_hdr_file(file_path)
print(resp)
