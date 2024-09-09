"""
Title: flow_rate_meas_to_avg.py

Summary:
Program intakes the .csv files produced for calibration of the SLI-0430 flow sensor using the fluigent (0-1 bar) pressure
pump. The input files ,.csv, came from the sensiron flow viewer software for the USB connection. Where each input file
is the flow rate data at a constant pressure (named pressure_mbar.csv, where pressure = a number). Program outputs a
.csv file of the form:

[Pressure [mbar], # of Samples, Avg. Flow [uL/min], u_sli_o [uL/min], u_sli_1 [uL/min]] ; # of Samples = # of samples of flow rate takem, Avg.Flow = average of all flow rate measurements

for each viscosity case, in ./outputs/avg_flow_rate_from_meas/frcase/, where frcase = negative_q or positive_q.
Program assumes that viscosities of the fluids are in cSt (like for silicone oil) and path for input file is of the form:

../../data/si_oil/flow_rate_measurements/flow_case/visc_visc_value_cSt.csv

Where,
flow_case ~ positive_q or negative_q
visc_value ~ value of viscosity of oil tested in cSt

Output of code is to be used in program to calculate correction factor for output flow rate from SLI 0430 flow sensor.

Dependencies:
1. Path from pathlib
2. numpy
3. pandas
4. csv
5. sensiron_first_order_uncertainty from functions.py

Notes:
    1. must specify flow case, and viscosity on each run (lines 47 and 50)
    2. for general use of program will want to change path of input data, p, and path of removal string, removal_string
        (see lines 54, 67)
    3. program outputs both zero and first order uncertainty in .csv file, to add higher order uncertainties one must
        edit/create uncertainty functions in functions.py

"""


from pathlib import Path
import numpy as np
import pandas as pd
import csv
from functions import sensiron_zero_order_uncertainty, sensiron_first_order_uncertainty

#specify flow case (negative_q or positive_q) (change on each run)
flow_case = 'positive_q'

#specify viscosity of Si oil (5,10,20,50,100 cSt) (change on each run)
viscosity = 5


#input path of folder where csv files are stored
p = Path('../../data/si_oil/flow_rate_measurements/' + flow_case +'/visc_' + str(viscosity)+'_cSt/')

#create list of paths of csv files in the path directory specified in above line
csv_paths = list(p.glob('./*.csv'))

#create empty dictionary to hold edited csv data as dataframe, key-value pair: ['pressure_in_mbar': dataframe_for_given_pressure]
dict_of_edited_csvs = {}

for path in csv_paths:
    #converting path to string
    p_str = str(path)

    #creating name of key for dictionary (equal to value of pressure in mbar)
    removal_string = '..\\..\\data\\si_oil\\flow_rate_measurements\\'+flow_case+'\\'+'visc_'+str(viscosity)+'_cSt' # will need to change for different path of input data
    edit_one = p_str.replace(removal_string,'')
    edit_two = edit_one.lstrip(r'\'')
    key_title =edit_two.strip('_mbar.csv')

    #edit .csv file output from sensiron flow sensor software (remove unecessary lines)
    #create empty list to store each row of .csv file
    list_of_csv_rows = []

    #open given .csv file
    with open(p_str, newline='') as csvfile:

        #create reader object
        reader = csv.reader(csvfile)

        #append each row of .csv file to list_of_csv_rows
        for row in reader:
            list_of_csv_rows.append(row)

        #close .csv file
        csvfile.close()
    #create list of column names
    col_names = list_of_csv_rows[14]

    #create numpy array for all measurement data
    data_array = np.array(list_of_csv_rows[15:len(list_of_csv_rows)]) #dtype=float)

    #create pandas dataframe of form [Sample # Relative Time[s] Flow [ul/min]]
    df = pd.DataFrame(data_array, columns=col_names)
    df = df.dropna()

    #convert columns to ints and floats
    df['Sample #'] = df['Sample #'].astype(int)
    df['Relative Time[s]']=df['Relative Time[s]'].str.replace(',','').astype(float)
    df['Flow [ul/min]']=df['Flow [ul/min]'].astype(float)

    #add dataframe to dictionary
    dict_of_edited_csvs[key_title] = df

'''
for each dataframe in dictionary calculate the average flow rate, total number of samples, and first order uncertainty
create new dataframe of form:

['Pressure [mbar]' '# of Samples' 'Avg. Flow [uL/min]' 'u_sli_o [uL/min]' 'u_sli_1 [uL/min]']

see sensiron_first_order_uncertainty fn in functions.py
'''
dict_of_avg_flow_w_u_1 =  sensiron_first_order_uncertainty(dict_of_edited_csvs, flow_meter='SLI-0430', bits=11)

# #creating empty dictionary to store average values of flow rate and # of samples for each pressure case
# dict_of_avg_flow ={}
#
# for key in dict_of_edited_csvs:
#
#     #obtaining flow and sample values from dataframe
#     flow_array = dict_of_edited_csvs[key]['Flow [ul/min]'].values
#     sample_series_array = dict_of_edited_csvs[key]['Sample #'].values
#
#     #calculating average flow rate
#     avg_flow = np.average(flow_array)
#
#     #calculating total number of samples
#     num_samples = len(sample_series_array)
#
#     #adding to dict_of_avg_flow
#     dict_of_avg_flow[key] = [int(key), num_samples, avg_flow]

#creating dataframe of form ['Pressure [mbar]' '# Samples' 'Avg. Flow [uL/min]' 'u_sli_o [uL/min]' 'u_sli_1 [uL/min]']
column_names = ['Pressure [mbar]', '# Samples', 'Avg. Flow [uL/min]','u_sli_o [uL/min]', 'u_sli_1 [uL/min]' ]
avg_flow_df = pd.DataFrame.from_dict(dict_of_avg_flow_w_u_1, orient='index', columns=column_names)

#sorting avg_flow_df in ascending order
avg_flow_df_sort = avg_flow_df.sort_values('Pressure [mbar]')

#resetting index
avg_flow_df_sort=avg_flow_df_sort.reset_index()
avg_flow_df_sort= avg_flow_df_sort.drop(['index'], axis=1)

print(avg_flow_df_sort)

#output dataframe to .csv file
question_one = input("Output dataframe of average flow rates at tested pressures as .csv file? (y/n): ")
while question_one !='y' and question_one != 'n':
    question_one = input("please input 'y' or 'n': ")
if question_one == 'y':
    check_one = input('This is for test ' + flow_case + ' '+ str(viscosity) + ' cSt is this the case you want to output? (y/n): ')
    while check_one !='y' and check_one !='n':
        check_one = input("please input 'y' or 'n': ")
    if check_one =='y':
        avg_flow_df_sort.to_csv('./outputs/avg_flow_rate_from_meas/'+flow_case+'/'+str(viscosity)+'_cSt.csv')
    if check_one == 'n':
        print(flow_case + ' '+ str(viscosity) + ' cSt has not been output to .csv')
else:
    print(flow_case + ' '+ str(viscosity) + ' cSt has not been output to .csv')
