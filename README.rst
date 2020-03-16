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

* UN Census data for age demographics: http://data.un.org/Data.aspx?d=POP&f=tableCode%3a22

* COVID-19 time series: https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/


