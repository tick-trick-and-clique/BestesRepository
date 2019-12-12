import matplotlib.pyplot as plt
import numpy as np


def stats_from_array_data(filename, x_value):
    fopen = open(filename, "r")
    means = []
    stds = []
    n = 0
    failed = 0
    for line in fopen.readlines():
        line = line.rstrip(";")
        list = line.split(";")
        data_list = []
        for i in list:
            try:
                data_list.append(float(i))
                n += 1
            except ValueError:
                failed += 1
        array = np.array(data_list)
        means.append(array.mean())
        stds.append(array.std())
    return x_value, means, stds, n, failed


def build_bar_plot(x, y, e, n, title, ylim, anno_height, ylabel):
    fig = plt.figure()
    plt.bar(x, y)
    print(e)
    plt.errorbar(x, y, yerr=[np.zeros(len(e)), e], linestyle='None', elinewidth=1, capsize=3, )
    plt.xlabel("#Nodes")
    plt.ylabel(ylabel)
    axes = plt.gca()
    axes.set_ylim([0, ylim])
    i = 0
    for a in x:
        label = str(n[i])
        i += 1
        plt.annotate(label, (a, anno_height), textcoords="offset points", xytext=(0, 10), ha='center', color="r")
    plt.suptitle(title)
    return fig


def data_for_plot_from_stats_ga(list_of_stats):
    x = [i[0] for i in list_of_stats]
    y = [i[1][0] for i in list_of_stats]
    e = [i[2][0] for i in list_of_stats]
    n = [i[3] for i in list_of_stats]
    failed = [i[4] for i in list_of_stats]
    return x, y, e, n, failed

def data_for_plot_from_stats_bk(stats):
    x, y, e, n, failed = stats
    for i in range(len(y)):
        rel_err = e[i]/y[i]
    return


if __name__ == '__main__':

    # Build plot for graph alignment using bron-kerbosch
    stat3 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_bk_3_0.5.txt", 3)
    stat4 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_bk_4_0.5.txt", 4)
    stat5 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_bk_5_0.5.txt", 5)
    stat6 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_bk_6_0.5.txt", 6)
    stat7 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_bk_7_0.5.txt", 7)
    x, y, e, n, failed = data_for_plot_from_stats_ga([stat3, stat4, stat5, stat6, stat7])
    fig = build_bar_plot(x, y, e, n,  "Graph Alignment [Bron-Kerbosch]", 200, 175, "Time [s]")
    plt.savefig("GraphAlignment_BronKerbosch")
    plt.show()
    plt.close(fig)

    # Build plot for graph alignment using cordella
    stat3 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_mb_3_0.5.txt", 3)
    stat4 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_mb_4_0.5.txt", 4)
    stat5 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_mb_5_0.5.txt", 5)
    stat6 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_mb_6_0.5.txt", 6)
    stat7 = stats_from_array_data("Benchmarking\GraphAlignment\\benchmark_ga_mb_7_0.5.txt", 7)
    x, y, e, n, failed = data_for_plot_from_stats_ga([stat3, stat4, stat5, stat6, stat7])
    y = [i*1000 for i in y]
    e = [i*1000 for i in e]
    fig = build_bar_plot(x, y, e, n, "Graph Alignment [VF2]", 3.5, 3, "Time [ms]")
    plt.savefig("GraphAlignment_VF2")
    plt.show()
    plt.close()

    """
    # Build plot for singly bron-kerbosch, assuming that error propagation is additive in relative errors (!)
    stat_random = stats_from_array_data("Benchmarking\Bron-Kerbosch\\benchmark_bk_p_random.txt", 3)
    stat_max = stats_from_array_data("Benchmarking\Bron-Kerbosch\\benchmark_bk_p_max.txt", 4)
    data_for_plot_from_stats_bk(stat_random)
    fig = build_bar_plot(x, y, e)
    plt.savefig("GraphAlignment_BronKerbosch")
    # plt.show()
    plt.close()
    """