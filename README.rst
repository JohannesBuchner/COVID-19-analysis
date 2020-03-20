COVID-19 toy analysis
============================

The number of confirmed cases depends strongly on the testing approach
taken by each country's government. 

I was interested whether one can infer the underlying infected population
based on the number of deaths.
In the script, I also tried to incorporate 
population demographics (age distribution of each country),
to correctly identify the country-specific vulnerable population size.

.. image:: https://raw.githubusercontent.com/JohannesBuchner/COVID-19-analysis/master/ratio_beds_some.png

Things I notice / interpret (as a non-expert!):

* South Korea and Diamond Princess are consistent in mortality,
  and thought to be quite complete in infection testing.
  Other countries are probably under-counting the infected.
* Phases can be seen: 

  1. first a right-down line (Early Iran, South Korea, US now), 
     perhaps the expansion of the infection in the population, (2)
  2. increase to the top right (Iran, Japan), perhaps because 
     delayed deaths are accumulating.
  3. Vertical upwards (China, South Korea): 
     New infections have been stopped. Delayed deaths accumulate.
  4. Return to left (China): people recover, the health care system is relaxing.

* In the top right of the plot, the health care system is highly stressed (number of infected large 
  compared to available hospital beds).
  Italy and Iran are there. 
  The number of deaths increase as a country heads to the right.
  Spain is going there as well.

* The US is speeding to the right, but (surprisingly?) shows 
  little sign of under-counting the infected.

With all countries:

.. image:: https://raw.githubusercontent.com/JohannesBuchner/COVID-19-analysis/master/ratio_beds.png

Things I notice / interpret (as a non-expert!):

* Germany, Austria (and Denmark, Norway) are at the bottom of the chart --
  mortality is unusually low there. I am unsure if this is because
  of undercounting of deaths, over-counting of infected (unlikely),
  or quality and accessibility of the health care system.

* 
  

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
* https://neherlab.org/covid19/
