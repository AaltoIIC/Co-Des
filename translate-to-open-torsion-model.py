#import dtweb
from cmath import exp
from venv import create
from pyld import jsonld
import json
import pprint
import yaml
from opentorsion.disk_element import Disk
from opentorsion.shaft_element import Shaft
from opentorsion.assembly import Assembly


FILENAME = "twindocs/windmillComponent.yaml"

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



def get_file_in_dict(filename):
    if filename[-5:] == '.yaml':
        with open(filename, 'r') as yamlfile:
            doc = yaml.load(yamlfile, Loader=yaml.FullLoader)

    elif filename[-5:]== '.json':
        with open(filename, 'r') as jsonfiler:
            doc = json.load(jsonfiler)

    else:
        raise Exception("File format not supported. The supported formats are YAML and JSON.")

    return doc

def translate_to_open_torsion_model(expanded_doc):
    shafts, disks = [], []

    expanded_dict = expanded_doc[0]
    elements =  expanded_dict["https://tors.twinschema.org/elements"]
    for element in elements:
        if element["@type"] == [DISK]:
            disks.append(create_disk(element))
        elif element["@type"] == [SHAFTDISCRETE]:
            shafts.append(create_shaft_discrete(element))
        else:
            print("Element type not recognized, ignoring element...")

    return Assembly(shafts, disk_elements=disks)


def create_disk(element):
    disk = Disk(int(element[INCOORDINATE][0]['@value']), float(element[INERTIA][0]['@value']), element[DAMPING][0]['@value']) #Disk(node, inertia, c=0) 
    print("Disk: ", int(element[INCOORDINATE][0]['@value']), float(element[INERTIA][0]['@value']), element[DAMPING][0]['@value'])
    #print(disk)
    return disk

def create_shaft_discrete(element):
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
        print("Shaft", int(element[INCOORDINATE][0]['@value']), int(element[OUTCOORDINATE][0]['@value']), None, None, stiffness, inertia, damping)
        shaft = Shaft(int(element[INCOORDINATE][0]['@value']), int(element[OUTCOORDINATE][0]['@value']), None, None, k=stiffness, I=inertia, c=damping) #inCoordinate, outCoordinate, L, odl, idl=0, G=80e9, E=200e9, rho=8000, k=None, I=0.0, c=0.0

    except:
        #Stiffness does not exist. Using outer diameter, length, and optionally inner diameter for shaft calculations
        outer_diameter = element[OUTER_DIAMETER][0]['@value']
        length = element[LENGTH][0]['@value']
        try:
            inner_diameter = element[INNER_DIAMETER][0]['@value']
        except:
            #Inner diameter is not defined
            inner_diameter = None
        shaft = Shaft(int(element[INCOORDINATE][0]['@value']), int(element[OUTCOORDINATE][0]['@value']), length, outer_diameter, idl=inner_diameter, I=inertia, c=damping) #inCoordinate, outCoordinate, L, odl, idl=0, G=80e9, E=200e9, rho=8000, k=None, I=0.0, c=0.0
    
    return shaft

def analysis(assembly):
    from opentorsion.plots import Plots
    #Copied from openTorsion examples
    ## Calculation of the eigenfrequencies of the powertrain
    omegas_damped, eigenfrequencies, damping_ratios = assembly.modal_analysis()

    ## Print eigenfrequencies.
    ## The list contains each eigenfrequency twice: e.g. eigenfrequencies = [1st, 1st, 2nd, 2nd, 3rd, 3rd, ...]
    print("Eigenfrequencies: ", eigenfrequencies.round(3))

    ## Initiate plotting tools calling Plots(assembly)
    plot_tools = Plots(assembly)

    ## Plot eigenmodes, input number of eigenmodes
    plot_tools.figure_eigenmodes(modes=3)
    plot_tools.campbell_diagram()


def main():
    dict_file = get_file_in_dict(FILENAME)
    #print(dict_file)
    expanded_doc = jsonld.expand(dict_file) #<-- Why everything is a list?
    #print('Expanded document (with PyLD):')

    #pprint.pprint(expanded_doc)
    assembly = translate_to_open_torsion_model(expanded_doc)
    
    #Analyze model
    analysis(assembly)


if __name__ == "__main__":
    main()