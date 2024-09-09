# sli_0430_correction_factor_code
## Summary
Python codebase for automating calculation of correction factor for linearized digital flowrate measurement output from SLI-0430 Sensirion flow sensor for general fluids (i.e. fluids not factory calibrated). Code was developed to determine a correction factor for the sensor output flowrates of various viscosities of Silicone oil. Mass flow rate data is used to obtain the true flow rate measurement, for which the sensor output value is corrected to. Note that code could be generalized for volume flow rate if necessary, as mass flow rate implementation requires knowledge of fluid density. Code intakes .csv files for the sensor output flow rate, and the experimentally determined mass flow rate, at different pressures and viscosities. The code then performs OLS estimation to estimate a linear equation that corrects the digital flowrate measurement to the 'true' flow rate measurement that was obtained experimentally. Considers both negative and positive flowrate data.

## Dependencies
1. functions.py
2. csv
3. matplotlib
4. numpy
5. pandas
6. pathlib
7. statsmodels.api

## 
