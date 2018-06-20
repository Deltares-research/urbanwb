import numpy as np
import pandas as pd
import time
from functools import reduce


start = time.time()
data = pd.read_csv('pysol/owl_sdf.csv')
iters = np.shape(data['date'])[0]
owl = data['owl']
# owl_level --- target owl, as well as the initial owl.
owl_level = 1.6


# method 1:
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
            rp.append(self.num_event/(1 + m))
        return rp


if __name__ == '__main__':
    # validation
    start = time.time()

    my_lst = np.ones(iters) * 1.6 - pd.Series.tolist(owl)
    k = OWL(my_lst)

    print('max', max(k.max_stor()), 'min', min(k.max_stor()))
    print(k.max_storage)
    print(k.rank)
    print(k.return_time())

    end = time.time()
    print(f'Model runtime: {end - start:.4f}s')
    print('-----'*6)


    # validatation 2

    my_newlist = np.random.randint(0, 10, 80)
    print(my_newlist)
    k = OWL(my_newlist)
    print('max', max(k.max_stor()), 'min', min(k.max_stor()))
    print(k.max_storage)
    print(k.rank)
    print(k.return_time())