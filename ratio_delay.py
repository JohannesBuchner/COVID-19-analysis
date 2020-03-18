import numpy as np
import matplotlib.pyplot as plt
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

print("loading population data...")
pop = pandas.concat([
	pandas.read_csv('UNdata_Export_20200316_150200133.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_150838749.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_151648629.csv.gz'),
	pandas.read_csv('UNdata_Export_20200316_152402097.csv.gz'),
	])

#print("countries:", sorted(set(pop["Country or Area"])))

for tau in range(1, 14):
	print("per-country extraction:")
	print()
	print("%20s %6s %14s %s" % ("Country", "Deaths", "Population", "Vulnerable fraction"))
	#for rows1, rows2 in zip(open(f1), open(f2)):
	for (i, row1), (_, row2) in zip(d1.iterrows(), d2.iterrows()):
		timeseries_reported = np.array(row1[4:], dtype=int)
		timeseries_dead = np.array(row2[4:], dtype=int)
		country = row1.name
		pop_country = pop[pop["Country or Area"] == country_name_replacement.get(row1.name, row1.name)]
		if len(pop_country) == 0: # or pop_country.Year.dtype.char == 'O':
			continue
		if timeseries_dead.max() <= 5:
			continue
		#if country not in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South']:
		#	continue
		
		year = pandas.to_numeric(pop_country.Year)
		country_recent = pop_country[year == year.max()]
		num_people = [country_recent[country_recent.Age.isin(ages)].Value.sum()
			for ages in agegroups]
		vulnerable_number = np.array(num_people) * agegroups_mortality
		
		print("%20s %6d %14d %.2f%%" % (country, sum(timeseries_dead), 
			sum(num_people), sum(vulnerable_number) * 100 / sum(num_people)))
		
		mask = timeseries_dead[tau:] > 5
		x = timeseries_reported[:-tau][mask] / vulnerable_number.sum()
		y = timeseries_dead[tau:][mask] / timeseries_reported[:-tau][mask]
		l, = plt.plot(x, y,
			'o-' if country in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South'] else 's-', ms=2,
			label=country, alpha=0.5)
		
		if len(y) > 0:
			plt.plot(x[-1], y[-1],
				'o' if country in ['US', 'Germany', 'Japan', 'Italy', 'Korea, South'] else 's',
				color=l.get_color())
			plt.text(x[-1], y[-1], country, va='bottom', ha='left', size=8)

	plt.xlabel('# of Cases / Vulnerable Population')
	plt.ylabel('# of Deaths / # of Cases')
	plt.xscale('log')
	plt.yscale('log')
	plt.ylim(1e-3, 10)
	plt.legend(loc='best', ncol=3, prop=dict(size=8))
	plt.savefig('ratio_tau%d.png' % tau, bbox_inches='tight')
	plt.close()
