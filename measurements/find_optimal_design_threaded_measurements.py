from openapi_parser import parse, enumeration
import dtweb
from pyld import jsonld
import numpy as np
import itertools
import gc
import time
import threading
import requests
from queue import Queue

# For testing
gc.disable()


MAX_CONNECTIONS = 24
DTID_OF_DDT = "https://dtid.org/2ef85647-aee2-40c5-bb5a-380c9563ed16"
#LIST_OF_COMPONENT_CANDIDATES = ["https://dtid.org/e85c46f4-bdc2-4e0e-acd2-6b0ae582072d", "https://dtid.org/1febe1f0-16ff-4245-8fb2-759c93b01808", "https://dtid.org/efa0d72f-994d-4ad4-9f16-f1565371a18d"] #Turbine, shaft, rotor
LIST_OF_COMPONENT_CANDIDATES = ["https://dtid.org/e85c46f4-bdc2-4e0e-acd2-6b0ae582072d", "https://dtid.org/1febe1f0-16ff-4245-8fb2-759c93b01808", "https://dtid.org/efa0d72f-994d-4ad4-9f16-f1565371a18d", "https://dtid.org/6ae3e218-2152-4635-a61a-696c6e0584e6", "https://dtid.org/977bf820-fc6a-49c8-8002-388f7beb1148"]

#twinschema
DTID = "https://twinschema.org/dt-id"
API_DEFFINITIONS = "https://twinschema.org/apiDefinitions"
OPEN_API_DEFINITION = "https://twinschema.org/OpenAPIDefinition"
API_DOCUMENT_URL = "https://twinschema.org/apiDocumentUrl"
JSON_FORMAT = "https://twinschema.org/json"
YAML_FORMAT = "https://twinschema.org/yaml"
NAME = "https://twinschema.org/name"

#ddt
ASSEMBLY_TEMPLATE = "https://ddt.twinschema.org/assemblyTemplate"
LIST_OF_ANALYSES = "https://ddt.twinschema.org/analysisRuns"
COMPONENTS = "https://ddt.twinschema.org/components"
COMPONENT_POSITION = "https://ddt.twinschema.org/position"
COMPONENT_REQUIREMENTS = "https://ddt.twinschema.org/requirements"
COMPONENT_REQUIREMENT_TYPE = "https://ddt.twinschema.org/requirementType"
COMPONENT_TYPE = "https://ddt.twinschema.org/componentType"
REQUIREMENT_VALUE = "https://ddt.twinschema.org/requirementValue"
LOWER_THAN = "https://ddt.twinschema.org/LowerThan"
LOWER_THAN_OR_EQUAL = "https://ddt.twinschema.org/LowerThanOrEqual"
EQUAL = "https://ddt.twinschema.org/Equal"
GREATER_THAN_OR_EQUAL = "https://ddt.twinschema.org/GreaterThanOrEqual"
GREATER_THAN = "https://ddt.twinschema.org/GreaterThan"
SUITABLE_SERVICES = "https://ddt.twinschema.org/suitableAnalysisServices"

#tors:
LINSPACE_START = "https://tors.twinschema.org/startLinspace"
LINSPACE_STOP = "https://tors.twinschema.org/stopLinspace"
LINSPACE_NUM = "https://tors.twinschema.org/numLinspace"
ANALYSIS_PARAMETERS = "https://ddt.twinschema.org/analysisParameters"
TORQUE_ANALYSIS = "https://tors.twinschema.org/TorqueAmplitudeAnalysis"
RPM_LINSPACE_PARAMS = "https://tors.twinschema.org/rpmLinspace"

class AnalysisResults:
    def __init__(self, component_urls, analysis_results): #List of component urls forming assembly, dict of analysis results. Key = analysis name, value = analysis result
        self.component_urls = component_urls
        self.analysis_results = analysis_results
    
    def __str__(self) -> str:
        if len(self.component_urls) > 1:
            return ", ".join(self.component_urls) + " " + str(self.analysis_results)
        else:
            return str(self.component_urls[0]) + str(self.analysis_results)


def generate_assembly_instance(components_list): #components_list = list of urls of components included in the assembly. Index 0 = pos 0, index 1 = pos 1, ...
    return ", ".join(components_list) #+ " result: " + str(result)

def print_results(results_array, shape):
    for idx in itertools.product(*[range(s) for s in shape]):
        index = np.ravel_multi_index(idx, shape)
        print(idx, index, results_array[index])

def torque_analysis(analysis, component_urls_for_assembly, analysis_results):
        #print('\nFound torque analysis!\n')
        #Select first analysis service
        analysis_service_dtid = analysis[SUITABLE_SERVICES][0][DTID][0]["@value"]
        ddt = dtweb.client.fetch_dt_doc(analysis_service_dtid)
        expanded_service_ddt = jsonld.expand(ddt)
        if expanded_service_ddt[0][API_DEFFINITIONS][0]["@type"][0] == OPEN_API_DEFINITION:
            open_api_spec_yaml_url = expanded_service_ddt[0][API_DEFFINITIONS][0][API_DOCUMENT_URL][0][YAML_FORMAT][0]["@value"]
            spec = parse(open_api_spec_yaml_url)
            #Select first path and POST method
            for operation in spec.paths[0].operations:
                if operation.method == enumeration.OperationMethod.POST:
                    #Extract necessary data from DDT and create dict
                    ddt_data = {}
                    
                    #Extract linspace params
                    parameters = analysis[ANALYSIS_PARAMETERS][0] #Dict of analysis parameters
                    rpm_parameters = parameters[RPM_LINSPACE_PARAMS][0]
                    rpm_linspace_dict = {}
                    rpm_linspace_dict["start"] = rpm_parameters[LINSPACE_START][0]["@value"]
                    rpm_linspace_dict["stop"] = rpm_parameters[LINSPACE_STOP][0]["@value"]
                    rpm_linspace_dict["num"] = rpm_parameters[LINSPACE_NUM][0]["@value"]

                    #Add data to ddt data dict
                    ddt_data["linspace"] = rpm_linspace_dict
                    ddt_data["assembly_urls"] = component_urls_for_assembly

                    #Parsing Open API spec

                    #Select first server
                    server = spec.servers[0]
                    #Path
                    path = spec.paths[0]

                    #Content type
                    content_type = operation.request_body.content[0].type.value
                    headers = {"Content-type": content_type}

                    #Forming request
                    request_data = {}
                    properties = operation.request_body.content[0].schema.properties
                    for prop in properties:
                        if ddt_data[prop.name]:
                            request_data[prop.name] = ddt_data[prop.name]
                    response = requests.post(server.url + path.url, json=request_data, headers=headers)
                    max_amplitude = response.json()["max_amplitude"]
                    break
        name = expanded_service_ddt[0][NAME][0]["@value"]
        analysis_results[name] = max_amplitude

def analyze_assembly(component_urls_for_assembly, analyses, results, task_queue, semaphore): #analyses = list of analyses defined in DDT
    #print('\nSTARTING ANALYSIS')
    semaphore.acquire()
    task = task_queue.get()
    
    analysis_results = {}
    threads = []
    for analysis in analyses:
        if TORQUE_ANALYSIS in analysis["@type"]:
            t = threading.Thread(target=torque_analysis, args=(analysis, component_urls_for_assembly, analysis_results,))
            threads.append(t)
            t.start() 
        #TODO: add more analyses 
    for t in threads:
        t.join()

    task_queue.task_done()
    semaphore.release()

    results.append(AnalysisResults(component_urls_for_assembly, analysis_results))

def check_requirements(component_type, requirements, component_dtid, suitable_component_urls):
    component_expanded_doc = jsonld.expand(dtweb.client.fetch_dt_doc(component_dtid))
    #Here check requirements
    if component_type in component_expanded_doc[0]["@type"]: #The component type matches to the searched type
        #Check other requirements
        #print(component_expanded_doc)
        accept_component = True
        for requirement in requirements:
            try:
                key = list(requirement[REQUIREMENT_VALUE][0].keys())[0] #Extract key
                required_value = requirement[REQUIREMENT_VALUE][0][key][0]["@value"]#Extract value
                condition = requirement["@type"][0] #Extract condition
                try:
                    component_value = component_expanded_doc[0][key][0]["@value"]
                    #print("Required_value: ", required_value)
                    #print("Component_value: ", component_value)
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
            except:
                #TODO: accept also other requirements than numeric values. Example: MustBeDefined
                pass
        
        if accept_component:
            suitable_component_urls.append(component_dtid)
            #print("component accepted", component_dtid)

def find_suitable_components_from_list_of_urls(component_type, requirements, list_of_component_dtids): # component_type, requirements = component requirements part of the DDT document
    suitable_component_urls = []
    threads = []
    for component_dtid in list_of_component_dtids:
        t = threading.Thread(target=check_requirements, args=(component_type, requirements, component_dtid, suitable_component_urls,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    return suitable_component_urls    

def find_optimal_assemblies(dtid_of_DDT, component_candidates, execution_times):
    # Read DDT and find components
    read_counter_ns = time.monotonic_ns()

    ddt = dtweb.client.fetch_dt_doc(dtid_of_DDT)
    expanded_ddt = jsonld.expand(ddt)
    components_unsorted = expanded_ddt[0][ASSEMBLY_TEMPLATE]
    components = sorted(components_unsorted, key = lambda component: component[COMPONENT_POSITION][0]['@value'], reverse=False)#Order components based on their position
    analyses = expanded_ddt[0][LIST_OF_ANALYSES]

    timer_ns = time.monotonic_ns() - read_counter_ns
    execution_times.append(timer_ns)
    print("Read DDT", timer_ns/10**9)

    # Find possible components for each component position
    find_counter_ns = time.monotonic_ns()
    component_options_urls = [] #Two-dimensional list, in which first index (i) corresponds to component position and the list in that index contains urls of suitable documents
    for i in range(len(components)):
        component_option_url = find_suitable_components_from_list_of_urls(components[i]["@type"][0], components[i][COMPONENT_REQUIREMENTS], component_candidates)
        component_options_urls.append(component_option_url)

    timer_ns = time.monotonic_ns() - find_counter_ns
    execution_times.append(timer_ns)
    print("Time to search components", timer_ns/10**9)

    # Create very multidimensional array for looping through solutions
    analysis_counter_ns = time.monotonic_ns()
    shape = [len(suitable_components) for suitable_components in component_options_urls]
    results = [] #Initialize results array. Index is the assembly candidate and value is AnalysisResults object.
    threads = []

    #For limiting concurrent requests
    task_queue = Queue()
    semaphore = threading.Semaphore(MAX_CONNECTIONS)

    for idx in itertools.product(*[range(s) for s in shape]):
        #Collect component urls for assembly
        component_urls_for_assembly = []
        for i in range(len(component_options_urls)):
            component_urls_for_assembly.append(component_options_urls[i][idx[i]])
        #print(component_urls_for_assembly)

        #Send the system consisting of components for analysis
        t = threading.Thread(target=analyze_assembly, args=(component_urls_for_assembly, analyses, results, task_queue, semaphore,))
        threads.append(t)
        t.start()
        task_queue.put("task")

    task_queue.join()

    timer_ns = time.monotonic_ns() - analysis_counter_ns
    execution_times.append(timer_ns)
    print("Time to analyze assemblies", timer_ns/10**9)

    results_sorted = sorted(results, key=lambda x: x.analysis_results["Analysis service for torsional vibration"])
    print_results(results, shape)
    print("Three best solutions")
    for result_object in results_sorted[:3]:
        print(result_object)


def test_func(dtid_of_ddt, list_of_component_candidates, filename):
    execution_times = [] #Order: Read DDT, Find Suitable Components,Analyzing Assemblies, Total Time
    start_counter_ns = time.monotonic_ns()
    find_optimal_assemblies(dtid_of_ddt, list_of_component_candidates, execution_times)
    end_counter_ns = time.monotonic_ns()
    timer_ns = end_counter_ns - start_counter_ns
    with open(filename, "a") as f:
        for value in execution_times:
            f.write(f"{value/10**9:.3f},")
        f.write(f"{timer_ns/10**9:.3f}\n")



if __name__ == "__main__":
    filename = "measurements_test_main.csv"
    test_func(DTID_OF_DDT, LIST_OF_COMPONENT_CANDIDATES, filename)

# For testing
gc.enable()