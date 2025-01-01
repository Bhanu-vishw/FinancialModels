# FM 5151: Final project

Your name: Bhanu Vishwakarma 
Your email: vishw045@umn.edu

(Fill in details below for how to run, etc.)


Structure: 

\final_starter\starter\pkg\src\final: contains .py files including the ones newly created - volatility.py (for realized volitility calculation using EWMA model)
                                                                                          - riskfreerate.py (risk free rate calculation)
                                                                                          - everything else is same only with updated code lines

\final_starter\starter\pkg\test: conatins the unit tests - added a unit test for riskfreerate.py

\final_starter\starter\analysis: conatins csv output and analysis for part 2 & 3 - includes all the sub parts along with short write ups about the codes
                                                                                 - the output csv 'options_with_vol.csv'


How to produce results:

I have already saved the files with outputs but in order to produce the results you just have to run-all the .ipynb file (analysis_part_2 & ananlysis_part_3). Also, I have tried to provide comments for each line of code in order, about what it is doing and the steps followed to produce results. 


Note:

1) There are no extra libraries required to produce the results hence I haven't included anything in pyproject.toml file.
2) For extra credits, I have included a variance reduction technique in generate() function of class GBMPathGenerator - descrption in analysis_part_3 file