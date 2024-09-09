"""
Title: mass_fr_to_vol_fr.py

Summary:
Code intakes .csv files containing the mass flow rate data for use in developing correction factor for fluids measured with
the SLI-0430 flow meter from sensiron. Intakes the .csv files, which are of the form:

[P [mbar], Measurement Time [s], M_i [g], M_f [g]]

assumed to have naming convention visc_(visc_val)_cSt_mass_(fr_case).csv where,

(visc_val) = value of viscosity of fluid in centistokes
(fr_case) = n_q or p_q for positive and negative flow rate setups respectively.

the path used for the original set of data used in this code is:
'../../data/si_oil/mass_balance_measurements/'+ flow_case+'/' ; flow_case = negative_q or positive_q

These files are to be created manually from measured data during flow rate correction experiments. Output of this code is
the calculated mass flow rate and volume flow rate from the experimental measurements. Of the form:

[P[mbar], m_dot [kg/s], Q [uL/min], u_q_vl [uL/min]]

saved to ./outputs/v_fr_from_m_fr/(fr_case)/(visc_val)_cSt_density_kg_per_m_cubed

 Where:

m_dot [kg/s] = (M_f - M_i)[g]/(Measurement Time [s])*(1 kg/1000 g)
Q [m^3/s] = m_dot[kg/s]/density[kg/m^3]
Q [uL/min] = Q[m^3/s]*{1000L/1m^3]*[60s/1min]*[10^6 uL/1L]
density = [913, 930,950, 960, 960] for 5, 10, 20, 50, 100 cSt Si oil respectivley (from sigma aldrich)

Output of code is to be used in program to calculate correction factor for output flow rate from SLI 0430 flow sensor.

Dependencies:
1. Path from pathlib
2. pandas

Notes:
    1. must change flow_case for positive_q or negative_q measurements (see line 57)
    2. need to change path,p, from which input files are taken if you want to use different measurement data (see line 70)
    3. must change removal_str_1 if path, p, is changed (see line 80)
    4. must change values of density, rho, for a given viscosity if fluid is not Si oil, may also want to make it a non-conditional
        statement if only one fluid is considered (see lines 99-108)
    5. Uncertainty in density value is not considered in calculation of u_q_vl (manufacturer did not have any data on the
        uncertainty in their stated density and I did not measure the density myself). Easy to include in main for loop,
        would just need to change the density for each si oil case and add a line calculating the density uncertainty
        and add this uncertainty multiplied by its associated sensitivity to the u_q_vl calculation and take the root sum
        square of the values.

"""


from pathlib import Path
import pandas as pd

#specify flow case (negative_q or positive_q) (change on each run)
flow_case = 'negative_q'

#create variable for end of string (given by file nameing convention visc_5_cSt_mass_(n or p)_q.csv) based on value of flow_case
if flow_case == 'negative_q':
    end_of_csv = '_mass_n_q.csv'
elif flow_case == 'positive_q':
    end_of_csv = '_mass_p_q.csv'
else:
    end_of_csv = 'retry'
    print("please input 'negative_q' or 'positive_q'")

if end_of_csv !='retry':
    #input path of folder where csv files are stored
    p = Path('../../data/si_oil/mass_balance_measurements/'+ flow_case+'/') #will need to change for different path of files

    #create list of paths of csv files in the path directory specified in above line
    csv_paths = list(p.glob('./*.csv'))

    #creating dictionary of dataframes for mass data entered into excel for each viscosity
    dict_of_csvs ={}

    for path in csv_paths:
        str_path = str(path)
        removal_str_1 = '..\\..\\data\\si_oil\\mass_balance_measurements\\'+flow_case+'\\visc_' #will need to change for general runs
        removal_str_2 = end_of_csv
        edit_one = str_path.replace(removal_str_1,'')
        key_title = edit_one.replace(removal_str_2,'')
        df = pd.read_csv(path)
        dict_of_csvs[key_title] = df

    # calculating mass flow rate [kg/s] and volumetric flow rate [uL/min] for each viscosity case
    dict_of_frs={}

    for key in dict_of_csvs:
        #accessing dataframe at given key
        df = dict_of_csvs[key]

        # creating df for output
        output_df = pd.DataFrame(df['P [mbar]'])

        #determing density [kg/m^3] of oil given its viscosity (on bottle and sigma_aldrich website) [kg/m^3] value given in laminar_flow_rate_calcs.xlsx
        #change to single value if only one fluid considered or change values if multiple viscosities of same fluid considered
        if key == '5_cSt':
            rho = 913
        elif key == '10_cSt':
            rho = 930
        elif key == '20_cSt':
            rho = 950
        elif key == '50_cSt':
            rho = 960
        elif key =='100_cSt':
            rho = 960

        print(key + ', density: '+ str(rho))

        #calculating mass difference
        df['M_diff [kg]'] = (df['M_f [g]'] - df['M_i [g]'])*(1/1000)

        #calculating mass flow rate [kg/s]
        df['m_dot [kg/s]'] = df['M_diff [kg]']/df['Measurement Time [s]']

        #calculating uncertainty in mass flow rate
        df['u_m_dot [kg/s]'] = df['M_diff [kg]']/(df['Measurement Time [s]']*df['Measurement Time [s]'])*0.005

        #print(df)
        #calculating volume flow rate [m^3/s] (Q =m_dot/rho)
        q_m_cubed_per_s = df['m_dot [kg/s]']/rho

        #calculating uncertainty in volume flow rate
        u_q_vl = (1/rho)*df['u_m_dot [kg/s]']

        #converting vol fr to [uL/min] (Q [uL/min] = Q[m^3/s]*{1000L/1m^3]*[60s/1min]*[10^6 uL/1L])
        q_ul_per_min = q_m_cubed_per_s*(60000*10**6)
        u_q_ul_per_min = u_q_vl*(60000*10**6)

        #creating output_df
        output_df['m_dot [kg/s]'] = df['m_dot [kg/s]']
        output_df['u_m_dot [kg/s]'] = df['u_m_dot [kg/s]']
        output_df['Q [uL/min]'] = q_ul_per_min
        output_df['u_q_vl [uL/min]'] = u_q_ul_per_min
        #print(output_df)

        #add output df to dictionary
        dict_of_frs[key+'_'+str(rho)+'_kg_per_m_cubed'] = output_df

    #give user option to output to .csv
    question = input("output results to .csv? (y/n): ")
    while question != 'y' and question !='n':
        question = input("please input 'y' or 'n': ")
    if question == 'y':
        for key in dict_of_frs:
            df = dict_of_frs[key]
            df.to_csv('./outputs/v_fr_from_m_fr/'+flow_case+'/'+key+'.csv')
    elif question =='n':
        print('results not output to .csv')
