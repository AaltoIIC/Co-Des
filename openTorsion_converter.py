import dtweb
from cmath import exp
from venv import create
from pyld import jsonld
from opentorsion.disk_element import Disk
from opentorsion.shaft_element import Shaft
from opentorsion.assembly import Assembly

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


def find_highest_out_coordinate(expanded_doc):
    pass


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
    print("Some basic analysis could be defined here")

def return_assembly_from_url(dtid):
    #Read dt doc from Twinbase
    dict_file = dtweb.client.fetch_dt_doc(dtid)
    #Expand dt doc
    expanded_doc = jsonld.expand(dict_file)
    #Create assembly using the doc
    return translate_to_open_torsion_model(expanded_doc)

def main():
    dtid_model = "https://dtid.org/e09a43fa-fea6-41e7-907b-3fb5a0d17371"
    #Read dt doc from Twinbase
    assembly = return_assembly_from_url(dtid_model)
    analysis(assembly)

if __name__ == "__main__":
    main()