from openTorsion_converter import return_multi_component_assembly_from_list_of_urls
from forced_response import forced_response
import dtweb
from pyld import jsonld
import numpy as np
import itertools
import random
import heapq
import pprint

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
COMPONENT_TYPE = "https://ddt.twinschema.org/componentType"
WINDMILL_FORCED_RESPONSE_ANALYSIS = "https://tors.twinschema.org/TorqueAmplitudeAnalysis"

#tors:

def generate_assembly_instance(components_list): #components_list = list of urls of components included in the assembly. Index 0 = pos 0, index 1 = pos 1, ...
    return ", ".join(components_list) #+ " result: " + str(result)

def print_results(results_array):
    for idx in itertools.product(*[range(s) for s in results_array.shape]):
        print(idx, results_array[idx])

def analyze_assembly(assembly, analyses): #analyses = list of analyses defined in DDT
    return random.randint(1, 100)
    print('\nSTARTING ANALYSIS')
    # print("analyses:")
    # pprint.pprint(analyses)
    analysis_results = []
    for analysis in analyses:
        # print('Analysis type:', WINDMILL_FORCED_RESPONSE_ANALYSIS)
        # print('Analysis type:', analysis['@type'])
        if WINDMILL_FORCED_RESPONSE_ANALYSIS in analysis['@type']:
            print('\nFound windmill analysis!\n')
            rpm_linspace = np.linspace(0.1, 25, 5000)

            max_amplitude = forced_response(assembly, rpm_linspace)
            print('\nMax amplitude:', max_amplitude)
            # analysis_results.append({analysis: {'max_amplitude': max_amplitude}})
            analysis_results.append(max_amplitude)
        else:
            print('\nDid not find windmill analysis.\n')


    # return analysis_results[0][WINDMILL_FORCED_RESPONSE_ANALYSIS][max_amplitude]
    return analysis_results[0]

def find_suitable_components_from_catalogues(component_type, requirements, catalogue_urls): # component_type, requirements = component requirements part of the DDT document, catalogues = list of catalogue urls
    suitable_component_documents = []
    suitable_component_urls = []
    #print(component_type)
    for catalogue_url in catalogue_urls:
        catalogue = dtweb.client.fetch_dt_doc(catalogue_url)
        expanded_catalogue = jsonld.expand(catalogue)
        components_in_catalogue = expanded_catalogue[0][COMPONENTS]
        for component in components_in_catalogue:
            component_dtid = component[DTID][0]["@value"]
            component_expanded_doc = jsonld.expand(dtweb.client.fetch_dt_doc(component_dtid))
            #Here check requirements
            #if component_expanded_doc[0][]
            suitable_component_documents.append(component_expanded_doc)
            suitable_component_urls.append(component_dtid)
            #print(component_expanded_doc)
            #print()

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
        component_option_document, component_option_url = find_suitable_components_from_catalogues(components[i]['@type'], components[i][COMPONENT_REQUIREMENTS], catalogue_urls)
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
        assembly = return_multi_component_assembly_from_list_of_urls(component_urls_for_assembly)
        # assembly = 1
        result = analyze_assembly(assembly, analyses)
        results[idx] = result

    print_results(results)
    best_solutions = [] #Format 
    indices =  np.argpartition(results.flatten(), -number_of_optimal_solutions)[-number_of_optimal_solutions:]
    print(np.vstack(np.unravel_index(indices, results.shape)).T)
    for index in np.vstack(np.unravel_index(indices, results.shape)).T:
        best_solutions.append( [generate_assembly_instance( [component_options_urls[i][index[i]] for i in range(len(index))] ), results[tuple(index)]] )

    best_solutions_sorted = sorted(best_solutions, key=lambda result: result[-1], reverse=True)
    print(best_solutions)
    print(best_solutions_sorted)



def main():
    find_optimal_assemblies(DTID_OF_DDT, CATALOGUES, number_of_optimal_solutions=3)

if __name__ == "__main__":
    main()