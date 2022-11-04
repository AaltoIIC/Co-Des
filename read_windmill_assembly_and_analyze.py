from openTorsion_converter import return_multi_component_assembly_from_url


def analysis(assembly):
    
    # Sampo and Urho add analysis for assembly here
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
    dtid_multicomponent_model = "https://dtid.org/890f7d85-626e-4e05-960e-9d1bc7af32fd"
    assembly_multicomponent = return_multi_component_assembly_from_url(dtid_multicomponent_model)
    #Analyze assembly
    analysis(assembly_multicomponent)


if __name__ == "__main__":
    main()