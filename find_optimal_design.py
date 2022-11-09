from openTorsion_converter import return_multi_component_assembly_from_list_of_urls
import dtweb
from pyld import jsonld
import numpy as np
import itertools
import random
import heapq

DTID_OF_DDT = "https://dtid.org/2ef85647-aee2-40c5-bb5a-380c9563ed16"
CATALOGUES = ["https://dtid.org/2d94ede9-eb21-4972-a142-141611ea922e"]

#twinschema
DTID = "https://twinschema.org/dt-id"

#ddt
ASSEMBLY_TEMPLATE = "https://ddt.twinschema.org/assemblyTemplate"
LIST_OF_ANALYSES = "https://ddt.twinschema.org/analysisRuns"
COMPONENTS = "https://ddt.twinschema.org/components"
COMPONENT_POSITION = "https://ddt.twinschema.org/position"
COMPONENT_REQUIREMENTS = "https://ddt.twinschema.org/requirements"
COMPONENT_REQUIREMENT_TYPE = "https://ddt.twinschema.org/requirementType"
REQUIREMENT = "https://ddt.twinschema.org/requirementValue"
LOWER_THAN = "https://ddt.twinschema.org/LowerThan"
LOWER_THAN_OR_EQUAL = "https://ddt.twinschema.org/LowerThanOrEqual"
EQUAL = "https://ddt.twinschema.org/Equal"
GREATER_THAN_OR_EQUAL = "https://ddt.twinschema.org/GreaterThanOrEqual"
GREATER_THAN = "https://ddt.twinschema.org/GreaterThan"

#tors:


def generate_assembly_instance(components_list): #components_list = list of urls of components included in the assembly. Index 0 = pos 0, index 1 = pos 1, ...
    return ", ".join(components_list) #+ " result: " + str(result)

def print_results(results_array):
    for idx in itertools.product(*[range(s) for s in results_array.shape]):
        print(idx, results_array[idx])

def analyze_assembly(assembly, analyses): #analyses = list of analyses defined in DDT
    return random.randint(1,100)

def find_suitable_components_from_catalogues(component_type, requirements, catalogue_urls): # component_type, requirements = component requirements part of the DDT document, catalogues = list of catalogue urls
    suitable_component_documents = []
    suitable_component_urls = []
    for catalogue_url in catalogue_urls:
        catalogue = dtweb.client.fetch_dt_doc(catalogue_url)
        expanded_catalogue = jsonld.expand(catalogue)
        components_in_catalogue = expanded_catalogue[0][COMPONENTS]
        for component in components_in_catalogue:
            component_dtid = component[DTID][0]["@value"]
            component_expanded_doc = jsonld.expand(dtweb.client.fetch_dt_doc(component_dtid))
            #Here check requirements
            if component_type in component_expanded_doc[0]["@type"]: #The component type matches to the searched type
                #Check other requirements
                print(component_expanded_doc)
                accept_component = True
                for requirement in requirements:
                    key = list(requirement[REQUIREMENT][0].keys())[0] #Extract key
                    required_value = requirement[REQUIREMENT][0][key][0]["@value"]#Extract value
                    condition = requirement["@type"][0] #Extract condition
                    try:
                        component_value = component_expanded_doc[0][key][0]["@value"]
                        print("Required_value: ", required_value)
                        print("Component_value: ", component_value)
                        if condition == LOWER_THAN:
                            if not component_value < required_value:
                                accept_component = False
                        elif condition == LOWER_THAN_OR_EQUAL:
                            if not component_value <= required_value:
                                accept_component = False
                        elif condition == EQUAL:
                            if not component_value == required_value:
                                accept_component = False
                        elif condition == GREATER_THAN_OR_EQUAL:
                            if not component_value >= required_value:
                                accept_component = False
                        elif condition == GREATER_THAN:
                            if not component_value > required_value:
                                accept_component = False
                        else:
                            #Unknown condition
                            accept_component = False                        
                    except:
                        #Key not find
                        pass
                
                if accept_component:
                    suitable_component_documents.append(component_expanded_doc)
                    suitable_component_urls.append(component_dtid)
                    print("component accepted", component_dtid)


        return suitable_component_documents, suitable_component_urls

def find_optimal_assemblies(dtid_of_DDT, catalogue_urls, number_of_optimal_solutions=1):
    # Read DDT and find components
    ddt = dtweb.client.fetch_dt_doc(dtid_of_DDT)
    expanded_ddt = jsonld.expand(ddt)
    
    components_unsorted = expanded_ddt[0][ASSEMBLY_TEMPLATE]
    components = sorted(components_unsorted, key = lambda component: component[COMPONENT_POSITION][0]['@value'], reverse=False)#Order components based on their position
    analyses = expanded_ddt[0][LIST_OF_ANALYSES]

    # Find possible components for each component position
    #TODO: Which list is best? The first option avoids looking component details twice from twinbase
    component_options = [] #Two-dimensional list, in which first index (i) corresponds to component position and the list in that index contains DT documents of suitable components
    component_options_urls = [] #Two-dimensional list, in which first index (i) corresponds to component position and the list in that index contains urls of suitable documents
    for i in range(len(components)):
        component_option_document, component_option_url = find_suitable_components_from_catalogues(components[i]["@type"][0], components[i][COMPONENT_REQUIREMENTS], catalogue_urls)
        component_options.append(component_option_document)
        component_options_urls.append(component_option_url)

    # Create very multidimensional array for looping through solutions
    shape = [len(suitable_components) for suitable_components in component_options_urls]
    results = np.zeros(shape) #Initialize results array. Value in place (i, j, k, ...) describes the solution score #TODO: how this will be defined
    for idx in itertools.product(*[range(s) for s in shape]):
        component_urls_for_assembly = []
        for i in range(len(component_options_urls)):
            component_urls_for_assembly.append(component_options_urls[i][idx[i]])
        print(component_urls_for_assembly)
        #Creating assembly from urls
        #assembly = return_multi_component_assembly_from_list_of_urls(component_urls_for_assembly)
        assembly = 1
        result = analyze_assembly(assembly, analyses)
        results[idx] = result

    print_results(results)
    best_solutions = [] #Format 
    indices =  np.argpartition(results.flatten(), -number_of_optimal_solutions)[-number_of_optimal_solutions:]
    print(np.vstack(np.unravel_index(indices, results.shape)).T)
    for index in np.vstack(np.unravel_index(indices, results.shape)).T:
        best_solutions.append( [generate_assembly_instance( [component_options_urls[i][index[i]] for i in range(len(index))] ), results[tuple(index)]] )

    best_solutions_sorted = sorted(best_solutions, key=lambda result: result[-1], reverse=True)
    print(best_solutions_sorted)



def main():
    find_optimal_assemblies(DTID_OF_DDT, CATALOGUES, number_of_optimal_solutions=3)

if __name__ == "__main__":
    main()