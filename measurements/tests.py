from find_optimal_design_threaded_measurements import test_func
import dtweb
from pyld import jsonld


FILENAME = "measurementstest.csv"
NUMBER_OF_MEASUREMENTS = 1



COMPONENTS = "https://ddt.twinschema.org/components"
DTID = 'https://twinschema.org/dt-id'


DTID_OF_DDT = "https://dtid.org/2ef85647-aee2-40c5-bb5a-380c9563ed16"


CATALOGUE_URL = "https://dtid.org/4802e224-b05d-45df-9b5e-35a8f23af79f"

USE_CATALOGUE = True

LIST_OF_COMPONENT_CANDIDATES = ["https://dtid.org/e85c46f4-bdc2-4e0e-acd2-6b0ae582072d", 
                                "https://dtid.org/1febe1f0-16ff-4245-8fb2-759c93b01808", 
                                "https://dtid.org/efa0d72f-994d-4ad4-9f16-f1565371a18d", 
                                "https://dtid.org/6ae3e218-2152-4635-a61a-696c6e0584e6", 
                                "https://dtid.org/977bf820-fc6a-49c8-8002-388f7beb1148"]

def read_dt_ids_from_catalog(catalogue_url):
    catalogue = dtweb.client.fetch_dt_doc(catalogue_url)
    expanded_catalogue = jsonld.expand(catalogue)
    components_in_catalogue = expanded_catalogue[0][COMPONENTS]
    return components_in_catalogue                       

def main():
    if USE_CATALOGUE:
        component_candidates_raw = read_dt_ids_from_catalog(CATALOGUE_URL)
        component_candidates = list(map(lambda x: x[DTID][0]["@value"], component_candidates_raw))
    else:
       component_candidates = LIST_OF_COMPONENT_CANDIDATES
    
    # component_candidates_mid = component_candidates[40:]
    # component_candidates_mid.append(component_candidates[0])
    # component_candidates_mid.append(component_candidates[20])
    # component_candidates = component_candidates_mid
    print("Component candidates")
    print(component_candidates)
    print("----------------------")
    with open(FILENAME, "w") as f:
        f.write("ReadDDT,FindSuitableComponents,AnalyzingAssemblies,TotalTime\n")
    for _ in range(NUMBER_OF_MEASUREMENTS):
        test_func(DTID_OF_DDT, component_candidates, FILENAME)

if __name__ == "__main__":
    main()


{'@type': ['https://ddt.twinschema.org/Component', 'https://tors.twinschema.org/Rotor'], 'https://twinschema.org/baseurl': [{'@value': 'https://juusoautiosalo.github.io/dev-twinbase-ddt'}], 'https://twinschema.org/description': [{'@value': 'A rotor component for a windmill to be used to construct a torsional vibration analysis via a digital design template.'}], 'https://twinschema.org/dt-id': [{'@value': 'https://dtid.org/c8060ee0-8abe-4a25-a3b3-7f90ea55d616'}], 'https://twinschema.org/edit': [{'@value': 'https://github.com/juusoautiosalo/dev-twinbase-ddt/edit/main/docs/c8060ee0-8abe-4a25-a3b3-7f90ea55d616/index.yaml'}], 'https://twinschema.org/edit-json': [{'@value': 'https://github.com/juusoautiosalo/dev-twinbase-ddt/edit/main/docs/c8060ee0-8abe-4a25-a3b3-7f90ea55d616/index.json'}], 'https://twinschema.org/hosting-iri': [{'@value': 'https://juusoautiosalo.github.io/dev-twinbase-ddt/c8060ee0-8abe-4a25-a3b3-7f90ea55d616'}], 'https://twinschema.org/name': [{'@value': 'Windmill rotor 400000 exc 4.71e+03'}], 'https://tors.twinschema.org/elements': [{'@type': ['https://tors.twinschema.org/Disk'], 'http://www.w3.org/2000/01/rdf-schema#comment': [{'@language': 'en', '@value': 'Rotor inner part'}], 'https://tors.twinschema.org/damping': [{'@value': 1}], 'https://tors.twinschema.org/inCoordinate': [{'@value': 0}], 'https://tors.twinschema.org/inertia': [{'@value': '4.71e+03'}]}, {'@type': ['https://tors.twinschema.org/ShaftDiscrete'], 'http://www.w3.org/2000/01/rdf-schema#comment': [{'@language': 'en', '@value': 'Spring that connects inner and outer parts of rotor'}], 'https://tors.twinschema.org/damping': [{'@value': 0}], 'https://tors.twinschema.org/inCoordinate': [{'@value': 0}], 'https://tors.twinschema.org/outCoordinate': [{'@value': 1}], 'https://tors.twinschema.org/stiffness': [{'@value': '5.64e+09'}]}, {'@type': ['https://tors.twinschema.org/Disk'], 'http://www.w3.org/2000/01/rdf-schema#comment': [{'@language': 'en', '@value': 'Rotor outer part'}], 'https://tors.twinschema.org/damping': [{'@value': 0}], 'https://tors.twinschema.org/inCoordinate': [{'@value': 1}], 'https://tors.twinschema.org/inertia': [{'@value': '7.52e+04'}]}], 'https://tors.twinschema.org/power': [{'@value': 400000}], 'https://tors.twinschema.org/properties': [{'@type': ['https://tors.twinschema.org/Excitation'], 'http://www.w3.org/2000/01/rdf-schema#comment': [{'@language': 'en', '@value': 'Definition of excitations caused by this component. The excitation values are defined in tors:excitationValuesRpmPercentage as list of two-item lists that contain 1) the RPM multiple and 2) the value of excitation in percentages.'}], 'https://tors.twinschema.org/excitationValuesRpmPercentage': [{'@value': 4}, {'@value': 0.002068}, {'@value': 6}, {'@value': 0.0189}, {'@value': 8}, {'@value': 0.00174}, {'@value': 10}, {'@value': 0.004166}, {'@value': 12}, {'@value': 0.01605}, {'@value': 14}, {'@value': 0.002008}, {'@value': 16}, {'@value': 0.0008396}], 'https://tors.twinschema.org/inCoordinate': [{'@value': 1}]}]}
