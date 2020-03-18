COVID-19 analysis with Stan
============================

The number of confirmed cases depends strongly on the testing approach
taken by each country's government. 

I was interested whether one can infer the underlying infected population
based on the number of deaths.
In the script, I also tried to incorporate 
population demographics (age distribution of each country),
to correctly identify the country-specific vulnerable population size.

However, the results do not seem to make sense (yet).

Data
---------

* UN data for age demographics: http://data.un.org/Data.aspx?d=POP&f=tableCode%3a22
* UN data for hospital beds: http://data.un.org/Data.aspx?d=WHO&f=MEASURE_CODE%3aWHS6_102

* COVID-19 time series: https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/

Reading recommendations
-----------------------

* https://www.tableau.com/about/blog/2020/3/ten-considerations-you-create-another-chart-about-covid-19
* Riou+2020 paper: https://www.medrxiv.org/content/10.1101/2020.03.04.20031104v1.full.pdf
* also discussed here: https://statmodeling.stat.columbia.edu/2020/03/07/coronavirus-age-specific-fatality-ratio-estimated-using-stan/
* https://coronavirus.jhu.edu/
