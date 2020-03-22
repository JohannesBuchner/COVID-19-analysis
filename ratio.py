import numpy as np
import matplotlib.pyplot as plt
import pandas
import os
from datetime import datetime
from adjustText import adjust_text

print("loading COVID-19 data...")
f1 = 'time_series_19-covid-Confirmed.csv'
f2 = 'time_series_19-covid-Deaths.csv'
f3 = 'time_series_19-covid-Recovered.csv'
d1 = pandas.read_csv(f1)
d2 = pandas.read_csv(f2)
d3 = pandas.read_csv(f3)
d1 = d1.groupby('Country/Region').sum()
d2 = d2.groupby('Country/Region').sum()
d3 = d3.groupby('Country/Region').sum()

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
country_briefname_replacement = {
	'Iran (Islamic Republic of)':'Iran',
	'United Kingdom':'UK',
	'Korea, South': 'South Korea',
	'Republic of Korea': 'South Korea',
}

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

# approximation to Riou+20 paper
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
	pandas.read_csv('UNdata/UNdata_Export_20200316_150200133.csv.gz'),
	pandas.read_csv('UNdata/UNdata_Export_20200316_150838749.csv.gz'),
	pandas.read_csv('UNdata/UNdata_Export_20200316_151648629.csv.gz'),
	pandas.read_csv('UNdata/UNdata_Export_20200316_152402097.csv.gz'),
	])

beds = pandas.read_csv('UNdata/UNdata_Export_hospitalbeds.csv')

prop_cycle = plt.rcParams['axes.prop_cycle']
colors = prop_cycle.by_key()['color'] * 100

marked_countries = ['Japan', 'China', 'South Korea', 'US', 'Iran', 'Italy', 'Spain', 'France', 'UK', 'Germany']
#marked_countries = ['US', 'Germany', 'Japan', 'Italy', 'Korea, South', 'Iran']
#marked_countries_colors = {'US':'red', 'Japan':'brown', 'Italy':'green', 
#	'Korea, South':'black', 'Iran':'blue', 'France':'lime', 'China':'pink',
#	'Spain':''}
marked_countries_colors = {c:colors.pop(0) for c in marked_countries}

#print("countries:", sorted(set(pop["Country or Area"])))

a = plt.figure(figsize=(6, 7))
ax = a.gca()
b = plt.figure(figsize=(6, 7))
bx = b.gca()

use_all_countries = os.environ.get('COUNTRIES', 'all') == 'all'
atexts = []
btexts = []
capacities = []
#min_dead = 4
min_series = 10
min_series = 7

print("per-country extraction:")
print()
print("%20s %4s %6s %14s %s" % ("Country", "Beds", "Deaths", "Population", "Vulnerable fraction"))
#for rows1, rows2 in zip(open(f1), open(f2)):
for (i, row1), (_, row2), (_, row3) in zip(d1.iterrows(), d2.iterrows(), d3.iterrows()):
	timeseries_reported = np.array(row1[4:], dtype=int)
	timeseries_dead = np.array(row2[4:], dtype=int)
	timeseries_recovered = np.array(row3[4:], dtype=int)
	country = row1.name
	pop_country = pop[pop["Country or Area"] == country_name_replacement.get(row1.name, row1.name)]
	if len(pop_country) == 0: # or pop_country.Year.dtype.char == 'O':
		print("skipping", country, "no population data")
		continue
	beds_country = beds[beds["Country or Area"] == country_name_replacement.get(row1.name, row1.name)]
	year = pandas.to_numeric(beds_country["Year(s)"])
	# from "number of beds per 10000 people" compute "number of beds per person":
	beds_recent = np.array(beds_country.Value[year == year.max()]) / 10000
	if len(beds_recent) == 0:
		beds_recent = 0
		#print("skipping", country, "no bed data")
		continue
	else:
		beds_recent = beds_recent[0]

	#if country not in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South']:
	#	continue
	country_brief = country_briefname_replacement.get(country, country)
	
	year = pandas.to_numeric(pop_country.Year)
	country_recent = pop_country[year == year.max()]
	# total number of people in each age group
	num_people = [country_recent[country_recent.Age.isin(ages)].Value.sum()
		for ages in agegroups]
	# corrected for vulnerability
	vulnerable_number = np.array(num_people) * agegroups_mortality
	# number of hospital beds available in the country
	beds_total = beds_recent * sum(num_people)
	# corrected for vulnerability of the population
	capacity = beds_total * sum(vulnerable_number) / sum(num_people)
	
	print("%20s %6d %6d %14d %.2f%%" % (country, beds_recent, max(timeseries_dead), 
		sum(num_people), sum(vulnerable_number) * 100 / sum(num_people)))
	#print("%20s %9d" % (country, beds_recent * sum(vulnerable_number)))
	#capacities.append("| %20s | %9d |" % (country, beds_recent * sum(vulnerable_number)))
	if beds_recent > 0 and sum(vulnerable_number) > 100000:
		capacities.append(((timeseries_reported - timeseries_recovered)[-1] / capacity, country_brief, capacity))
	
	if country_brief in marked_countries_colors:
		color = marked_countries_colors[country_brief]
	else:
		if not use_all_countries: 
			continue
		color = colors.pop(0)
	
	# for small countries, require a higher number of dead, 
	# otherwise the estimates are all over the place
	min_dead = max(4,  1 * 2 * 100000 / sum(vulnerable_number))
	
	if timeseries_dead.max() < min_dead:
		#print("skipping", country, "not enough dead", timeseries_dead.max(), 1 * 2 * 100000 / sum(vulnerable_number))
		continue
	
	timeseries_cases = timeseries_reported - timeseries_recovered
	
	mask = timeseries_dead >= min_dead
	if not mask.any():
		#print("skipping", country, "not enough dead", timeseries_dead.max())
		pass
	
	#mask = np.logical_and(timeseries_dead >= 3, timeseries_reported / vulnerable_number.sum() > 1e-5)
	x = timeseries_cases[mask] / vulnerable_number.sum()
	y = timeseries_dead[mask] / timeseries_reported[mask]
	marker = 'o-' if country_brief in marked_countries else 's-'
	size = 8 if mask.sum() > min_series else 4
	if mask.any():
		l, = ax.plot(x[-1], y[-1], marker, ms=size, color=color)
		atexts.append(ax.text(x[-1], y[-1], country_brief, va='bottom', ha='left', size=8))
		if mask.sum() > 10 or country_brief in marked_countries:
			ax.plot(x, y, marker, ms=2, label=country_brief, alpha=0.2, color=color)
	
	elif timeseries_cases[-1] / vulnerable_number.sum() > 1e-5:
		ax.plot(timeseries_cases[-1] / vulnerable_number.sum(), 1e-3,
			marker, color=color, ms=2)
		ax.text(timeseries_cases[-1] / vulnerable_number.sum(), 1e-3,
			'  ' + country_brief, va='bottom', ha='center', size=6, rotation=90)

	x = timeseries_cases[mask] / capacity
	y = timeseries_dead[mask] / timeseries_reported[mask]
	if mask.any():
		l, = bx.plot(x[-1], y[-1], marker, ms=size, color=color)
		btexts.append(bx.text(x[-1], y[-1], country_brief, va='bottom', ha='left', size=8))
		if mask.sum() > min_series or country_brief in marked_countries:
			bx.plot(x, y, marker, ms=2, label=country_brief, alpha=0.2, color=l.get_color())
	
	else:
		bx.plot(timeseries_cases[-1] / capacity, 1e-3,
			marker, color=color, ms=2)
		bx.text(timeseries_cases[-1] / capacity, 1e-3,
			'  ' + country_brief, va='bottom', ha='center', size=6, rotation=90)

with open("capacities.rst", 'w') as f:
	f.write("""
=============================
Health care system capacities
=============================

Here, the number of infected a country can handle is listed.
This is number of vulnerable people multiplied by the number of 
available hospital beds per person. 
Data comes from UN data compilations (age demographics and hospital bed data). 
The number of vulnerable people is computed based on published mortality factors for age groups (Riou+2020).

How to read this
-----------------

To compare with the current status, subtract the number infected by the number recovered.
This gives you information of how stressed the health system is.

(From doubling times, you can also extrapolate in how many days
the health system will become insufficient).

Top stressed countries
-----------------------


==================  ===========
 Country             Capacity 
==================  ===========
""")
	for stress, country, capacity in sorted(capacities, reverse=True):
		if capacity > 100 and stress > 0.3:
			f.write("%-15s   %10d\n" % (country, capacity))
	f.write("==================  ===========\n\n")

	f.write("""

Alphabetical
-----------------------

==================  ===========
 Country             Capacity 
==================  ===========
""")
	for stress, country, capacity in capacities:
		f.write("%-15s   %10d\n" % (country[:15], capacity))
	f.write("==================  ===========\n\n")


plt.sca(ax)
ax.text(0.02, 1.0, """How to read this graph:
The horizontal axis represents penetration of the population.
The vertical axis indicates under-reporting of infections
(compare to Diamond Princess and South Korea).
Deaths (rare!) occur after a delay. For example, in China and 
South Korea, deaths keep increasing after no new infections.

Definitions:
Vulnerable population = Country demographic age groups multiplied 
by their relative mortality (taken from Riou et al. 2020).
# of infected = confirmed cases - recovered cases
""", va='bottom', ha='left', transform=ax.transAxes, size=10)

ax.text(0.98, 0.98, "@JohannesBuchner (%s)" % datetime.now().strftime("%Y-%m-%d"), va='top', ha='right',
	transform=ax.transAxes, size=8, color="gray")

plt.xlabel('# of Infected / Vulnerable Population')
plt.ylabel('# of Deaths / # of Confirmed cases')
plt.xscale('log')
plt.yscale('log')
ax.tick_params(axis='both', direction='inout', which='both', 
	bottom=True, top=True, left=True, right=True,)
plt.xticks([1e-4, 1e-3, 1e-2], ['0.01%', '0.1%', '1%'])
plt.yticks([1e-3, 1e-2, 1e-1, 1], ['0.1%', '1%', '10%', '100%'])
plt.hlines(7/712, 1e-5, 2e-2, linestyles=['--'], color='gray')
plt.text(2e-2, 7/712, 'Diamond Princess', ha='right', va='bottom', size=6)
plt.ylim(1e-3, 0.2)
plt.xlim(1e-5, 2e-2)
adjust_text(atexts)
#plt.legend(loc='best', ncol=3, prop=dict(size=8))
if use_all_countries:
	plt.savefig('ratio.pdf', bbox_inches='tight')
	plt.savefig('ratio.png', bbox_inches='tight', dpi=120)
else:
	plt.savefig('ratio_some.pdf', bbox_inches='tight')
	plt.savefig('ratio_some.png', bbox_inches='tight', dpi=120)
plt.close()

#plt.plot([1e-6, 1e-3], [5e-6/1e-6, 5e-6/1e-3], ':', color='gray', alpha=0.5)

plt.sca(bx)
bx.text(0.98, 0.98, "@JohannesBuchner (%s)" % datetime.now().strftime("%Y-%m-%d"), va='top', ha='right',
	transform=bx.transAxes, size=8, color="gray")

bx.text(0.02, 1.0, """How to read this graph:
The horizontal axis represents stress on the health care system.
The vertical axis indicates under-reporting of infections
(compare to Diamond Princess and South Korea).
Deaths (rare!) occur afteJapan 	221225r a delay. For example, in China and 
South Korea, deaths keep increasing after no new infections.

Definitions:
Vulnerable population = Country demographic age groups multiplied 
by their relative mortality (taken from Riou et al. 2020).
# of infected = confirmed cases - recovered cases
""", va='bottom', ha='left', transform=bx.transAxes, size=10)
plt.xlabel("# of Infected / Vulnerable Population / # hospital beds per person")
plt.ylabel('# of Deaths / # of Confirmed cases')
plt.xscale('log')
plt.yscale('log')
bx.tick_params(axis='both', direction='inout', which='both', 
	bottom=True, top=True, left=True, right=True,)
	#labelbottom=True, labeltop=True, labelleft=True, labelright=True)
plt.xticks([1e-2, 1e-1, 1], ['1%', '10%', '100%'])
plt.yticks([1e-3, 1e-2, 1e-1, 1], ['0.1%', '1%', '10%', '100%'])
plt.hlines(7/712, 1e-3, 8, linestyles=['--'], color='gray')
plt.text(8, 7/712, 'Diamond Princess', ha='right', va='bottom', size=6)
plt.ylim(1e-3, 0.2)
plt.xlim(1e-3, 8)
bx.fill_between([1.0, 8], [1e-3, 1e-3], [0.2, 0.2], color='yellow', alpha=0.05)
bx.fill_between([1.2, 8], [1e-3, 1e-3], [0.2, 0.2], color='yellow', alpha=0.05)
bx.fill_between([1.2**2, 8], [1e-3, 1e-3], [0.2, 0.2], color='yellow', alpha=0.05)
adjust_text(btexts)
#plt.legend(loc='best', ncol=3, prop=dict(size=8))
if use_all_countries:
	plt.savefig('ratio_beds.pdf', bbox_inches='tight')
	plt.savefig('ratio_beds.png', bbox_inches='tight', dpi=120)
else:
	plt.savefig('ratio_beds_some.pdf', bbox_inches='tight')
	plt.savefig('ratio_beds_some.png', bbox_inches='tight', dpi=120)
plt.close()
