import time
from functools import reduce
from itertools import groupby

import numpy as np
import pandas as pd

import urbanwb


class SDF_Curve(object):
    def __init__(self, owl_data, num_year, ow_level):
        """
        creates an instance of open water level series and analyses it
        """
        # owl_data --- series of open water level
        # ow_level --- target open water level as well as the inital open water level
        # event_list --- list of events which are separated by zeros
        # max_storage --- list of maximums of each event
        # rank --- rank of max storage which is sorted from highest to lowest
        # num_event --- total number of events
        # num_year --- number of years of given time series
        # return_time_list --- return time of the rank

        self.owl = np.ones(len(owl_data)) * ow_level - owl_data
        self.event_list = self.event_partition()
        self.max_storage = self.max_stor()
        self.rank = self.ranking()
        self.num_event = len(self.rank)
        self.num_year = num_year
        self.return_time_list = self.return_time()
        # self.trendline = self.trendline()

    def event_partition(self):
        """
        differentiates events (segment events by zeros first, then remove empty lists[])
        """
        # needs update: last event does not end with zeros
        rt = []
        n = 0
        # update owl by add 0 to the end so the last event will end with zero.
        self.owl = np.append(self.owl, [0])
        for i in range(len(self.owl)):
            if self.owl[i] == 0:
                rt.append(self.owl[n:i])
                n = i + 1
        return [value for value in rt if len(value) != 0]

    def max_stor(self):
        """
        calculates event maximums and stores in a list.
        """
        storage = []
        for event in self.event_list:
            storage.append(reduce(lambda x, y: x if (x > y) else y, event))
        return storage

    def ranking(self):
        """
        sorts the max_storage list, ranks the event maximum from highest to lowest.
        """
        rank = sorted(self.max_storage, reverse=True)
        return rank

    def return_time(self):
        """
        calculates the return period of event extremes by formula : return time = number of years / rank No.
        """
        rt = []
        for m in range(len(self.rank)):
            rt.append(self.num_year / (1 + m))
        return rt

    # def trendline(self):
    #     """
    #     get the coefficient k and b of the trend line of return time(year) and maximum open water level above target
    #     water level(owl) (y = kln(x)+b)
    #     """
    #     coe = np.polyfit(np.log(self.return_time_list), self.rank, 1)
    #     return coe[0], coe[1]

    # def required_storage_capacity(self):
    #     """
    #     calculates required storage capacity using formula obtained from plot_trendline() for return period ranging
    #     from 1 year to 100 year
    #     """
    #     # a, b --- corresponding coefficients of formula
    #     a, b = self.trendline[0], self.trendline[1]
    #     # rqd_stor_cap --- list of required storage capacity
    #     rqd_stor_cap = []
    #     for t in [
    #         1,
    #         2,
    #         5,
    #         10,
    #         20,
    #         50,
    #         100,
    #     ]:  # for return period of 1, 2, 5, 10, 20, 50, 100 year
    #         rqd_stor_cap.append(a * np.log(t) + b)
    #     return rqd_stor_cap


class SDF_curve2:
    def __init__(self, segment_marks, owl, ow_level):
        self.segment_marks = segment_marks
        self.ow_level = ow_level
        self.owl = np.append(
            np.ones(len(owl)) * self.ow_level - owl, 0
        )  # add 0 to end with 0
        self.ranking = sorted(self.get_maxima(), reverse=True)

    def get_maxima(
        self,
    ):
        maxima = []
        for i in range(len(self.segment_marks) - 1):
            maxima.append(
                max(self.owl[self.segment_marks[i] : self.segment_marks[i + 1]])
            )
        return maxima


def running_counter(source_list):
    "function calculates, following the list sequence how many times a number is repeated"
    return [(k, sum(1 for i in g)) for k, g in groupby(source_list)]


def get_segment_index(owl):

    interim = np.zeros_like(owl)
    for i in range(len(owl)):
        if owl[i] != 0:
            interim[i] = 1
    count_list = running_counter(interim)

    # test numbers of timesteps match or not
    empty = []
    for element in count_list:
        empty.append(element[1])
    if reduce((lambda x, y: x + y), empty) != len(owl):
        raise SystemExit("number of time steps does not match.")

    # analyze the count_list to get the index of segments.
    t = 0
    segment_index = [0]
    base_index = 0
    while t <= len(count_list) - 1:
        if t % 2 == 0:
            segment_index.append(count_list[t][1] + base_index)
        base_index += count_list[t][1]
        t += 1
    return segment_index


if __name__ == "__main__":
    start = time.time()
    path = urbanwb.urbanwbdir / ".." / "input"
    data = pd.read_csv(path / "integration_test" / "owl.csv")
    iters = np.shape(data["owl_11"])[0]
    owl = pd.Series.tolist(data["owl_11"])
    ow_level = 1.5
    k = SDF_Curve(owl, 30, ow_level)
    print("max", max(k.max_stor()), "min", min(k.max_stor()))
    print(k.rank)
    print(k.return_time())
    print(k.required_storage_capacity())
    end = time.time()
    print(f"Model runtime: {end - start:.4f}s")
    print("-----" * 8)
