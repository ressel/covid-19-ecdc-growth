#!/usr/bin/python3

import datetime
import math
import matplotlib.lines as mlines
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, LogLocator
from matplotlib.font_manager import FontProperties
import numpy as np
import pandas as pd
import sys

# Plots the growth in COVID-19 cases or deaths from the day each country
# reached 100 cases or 10 deaths, respectively.

# The ECDC data is in Excel format, requiring Pandas or something else that can
# read that format.

# To avoid downloading the data for every run, run this once per day and then
# pass the local file name on the command line:
# wget https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-2020-03-22.xlsx

column = 'Cases'

# Argument handling
arg = 1
option = sys.argv[arg] if len(sys.argv) > arg else ''
if option == '-d' or option == '-deaths' :
     column = 'Deaths'
     arg = 2
path = sys.argv[arg] if len(sys.argv) > arg else 'https://www.ecdc.europa.eu/sites/default/files/documents/COVID-19-geographic-disbtribution-worldwide-' + datetime.date.today().isoformat() + '.xlsx'

df = pd.read_excel(path)

min_y = 100 if column == 'Cases' else 10

country_dict = {}
# Group by 'GeoId' and not "Countries and territories" because the latter has
# inconsistent capitalization ('CANADA' and 'Canada').
for country, group in df.groupby('GeoId'):
     # Reverse the time order for each group
     df2 = group.iloc[::-1][['DateRep', column]]
     df2['cum'] = df2[column].cumsum()
     df2 = df2.loc[df2['cum'] >= min_y]
     if len(df2) > 1:
          country_dict[country] = df2[['DateRep', 'cum']]

countries = ['US', 'DE', 'IT', 'FR', 'ES', 'CN', 'KR', 'JP']

# Limit to 5 days past the second longest (for China)
counts = np.array([len(country_dict[c]) for c in countries])
counts.partition(len(counts) - 1)
max_x = min(counts[-2] + 5, counts[-1])
max_y = max(country_dict[c].iloc[-1]['cum'] for c in countries)

fig, ax = plt.subplots()
plt.yscale('log')
plt.grid()
ax.yaxis.set_major_locator(LogLocator(subs=(1, 2, 5)))
# Don't use scientific notation for the y-axis and add thousand separators
ax.yaxis.set_major_formatter(FuncFormatter(lambda x, pos: '{:,.0f}'.format(x)))

# Draw dotted lines indicating doubling in 1-7 days.
for d in range(1, 8):
     x2 = math.log(max_y / min_y) / math.log(pow(2, 1 / d))
     y2 = max_y
     if x2 > max_x - 1:
          x2 = max_x - 1
          y2 = pow(pow(2, 1 / d), x2) * min_y
     ax.add_line(mlines.Line2D([0, x2], [min_y, y2],
                               c='#666', ls='dotted', lw=0.75))

# Plot the selected countries and print the total for each country.
for country in countries:
     df2 = country_dict[country]
     c = min(max_x, len(df2))
     ax.plot(range(c), df2['cum'][:c],
             label=country, lw=0.75, marker='.', ms=4)
     print(country, df2.iloc[-1]['cum'])

# change window and default file name to something else than figure 1:
f = plt.gcf()
f.canvas.set_window_title('covid-19-' + column.lower() + '-ecdc')

chart_title = 'Coronavirus Total ' + column
chart_source = 'Source: ' + path
plt.title(chart_title)
font = FontProperties()
font.set_size('x-small')
plt.figtext(0.99, 0.01, chart_source, fontproperties=font, horizontalalignment='right')
ax.legend(loc='lower right')
plt.xlim(left=0)
plt.ylim(bottom=min_y)

plt.show()
