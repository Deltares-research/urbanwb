import math

import fire
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

### RDL 20210503
### Determination of rainfall events, storage events and combined events.
###              The combined events are applied for event separation for measure effectiveness and for SDF Curves (TO BE IMPLEMENTED).
###              Rainfall events are separated by 6 hours no rainfall. Storage events are separated by 1 hour no storage (OWL above target level).
###              If the applied time step size is larger than 6 hours, events are separated by a single time step without rainfall / without storage

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
def making_marks(precipitation, timestep, owl_stor):
      
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

###END RDL 20210503

def ranking(df, x, num):
    """
    According to the event mark, get the sum of x for each event, and then rank the sum from highest to lowest.

    Args:
        df (dataframe): a dataframe to do computations on
        x (string): a header of the dataframe
        num (integer): the total number of events

    Returns:
        (numpy.ndarray): an array of values ranked in a descending order
    """
    rank = np.zeros(num)
    for i in range(num):
        rank[i] = sum(df[df.mark == i][x])
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


def find_corresponding_T_for_array(
    t_array, array, vararr=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 30, 40, 50]
):
    """
    Compute corresponding return period T (i.e. T=1/P, P is the probability of exceedance) for a certain return value in
    an array through linear interpolation, in order to compute an averaged value as runoff frequency reduction factor
    (The algorithm can be modified with the new code in the jupyter notebook despite the same results)

    Args:
        t_array ()
    Returns:
    """
    database = []
    for var in vararr:
        # print(var, 'case:')
        t_value = 0.0
        try:
            for counter, value in enumerate(array):
                if value < var:
                    # print(value)
                    v_below = array[counter]
                    v_above = array[counter - 1]
                    # print('v-above', counter-1, v_above)
                    # print('v-below', counter, v_below)
                    # print('---'*6)
                    t_up = t_array[counter - 1]
                    t_below = t_array[counter]
                    # print('T-up', t_up)
                    # print('T-below', t_below)
                    t_value = t_up - (v_above - var) / (v_above - v_below) * (
                        t_up - t_below
                    )
                    # print('T_value', t_value)
                    break
        except KeyError:
            # print('below',counter, array[counter])
            # print('above',counter, array[counter])
            t_value = math.inf
        finally:
            database.append(t_value)
    return database


def getconstants(inputfilename, num_year=30):
    """
    Get the constant --- Runoff frequency reduction factor averaged over several specified runoff return value.

    Args:
        inputfilename (string): path of the runoff time series resulted from the urbanwb model
        num_year (integer): total number of years of the time series
    """
    m = Analyse(filename=inputfilename, num_year=num_year)
    results = m.getconstants()
    mean_constants = []
    for key in results.keys():
        new_var_array = []
        var_array = results[key]
        for var in var_array:
            if var < 2000:
                new_var_array.append(var)
        if new_var_array is not None:
            mean_constants.append(np.round(np.mean(new_var_array), 2))
    outputfilename = "".join(list(inputfilename)[:-4]) + "_constants.txt"
    print(results)
    # np.savetxt(outputfilename, results, )
    with open(outputfilename, "w") as f:
        for key, value in results.items():
            f.write("%s:%s\n" % (key, value))
        f.write("%s" % mean_constants)


def getconstants_measures(data, owl_stor , num_year=30,timestep=3600):
    """
    Get the constant --- Runoff frequency reduction factor averaged over several specified runoff return value.

    Args:
        inputfilename (string): filename of the runoff time series resulted from the urbanwb model
        num_year (integer): total number of years of the time series
    """
    # TODO consolidate with getconstants above
    m = Analyse(data=data, 
                num_year=num_year,
                timestep=3600, 
                owl_stor = owl_stor)
    results = m.getconstants()
    mean_constants = []
    for key in results.keys():
        new_var_array = []
        var_array = results[key]
        for var in var_array:
            if var < 2000:
                new_var_array.append(var)
        if new_var_array is not None:
            mean_constants.append(np.round(np.mean(new_var_array), 2))
    for i in range(len(mean_constants)):
        if np.isnan(mean_constants[i]) == True or mean_constants[i] > 1000:
            mean_constants[i] = 1000
        else:
            pass
    else:
        pass

    # if there is no change in runoff, then reduction factor = 0 (e.g. at implementing on unpaved when he unpaved area already has no runoff)
    if data[data.keys()[3]].sum() == data["Baseline"].sum():
        mean_constants = [1]
    return results, mean_constants


class Analyse(object):
    """
    Integrate all functions, basically functioning, requiring further development
    """

    def __init__(
        self,
        filename=None,
        data=None,
        num_year=30,
        timestep = 3600,
        owl_stor = None,
    ):
        if filename is None:
            assert data is not None
            self.output_name = "results_measures.csv"
            self.df = data
        elif data is None:
            assert filename is not None
            self.name = filename
            # automatically create output name according to inputname: first remove ".csv" then add "_results.csv"
            self.output_name = "".join(list(self.name)[:-4]) + "_results.csv"
            self.df = pd.read_csv(
                self.name,
            )
        self.df = self.df.fillna(0)
        self.dictionary = self.df.to_dict("list")
        self.num_year = num_year
        self.timestep = timestep
        self.owl_stor = owl_stor
        # making event marks according to new sep
        self.df["mark"] = making_marks(self.df["P_atm"],self.timestep,self.owl_stor["Baseline"])
        self.measure_dictionary = removekey(
            self.dictionary, "Date", "P_atm", "Baseline"
        )
        self.makingranks = self.makingranks()

    def getconstants(
        self,
    ):  # consider changing function name to avoid confusion.
        emp = dict()
        baseT = find_corresponding_T_for_array(
            t_array=self.makingranks["T_list"], array=self.makingranks["Rank_baseline"]
        )
        for key in self.makingranks.keys():
            if key not in ["Rank_P", "T_list", "Rank_baseline"]:
                a = find_corresponding_T_for_array(
                    t_array=self.makingranks["T_list"], array=self.makingranks[key]
                )
                c = [y / x for x, y in zip(baseT, a)]
                emp[key] = c
                np.mean(c)
        return emp

    def save_constants(self):
        pass

    def makingranks(
        self,
    ):
        # unchanged, I made a mistake here, should be self.emp rather than emp. Not a big problem.
        emp = dict()
        emp["Rank_P"] = ranking(self.df, "P_atm", int(max(self.df.mark) + 1))
        # create T list (30 yr, thus starting from (30+1/1) according to Weibull formula)
        emp["T_list"] = [
            (self.num_year + 1) / m for m in range(1, len(emp["Rank_P"]) + 1)
        ]
        # rank runoff on the baseline case
        emp["Rank_baseline"] = ranking(self.df, "Baseline", int(max(self.df.mark) + 1))
        for key in self.measure_dictionary.keys():
            emp[key] = ranking(self.df, key, int(max(self.df.mark) + 1))
        data = pd.DataFrame.from_dict(emp)
        return data

    def save_to_csv(
        self,
    ):
        self.makingranks.to_csv(self.output_name)

    def plotting(
        self,
        measure_name,
        addition_name,
        xlim_down=5,
        xlim_up=20,
    ):
        self.data = self.makingranks

        plt.figure(figsize=(9, 6))
        plt.semilogy(
            self.data.Rank_P, self.data.T_list, "b--", label="Precipitation", ms=2
        )
        plt.semilogy(
            self.data.Rank_baseline, self.data.T_list, "k-", label="Baseline", ms=2
        )
        measures_rank_dictionary = removekey(
            self.data.to_dict("list"), "Rank_P", "Rank_baseline", "T_list"
        )

        for key in measures_rank_dictionary.keys():
            plt.semilogy(
                measures_rank_dictionary[key], self.data.T_list, label=key, ms=2
            )

        x = np.linspace(0, 100, 200)
        # plt.legend(loc='best',frameon=False)
        plt.legend(loc="upper right", frameon=True)
        plt.xlabel("Runoff (mm)")
        plt.ylabel("T (year)")
        plt.title(measure_name)
        plt.xlim(xlim_down, xlim_up)

        # add grid
        ax = plt.gca()
        ax.yaxis.grid(linestyle="--", linewidth=0.5, which="both")
        ax.xaxis.grid(linestyle="--", linewidth=0.5, which="both")

        plt.savefig("figures/" + addition_name + measure_name + ".png")
        
#NEW CODE: NEW CLASS FOR PEAK REDUCTION
## NEW CODE --------------------------------------------------------------------------------------------

def rankingmax(df, x, num):
    """
    According to the event mark, get the maximum of x for each event, and then rank the sum from highest to lowest.
    This is used to calculate the peak factor

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

def find_corresponding_T_for_array_PEAK(
    t_array, array, vararr=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
):
    #TODO: make vararr standard
    """
    Compute corresponding return period T (i.e. T=1/P, P is the probability of exceedance) for a certain return value in
    an array through linear interpolation, in order to compute an averaged value as runoff frequency reduction factor
    (The algorithm can be modified with the new code in the jupyter notebook despite the same results)

    Args:
        t_array ()
    Returns:
    """
    database = []
    
    vararr2 = []   
    for i in range (len(array)):
        if i>5:
            vararr2.append(round(array[i],0))
            if array[i] ==0:
                break
    vararr2 = np.unique(vararr2)
    vararr2 = vararr2[vararr2 != 0]
    
    for var in vararr2:
        # print(var, 'case:')
        t_value = 0.0
        try:
            for counter, value in enumerate(array):
                if value < var:
                    # print(value)
                    v_below = array[counter]
                    v_above = array[counter - 1]
                    # print('v-above', counter-1, v_above)
                    # print('v-below', counter, v_below)
                    # print('---'*6)
                    t_up = t_array[counter - 1]
                    t_below = t_array[counter]
                    # print('T-up', t_up)
                    # print('T-below', t_below)
                    t_value = t_up - (v_above - var) / (v_above - v_below) * (
                        t_up - t_below
                    )
                    # print('T_value', t_value)
                    break
        except KeyError:
            # print('below',counter, array[counter])
            # print('above',counter, array[counter])
            t_value = math.inf
        finally:
            database.append(t_value)
    return database


def getconstants_measures_peak(data, owl_stor , num_year=30,timestep=3600):
    """
    Get the constant --- Peak runoff frequency reduction factor averaged over several specified runoff return value.

    Args:
        inputfilename (string): filename of the runoff time series resulted from the urbanwb model
        num_year (integer): total number of years of the time series
    """
    # TODO consolidate with getconstants above
    m = Analyse_peak(data=data, num_year=num_year,timestep=3600,owl_stor = owl_stor)
    results = m.getconstants()
    mean_constants = []
    for key in results.keys():
        new_var_array = []
        var_array = results[key]
        for var in var_array:
            if var < 2000:
                new_var_array.append(var)
        if new_var_array is not None:
            mean_constants.append(np.round(np.mean(new_var_array), 2))
    for i in range(len(mean_constants)):
        if np.isnan(mean_constants[i]) == True or mean_constants[i] > 1000:
            mean_constants[i] = 1000
        else:
            pass
    else:
        pass

    # if there is no change in runoff, then reduction factor = 0 (e.g. at implementing on unpaved when he unpaved area already has no runoff)
    if data[data.keys()[3]].sum() == data["Baseline"].sum():
        mean_constants = [1]
    return results, mean_constants


class Analyse_peak(object):
    """
    Integrate all functions, basically functioning, requiring further development
    """

    def __init__(
        self,
        filename=None,
        data=None,
        num_year=30,
        timestep = 3600,
        owl_stor = None,
    ):
        if filename is None:
            assert data is not None
            self.output_name = "results_measures.csv"
            self.df = data
        elif data is None:
            assert filename is not None
            self.name = filename
            # automatically create output name according to inputname: first remove ".csv" then add "_results.csv"
            self.output_name = "".join(list(self.name)[:-4]) + "_results.csv"
            self.df = pd.read_csv(
                self.name,
            )
        self.df = self.df.fillna(0)
        self.dictionary = self.df.to_dict("list")
        self.num_year = num_year
        self.timestep = timestep
        self.owl_stor = owl_stor
        # making event marks according to new sep 
        self.df["mark"] = making_marks(self.df["P_atm"],self.timestep,self.owl_stor["Baseline"])
        self.measure_dictionary = removekey(
            self.dictionary, "Date", "P_atm", "Baseline"
        )
        self.makingranks = self.makingranks()

    def getconstants(
        self,
    ):  # consider changing function name to avoid confusion.
        emp = dict()
        baseT = find_corresponding_T_for_array_PEAK(
            t_array=self.makingranks["T_list"], array=self.makingranks["Rank_baseline"]
        )
        for key in self.makingranks.keys():
            if key not in ["Rank_P", "T_list", "Rank_baseline"]:
                a = find_corresponding_T_for_array_PEAK(
                    t_array=self.makingranks["T_list"], array=self.makingranks[key]
                )
                c = [y / x for x, y in zip(baseT, a)]
                emp[key] = c
                np.mean(c)
        return emp

    def save_constants(self):
        pass

    def makingranks(
        self,
    ):
        # unchanged, I made a mistake here, should be self.emp rather than emp. Not a big problem.
        emp = dict()
        emp["Rank_P"] = rankingmax(self.df, "P_atm", int(max(self.df.mark) + 1))
        # create T list (30 yr, thus starting from (30+1/1) according to Weibull formula)
        emp["T_list"] = [
            (self.num_year + 1) / m for m in range(1, len(emp["Rank_P"]) + 1)
        ]
        # rank runoff on the baseline case
        emp["Rank_baseline"] = rankingmax(self.df, "Baseline", int(max(self.df.mark) + 1))
        for key in self.measure_dictionary.keys():
            emp[key] = rankingmax(self.df, key, int(max(self.df.mark) + 1))
        data = pd.DataFrame.from_dict(emp)
        return data

    def save_to_csv(
        self,
    ):
        self.makingranks.to_csv(self.output_name)

    def plotting(
        self,
        measure_name,
        addition_name,
        xlim_down=5,
        xlim_up=20,
    ):
        self.data = self.makingranks

        plt.figure(figsize=(9, 6))
        plt.semilogy(
            self.data.Rank_P, self.data.T_list, "b--", label="Precipitation", ms=2
        )
        plt.semilogy(
            self.data.Rank_baseline, self.data.T_list, "k-", label="Baseline", ms=2
        )
        measures_rank_dictionary = removekey(
            self.data.to_dict("list"), "Rank_P", "Rank_baseline", "T_list"
        )

        for key in measures_rank_dictionary.keys():
            plt.semilogy(
                measures_rank_dictionary[key], self.data.T_list, label=key, ms=2
            )

        x = np.linspace(0, 100, 200)
        # plt.legend(loc='best',frameon=False)
        plt.legend(loc="upper right", frameon=True)
        plt.xlabel("Runoff (mm)")
        plt.ylabel("T (year)")
        plt.title(measure_name)
        plt.xlim(xlim_down, xlim_up)

        # add grid
        ax = plt.gca()
        ax.yaxis.grid(linestyle="--", linewidth=0.5, which="both")
        ax.xaxis.grid(linestyle="--", linewidth=0.5, which="both")

        plt.savefig("figures/" + addition_name + measure_name + ".png")

##Analysis peaks of OWL_storage ==================================================================================

def find_corresponding_T_for_array_owl(
    t_array, array, vararr=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
):
    #TODO: make vararr standard
    """
    Compute corresponding return period T (i.e. T=1/P, P is the probability of exceedance) for a certain return value in
    an array through linear interpolation, in order to compute an averaged value as runoff frequency reduction factor
    (The algorithm can be modified with the new code in the jupyter notebook despite the same results)

    Args:
        t_array ()
    Returns:
    """
    database = []
    
    vararr2 = []   
    for i in range (len(array)):
        if i>5:
            vararr2.append(round(array[i],1))
            if array[i] ==0:
                break
    vararr2 = np.unique(vararr2)
    vararr2 = vararr2[vararr2 != 0]
    
    for var in vararr2:
        # print(var, 'case:')
        t_value = 0.0
        try:
            for counter, value in enumerate(array):
                if value < var:
                    # print(value)
                    v_below = array[counter]
                    v_above = array[counter - 1]
                    # print('v-above', counter-1, v_above)
                    # print('v-below', counter, v_below)
                    # print('---'*6)
                    t_up = t_array[counter - 1]
                    t_below = t_array[counter]
                    # print('T-up', t_up)
                    # print('T-below', t_below)
                    t_value = t_up - (v_above - var) / (v_above - v_below) * (
                        t_up - t_below
                    )
                    # print('T_value', t_value)
                    break
        except KeyError:
            # print('below',counter, array[counter])
            # print('above',counter, array[counter])
            t_value = math.inf
        finally:
            database.append(t_value)
    return database


#getting constants for storage peak frequency reduction factor
def getconstants_measures_owl(data, owl_stor , num_year=30,timestep=3600):
    """
    Get the constant --- Storage frequency reduction factor averaged over several specified runoff return value.

    Args:
        inputfilename (string): filename of the runoff time series resulted from the urbanwb model
        num_year (integer): total number of years of the time series
    """
    # TODO consolidate with getconstants above
    m = Analyse_owl(data=data, num_year=num_year,timestep=3600,owl_stor = owl_stor)
    results = m.getconstants()
    mean_constants = []
    for key in results.keys():
        new_var_array = []
        var_array = results[key]
        for var in var_array:
            if var < 2000:
                new_var_array.append(var)
        if new_var_array is not None:
            mean_constants.append(np.round(np.mean(new_var_array), 2))
    for i in range(len(mean_constants)):
        if np.isnan(mean_constants[i]) == True or mean_constants[i] > 1000:
            mean_constants[i] = 1000
        else:
            pass
    else:
        pass

    # if there is no change in runoff, then reduction factor = 0 (e.g. at implementing on unpaved when he unpaved area already has no runoff)
    if data[data.keys()[3]].sum() == data["Baseline"].sum():
        mean_constants = [1]
    return results, mean_constants


#analysis for storage peaks        
class Analyse_owl(object):
    """
    Integrate all functions, basically functioning, requiring further development
    """

    def __init__(
        self,
        filename=None,
        data=None,
        num_year=30,
        timestep = 3600,
        owl_stor = None,
    ):
        if filename is None:
            assert data is not None
            self.output_name = "results_measures.csv"
            self.df = data
        elif data is None:
            assert filename is not None
            self.name = filename
            # automatically create output name according to inputname: first remove ".csv" then add "_results.csv"
            self.output_name = "".join(list(self.name)[:-4]) + "_results.csv"
            self.df = pd.read_csv(
                self.name,
            )
        self.df = self.df.fillna(0)
        self.dictionary = self.df.to_dict("list")
        self.num_year = num_year
        self.timestep = timestep
        self.owl_stor = owl_stor
        
        # making event marks according to new sep (6 consective zeros as separation)
        self.df["mark"] = making_marks(self.df["P_atm"],self.timestep,self.owl_stor["Baseline"])
        self.measure_dictionary = removekey(
            self.dictionary, "Date", "P_atm", "Baseline"
        )
        self.makingranks = self.makingranks()

    def getconstants(
        self,
    ):  # consider changing function name to avoid confusion.
        emp = dict()
        baseT = find_corresponding_T_for_array_owl(
            t_array=self.makingranks["T_list"], array=self.makingranks["Rank_baseline"]
        )
        for key in self.makingranks.keys():
            if key not in ["Rank_P", "T_list", "Rank_baseline"]:
                a = find_corresponding_T_for_array_owl(
                    t_array=self.makingranks["T_list"], array=self.makingranks[key]
                )
                c = [y / x for x, y in zip(baseT, a)]
                emp[key] = c
                np.mean(c)
        return emp

    def save_constants(self):
        pass

    def makingranks(
        self,
    ):
        # unchanged, I made a mistake here, should be self.emp rather than emp. Not a big problem.
        emp = dict()
        emp["Rank_P"] = rankingmax(self.df, "P_atm", int(max(self.df.mark) + 1))
        # create T list (30 yr, thus starting from (30+1/1) according to Weibull formula)
        emp["T_list"] = [
            (self.num_year + 1) / m for m in range(1, len(emp["Rank_P"]) + 1)
        ]
        # rank runoff on the baseline case
        emp["Rank_baseline"] = rankingmax(self.df, "Baseline", int(max(self.df.mark) + 1))
        for key in self.measure_dictionary.keys():
            emp[key] = rankingmax(self.df, key, int(max(self.df.mark) + 1))
        data = pd.DataFrame.from_dict(emp)
        return data

    def save_to_csv(
        self,
    ):
        self.makingranks.to_csv(self.output_name)

    def plotting(
        self,
        measure_name,
        addition_name,
        xlim_down=5,
        xlim_up=20,
    ):
        self.data = self.makingranks

        plt.figure(figsize=(9, 6))
        plt.semilogy(
            self.data.Rank_P, self.data.T_list, "b--", label="Precipitation", ms=2
        )
        plt.semilogy(
            self.data.Rank_baseline, self.data.T_list, "k-", label="Baseline", ms=2
        )
        measures_rank_dictionary = removekey(
            self.data.to_dict("list"), "Rank_P", "Rank_baseline", "T_list"
        )

        for key in measures_rank_dictionary.keys():
            plt.semilogy(
                measures_rank_dictionary[key], self.data.T_list, label=key, ms=2
            )

        x = np.linspace(0, 100, 200)
        # plt.legend(loc='best',frameon=False)
        plt.legend(loc="upper right", frameon=True)
        plt.xlabel("Runoff (mm)")
        plt.ylabel("T (year)")
        plt.title(measure_name)
        plt.xlim(xlim_down, xlim_up)

        # add grid
        ax = plt.gca()
        ax.yaxis.grid(linestyle="--", linewidth=0.5, which="both")
        ax.xaxis.grid(linestyle="--", linewidth=0.5, which="both")

        plt.savefig("figures/" + addition_name + measure_name + ".png")

if __name__ == "__main__":
    fire.Fire(getconstants)
