"""
Title: plotting_and_ls_combined.py

Summary:
Code intakes .csv files created by flow_meter_fr_and_meas_fr_to_csv.py (in ./outputs/combined_pos_neg_q)
of form:

[P [mbar] Q_sli [uL/min] Q_mass_meas [uL/min], u_q_sli [uL/min], u_q_sli_rel [%],Q_mass_meas [uL/min] ,u_q_m [uL/min], u_q_m_rel [%]]

and applies OLS estimation to fit a correction relationship between the flow rate measured by the sensirion flow meter
, Q_sli, for IPA calibration, and the true flow rate of the fluid, Q_mass_meas, where this relationship is of the form:

Q_actual = B_1*Q_sli + B_o

OLS estimation is performed using statsmodels.api, which is a library used to streamline least squares analysis in python.
In this case the library is used for a general linear model of the form:

y = XB+e

Where,
y=NX1 response vector (Measured Responses)
X=NXM model matrix (known constants, either predetermined or measured)
B=MX1 parameter vector
e = NX1 normal error vector(~N(0,I*sigma^2)

For OLS estimation, the Best Linear Unbiased Estimator (BLUE) is

B_hat = (X^T*X)^-1*X^T*y

The estimate of the error variance (sigma_hat^2) is

sigma_hat^2 = sum((y_i-y_hat_i)^2)/(n-r) = SSE/(n-r)

where,
n= number of observations
r = rank of X

The estimate of the covariance matrix of the parameters is given by

cov_hat(B_hat) = (X^T*X)^-1*sigma_hat^2

where the diagonal of the covariance matrix is the variance of each parameter

Proportion of variance explained by regression (coeffecient of determination), R^2 is calculated by

R^2 = (sum((y_i-y_bar)^2)-sum((y_i-y_hat_i)^2))/sum((y_i-y_bar)^2) = (SST-SSE)/SST

Program determines the above values, then makes plots for each viscosity of a given flow case of Q_actual vs. Q_measured
where both the measured values (and their uncertainties) and a line of the estimate are plotted. Also included on the plot is the relationship equation
with estimated parameters and the R^2 value for each case. Program also outputs the value of the parameters as .csv files
to ./outputs/estimated_parameters/flow_case/visc_cSt.csv. (will include uncertainty in output and graphs)

Dependencies:
1. matplotlib.pyplot
2. pandas
3. Path from pathlib
4. numpy
5. statsmodels.api

Notes:


"""

import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path
import numpy as np
import statsmodels.api as sm


# specify path of data to use for correction fitting
p = Path('./outputs/combined_pos_neg_q/')

# create list of paths of csv files in the path directory specified in above line
csv_paths = list(p.glob('./*.csv'))

# creating dictionary of dataframes for each set of correction data with key value pair {visc: df}
dict_of_combined_data = {}
for path in csv_paths:
    # creating a variable that is the path in string form
    p_str = str(path)
    # editing string form of path to be of form visc_cSt for use as key in dictionary, key form: visc_cSt
    edit = p_str.replace('outputs\\combined_pos_neg_q\\','')
    key = edit.replace('.csv', '')

    # creating dataframe from .csv file at path
    df = pd.read_csv(path, index_col=0)
    # adding dataframe to dictionary
    dict_of_combined_data[key] = df

# plotting Q_mass_meas = f(Q_sli) for each dataframe in dict_of_correction_data as well as performing OLS estimation and
#obtaing value of parameters and uncertainty at 95% confidence
dict_of_params_and_uncert = {}
for key in dict_of_combined_data:

    # accessing dataframe
    df = dict_of_combined_data[key]

    # accessing calculated average flow rate data from sensiron software output and its uncertainty
    q_sli_exp_data = df['Q_sli [uL/min]']
    u_q_sli = df['u_q_sli [uL/min]']

    # accessing flow rates calculated from mass measurements and its uncertainty
    q_mass_meas_exp_data = df['Q_mass_meas [uL/min]']
    u_q_m = df['u_q_m [uL/min]']

    """
    Fitting Simple Linear Regression Model using statsmodels library OLS estimation, note this library uses the general
    linear model  structure in matrix form:

    y_vec = (X_mat)(B_Vec) + e_vec

    see documentation at: https://www.statsmodels.org/stable/index.html
    """
    """
    Defining X_mat, note that for simple linear regression with intercept the model can be represented as

    y = B_o + B_1x + e

    in matrix form as shown above this gives

    X_mat = |1 x_1|
            | .  .|
            | .  .|
            |1 x_n|

    B_vec = | B_o |
            | B_1 |

    """

    # creating x_matrix from data (note correction factor is finding model between
    x_mat = np.transpose(np.array(q_sli_exp_data.values))
    x_mat = sm.add_constant(x_mat)

    # creating model object
    model = sm.OLS(q_mass_meas_exp_data, x_mat)
    # fitting model
    results = model.fit()
    print(key)
    print(results.summary())

    # obtaining estimated parameters
    est_params = results.params
    # obtining beta_hat_vec = [B_o_hat B_1_hat]^T
    beta_hat = est_params.values

    #intercept estimate
    beta_0_hat = beta_hat[0]
    #slope estimate
    beta_1_hat = beta_hat[1]

    #obtaining 95% confidence interval for parameters
    conf_int = results.conf_int()
    lower_bound_b_0_hat = conf_int[0]['const']
    lower_bound_b_1_hat = conf_int[0]['x1']

    #calculating uncertainty in the parameters at 95% CI
    u_b_0_hat = beta_0_hat-lower_bound_b_0_hat
    u_b_1_hat = beta_1_hat-lower_bound_b_1_hat

    #calculating relative uncertainty
    u_b_0_hat_rel = abs(u_b_0_hat/beta_0_hat)*100
    u_b_1_hat_rel = abs(u_b_1_hat/beta_1_hat)*100

    # calculating E_y_hat = X*B_hat
    # E_y_hat = x_mat*beta_hat #for no intercept
    E_y_hat = np.matmul(x_mat, beta_hat)  # with intercept

    # obtaining R^2
    r_squared = results.rsquared

    #creating entry in dict_of_params_and_uncert: [viscosity, beta_0_hat, u_beta_0_hat, u_beta_0_hat_rel, beta_1_hat, u_beta_1_hat, u_beta_1_hat_rel, r_squared]
    viscosity = int(key.replace('_cSt',''))
    dict_of_params_and_uncert[key] = [viscosity, beta_0_hat, u_b_0_hat, u_b_0_hat_rel, beta_1_hat, u_b_1_hat, u_b_1_hat_rel, r_squared]

    # plotting values
    plt.rc('font', family='Times New Roman')
    plt.rcParams.update({'font.size': 12})
    fig, ax = plt.subplots()
    ax.errorbar(q_sli_exp_data, q_mass_meas_exp_data, yerr=u_q_m, xerr=u_q_sli, marker="o",  fillstyle = 'none',fmt=' ',
                capsize=3, ecolor='blue' , color='blue')
    ax.plot(q_sli_exp_data, E_y_hat, "--", color="black")

    # adding estimated correction equation to plot (upper left corner)
    upper_x_bound_txt = plt.xlim()[1]
    lower_x_bound_txt = plt.xlim()[0]
    upper_y_bound_txt = plt.ylim()[1]
    lower_y_bound_txt = plt.ylim()[0]

    # write equation
    eqn = r'$\mathdefault{Q_{actual}}$' + r'[$\frac{\mathdefault{\mu L}}{\mathdefault{min}}$] ' + ' = ' + '(' + str(
        round(beta_hat[1],
              4)) + ')' + r'$\mathdefault{Q_{measured}}$' + r'[$\frac{\mathdefault{\mu L}}{\mathdefault{min}}$] ' + ' + ' + '(' + str(
        round(beta_hat[0], 4)) + ')' + r'[$\frac{\mathdefault{\mu L}}{\mathdefault{min}}$]'

    props = dict(facecolor='white')

    # plot estimated equation and r^2 value on graph
    # notice, setting the position of the text argument to be based on location relative to the axes of the figure ( (0,0) = bottom left (1,1) = top right)
    eqn_plt = plt.text(0.02, .96,
                       eqn + '\n' + r'$\mathdefault{R^2}$' + ' = ' + str(round(r_squared, 5)),
                       horizontalalignment='left', verticalalignment='top', fontsize=12,
                       fontfamily='Times New Roman', bbox=props, transform=ax.transAxes)
    plt.legend(['Fit', 'Measurements'], loc='lower right', framealpha=1, edgecolor='black', fancybox=False)

    # add y and x labels
    plt.ylabel(r'$\mathdefault{Q_{actual}}$' + r'[$\frac{\mathdefault{\mu L}}{\mathdefault{min}}$]', fontsize=12)
    plt.xlabel(r'$\mathdefault{Q_{measured}}$' + r'[$\frac{\mathdefault{\mu L}}{\mathdefault{min}}$]', fontsize=12)

    fig.set_size_inches(8,6)
    plt.grid()
    plt.show()

#creating dataframe of form: [index = vsic_cSt, columns = [viscosity, beta_0_hat, u_beta_0_hat, u_beta_0_hat_rel, beta_1_hat, u_beta_1_hat, u_beta_1_hat_rel, r_squared]]
df_params = pd.DataFrame.from_dict(dict_of_params_and_uncert, orient='index', columns=['Viscosity [cSt]','beta_0_hat [uL/min]', 'u_beta_0_hat [uL/min]', 'u_beta_0_hat_rel [%]', 'beta_1_hat', 'u_beta_1_hat', 'u_beta_1_hat_rel [%]', 'r_squared'])

#sorting in ascending order of viscosity
df_sort = df_params.sort_values(by=['Viscosity [cSt]'])

#resetting index
df_sort = df_sort.reset_index()
df_sort = df_sort.drop(['index'], axis =1)

#outputting df as .csv in ./outputs/est_params_and_uncert
question = input('Output dataframe of parameters and uncertainties (95% CI) as .csv files? (y/n): ')
while question != 'y' and question !='n':
    question = input("please input 'y' or 'n': ")
if question == 'y':
    df_sort.to_csv('./outputs/est_params_and_uncert/estimated_params_and_uncert.csv')
elif question =='n':
    print('results not output to .csv')