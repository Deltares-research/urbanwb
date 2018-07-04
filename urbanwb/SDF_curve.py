import numpy as np
import pandas as pd
import time
from functools import reduce


start = time.time()
data = pd.read_csv("pysol/owl_sdf.csv")
iters = np.shape(data["date"])[0]
owl = data["owl"]
# owl_level --- target owl, as well as the initial owl.
owl_level = 1.6


class OWL(object):
    def __init__(self, owl_data):
        self.owl = owl_data
        self.event_list = self.event_partition()
        self.max_storage = self.max_stor()
        self.rank = self.ranking()
        self.num_event = len(self.rank)

    def event_partition(self):
        """
        differentiates events. segment events by zeros first, then remove empty lists[],
        finally, a list of events is obtained
        """
        rt = []
        n = 0
        for i in range(len(self.owl)):
            if self.owl[i] == 0:
                rt.append(self.owl[n:i])
                n = i + 1
        return [value for value in rt if len(value) != 0]

    def max_stor(self):
        """
        gets a list of event maximum.
        """
        storage = []
        for event in self.event_list:
            storage.append(reduce(lambda x, y: x if (x > y) else y, event))
        return storage

    def ranking(self):
        """
        sorts the max_storage list, ranks the event maximum from highest to lowest.
        """
        return sorted(self.max_storage, reverse=True)

    def return_time(self):
        """
        gets the return period of event extremes.
        """
        rp = []
        for m in range(self.num_event):
            rp.append(self.num_event / (1 + m))
        return rp


if __name__ == "__main__":
    # validation --- discharge = 5/3
    start = time.time()

    my_lst = np.ones(iters) * 1.6 - pd.Series.tolist(owl)
    k = OWL(my_lst)

    print("max", max(k.max_stor()), "min", min(k.max_stor()))
    print(k.rank)
    print(k.return_time())

    end = time.time()
    print(f"Model runtime: {end - start:.4f}s")
    print("-----" * 6)

    # series 2 --- discharge = 10/3
    print("discharge", 10 / 3)
    my_lst = np.ones(iters) * 1.6 - pd.Series.tolist(data["owl2"])
    k = OWL(my_lst)
    print("max", max(k.max_stor()), "min", min(k.max_stor()))
    print("number of events", k.num_event)
    print(k.rank)
    print(k.return_time())
    print("-----" * 6)

    # series 3 --- discharge = 20/3
    print("discharge", 20 / 3)
    my_lst = np.ones(iters) * 1.6 - pd.Series.tolist(data["owl3"])
    k = OWL(my_lst)
    print("max", max(k.max_stor()), "min", min(k.max_stor()))
    print("number of events", k.num_event)
    print(k.rank)
    print(k.return_time())
    print("-----" * 6)

    # series 4 --- discharge = 40/3
    print("discharge", 40 / 3)
    my_lst = np.ones(iters) * 1.6 - pd.Series.tolist(data["owl4"])
    k = OWL(my_lst)
    print("max", max(k.max_stor()), "min", min(k.max_stor()))
    print("number of events", k.num_event)
    print(k.rank)
    print(k.return_time())
    print("-----" * 6)

    # series 5 --- discharge = 80/3
    print("discharge", 80 / 3)
    my_lst = np.ones(iters) * 1.6 - pd.Series.tolist(data["owl5"])
    k = OWL(my_lst)
    print("max", max(k.max_stor()), "min", min(k.max_stor()))
    print("number of events", k.num_event)
    print(k.rank)
    print(k.return_time())
    print("-----" * 6)

    # series 5 --- discharge = 160/3
    print("discharge", 160 / 3)
    my_lst = np.ones(iters) * 1.6 - pd.Series.tolist(data["owl6"])
    k = OWL(my_lst)
    print(k.max_stor())
    print("number of events", k.num_event)
    print(k.rank)
    print(k.return_time())
    print("-----" * 6)
