# sli_0430_correction_factor_code
## Summary
Python codebase for automating calculation of correction factor for linearized digital flowrate measurement output from SLI-0430 Sensirion flow sensor for general fluids (i.e. fluids not factory calibrated). Code was developed to determine a correction factor for the sensor output flowrates of various viscosities of Silicone oil. Mass flow rate data is used to obtain the true flow rate measurement, for which the sensor output value is corrected to. Note that code could be generalized for volume flow rate if necessary, as mass flow rate implementation requires knowledge of fluid density. Code intakes .csv files for the sensor output flow rate, and the experimentally determined mass flow rate, at different pressures and viscosities. The code then performs OLS estimation to estimate a linear equation that corrects the digital flowrate measurement to the 'true' flow rate measurement that was obtained experimentally. Considers both negative and positive flowrate data. Each code file has indepth commenting/description, further improvement needed to generalize code. Uncertainties given at 95% confidence level.

## Dependencies
1. functions.py
2. csv
3. matplotlib
4. numpy
5. pandas
6. pathlib
7. statsmodels.api

## Order of Use of Code Files
1. mass_fr_to_vol_fr.py (convert masss flow rate measurements to volume flow rate measurements)
2. flow_rate_meas_to_avg.py (obtain average flow rate measurement from sampled SLI-0430 flow measurements)
3. flow_meter_fr_and_meas_fr_to_csv.py (place 'true' flow rate measurements and sensor output measurements in same file for OLS fitting and plotting)
4. neg_and_pos_q_combined_file.py [optional] (combine negative and positive flow rate data into same file)
5. plotting_combined_df.py (obtain OLS fit for correction factor, plot estimated line and experimental data, output estimated parameters)
