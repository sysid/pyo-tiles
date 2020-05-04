import sys
from template import Template

if len(sys.argv) != 2:
    print(f"\n-E- Usage: ipy.py 'model.dill'")
    sys.exit(1)

m = PatientScheduling.load_result(sys.argv[1])
print(f"\n -M- model {sys.argv[1]} available in variable: m")
