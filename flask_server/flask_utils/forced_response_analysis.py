"""
This script was copied from openTorsion:
https://github.com/Aalto-Arotor/openTorsion/blob/26b91ee9d0a6c5c3e5c99c3b56f8235213730288/opentorsion/examples/forced_response.py

The script has been modified for the use case by R. Ala-Laurinaho, S. Laine, and J. Autiosalo.

License:
https://github.com/Aalto-Arotor/openTorsion/blob/26b91ee9d0a6c5c3e5c99c3b56f8235213730288/LICENSE
"""

import numpy as np
import scipy.linalg as LA

from opentorsion.shaft_element import Shaft
from opentorsion.disk_element import Disk
from opentorsion.gear_element import Gear
from opentorsion.assembly import Assembly
from opentorsion.excitation import SystemExcitation
from opentorsion.plots import Plots
from flask_utils.openTorsion_converter import return_multi_component_assembly_and_excitation_from_list_of_urls
import time

"""
Forced response analysis based on https://doi.org/10.1109/TIE.2010.2087301.
"""


def generator_torque(rpm):
    """
    Generator torque as a function of rotor rotating speed.
    """
    rated_T = 2.9e6

    if rpm < 4:
        torque = 0

    elif rpm < 15:
        m = (0.5 - 0.125) / (15 - 4) * rated_T
        b = 0.5 * rated_T - m * 15

        torque = m * rpm + b

    elif rpm < 22:
        P = rated_T * 15

        torque = P / rpm

    else:
        torque = 0

    return torque


def get_windmill_excitation(rpm):
    """
    Cogging torque and torque ripple as harmonic excitation.
    (Table III from https://doi.org/10.1109/TIE.2010.2087301)
    """
    f_s = rpm
    vs = np.array([4, 6, 8, 10, 12, 14, 16])
    omegas = 2 * np.pi * vs * f_s

    rated_T = 2.9e6
    amplitudes = np.array(
        [0.0018, 0.0179, 0.0024, 0.0034, 0.0117, 0.0018, 0.0011]
    ) * generator_torque(rpm)
    amplitudes[4] += rated_T * 0.0176 #TODO: what is this???

    return omegas, amplitudes


def forced_response(assembly, excitation_dict, rpm_linspace):
    """
    Run a forced response analysis to an opentorsion assembly.

    First, the assembly is given harmonic excitation as input.
    Finally, the system response is calculated and plotted.

    Args:
      assembly: Windmill drivetrain as opentorsion assembly object.
      excitation_dict: keys are node coordinates and value is excitation at that coordinate. 
      Excitation value is list of tuples [(multiplier, excitation as percentage of the torque)]
      rpm_linspace: Dict containing "start", "stop", and "num" keys for linspace.

    Returns:
      max_amplitude: Highest vibration amplitude that occurred during the analysis.
    """
    M, K = assembly.M(), assembly.K()  # Mass and stiffness matrices
    assembly.xi = 0.02  # modal damping factor, a factor of 2 % can be used for all modes in a conservative design
    C = assembly.C_modal(M, K)  # Damping matrix

    ## Modal analysis
    A, B = assembly.state_matrix(C)
    lam, vec = LA.eig(A, B)
    freqs = np.sort(np.absolute(lam)) / (2 * np.pi)  # eigenfrequencies

    VT_element1 = []
    VT_element2 = []


    ## The excitation depends on the rotational speed of the system.
    ## Here the response is calculated at each rotational speed.
    ## The responses at each rotational speed are summed up to get the total response.
    multipliers = sorted(list(set([item[0] for sublist in excitation_dict.values() for item in sublist]))) #Get unique multipliers from exitation dict, and sort
    node_excitation_amplitudes = {} #Dict in which key is node coordinate an value is list of percentages
    for excitation_node, excitations in excitation_dict.items():
        #Convert excitations into dict for easier coding
        excitations_of_node = dict(excitations)
        #Loop through omegas
        amplitude_percentage_list = []
        for multiplier in multipliers:
            #If there is an excitation with this omega
            if multiplier in excitations_of_node:
                amplitude_percentage_list.append(excitations_of_node[multiplier])
            #If not, excitation is 0
            else:
                amplitude_percentage_list.append(0)
        node_excitation_amplitudes[excitation_node] = np.array(amplitude_percentage_list)
        
    rpms = np.linspace(start=rpm_linspace["start"], stop=rpm_linspace["stop"], num=rpm_linspace["num"])
    for rpm in rpms:
        omegas = 2 * np.pi * np.array(multipliers) * rpm
        try:
            U = SystemExcitation(assembly.dofs, omegas)
        except IndexError:
            #Excitation matrix is incorrect
            return -1
        
        for excitation_node, amplitude_percentage_list in node_excitation_amplitudes.items():
            U.add_harmonic(excitation_node, amplitude_percentage_list * generator_torque(rpm)) # The rpm-torque profile has to be defined by the analysis, here we are using generator_torque

        #X, tanphi = assembly.ss_response(M, C, K, U.excitation_amplitudes(), omegas)

        T_v, T_e = assembly.vibratory_torque(M, C, K, U.excitation_amplitudes(), omegas)

        VT_element1.append(np.sum(T_e[0]))
        VT_element2.append(np.sum(T_e[1]))

    T_e = np.array(
        [np.array(VT_element1), np.array(VT_element2)]
    )  # Total response (shaft torque)

    # plot_tools = Plots(assembly)
    # plot_tools.torque_response_plot(rpm_linspace, T_e, show_plot=True)
    # print(T_e)


    max_amplitude = np.max(T_e)
    # print("MAX_AMPLITUDE", max_amplitude)

    return max_amplitude



def forced_response_analysis(component_urls_for_assembly, rpm_linspace):
    start = time.time()
    assembly, excitation = return_multi_component_assembly_and_excitation_from_list_of_urls(component_urls_for_assembly)
    print("Creating assembly", time.time() - start)
    start = time.time()
    results = forced_response(assembly, excitation, rpm_linspace)
    print("Analysis", time.time() - start)
    return results

def main():
    DTIDs = ["https://dtid.org/e85c46f4-bdc2-4e0e-acd2-6b0ae582072d", "https://dtid.org/1febe1f0-16ff-4245-8fb2-759c93b01808", "https://dtid.org/efa0d72f-994d-4ad4-9f16-f1565371a18d"]
    forced_response_analysis(DTIDs, {"start": 0.1, "stop": 25, "num": 50})

if __name__ == "__main__":
    main()