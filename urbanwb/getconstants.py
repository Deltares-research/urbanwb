import numpy as np
import pandas as pd
import fire

# make the marks using precipitation data(rules : sepearte hourly rainfall events by six consective zeros)
def making_marks(precipitation):
    # first create an empty mark arary.
    mark = np.zeros_like(precipitation)
    # give values to the mark array.
    for i in range(len(precipitation)):
        if i < 6:
            mark[i] = 0
        else:
            if precipitation[i] > 0:
                if sum(precipitation[i-6:i]) > 0:
                    mark[i] = mark[i-1]
                else:
                    mark[i] = mark[i-1] + 1
            else:
                mark[i] = mark[i-1]
    return mark


# according to the event mark, get to sum of x for each event, and rank the sum from highest to lowest.
def ranking(df, x, num):
    rank = np.zeros(num)
    for i in range(num):
        rank[i] = sum(df[df.mark==i][x])
    return sorted(rank, reverse=True)


from collections import OrderedDict
# from pastas import * # timeseries analysis tool
import numpy as np
import matplotlib.pyplot as plt


def removekey(d, *keys):
    r = dict(d)
    for _ in keys:
        del r[_]
    return r

# removekey(dictionary, "Date", "Baseline", "Unnamed: 0", "P_atm").keys()

class Analyse(object):

    def __init__(self, filename, num_year=30, ):
        self.name = filename
        # automatically create output name according to inputname: first remove ".csv" then add "_results.csv"
        self.output_name = ''.join(list(self.name)[:-4]) + "_results.csv"
        self.df = pd.read_csv(self.name, )
        self.df = self.df.fillna(0)
        self.dictionary = self.df.to_dict('list')
        self.num_year = num_year

        # making event marks according to precipitation (6 consective zeros as separation)
        self.df["mark"] = making_marks(self.df["P_atm"])
        self.measure_dictionary = removekey(self.dictionary, "Unnamed: 0", "Date", "P_atm", "Baseline")
        self.makingranks = self.makingranks()

    def getconstants(self,):
        pass
        print(["storage cap mm", 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50])
        emp = dict()
        baseT = find_corresponding_T_for_array(t_array=self.makingranks["T_list"], array=self.makingranks["Rank_baseline"])
        for key in self.makingranks.keys():
            if key not in ["Rank_P", "T_list", "Rank_baseline"]:
                a = find_corresponding_T_for_array(t_array=self.makingranks["T_list"], array=self.makingranks[key])
                c = [y/x for x, y in zip(baseT, a)]
                emp[key] = c
        return emp

    def save_constants(self):
        pass

    def makingranks(self, ):
        # unchanged,
        emp = dict()
        emp["Rank_P"] = ranking(self.df, "P_atm", int(max(self.df.mark) + 1))
        # create T list (30 yr, thus starting from (30+1 / 1)), could put it as argument for more general running, but not for now.
        emp["T_list"] = [(self.num_year + 1) / m for m in range(1, len(emp["Rank_P"]) + 1)]
        # rank runoff on the baseline case
        emp["Rank_baseline"] = ranking(self.df, "Baseline", int(max(self.df.mark) + 1))
        for key in self.measure_dictionary.keys():
            emp[key] = ranking(self.df, key, int(max(self.df.mark) + 1))
        data = pd.DataFrame.from_dict(emp)
        return data

    def save_to_csv(self, ):
        self.makingranks().to_csv(self.output_name)

    def plotting(self, measure_name, addition_name, xlim_down=5, xlim_up=20, ):
        self.data = self.makingranks()

        plt.figure(figsize=(9, 6))
        plt.semilogy(self.data.Rank_P, self.data.T_list, "b--", label="Precipitation", ms=2)
        plt.semilogy(self.data.Rank_baseline, self.data.T_list, "k-", label="Baseline", ms=2)
        measures_rank_dictionary = removekey(self.data.to_dict('list'), "Rank_P", "Rank_baseline", "T_list")

        for key in measures_rank_dictionary.keys():
            plt.semilogy(measures_rank_dictionary[key], self.data.T_list, label=key, ms=2)

        x = np.linspace(0, 100, 200)
        # plt.legend(loc='best',frameon=False)
        plt.legend(loc='upper right', frameon=True)
        plt.xlabel("Runoff (mm)")
        plt.ylabel("T (year)")
        plt.title(measure_name + "(1981-2011)")
        plt.xlim(xlim_down, xlim_up)

        # add grid
        ax = plt.gca()
        ax.yaxis.grid(linestyle='--', linewidth=0.5, which='both')
        ax.xaxis.grid(linestyle='--', linewidth=0.5, which='both')

        plt.savefig("figures/" + addition_name + measure_name + ".png")


import math

def find_corresponding_T_for_array(t_array, array, vararr = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50]):
    database = []
    for var in vararr:
        # print(var, 'case:')
        try:
            for counter, value in enumerate(array):
                if value < var:
                    # print(value)
                    v_below = array[counter]
                    v_above = array[counter-1]
                    # print('v-above',counter-1, v_above)
                    # print('v-below',counter, v_below)
                    # print('---'*6)
                    t_up = t_array[counter-1]
                    t_below = t_array[counter]
                    # print('T-up',t_up)
                    # print('T-below',t_below)
                    t_value = t_up - (v_above - var)/(v_above - v_below) * (t_up - t_below)
                    # print('T_value',t_value)
                    break
        except KeyError:
            # print('below',counter, array[counter])
            # print('above',counter, array[counter])
            t_value = math.inf
        finally:
            database.append(t_value)
    return database


def getconstants(inputfilename, num_year=30):
    m = Analyse("pysol/" + inputfilename, num_year=num_year)
    results = m.getconstants()
    outputfilename = ''.join(list(inputfilename)[:-4]) + "_constants.txt"
    print(results)
    # np.savetxt(outputfilename, results, )
    with open(outputfilename, 'w') as f:
        for key, value in results.items():
            f.write('%s:%s\n' % (key, value))

if __name__ == "__main__":
    fire.Fire(getconstants)