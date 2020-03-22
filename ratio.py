import numpy as np
import matplotlib.pyplot as plt
import pandas
import os
from datetime import datetime, timedelta
from adjustText import adjust_text
from numpy import log, exp
import locale

locale.setlocale(locale.LC_ALL, "en_US.utf8")

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
predictions = []
#min_dead = 4
min_series = 10
min_series = 7

dates = [datetime.strptime(c, "%m/%d/%y").date() for c in d1.columns[2:]]

print("per-country extraction:")
print()
print("%20s %4s %6s %14s %s" % ("Country", "Beds", "Deaths", "Population", "Vulnerable fraction"))
#for rows1, rows2 in zip(open(f1), open(f2)):
for (i, row1), (_, row2), (_, row3) in zip(d1.iterrows(), d2.iterrows(), d3.iterrows()):
	
	timeseries_reported = np.array(row1[2:], dtype=int)
	timeseries_dead = np.array(row2[2:], dtype=int)
	timeseries_recovered = np.array(row3[2:], dtype=int)
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
		
		if country_brief in marked_countries_colors or use_all_countries:
			plt.figure()
			plt.title(country)
			plt.plot(timeseries_reported - timeseries_recovered, 'o-')
			lo, hi = 0, len(timeseries_reported) + 21
			x = np.arange(len(timeseries_reported) - 7, hi)
			logy_data = log(timeseries_reported - timeseries_recovered)
			i0 = len(timeseries_reported) - 1
			x0 = i0
			logy0 = logy_data[i0]
			
			logload = log(timeseries_reported - timeseries_recovered)[-4:][::-1]
			
			if (timeseries_reported - timeseries_recovered >= capacity).any():
				# already passed limit once
				xmid = np.where(timeseries_reported - timeseries_recovered >= capacity)[0].min()
				predictions.append((xmid, xmid, xmid, country_brief))
			elif (logload > 0).all():
				plt.text(x0, exp(logy0), dates[-1], ha='right', va='bottom')
				logloadmid = -np.median(logload[1:] - logload[:-1])
				logloadmax = -np.max(logload[1:] - logload[:-1])
				logloadmin = -np.min(logload[1:] - logload[:-1])
				#logloadmid, logloadmax, logloadmin = 0, 0, 0
				plt.plot(x, exp(logy0 + (x - x0) * logloadmid), '--', alpha=0.5, color='gray')
				plt.plot(x, exp(logy0 + (x - x0) * logloadmin), ':', alpha=0.5, color='gray')
				plt.plot(x, exp(logy0 + (x - x0) * logloadmax), ':', alpha=0.5, color='gray')
				if exp(logy0) < capacity:
					maskmid = exp(logy0 + (x - x0) * logloadmid) > capacity
					maskmin = exp(logy0 + (x - x0) * logloadmin) > capacity
					maskmax = exp(logy0 + (x - x0) * logloadmax) > capacity
					xmid = x[maskmid].min() if maskmid.any() else hi
					xmin = x[maskmin].min() if maskmin.any() else hi
					xmax = x[maskmax].min() if maskmax.any() else hi
				
					plt.vlines(xmid, 1, capacity, color='gray', alpha=0.2)
					plt.vlines(xmin, 1, capacity, color='gray', alpha=0.2)
					plt.vlines(xmax, 1, capacity, color='gray', alpha=0.2)
					predictions.append((xmid, xmin, xmax, country_brief))
			
			plt.hlines(capacity, 0, hi)
			plt.text(0, capacity, '  Health care system capacity', 
				ha='left', va='bottom', size=8)
			plt.ylim(1, capacity * 5)
			plt.xlim(0, None)
			plt.ylabel("Number of infected - recovered")
			plt.xlabel("Days since %s" % (dates[0]).strftime('%Y-%m-%d'))
			plt.yscale('log')
			plt.savefig('results/%s.png' % country_brief)
			plt.close()
	
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

with open("results/capacities.rst", 'w') as f:
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

*To find out how stressed the health system of a country is*:

Compare the capacity with the current status, by subtracting the number infected by the number recovered.

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

All countries.

Here I also crudely predict when the health system will become insufficient. 
This extrapolated from the day-to-day doubling times from the last 4 days.

==================  ===========  ======================   ======
 Country             Capacity     Predicted Exhaustion     Fit
==================  ===========  ======================   ======
""")
	for stress, country, capacity in capacities:
		pred_country = [(xmid, xmin, xmax) for xmid, xmin, xmax, country_brief in predictions if country == country_brief]
		if len(pred_country) > 0:
			(xmid, xmin, xmax) = pred_country[0]
			if xmid > 0 and xmid < hi:
				f.write("%-15s   %10d      %s - %s          `Trend <https://raw.githubusercontent.com/JohannesBuchner/COVID-19-analysis/master/results/%s.png>`_\n" % (
					country[:15], capacity, 
					(dates[0] + timedelta(days=int(xmin))).strftime("%b %d"),
					(dates[0] + timedelta(days=int(xmax))).strftime("%b %d"),
					country,
					))
			else:
				f.write("%-15s   %10d      \n" % (country[:15], capacity))
		else:
			f.write("%-15s   %10d      \n" % (country[:15], capacity))
	f.write("==================  ===========  ======================   ======\n\n")


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
	plt.savefig('results/ratio.pdf', bbox_inches='tight')
	plt.savefig('results/ratio.png', bbox_inches='tight', dpi=120)
else:
	plt.savefig('results/ratio_some.pdf', bbox_inches='tight')
	plt.savefig('results/ratio_some.png', bbox_inches='tight', dpi=120)
plt.close()

#plt.plot([1e-6, 1e-3], [5e-6/1e-6, 5e-6/1e-3], ':', color='gray', alpha=0.5)

plt.sca(bx)
bx.text(0.98, 0.98, "@JohannesBuchner (%s)" % datetime.now().strftime("%Y-%m-%d"), va='top', ha='right',
	transform=bx.transAxes, size=8, color="gray")

bx.text(0.02, 1.0, """How to read this graph:
The horizontal axis represents stress on the health care system.
The vertical axis indicates under-reporting of infections
(compare to Diamond Princess and South Korea).
Deaths (rare!) occur after a delay. For example, in China and 
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
	plt.savefig('results/ratio_beds.pdf', bbox_inches='tight')
	plt.savefig('results/ratio_beds.png', bbox_inches='tight', dpi=120)
else:
	plt.savefig('results/ratio_beds_some.pdf', bbox_inches='tight')
	plt.savefig('results/ratio_beds_some.png', bbox_inches='tight', dpi=120)
plt.close()

fig = plt.figure(figsize=(6, 13))
ax = plt.gca()
#fig.patch.set_visible(False)
#ax.axis('off')
ax.spines['right'].set_visible(False)
#ax.spines['top'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)

i = 0
now = len(timeseries_reported)
countries = []
for xmid, xmin, xmax, country_brief in sorted(predictions, reverse=True):
	if xmid < hi:
		countries.append(country_brief.replace(' and ', '&').replace('Republic', 'Rep.'))
		#dates[-1].date() + (xmid - len(timeseries_reported)):
		plt.errorbar(y=i, x=xmid, xerr=[[xmid-xmin], [xmax-xmid]], 
			color='k' if xmid > now else 'r',
			capsize=4, marker='o', mfc=None)
		if xmid > now:
			plt.text(xmin, i, country_brief + '   ', ha='right', va='center')
		else:
			plt.text(xmin, i, '   ' + country_brief, ha='left', va='center')
		i += 1
ax.xaxis.tick_top()
ax.xaxis.set_label_position('top') 
plt.title("Prediction: when healthcare system limit is reached")
plt.text(0, -0.02, """A person you infect today may need a hospital bed in 10-14 days. 
But the hospitals may be crowded then. $\\rightarrow$ Delay the spread _now_.""", va='top',
	transform=ax.transAxes)
#plt.xlim(now, hi)
plt.ylim(-0.5, i - 0.5)
plt.vlines(now, -0.5, i - 0.5, color='gray', alpha=0.2)
plt.vlines(now + 7, -0.5, i - 0.5, color='gray', alpha=0.2)
plt.vlines(now + 14, -0.5, i - 0.5, color='gray', alpha=0.2)
#plt.yticks(range(len(countries)), countries)
plt.yticks([])

lo, _ = plt.xlim()
xticks = np.arange(lo-1, hi)
plt.xlim(lo-1, hi)
plt.xticks(xticks, [(dates[0] + timedelta(days=i)).strftime("%b %d") for i in xticks], rotation=90)
#plt.xticks(np.arange(now, hi), np.arange(hi - now))
#plt.text(-0, 1.01, "%s+X days:" % dates[-1], va='bottom', ha='left',
#	transform=ax.transAxes)
#plt.xticks([now, now+1, now+2, now+3, now+4, now+5, now+6, now+7, now+14, hi], [0, 1, 2, 3, 4, 5, 6, 7, '14', '+%d days' % (hi-now)])
#plt.xlabel("Day after %s" % dates[-1])
if use_all_countries:
	plt.savefig('results/predictions.pdf', bbox_inches='tight')
	plt.savefig('results/predictions.png', bbox_inches='tight', dpi=120)
else:
	plt.savefig('results/predictions_some.pdf', bbox_inches='tight')
	plt.savefig('results/predictions_some.png', bbox_inches='tight', dpi=120)

plt.close()

