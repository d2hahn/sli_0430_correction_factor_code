import pandas as pd
from pathlib import Path

#reading in sorted data from flow_meter_fr_and_meas_fr_to_csv for both the positive and negative flow case
#creating path varaibles of the folders where the .csv files are stored
p_pos = Path('./outputs/correction_data_for_fitting/positive_q/')
p_neg = Path('./outputs/correction_data_for_fitting/negative_q/')

#reading paths of all csv files in the paths described above into lists of paths
csv_pos = list(p_pos.glob('./*.csv'))
csv_neg = list(p_neg.glob('./*.csv'))

#creating dictionary of dataframes with key-value pair: 'visc_cSt': dataframe from csv files for positive_q
dict_of_pos_data ={}
for path in csv_pos:

    path_str = str(path)
    removal_str = 'outputs\\correction_data_for_fitting\\positive_q\\'
    edit = path_str.replace(removal_str,'')
    key = edit.replace('.csv','')

    dict_of_pos_data[key] = pd.read_csv(path, index_col=0)

#creating dictionary of dataframes with key-value pair: 'visc_cSt': dataframe from csv files for negative_q
dict_of_neg_data ={}
for path in csv_neg:

    path_str = str(path)
    removal_str = 'outputs\\correction_data_for_fitting\\negative_q\\'
    edit = path_str.replace(removal_str,'')
    key = edit.replace('.csv','')

    dict_of_neg_data[key] = pd.read_csv(path, index_col=0)

#creating dictionary of combined df's of data in ascending order i.e -Q_max to +Q_max
dict_of_combined_df = {}
for key in dict_of_pos_data:
    df_pos = dict_of_pos_data[key]
    df_neg = dict_of_neg_data[key]

    df_neg_flipped = df_neg.iloc[::-1]
    df_neg_flipped = df_neg_flipped.reset_index()
    df_neg_flipped = df_neg_flipped.drop(['index'], axis=1)

    df_combined = pd.concat([df_neg_flipped, df_pos])
    dict_of_combined_df[key] = df_combined

#outputting df's to .csv files in ./outputs/combined_pos_neg_q
question = input('Output dataframes as .csv files? (y/n): ')
while question != 'y' and question !='n':
    question = input("please input 'y' or 'n': ")
if question == 'y':
    for visc in dict_of_combined_df:
        df = dict_of_combined_df[visc]
        df.to_csv('./outputs/combined_pos_neg_q/'+'/'+visc+'.csv')
elif question =='n':
    print('results not output to .csv')

