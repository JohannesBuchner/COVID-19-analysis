import numpy as np
import matplotlib.pyplot as plt
import pandas

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
	pandas.read_csv('UNdata_Export_20200316_150200133.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_150838749.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_151648629.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_152402097.csv.gz'),
	])

beds = pandas.read_csv('UNdata_Export_hospitalbeds.csv')

#print("countries:", sorted(set(pop["Country or Area"])))

a = plt.figure(figsize=(7, 8))
ax = a.gca()
b = plt.figure(figsize=(7, 8))
bx = b.gca()

min_dead = 6

print("per-country extraction:")
print()
print("%20s %4s %6s %14s %s" % ("Country", "Beds", "Deaths", "Population", "Vulnerable fraction"))
#for rows1, rows2 in zip(open(f1), open(f2)):
for (i, row1), (_, row2), (_, row3) in zip(d1.iterrows(), d2.iterrows(), d3.iterrows()):
	timeseries_reported = np.array(row1[4:], dtype=int)
	timeseries_dead = np.array(row2[4:], dtype=int)
	timeseries_recovered = np.array(row3[4:], dtype=int)
	country = row1.name
	if timeseries_dead.max() < 1:
		#print("skipping", country, "not enough dead", timeseries_dead.max())
		continue
	pop_country = pop[pop["Country or Area"] == country_name_replacement.get(row1.name, row1.name)]
	if len(pop_country) == 0: # or pop_country.Year.dtype.char == 'O':
		print("skipping", country, "no population data")
		continue
	beds_country = beds[beds["Country or Area"] == country_name_replacement.get(row1.name, row1.name)]
	year = pandas.to_numeric(beds_country["Year(s)"])
	beds_recent = np.array(beds_country.Value[year == year.max()])
	if len(beds_recent) == 0:
		beds_recent = 0
	else:
		beds_recent = beds_recent[0]
	
	#if country not in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South']:
	#	continue
	
	year = pandas.to_numeric(pop_country.Year)
	country_recent = pop_country[year == year.max()]
	num_people = [country_recent[country_recent.Age.isin(ages)].Value.sum()
		for ages in agegroups]
	vulnerable_number = np.array(num_people) * agegroups_mortality
	
	print("%20s %4d %6d %14d %.2f%%" % (country, beds_recent, sum(timeseries_dead), 
		sum(num_people), sum(vulnerable_number) * 100 / sum(num_people)))
	
	timeseries_cases = timeseries_reported - timeseries_recovered
	
	mask = timeseries_dead >= min_dead
	#mask = np.logical_and(timeseries_dead >= 3, timeseries_reported / vulnerable_number.sum() > 1e-5)
	x = timeseries_cases[mask] / vulnerable_number.sum()
	y = timeseries_dead[mask] / timeseries_reported[mask]
	if mask.any():
		l, = ax.plot(x, y,
			'o-' if country in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South'] else 's-', ms=2,
			label=country, alpha=0.5)
	
	if len(y) > 0:
		ax.plot(x[-1], y[-1],
			'o' if country in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South'] else 's',
			color=l.get_color())
		ax.text(x[-1], y[-1], country, va='bottom', ha='left', size=8)
	elif timeseries_cases[-1] / vulnerable_number.sum() > 1e-5:
		ax.plot(timeseries_cases[-1] / vulnerable_number.sum(), 1e-3,
			'o' if country in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South'] else 's')
		ax.text(timeseries_cases[-1] / vulnerable_number.sum(), 1e-3,
			'  ' + country, va='bottom', ha='center', size=6, rotation=90)

	x = timeseries_cases[mask] / vulnerable_number.sum() / beds_recent
	y = timeseries_dead[mask] / timeseries_reported[mask]
	if mask.any():
		l, = bx.plot(x, y,
			'o-' if country in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South'] else 's-', ms=2,
			label=country, alpha=0.5)
	
	if len(y) > 0:
		bx.plot(x[-1], y[-1],
			'o' if country in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South'] else 's',
			color=l.get_color())
		bx.text(x[-1], y[-1], country, va='bottom', ha='left', size=8, rotation=33)
	elif timeseries_cases[-1] / vulnerable_number.sum() / beds_recent > 1e-7:
		bx.plot(timeseries_cases[-1] / vulnerable_number.sum() / beds_recent, 1e-3,
			'o' if country in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South'] else 's')
		bx.text(timeseries_cases[-1] / vulnerable_number.sum() / beds_recent, 1e-3,
			'  ' + country, va='bottom', ha='center', size=6, rotation=90)

plt.sca(ax)
ax.text(0.02, 0.98, """How to read this graph:
The horizontal axis represents penetration of the population.
The vertical axis indicates under-reporting of infections
(compare to Diamond Princess and South Korea).
Deaths (rare!) occur after a delay. For example, in China and 
South Korea, deaths keep increasing after no new infections.

Definitions:
Vulnerable population = Country demographics age groups multiplied 
by their relative mortality (taken from Riou et al. 2020).
# of infected = confirmed cases - recovered cases
""", va='top', ha='left', transform=ax.transAxes)
plt.xlabel('# of Infected / Vulnerable Population')
plt.ylabel('# of Deaths / # of Confirmed cases')
plt.xscale('log')
plt.yscale('log')
plt.hlines(7/712, 1e-5, 2e-2, linestyles=['--'], color='gray')
plt.text(2e-2, 7/712, 'Diamond Princess', ha='right', va='bottom', size=6)
plt.ylim(1e-3, 1)
plt.xlim(1e-5, 2e-2)
#plt.legend(loc='best', ncol=3, prop=dict(size=8))
plt.savefig('ratio.pdf', bbox_inches='tight')
plt.savefig('ratio.png', bbox_inches='tight')
plt.close()

#plt.plot([1e-6, 1e-3], [5e-6/1e-6, 5e-6/1e-3], ':', color='gray', alpha=0.5)

plt.sca(bx)
bx.text(0.02, 0.98, """How to read this graph:
The horizontal axis represents penetration of the population.
The vertical axis indicates under-reporting of infections
(compare to Diamond Princess and South Korea).
Deaths (rare!) occur after a delay. For example, in China and 
South Korea, deaths keep increasing after no new infections.

Definitions:
Vulnerable population = Country demographic age groups multiplied 
by their relative mortality (taken from Riou et al. 2020).
# of infected = confirmed cases - recovered cases
""", va='top', ha='left', transform=bx.transAxes)
plt.xlabel('# of Infected / Vulnerable Population / # hospital beds per 10,000 people')
plt.ylabel('# of Deaths / # of Confirmed cases')
plt.xscale('log')
plt.yscale('log')
plt.hlines(7/712, 1e-7, 1e-3, linestyles=['--'], color='gray')
plt.text(1e-3, 7/712, 'Diamond Princess', ha='right', va='bottom', size=6)
plt.ylim(1e-3, 1)
plt.xlim(1e-7, 1e-3)
#plt.legend(loc='best', ncol=3, prop=dict(size=8))
plt.savefig('ratio_beds.pdf', bbox_inches='tight')
plt.savefig('ratio_beds.png', bbox_inches='tight')
plt.close()
