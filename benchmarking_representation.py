import matplotlib.pyplot as plt
import numpy as np


def stats_from_array_data_ga(filename, x_value):
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


def stats_from_array_data_bk(filename, x_value):
    fopen = open(filename, "r")
    values = []
    for line in fopen.readlines():
        line = line.rstrip(";")
        list = line.split(";")
        i = float(list[0])
        values.append(i)
    ar = np.array(values)
    return ar.mean(), ar.std(), x_value


def build_bar_plot_ga(x, y, e, n, title, ylim, anno_height, ylabel):
    fig = plt.figure()
    plt.bar(x, y)
    plt.errorbar(x, y, yerr=[np.zeros(len(e)), e], linestyle='None', elinewidth=1, capsize=3)
    plt.xlabel("Number of Vertices", labelpad=12)
    plt.ylabel(ylabel, labelpad=12)
    axes = plt.gca()
    axes.set_ylim([0, ylim])
    plt.suptitle(title)
    return fig


def build_bar_plot_bk(x, y, e, ylim, anno_height):
    fig = plt.figure(figsize=(3.0, 4.8))
    plt.bar(x, y, width=0.7)
    plt.errorbar(x, y, yerr=[np.zeros(len(e)), e], linestyle='None', elinewidth=1, capsize=3)
    plt.xlabel("Pivot Type", labelpad=13)
    plt.xlim(-0.8, 1.8)
    plt.ylabel("Time [ms]", labelpad=13)
    axes = plt.gca()
    axes.set_ylim([0, ylim])
    for a in x:
        plt.annotate("30/30", (a, anno_height), textcoords="offset points", xytext=(0, 10), ha='center', color="r")
    plt.suptitle("Pivoting (Bron-Kerbosch)")
    plt.tight_layout(rect=(0, 0, 1, 0.90))
    return fig


def data_for_plot_from_stats_ga(list_of_stats):
    x = [i[0] for i in list_of_stats]
    y = [i[1][0] for i in list_of_stats]
    e = [i[2][0] for i in list_of_stats]
    n = [i[3] for i in list_of_stats]
    failed = [i[4] for i in list_of_stats]
    return x, y, e, n, failed


def data_for_plot_from_stats_bk(list_of_stats):
    x = [i[2] for i in list_of_stats]
    y = [i[0] for i in list_of_stats]
    e = [i[1] for i in list_of_stats]
    return x, y, e


if __name__ == '__main__':

    # Build plot for graph alignment using bron-kerbosch
    stat3 = stats_from_array_data_ga("Benchmarking\GraphAlignment_zweiteRunde\\benchmark_ga_bk_10.txt", 10)
    stat4 = stats_from_array_data_ga("Benchmarking\GraphAlignment_zweiteRunde\\benchmark_ga_bk_13.txt", 13)
    stat7 = stats_from_array_data_ga("Benchmarking\GraphAlignment_zweiteRunde\\benchmark_ga_bk_7.txt", 7)
    x, y, e, n, failed = data_for_plot_from_stats_ga([stat3, stat4, stat7])
    fig = build_bar_plot_ga(x, y, e, n,  "Graph Alignment (Bron-Kerbosch)", 30, 25, "Time [s]")
    plt.savefig("GraphAlignment_BronKerbosch")
    plt.show()
    plt.close(fig)

    # Build plot for graph alignment using cordella
    stat3 = stats_from_array_data_ga("Benchmarking\GraphAlignment_zweiteRunde\\benchmark_ga_mb_10.txt", 10)
    stat4 = stats_from_array_data_ga("Benchmarking\GraphAlignment_zweiteRunde\\benchmark_ga_mb_13.txt", 13)
    stat7 = stats_from_array_data_ga("Benchmarking\GraphAlignment_zweiteRunde\\benchmark_ga_mb_7.txt", 7)
    x, y, e, n, failed = data_for_plot_from_stats_ga([stat3, stat4, stat7])
    y = [i*1000 for i in y]
    e = [i*1000 for i in e]
    fig = build_bar_plot_ga(x, y, e, n, "Graph Alignment (VF2)", 250, 220, "Time [ms]")
    plt.savefig("GraphAlignment_VF2")
    plt.show()
    plt.close()


    # Build plot for singly bron-kerbosch, assuming that error propagation is additive in relative errors (!)
    stat_random = stats_from_array_data_bk("Benchmarking\Bron-Kerbosch\\benchmark_bk_p_random.txt", "Random")
    stat_max = stats_from_array_data_bk("Benchmarking\Bron-Kerbosch\\benchmark_bk_p_max.txt", "Max")
    x, y, e = data_for_plot_from_stats_bk([stat_random, stat_max])
    y = [i * 1000 for i in y]
    e = [i * 1000 for i in e]
    fig = build_bar_plot_bk(x, y, e, 1.25, 1.1)
    plt.savefig("BronKerbosch_Pivoting")
    plt.show()
    plt.close()
