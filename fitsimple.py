import os
import sys
import astropy.io.fits as pyfits
import numpy as np
import matplotlib.pyplot as plt
import numpy
import pandas

print("loading COVID-19 data...")
f1 = 'time_series_19-covid-Confirmed.csv'
f2 = 'time_series_19-covid-Deaths.csv'
d1 = pandas.read_csv(f1)
d2 = pandas.read_csv(f2)
d1 = d1.groupby('Country/Region').sum()
d2 = d2.groupby('Country/Region').sum()

country_name_replacement = {
	"United Arab Emirates": "",
	"Venezuela":"Venezuela (Bolivarian Republic of)",
	"United Kingdom":'United Kingdom of Great Britain and Northern Ireland', 
	"US":'United States of America',
	"Vietnam":'Viet Nam',
	"Brunei": 'Brunei Darussalam',
	"Bolivia": 'Bolivia (Plurinational State of)',
	'Curacao': 'Curaçao',
	'Iran':'Iran (Islamic Republic of)',
	'Russia': 'Russian Federation',
	'Korea, South': 'Republic of Korea',
}

deaths = []
confirmed = []
total_pop = []
vulnerable_pop = []
country_names = []

agegroups = [
 ['0 - 4', '5 - 9', '10 - 14',  '15 - 19'],
 ['20 - 24', '25 - 29'],
 ['30 - 34',  '35 - 39'],
 ['40 - 44',  '45 - 49'],
 ['50 - 54',  '55 - 59'],
 ['60 - 64',  '65 - 69'],
 ['70 - 74',  '75 - 79'],
 ['80 - 84', '85 - 89', '90 - 94', '95 - 99', '100 - 104', '105 - 109', '110 +'],
]
agegroups_age = np.array([20, 30, 40, 50, 60, 70, 80, 80])

# approximation from Rieu paper
agegroups_mortality = 0.4 * (np.exp(-((80. - agegroups_age) / 15)**1.6))

"""
plt.plot(agegroups_age, agegroups_mortality)
plt.xlabel('Age group')
plt.ylabel('Mortality')
plt.savefig('agegroups_mortality.png', bbox_inches='tight')
plt.close()
"""

print("loading population data...")
pop = pandas.concat([
	pandas.read_csv('UNdata_Export_20200316_150200133.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_150838749.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_151648629.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_152402097.csv.gz'),
	])

#print("countries:", sorted(set(pop["Country or Area"])))

print("per-country extraction:")
print()
print("%20s %6s %14s %s" % ("Country", "Deaths", "Population", "Vulnerable fraction"))
#for rows1, rows2 in zip(open(f1), open(f2)):
for (i, row1), (_, row2) in zip(d1.iterrows(), d2.iterrows()):
	timeseries_reported = np.array(row1[4:-4], dtype=int)
	timeseries_dead = np.array(row2[4:-4], dtype=int)
	country = row1.name
	#state   = rows1[0]
	#if state == "": 
	pop_country = pop[pop["Country or Area"] == country_name_replacement.get(row1.name, row1.name)]
	if len(pop_country) == 0: # or pop_country.Year.dtype.char == 'O':
		#print("    could not look up country:", country)
		continue
	if timeseries_dead.sum() == 0:
		continue
	if country not in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South']:
		continue
	
	deaths.append(timeseries_dead)
	confirmed.append(timeseries_reported)
	#print(country, pop_country.columns)
	year = pandas.to_numeric(pop_country.Year)
	country_recent = pop_country[year == year.max()]
	num_people = [country_recent[country_recent.Age.isin(ages)].Value.sum()
		for ages in agegroups]
	vulnerable_number = np.array(num_people) * agegroups_mortality
	vulnerable_pop.append(vulnerable_number.sum())
	country_names.append(country)
	total_pop.append(sum(num_people))
	
	print("%20s %6d %14d %.2f%%" % (country, sum(timeseries_dead), 
		sum(num_people), sum(vulnerable_number) * 100 / sum(num_people)))

deaths = np.array(deaths)
confirmed = np.array(confirmed)

print(np.shape(deaths), np.shape(confirmed), np.shape(vulnerable_pop), np.shape(country_names))

import pystan

stan_code = open('simple.stan').read()
sm = pystan.StanModel(model_code=stan_code)

for tau in range(14):
	# compute increase in deaths
	deaths_differential = deaths[:,1:] - deaths[:,:-1]
	# use a time delay of tau days
	if tau > 0:
		deaths_differential[:,tau:] = deaths_differential[:,:-tau]
		deaths_differential[:,:tau] = 0
	deaths_differential[deaths_differential < 0] = 0

	confirmed_differential = confirmed[:,1:] - confirmed[:,:-1]
	confirmed_differential[confirmed_differential < 0] = 0

	n_countries, n_data = np.shape(deaths_differential)

	data = dict(
		n_countries = n_countries,
		n_data = n_data,
		deaths = deaths_differential,
		confirmed = confirmed_differential,
		total_pop = total_pop,
		vulnerable_pop = vulnerable_pop,
	)
	fit = sm.sampling(data=data, iter=1000, chains=4)
	a = fit.extract(permuted=True)

	print("Mortality: %.3f +- %.3f%%" % (100*np.exp(a['log_rel_mortality']).mean(), 100*np.exp(a['log_rel_mortality']).std()))
	log_frac_infected_mean = np.log10(np.exp(a['log_frac_infected'])).mean(axis=0)
	log_frac_infected_std = np.log10(np.exp(a['log_frac_infected'])).std(axis=0)
	log_frac_discovered_mean = np.log10(np.exp(a['log_frac_discovered'])).mean(axis=0)
	log_frac_discovered_std = np.log10(np.exp(a['log_frac_discovered'])).std(axis=0)

	# for each country, report its frac_discovered
	for i, country in enumerate(country_names):
		print('%20s: %.3f +- %.3f %% discovered fraction' % (country, 
			10**(log_frac_discovered_mean[i]) * 100, 
			10**(log_frac_discovered_mean[i] - log_frac_discovered_std[i])*100))
		plt.errorbar(x=np.arange(n_data), y=log_frac_infected_mean[i], 
			yerr=log_frac_infected_std[i], label=country)

	plt.ylabel('$\log$(Fraction infected)')
	plt.xlabel('Time')
	plt.legend(loc='best')
	plt.savefig('simple_time_tau%d.pdf' % tau, bbox_inches='tight')
	plt.savefig('simple_time_tau%d.png' % tau, bbox_inches='tight')
	plt.close()

