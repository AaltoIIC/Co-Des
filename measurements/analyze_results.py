import csv
from statistics import mean, median, stdev
import matplotlib.pyplot as plt

FILENAME = "measurements_combined.csv"
FILENAME_RESULTS = "results.csv"

def read_results(filename):
    with open(filename, newline='') as csvfile:
        return list(csv.reader(csvfile, delimiter=';'))

def calc_MAS(values):
    mean_values = mean(values)
    sum = 0
    for value in values:
        sum += abs(mean_values-value)

    return sum/len(values) #Error


#Copied from: https://github.com/juusoautiosalo/dtweb-measurements/blob/main/plotting_module.py. Originally written by Juuso Autiosalo.
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
    
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex = True, figsize=(width,height))

    # Prepare data
    violindata = []
    quantiles = []
    #labels = []
    for key in data.keys():
        violindata.append(data[key])
        quantiles.append([0.05,0.5,0.95])
        #labels.append(key) #Set labels automatically

    # Plot
    plot1 = ax1.violinplot(dataset = violindata,
        points=100,
        widths=0.9,
        showmeans=False, showextrema=False, showmedians=False,
        quantiles=quantiles, 
        # bw_method=0.1
        )
    plot1['cquantiles'].set_linewidth(0.5)

    # Plot
    plot2 = ax2.violinplot(dataset = violindata,
        points=100,
        widths=0.9,
        showmeans=False, showextrema=False, showmedians=False,
        quantiles=quantiles, 
        # bw_method=0.1
        )
    plot2['cquantiles'].set_linewidth(0.5)
    
    ax1.set_ylim(3695, 3770)
    ax2.set_ylim(0, 9.2)

    # hide the spines between ax and ax2
    ax1.spines['bottom'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.xaxis.tick_top()
    ax1.tick_params(labeltop=False)  # don't put tick labels at the top
    ax2.xaxis.tick_bottom()

    # This looks pretty good, and was fairly painless, but you can get that
    # cut-out diagonal lines look with just a bit more work. The important
    # thing to know here is that in axes coordinates, which are always
    # between 0-1, spine endpoints are at these locations (0,0), (0,1),
    # (1,0), and (1,1).  Thus, we just need to put the diagonals in the
    # appropriate corners of each of our axes, and so long as we use the
    # right transform and disable clipping.

    d = .015  # how big to make the diagonal lines in axes coordinates
    # arguments to pass to plot, just so we don't keep repeating them
    kwargs = dict(transform=ax1.transAxes, color='k', clip_on=False)
    ax1.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
    ax1.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal

    kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
    ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
    ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal

    # Set texts to figure
    #ax1.set_title('Finding optimal design execution times')
    #axes.yaxis.grid(True)
    #ax2.set_xlabel('Phase')
    fig.text(0.015, 0.6, 'Execution time (s)', ha='center', va='center', rotation='vertical')
    #ax2.set_ylabel('Execution time (s)')
    #axes.set_ylim(bottom=0)
    #print(data)
    ax1.set_xticks(range(1,len(data.keys()) + 1))
    ax1.set_xticklabels(labels)
    plt.xticks(rotation=90)
    plt.tight_layout()
    # Axis dicointty
    fig.subplots_adjust(hspace=0.1)

    plt.show()

    figurename = 'execution_times' + '.pdf'
    fig.savefig(figurename)

def plot_results(results):
    divider = 1000 #Scale results to kN
    results_torsional_vibration = list(map(lambda x: float(x[-1])/divider, results)) #Change to float 
    results_torsional_vibration.sort()
    fig, ax = plt.subplots()
    plt.axline((0, 50000/divider), (1000, 50000/divider), color="red", linestyle="--")#50 kNm limit
    plt.plot(results_torsional_vibration, marker=".", markersize=2, linestyle="none")
    plt.text(-25,51, "Vibration torque limit", fontsize=10) #, bbox=dict(boxstyle="square", ec=(1, 1, 1), fc=(1, 1, 1),))
    #ax.set_title("Torsional vibration analysis")
    ax.set_ylabel("Torsional vibration amplitude [kNm]")
    ax.set_xlabel("Index")
    plt.show()

    figurename = 'results' + '.pdf'
    fig.savefig(figurename)


def read_execution_times(filename):
    with open(filename, "r") as f:
        reader = csv.DictReader(f)
        data = {}
        for row in reader:
            for header, value in row.items():
                try:
                    data[header].append(float(value))
                except KeyError:
                    data[header] = [float(value)]
    return data

def print_results(results):
    results_torsional_vibration = sorted(results, key=lambda x: float(x[-1])) #Change to float
    print("LEN", len(results_torsional_vibration))
    for result in results_torsional_vibration:
        print(result)


def print_network_fetch_times(data):
    print()
    print("|Value    |" + "|".join([f"{key:^22s}" for key in data.keys()]) + "|")
    print("-------------------------------------------------------------------------------------------------------")
    print("|Min      |" + "|".join([f"{min(values):>22.3f}" for values in data.values()]) + "|")
    print("|Max      |" + "|".join([f"{max(values):>22.3f}" for values in data.values()]) + "|")
    print("|Mean     |" + "|".join([f"{mean(values):>22.3f}" for values in data.values()]) + "|")
    print("|Median   |" + "|".join([f"{median(values):>22.3f}" for values in data.values()]) + "|")
    print("|Std. Dev.|" + "|".join([f"{stdev(values):>22f}" for values in data.values()]) + "|") #Mean absolute error
    print("|MAE      |" + "|".join([f"{calc_MAS(values):>22f}" for values in data.values()]) + "|")
    print()

def main():
    execution_times = read_execution_times(FILENAME)
    results = read_results(FILENAME_RESULTS)
    plot_results(results)
    print_results(results)
    print_network_fetch_times(execution_times)
    plot_network_fetch_times(execution_times)
    

if __name__ == "__main__":
    main()