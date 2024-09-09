"""
Title: flow_meter_fr_and_meas_fr_to_csv.py

Summary:
Code intakes .csv files created by :
1) flow_rate_meas_to_avg.py (in ./outputs/avg_flow_rate_from_meas/flow_case/), of form:

[[Pressure [mbar], # of Samples, Avg. Flow [uL/min], u_sli_o [uL/min], u_sli_1 [uL/min]] (average flow measurement from sensiron software for given test pressure w uncertainty)

2) mass_fr_to_vol_fr.py (in ./outputs/v_fr_from_m_fr/flow_case/), of form:

[P[mbar], m_dot [kg/s], Q [uL/min], u_q_vl [uL/min]] (mass flow rate and volumetric flow rate determined from measured mass difference over a specified time w uncertainty)

Where flow_case = positive_q or negative_q. Code outputs .csv files into ./outputs/correction_data_for_fitting/flow_case/
of form

[P [mbar] Q_sli [uL/min] Q_mass_meas [uL/min], u_q_sli [uL/min], u_q_sli_rel [%],Q_mass_meas [uL/min] ,u_q_m [uL/min], u_q_m_rel [%]]

Where,
Q_sli = Avg. Flow from sensirion measurements
Q_mass_meas = Q from mass difference over time interval measurements
u = uncertainty
u_rel = relative uncertainty

This output .csv file is then to be used for plotting of Q_mass_meas = f(Q_sli) and for OLS estimation of an appropriate correction
factor model for true flow rate measurements of a fluid that is not calibrated for a given sensiron flow meter.

Dependencies:
1. Path from pathlib
2. pandas

Notes:
    1. Program assumes that files in ./outputs/avg_flow_rate_from_meas/flow_case/ are named as visc_cSt.csv
    2. Program assumes that files in ./outputs/v_fr_from_m_fr/flow_case/ are named as visc_cSt_density_kh_per_m_cubed.csv
        2a) Program uses conditional to edit file names for use, visc_cSt_density_kh_per_m_cubed.csv, as keys for
            a dictionary, however this is not a general edit and the specific value of visc_cSt_density must be entered
            (see lines
"""

from pathlib import Path
import pandas as pd


#specify flow case (negative_q or positive_q) (change on each run)
flow_case = 'positive_q'

#input paths of folders where csv files are stored
p_meas = Path('./outputs/avg_flow_rate_from_meas/'+flow_case+'/')
p_v_fr_from_m_fr = Path('./outputs/v_fr_from_m_fr/'+flow_case+'/')

#create list of paths of csv files in the path directory specified in above line
csv_paths_meas = list(p_meas.glob('./*.csv'))
csv_paths_v_fr = list(p_v_fr_from_m_fr.glob('./*.csv'))

#creating dictionary of dataframe representing each viscosity case for the data from sensiron software
dict_of_meas_df ={}
for path in csv_paths_meas:
    #creating name of key for diciotnary to be visc_cSt
    path_str = str(path)
    removal_str = 'outputs\\avg_flow_rate_from_meas\\'+flow_case+'\\'
    csv_removal = '.csv'
    edit = path_str.replace(removal_str,'')
    key = edit.replace(csv_removal,'')

    #creating datframe for given csv file
    df = pd.read_csv(path, index_col = 0)

    #appending dataframe to dictionary
    dict_of_meas_df[key] = df


#creating dictionary of dataframe representing each viscosity case for the calculated volume flow rates from the mass data
dict_v_fr_df ={}
for p in csv_paths_v_fr:
    #creating name of key for diciotnary to be visc_cSt
    pstr=str(p)
    front_remove_str = 'outputs\\v_fr_from_m_fr\\'+flow_case+'\\'
    back_remove_str = '_kg_per_m_cubed.csv'
    edit_v_fr=pstr.replace(front_remove_str,'')
    edit_v_fr_2 = edit_v_fr.replace(back_remove_str,'')

    #print(edit_v_fr_2)
    #changing key name to just be viscosity like for the flow rate measured from the sli device (not very general at the moment)
    if edit_v_fr_2 =='100_cSt_960':
        key_v_fr = edit_v_fr_2.replace('_960','')
    elif edit_v_fr_2 =='50_cSt_960':
        key_v_fr = edit_v_fr_2.replace('_960','')
    elif edit_v_fr_2 =='20_cSt_950':
        key_v_fr = edit_v_fr_2.replace('_950','')
    elif edit_v_fr_2 =='10_cSt_930':
        key_v_fr = edit_v_fr_2.replace('_930','')
    elif edit_v_fr_2 =='5_cSt_913':
        key_v_fr = edit_v_fr_2.replace('_913','')

    #creating dataframe for given csv file
    df_v_fr = pd.read_csv(p, index_col = 0)

    #appending dataframe to dictionary
    dict_v_fr_df[key_v_fr] = df_v_fr

#creating dictionary of dataframes of form [P [mbar], Q_sli [uL/min], u_q_sli [uL/min], u_q_sli_rel [%],Q_mass_meas [uL/min] ,u_q_m [uL/min], u_q_m_rel [%]]
dict_of_combined_df = {}
for keys in dict_of_meas_df:

    df_meas = dict_of_meas_df[keys]
    df_v_fr_from_m_fr = dict_v_fr_df[keys]
    df_combined =  pd.DataFrame({'P [mbar]': df_meas['Pressure [mbar]'], 'Q_sli [uL/min]': df_meas['Avg. Flow [uL/min]'],'u_q_sli [uL/min]': df_meas['u_sli_1 [uL/min]'], 'u_q_sli_rel [%]':((df_meas['u_sli_1 [uL/min]']/abs(df_meas['Avg. Flow [uL/min]']))*100) })
    if flow_case =='negative_q':
        df_combined['Q_mass_meas [uL/min]'] = -1*df_v_fr_from_m_fr['Q [uL/min]']
    elif flow_case =='positive_q':
        df_combined['Q_mass_meas [uL/min]'] = df_v_fr_from_m_fr['Q [uL/min]']

    df_combined['u_q_m [uL/min]'] = df_v_fr_from_m_fr['u_q_vl [uL/min]']
    df_combined['u_q_m_rel [%]'] = df_v_fr_from_m_fr['u_q_vl [uL/min]']/abs(df_v_fr_from_m_fr['Q [uL/min]'])*100

    #appending combined df to dict_of_combined_df
    dict_of_combined_df[keys] = df_combined

#outputting combined dfs as .csv files
#give user option to output to .csv
question = input("output results to .csv? (y/n): ")
while question != 'y' and question !='n':
    question = input("please input 'y' or 'n': ")
if question == 'y':
    for visc in dict_of_combined_df:
        df = dict_of_combined_df[visc]
        df.to_csv('./outputs/correction_data_for_fitting/'+flow_case+'/'+visc+'.csv')
elif question =='n':
    print('results not output to .csv')



