COVID-19 activity
==================================

Approach
---------

We try to detecting when exponential growth is stopping, and compare
the contagion of countries.

To measure the contagion (progression of the desease), 
I plot the fraction deceased relative to the number of people in the country,
corrected for age demographics (as in my other analyses).
This is related to time, but I plot it on the y-axis, to make the labels
easier to read. So you have to read the plot from bottom to top rather than
left to right.

How exponential the growth is, is plotted on the x-axis. 
This shows the fraction of people deceased in the last 7 days (compared to
all up to that point). In exponential growths, this is a large percentage
(70-100%). If measure work, the country will move to the left (such as South Korea and China).

Data
---------

* UN data for age demographics: http://data.un.org/Data.aspx?d=POP&f=tableCode%3a22
* COVID-19 time series: https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_time_series/

Results
--------

.. image:: https://raw.githubusercontent.com/JohannesBuchner/COVID-19-analysis/master/results/ratio_expo.png

Discussion
-----------

Things I notice / interpret (as a non-expert!):

* Overall, there seems to be a passage on the middle right where all
  countries go through. Perhaps this is where the desease is starting
  to become a serious problem, and countries react.
* Italy is improving, while Spain is not as much.
* On the outer right envelope are Turkey and the US. What is up with Luxembourg?

Conclusions
-----------

I am not an epidemiologists. I recommend you listen to the experts.

Reading recommendations
-----------------------

* https://www.tableau.com/about/blog/2020/3/ten-considerations-you-create-another-chart-about-covid-19
* Riou+2020 paper: https://www.medrxiv.org/content/10.1101/2020.03.04.20031104v1.full.pdf
* also discussed here: https://statmodeling.stat.columbia.edu/2020/03/07/coronavirus-age-specific-fatality-ratio-estimated-using-stan/
* https://coronavirus.jhu.edu/
* https://neherlab.org/covid19/
