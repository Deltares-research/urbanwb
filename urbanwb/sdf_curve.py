from functools import reduce
from itertools import groupby

import fire
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


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

#RDL20210416 ===============================================================================
#DEFINITION RAIN EVENT
def making_marks_prec(precipitation,timestep):


### SEPARATION OF RAINFALL EVENTS
# t         = time step number
# ttot      = total number of time steps
# ptel      = counter for rain events, raised by 1 at the start of each new rain event
# pev[t]    = part of rain event (value = 1), or not (value = 0)
# pnr[t]    = number of rain event, raised by 1 at the start of each new rain event

# # DETERMINE TSEPRAIN
    tsize = timestep / 3600.
    ttot = len(precipitation)
    if tsize <= 1:
        tseprain = 6. / tsize
    else:
        if tsize < 2:
            tseprain = 6.
        else:
            if tsize < 3:
                tseprain = 2.
            else:
                tseprain = 1.

# # START DEFINITION OF RAIN EVENTS
    ptel = 0
    pev = np.zeros_like(precipitation)
    pnr = np.zeros_like(precipitation)

    for i in range(len(precipitation)):
        if ptel == 0:
            #Determine start of the first rain event
            if precipitation[i] > 0:
                ptel = 1
                pev[i] = 1
                pnr[i] = 1
            else:
                pev[i] = 0
                pnr[i] = 0
        else:
            #all the other rain events
            if precipitation[i] > 0:
                if pev[i-1] > 0:
                    #Continuation of current rain event
                    pev[i] = 1
                    pnr[i] = ptel
                else:
                    #Start of new rain event
                    ptel = ptel + 1
                    pev[i] = 1
                    pnr[i] = ptel
            else:
                if i <= ttot - tseprain:
                    #Still sufficient time steps left to separate rain events
                    if pev[i-1]>0:    
                        if sum(precipitation[int(i):int(i+tseprain)])>0:
                            # continuation of current rain event
                            pev[i] = 1
                            pnr[i] = ptel
                        else:
                            #Not part of rain event
                            pev[i] = 0
                            pnr[i] = ptel
                    else:
                            #Not part of rain event
                            pev[i] = 0
                            pnr[i] = ptel
                else:
                    if pev[i-1]>0:
                        #insufficient time steps left to separate rain events
                        if sum(precipitation[i : ttot]) > 0:
                            #continuation of last rain event
                            pev[i] = 1
                            pnr[i] = ptel
                        else:
                            # not part of last rain event
                            pev[i] = 0
                            pnr[i] = ptel
                    else:
                        pev[i] = 0
                        pnr[i] = ptel
               
            
    return pev, pnr

# END DEFINITION OF RAIN EVENTS

#DEFINITION STORAGE EVENTS
def making_marks_stor(precipitation, owl_stor):

### SEPARATION OF STORAGE EVENTS
# t         = time step number
# ttot      = total number of time steps
# stel      = counter for storage events, raised by 1 at the start of each new rain event
# sev[t]    = part of storage event (value = 1), or not (value = 0)
# snr[t]    = number of storage event, raised by 1 at the start of each new storage event
# seperation by 1 hour because of storage event

# # START DEFINITION OF RAIN EVENTS
    stel = 0
    sev = np.zeros_like(precipitation)
    snr = np.zeros_like(precipitation)
    for i in range(len(precipitation)):
        
        if stel == 0:
            #Determine start of the first rain event
            if owl_stor[i] > 0:
                stel = 1
                sev[i] = 1
                snr[i] = 1
            else:
                sev[i] = 0
                snr[i] = 0
        else:
            #all the other rain events
            if owl_stor[i] > 0:
                if sev[i-1] > 0:
                    #Continuation of current rain event
                    sev[i] = 1
                    snr[i] = stel
                else:
                    #Start of new rain event
                    stel = stel + 1
                    sev[i] = 1
                    snr[i] = stel
            else:
                sev[i] = 0
                snr[i] = stel
               
            
    return sev, snr

##END STORAGE EVENTS

#COMBINING PRECIPITATION EVENTS AND STORAGE EVENTS:  
def making_marks_sdf(precipitation, timestep, owl_stor):
      
### SEPARATION OF combination EVENTS
# t         = time step number
# ttot      = total number of time steps
# stel      = counter for storage events, raised by 1 at the start of each new rain event
# sev[t]    = part of storage event (value = 1), or not (value = 0)
# snr[t]    = number of storage event, raised by 1 at the start of each new storage event
# seperation by 1 hour because of storage event

    pev = making_marks_prec(precipitation,timestep)[0]
    sev = making_marks_stor(precipitation,owl_stor)[0]
    etel = 0
    enr = np.zeros_like(precipitation)

    for i in range(len(precipitation)):
        if etel == 0:
            if pev[i] > 0:
                etel = 1
                enr[i] = 1
            else:
                enr[i] = 0
        else:
            if pev[i] >0:
                if pev[i-1]>0:
                    enr[i] = etel
                else:
                    if sev[i-1]>0:
                        if sev[i] > 0:
                            enr[i] = etel
                        else:
                            etel = etel +1
                            enr[i] = etel
                    else: 
                        etel = etel + 1
                        enr[i] = etel
            else:
                enr[i] = etel

    return enr   

def rankingmax(df, x, num):
    """
    According to the event mark, get the maximum of x for each event, and then rank the sum from highest to lowest.
    
    Args:
        df (dataframe): a dataframe to do computations on
        x (string): a header of the dataframe
        num (integer): the total number of events

    Returns:
        (numpy.ndarray): an array of values ranked in a descending order
    """
    rank = np.zeros(num)
    for i in range(num):
        rank[i] = max(df[df.mark == i][x])
    return sorted(rank, reverse=True)

def removekey(d, *keys):
    """
    Remove keys in the dictionary

    Args:
        d (dictionary): a dictionary to be modified
        keys (string): keys in the dictionary to be removed

    Returns:
        (dictionary): a modified dictionary
    """
    r = dict(d)
    for _ in keys:
        del r[_]
    return r

class get_max_stor:
    def __init__(self, 
                 filename = None,
                 data = None,
                 num_year = 30,
                 timestep = 3600,
                 owl_stor = None,
                 baseline_ranks = None,
                ):

        self.num_year = num_year
        self.timestep = timestep
        self.df = pd.DataFrame()
        self.df["owl"] = owl_stor
        self.df["mark"] = baseline_ranks
        self.maxima = self.get_maxima(self.df,"owl",int(max(self.df.mark)+1))
    
    def get_maxima(
        self,
        df,
        x,
        num
    ):
        rank = np.zeros(num)
        for i in range(1,num):
            rank[i] = max(df[df.mark == i][x])
        return sorted(rank, reverse=True)

# def plot_sdf_curve2(csv_path, fig_path):
#     sdf = pd.read_csv(csv_path, index_col=0)

#     # Obtain the logarithmic equation for the pumping capacity
#     sdf["Treturn"] = 30 / (sdf.index + 1)

#     plt.figure(figsize=(15, 8))
#     df_vars = pd.DataFrame(columns=["q", "a", "b"])
#     df_vars["q"] = np.zeros(len(sdf.keys()[0:-1]))

#     # Function for the logarithmic equation
#     def func(a, b, x):
#         return a * np.log(x) + b

#     for i, key in enumerate(sdf.keys()[0:-1]):
#         x = (
#             sdf["Treturn"][5:200]
#             .reindex(sdf["Treturn"][5:200].index[::-1])
#             .reset_index(drop=True)
#         )
#         y = sdf[key][5:200].reindex(sdf[key][5:200].index[::-1]).reset_index(drop=True)
#         a, b = np.polyfit(np.log(x), y, 1)

#         df_vars.loc[i] = [key, a, b]

#         plt.plot(y,x )
#         plt.plot(func(a, b, x), x, label=key)

#     plt.yscale("log")
#     plt.xlabel("OWL_Storage [m3/ha]")
#     plt.ylabel("Return time [y]")
#     plt.gca().yaxis.grid(linestyle='--', linewidth = 0.5, which = 'both')
#     plt.gca().xaxis.grid(linestyle='--', linewidth = 0.5, which = 'both')
#     plt.xlim(0, 550)
#     plt.ylim(10**-1.9,31)
#     plt.legend()
#     plt.savefig(fig_path)

#     # Calculate required storage capacity for a set of return periods
#     req_storage = pd.DataFrame()
#     req_storage["Treturn"] = [1, 2, 5, 10, 20, 50, 100]
#     for i, key in enumerate(df_vars["q"]):
#         req_storage[key] = func(
#             df_vars["a"][i], df_vars["b"][i], req_storage["Treturn"]
#         )
#     req_storage = req_storage.set_index("Treturn")
#     req_storage = req_storage.T
# #     print (req_storage.index.values.astype("int"))
#     # SDF Curve
#     plt.figure(figsize=(15, 8))
#     x_1 = []
#     y_1 = pd.DataFrame()
#     for key in req_storage:
#         x_stor = req_storage.index.values.astype("int")
#         y_dis = (
#             req_storage[key]
#         ) 
#         y_1[key] = y_dis
#         # 0.01 for converting ow_area to total area
#         plt.plot(
#             x_stor[y_dis > -0.001], y_dis[y_dis > -0.001], label=key, ms=10, marker="."
#         )
  
#     plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.8)
#     plt.minorticks_on()
#     plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
#     plt.ylabel("Required storage capacity (m3/ha)")
#     plt.xlabel("Effective depth [mm]")
#     plt.legend(title = 'Return time [year]')
# #     plt.savefig(fig_path)
#     return y_1
#END RDL20210416 ===============================================================================


def plot_sdf_curve(csv_path, fig_path):
    sdf = pd.read_csv(csv_path, index_col=0)

    # Obtain the logarithmic equation for the pumping capacity
    sdf["Treturn"] = 30 / (sdf.index + 1)

    plt.figure(figsize=(15, 8))
    df_vars = pd.DataFrame(columns=["q", "a", "b"])
    df_vars["q"] = np.zeros(len(sdf.keys()[1:-1]))

    # Function for the logarithmic equation
    def func(a, b, x):
        return a * np.log(x) + b

    for i, key in enumerate(sdf.keys()[1:-1]):
        x = (
            sdf["Treturn"][0:100]
            .reindex(sdf["Treturn"][0:100].index[::-1])
            .reset_index(drop=True)
        )
        y = sdf[key][0:100].reindex(sdf[key][0:100].index[::-1]).reset_index(drop=True)
        a, b = np.polyfit(np.log(x), y, 1)

        df_vars.loc[i] = [key, a, b]
        plt.plot(x,func(a, b, x), label=key)

    plt.xscale("log")
    plt.ylim(0, 40)
    plt.legend()

    # Calculate required storage capacity for a set of return periods
    req_storage = pd.DataFrame()
    req_storage["Treturn"] = [1, 2, 5, 10, 20, 50, 100]
    for i, key in enumerate(df_vars["q"]):
        req_storage[key] = func(
            df_vars["a"][i], df_vars["b"][i], req_storage["Treturn"]
        )
    req_storage = req_storage.set_index("Treturn")
    req_storage = req_storage.T

    # SDF Curve
    plt.figure(figsize=(15, 8))
    for key in req_storage:
        x_stor = req_storage.index.values.astype("int") / 1000 * 9060000 / 86400
        y_dis = (
            req_storage[key] * (0.03 * 145000)/14.5
        )  # 0.01 for converting ow_area to total area
        plt.plot(
            x_stor[y_dis > -0.001], y_dis[y_dis > -0.001], label=key, ms=10, marker="."
        )
    plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.8)
    plt.minorticks_on()
    plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
    plt.ylabel("Required storage capacity (m3/ha)",size = 14)
    plt.xlabel("Discharge capacity (m3/s)", size= 14)
    plt.title("SDF Curve example",size = 24)
    plt.legend(title = 'Return time [year]')
    plt.savefig(fig_path)


if __name__ == "__main__":
    # provide an auto generated cli based on the functions in this file
    fire.Fire()
