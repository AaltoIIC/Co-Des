from find_optimal_design_threaded_measurements import test_func
import dtweb
from pyld import jsonld


FILENAME = "measurements_test.csv"
NUMBER_OF_MEASUREMENTS = 1

DTID_OF_DDT = "https://dtid.org/2ef85647-aee2-40c5-bb5a-380c9563ed16"

USE_CATALOGUE = True

CATALOGUE_URL = "https://dtid.org/4802e224-b05d-45df-9b5e-35a8f23af79f"

LIST_OF_COMPONENT_CANDIDATES = ["https://dtid.org/e85c46f4-bdc2-4e0e-acd2-6b0ae582072d", 
                                "https://dtid.org/1febe1f0-16ff-4245-8fb2-759c93b01808", 
                                "https://dtid.org/19707b48-028a-49ef-abc1-778e68b6010f", 
                                "https://dtid.org/6ae3e218-2152-4635-a61a-696c6e0584e6", 
                                "https://dtid.org/977bf820-fc6a-49c8-8002-388f7beb1148"]


COMPONENTS = "https://ddt.twinschema.org/components"
DTID = 'https://twinschema.org/dt-id'

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
    
    # component_candidates_mid = component_candidates[::5]
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