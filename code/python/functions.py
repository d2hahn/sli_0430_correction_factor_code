
import pandas as pd
import numpy as np
import math as m

"""
Function: sensiron_zero_order_uncertatinty(dict_of_df,flow_meter='SLI-0430', bits =11)

Summary:
Function intakes a dictionary of dataframes (key-value pair {'pressure_in_mbar': dataframe_for_given_pressure}) of form:

[Sample # Relative Time[s] Flow [ul/min]]

along with a given sensiron flow meter and the resolution at which the data was sampled to calculate the zeroth order
uncertainty of each flow rate measurement obtained using the sensiron software and outputs a new dictionary of the form
{'pressure_in_mbar': dataframe_for_given_pressure} with dataframes of the form 

[Sample # Relative Time[s] Flow [ul/min] u_sli_o [uL/min]]

Inputs:
1. dict_of_df, dictionary of dataframes of the form [Sample # Relative Time[s] Flow [ul/min]]
2. flow_meter, type of sensiron flow meter used, currently only data for SLI-0430 is considered in fn
3. bits, resolution at which the sampling of the data was done in the sensiron viewer software

Notes:
1. For new sensiron flow meters must add a new conditonal case for the accuracy, full-scale, full range, etc. 

"""

def sensiron_zero_order_uncertainty(dict_of_df,flow_meter='SLI-0430', bits =11):
    if flow_meter == 'SLI-0430':
        full_scale = 1000 #uL/min
        full_range = 1200 #uL/min
        fs_acc_percent = 0.01
        mv_acc_percent = 0.20
    fs_acc = fs_acc_percent*full_scale
    resolution = (full_range/(2**bits-1))
    precision = 0.5*resolution

    dict_of_df_w_zero_order_uncertainty ={}

    for key in dict_of_df:
        df =dict_of_df[key]
        flow = df['Flow [ul/min]'].values
        flow_mv_acc = abs(flow*mv_acc_percent)
        flow_acc = np.where(flow_mv_acc>fs_acc, flow_mv_acc,fs_acc)
        u_sli_o = np.sqrt(np.square(flow_acc)+(precision)**2)
        df['u_sli_o [uL/min]'] = u_sli_o
        dict_of_df_w_zero_order_uncertainty[key] = df
    return(dict_of_df_w_zero_order_uncertainty)

'''
********************************************END OF FUNCTION************************************************************
'''

"""
Function: sensiron_first_order_uncertatinty(dict_of_df,flow_meter='SLI-0430', bits =11)

Summary:
Function intakes a dictionary of dataframes (key-value pair {'pressure_in_mbar': dataframe_for_given_pressure}) of form:

[Sample # Relative Time[s] Flow [ul/min]]

along with a given sensiron flow meter and the resolution at which the data was sampled to calculate the first order
uncertainty of each flow rate measurement obtained using the sensiron software and outputs a new dictionary of the form
{'pressure_in_mbar': list} with lists of the form 

[Pressure [mbar], # of Samples, Avg. Flow [uL/min], u_sli_o [uL/min], u_sli_1 [uL/min]]

Inputs:
1. dict_of_df, dictionary of dataframes of the form [Sample # Relative Time[s] Flow [ul/min]]
2. flow_meter, type of sensiron flow meter used, currently only data for SLI-0430 is considered in fn
3. bits, resolution at which the sampling of the data was done in the sensiron viewer software

Notes:
1. For new sensiron flow meters must add a new conditonal case for the accuracy, full-scale, full range, etc. 

"""

def sensiron_first_order_uncertainty(dict_of_df,flow_meter='SLI-0430', bits =11):
    if flow_meter == 'SLI-0430':
        full_scale = 1000 #uL/min
        full_range = 1200 #uL/min
        fs_acc_percent = 0.01
        mv_acc_percent = 0.20
    fs_acc = fs_acc_percent*full_scale
    resolution = (full_range/(2**bits-1))
    precision = 0.5*resolution

    dict_of_avg_flow_w_first_order_u = {}
    for key in dict_of_df:
        df =dict_of_df[key]
        flow = df['Flow [ul/min]'].values

        #calculating average flow rate from measurements
        avg_flow = np.mean(flow)

        #calculating std.dev of measurements
        std_dev = np.std(flow,ddof=1)

        #calculating total number of samples
        num_samples = len(flow)

        #calculating zeroth order uncertainty
        flow_mv_acc = abs(avg_flow*mv_acc_percent)
        if flow_mv_acc > fs_acc:
            flow_acc = flow_mv_acc
        else:
            flow_acc = fs_acc
        u_sli_o = m.sqrt((flow_acc**2)+(precision)**2)

        #calculating first order uncertainty
        u_sli_t  = (2*std_dev)/m.sqrt(num_samples)
        u_sli_1 = m.sqrt((u_sli_o**2)+(u_sli_t**2))

        dict_of_avg_flow_w_first_order_u[key] = [int(key), num_samples, avg_flow, u_sli_o, u_sli_1]
    return dict_of_avg_flow_w_first_order_u
'''
********************************************END OF FUNCTION************************************************************
'''

