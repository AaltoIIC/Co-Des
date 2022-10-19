import dtweb
from pyld import jsonld
import json
import pprint
import yaml

# Define filename
file = 'twindocs/windmillComponent.yaml'

# Open DT document in YAML format
with open(file[:-5] + '.yaml', 'r') as yamlfile:
        yamldoc = yaml.load(yamlfile, Loader=yaml.FullLoader)

# Dump contents of YAML to JSON
with open(file[:-5] + '.json', 'w') as jsonfilew:
    json.dump(yamldoc, jsonfilew, indent=4)

# Open the newly generated JSON file, just for lulz
with open(file[:-5] + '.json', 'r') as jsonfiler:
    doc = json.load(jsonfiler)

print('\nDT document (directly from JSON to python dict):')
pprint.pprint(doc)

# print('\n\n')
# compacted = jsonld.compact(doc, doc)
# print('Compacted document:')
# pprint.pprint(compacted)

print('\n\n')
expanded = jsonld.expand(doc)
print('Expanded document (with PyLD):')
pprint.pprint(expanded)

# normalized = jsonld.normalize(
#     doc, {'algorithm': 'URDNA2015', 'format': 'application/n-quads'})
# print(normalized)

# Dump expanded document to JSON file
with open(file[:-5] + '-expanded.json', 'w') as jsonfilew:
        json.dump(expanded, jsonfilew, indent=4)

# Dump expanded document to YAML file
with open(file[:-5] + '-expanded.yaml', 'w') as filew:
    yaml.dump(expanded, filew, default_flow_style=False, sort_keys=False, allow_unicode=True)

