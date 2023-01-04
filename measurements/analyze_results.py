import csv
from statistics import mean, median, stdev
import matplotlib.pyplot as plt

FILENAME = "measurements.csv"


#Copied from: https://github.com/juusoautiosalo/dtweb-measurements/blob/main/plotting_module.py. Originally written by Juuso Autiosalo
def plot_network_fetch_times(data):
    """
    Plots execution times of find_optimal_design_threaded.py script

    Args:
        data: Dict that contains column names as keys and list of data as values.
    """

    labels = ["Reading DDT", "Find components", "Analysis"]

    #Remove total time
    del data["TotalTime"]

    width = 5.0 # inches
    height = 5.0 # inches
    
    fig, axes = plt.subplots(figsize=(width,height))

    # Prepare data
    violindata = []
    quantiles = []
    #labels = []
    for key in data.keys():
        violindata.append(data[key])
        quantiles.append([0,0.5,0.99])
        #labels.append(key) #Set labels automatically

    # Plot
    plot = axes.violinplot(dataset = violindata,
        points=100,
        widths=0.9,
        showmeans=False, showextrema=False, showmedians=False,
        quantiles=quantiles, 
        # bw_method=0.1
        )
    plot['cquantiles'].set_linewidth(0.5)
    

    # Set texts to figure
    #axes.set_title('Finding optimal design execution times')
    axes.yaxis.grid(True)
    axes.set_xlabel('Phase')
    axes.set_ylabel('Execution time (s)')
    axes.set_ylim(bottom=0)
    print(data)
    axes.set_xticks(range(1,len(data.keys()) + 1))
    axes.set_xticklabels(labels)
    # plt.xticks(rotation=90)
    #plt.tight_layout()

    plt.show()

    figurename = 'execution_times' + '.pdf'
    fig.savefig(figurename)


def main():
    with open(FILENAME, "r") as f:
        reader = csv.DictReader(f)
        data = {}
        for row in reader:
            for header, value in row.items():
                try:
                    data[header].append(float(value))
                except KeyError:
                    data[header] = [float(value)]

    print()
    print("|Value    |" + "|".join([f"{key:^22s}" for key in data.keys()]) + "|")
    print("-------------------------------------------------------------------------------------------------------")
    print("|Min      |" + "|".join([f"{min(values):>22.3f}" for values in data.values()]) + "|")
    print("|Max      |" + "|".join([f"{max(values):>22.3f}" for values in data.values()]) + "|")
    print("|Mean     |" + "|".join([f"{mean(values):>22.3f}" for values in data.values()]) + "|")
    print("|Median   |" + "|".join([f"{median(values):>22.3f}" for values in data.values()]) + "|")
    print("|Std. Dev.|" + "|".join([f"{stdev(values):>22f}" for values in data.values()]) + "|")
    print()

    plot_network_fetch_times(data)
    #plot_data(data)

if __name__ == "__main__":
    main()