import magic
from ifcb.data.identifiers import parse

print(magic.from_file("D20230729T032906_IFCB110.roi"))

print(magic.from_file("D20230729T032906_IFCB110.roi", mime=True))

resp = parse("23r4slfjmlsjfls")
print(resp)
