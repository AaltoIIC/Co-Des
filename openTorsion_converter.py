import dtweb
from cmath import exp
from venv import create
from pyld import jsonld
from opentorsion.disk_element import Disk
from opentorsion.shaft_element import Shaft
from opentorsion.assembly import Assembly
import json

#How these should be fectched? Using some schema?
ELEMENTS = "https://tors.twinschema.org/elements"
DISK = "https://tors.twinschema.org/Disk"
DAMPING = "https://tors.twinschema.org/damping"
INCOORDINATE = "https://tors.twinschema.org/inCoordinate"
OUTCOORDINATE = "https://tors.twinschema.org/outCoordinate"
INERTIA = "https://tors.twinschema.org/inertia"
SHAFTDISCRETE = "https://tors.twinschema.org/ShaftDiscrete"
STIFFNESS = "https://tors.twinschema.org/stiffness"
LENGTH = "https://tors.twinschema.org/length" #TODO: update
OUTER_DIAMETER = "https://tors.twinschema.org/outerDiameter" #TODO: update
INNER_DIAMETER = "https://tors.twinschema.org/innerDiameter" #TODO: update

ASSEMBLY = "https://ddt.twinschema.org/assembly"
DTID = "https://twinschema.org/dt-id"
COMPONENT_POSITION = "https://ddt.twinschema.org/position"


def find_highest_out_coordinate(shafts, disks):
    highest_coordinate = 0
    for shaft in shafts:
        if shaft.nr > highest_coordinate:
            highest_coordinate = shaft.nr
    #Check from Sampo and Urho if this can be skipped
    for disk in disks:
        pass
    return highest_coordinate

#Translates one component into openTorsion model
def translate_to_open_torsion_model(expanded_doc, location=0): #location is added to all coordinates of components
    shafts, disks = [], []

    expanded_dict = expanded_doc[0]
    elements =  expanded_dict["https://tors.twinschema.org/elements"]
    for element in elements:
        if element["@type"] == [DISK]:
            disks.append(create_disk(element, location=location))
        elif element["@type"] == [SHAFTDISCRETE]:
            shafts.append(create_shaft_discrete(element, location=location))
        else:
            print("Element type not recognized, ignoring element...")

    return shafts, disks


def create_disk(element, location=0):
    disk = Disk(int(element[INCOORDINATE][0]['@value']) + location, float(element[INERTIA][0]['@value']), element[DAMPING][0]['@value']) #Disk(node, inertia, c=0) 
    print("Disk: ", int(element[INCOORDINATE][0]['@value']) + location, float(element[INERTIA][0]['@value']), element[DAMPING][0]['@value'])
    #print(disk)
    return disk

def create_shaft_discrete(element, location=0):
    #stiffness = float(element[STIFFNESS][0]['@value'])
    #print("Shaft", int(element[INCOORDINATE][0]['@value']), int(element[OUTCOORDINATE][0]['@value']), None, None, stiffness, float(element[INERTIA][0]['@value']), float(element[DAMPING][0]['@value']))
    try:
        inertia = float(element[INERTIA][0]['@value'])
    except:
        inertia = 0

    try:
        damping = float(element[DAMPING][0]['@value'])
    except:
        damping = 0


    try:
        stiffness = float(element[STIFFNESS][0]['@value'])
        shaft = Shaft(int(element[INCOORDINATE][0]['@value'])  + location, int(element[OUTCOORDINATE][0]['@value'])  + location, None, None, k=stiffness, I=inertia, c=damping) #inCoordinate, outCoordinate, L, odl, idl=0, G=80e9, E=200e9, rho=8000, k=None, I=0.0, c=0.0
        print("Shaft with stiffness", int(element[INCOORDINATE][0]['@value']) + location, int(element[OUTCOORDINATE][0]['@value'])  + location, None, None, stiffness, inertia, damping)
    except:
        #Stiffness does not exist. Using outer diameter, length, and optionally inner diameter for shaft calculations
        outer_diameter = element[OUTER_DIAMETER][0]['@value']
        length = element[LENGTH][0]['@value']
        try:
            inner_diameter = element[INNER_DIAMETER][0]['@value']
        except:
            #Inner diameter is not defined
            inner_diameter = None
        shaft = Shaft(int(element[INCOORDINATE][0]['@value']) + location, int(element[OUTCOORDINATE][0]['@value']) + location, length, outer_diameter, idl=inner_diameter, I=inertia, c=damping) #inCoordinate, outCoordinate, L, odl, idl=0, G=80e9, E=200e9, rho=8000, k=None, I=0.0, c=0.0
        print("Shaft with diameter", int(element[INCOORDINATE][0]['@value']) + location, int(element[OUTCOORDINATE][0]['@value'])  + location, length, outer_diameter, inner_diameter, inertia, damping)
    return shaft

def analysis(assembly):
    print("Some basic analysis could be defined here")

#Read doc from twinbase and expand it
def read_and_expand(dtid):
    #Read dt doc from Twinbase
    dict_file = dtweb.client.fetch_dt_doc(dtid)
    #Expand dt doc and return
    return jsonld.expand(dict_file)

def return_component_assembly_from_url(dtid):
    expanded_doc = read_and_expand(dtid)
    shafts, disks = translate_to_open_torsion_model(expanded_doc)
    return Assembly(shafts, disk_elements=disks)

def return_component_assembly_from_json_file(filename):
    with open(filename, 'r') as jsonfile:
        doc = json.load(jsonfile)
    expanded_doc = jsonld.expand(doc)
    shafts, disks = translate_to_open_torsion_model(expanded_doc)
    return Assembly(shafts, disk_elements=disks)

def return_components_from_url(dtid, location=0):
    expanded_doc = read_and_expand(dtid)
    shafts, disks = translate_to_open_torsion_model(expanded_doc, location=location)
    return shafts, disks

def return_components_from_json_file(filename, location=0):
    with open(filename, 'r') as jsonfile:
        doc = json.load(jsonfile)
    expanded_doc = jsonld.expand(doc)
    shafts, disks = translate_to_open_torsion_model(expanded_doc, location=location)
    return shafts, disks

def return_multi_component_assembly_from_url(dtid):
    expanded_doc = read_and_expand(dtid)
    components_unsorted = expanded_doc[0][ASSEMBLY]
    components = sorted(components_unsorted, key = lambda component: component[COMPONENT_POSITION][0]['@value'], reverse=True)


    shafts, disks = [], []
    highest_out_coordinate = 0 #current highest coordinate
    #For each component in component list, get nodes (i.e. shafts and disks)
    for component in components:
        component_url = component[DTID][0]['@value']
        shafts_new, disks_new = return_components_from_url(component_url, location=highest_out_coordinate)
        highest_out_coordinate = find_highest_out_coordinate(shafts_new, disks_new)
        shafts = shafts + shafts_new
        disks = disks + disks_new

    return Assembly(shafts, disk_elements=disks)

def return_multi_component_assembly_from_json_file(filename):
    with open(filename, 'r') as jsonfile:
        doc = json.load(jsonfile)
    expanded_doc = jsonld.expand(doc)
    components_unsorted = expanded_doc[0][ASSEMBLY]
    components = sorted(components_unsorted, key = lambda component: component[COMPONENT_POSITION][0]['@value'])


    shafts, disks = [], []
    highest_out_coordinate = 0 #current highest coordinate
    #For each component in component list, get nodes (i.e. shafts and disks)
    for component in components:
        component_url = component[DTID][0]['@value']
        shafts_new, disks_new = return_components_from_url(component_url, location=highest_out_coordinate)
        highest_out_coordinate = find_highest_out_coordinate(shafts_new, disks_new)
        shafts = shafts + shafts_new
        disks = disks + disks_new

    return Assembly(shafts, disk_elements=disks)

def return_multi_component_assembly_from_json_file_all_local(file):
    expanded_doc = jsonld.expand(file)
    components_unsorted = expanded_doc[0][ASSEMBLY]
    components = sorted(components_unsorted, key = lambda component: component[COMPONENT_POSITION][0]['@value'])


    shafts, disks = [], []
    highest_out_coordinate = 0 #current highest coordinate
    #For each component in component list, get nodes (i.e. shafts and disks)
    for component in components:
        component_url = component[DTID][0]['@value']
        shafts_new, disks_new = return_components_from_json_file(component_url, location=highest_out_coordinate)
        highest_out_coordinate = find_highest_out_coordinate(shafts_new, disks_new)
        shafts = shafts + shafts_new
        disks = disks + disks_new

    return Assembly(shafts, disk_elements=disks)
    


def main():
    #Test single component
    #dtid_model = "https://dtid.org/e09a43fa-fea6-41e7-907b-3fb5a0d17371"
    #assembly = return_component_assembly_from_url(dtid_model)
    #analysis(assembly)

    #Test assembly
    """
    dtid_multicomponent_model = "https://dtid.org/890f7d85-626e-4e05-960e-9d1bc7af32fd"
    assembly_multicomponent = return_multi_component_assembly_from_url(dtid_multicomponent_model)
    analysis(assembly_multicomponent)
    """

    #For local testing of assembly file (components are read from Twinbase)
    file_name = "twindocs/assemblyInstance.json"
    assembly_multicomponent = return_multi_component_assembly_from_json_file(file_name)
    analysis(assembly_multicomponent)

if __name__ == "__main__":
    main()