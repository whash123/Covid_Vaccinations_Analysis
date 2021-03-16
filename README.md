# Covid Vaccinations Analysis

This is a Python project analyzing and visualizing the current progress for the Covid vaccination rollout across the world. You can find the link to the dataset here, which is updated each day to include more vaccination data:
[Covid data](https://www.kaggle.com/gpreda/covid-world-vaccination-progress)

Note I performed this analysis on vaccination data up until 3/13/21 so things obviously could have changed since then!

Above in the files you can find a Jupyter notebook file and a normal Python .py scipt where you can play around with the analysis and visualizations. You will see many of them are built as functions that you can pass different arguments for and have a look at altered charts from the ones I have produced in this file. Similarly, the plots you will find below are static images; if you download the notebook or script, you will have access to the interactable plotly charts.

Have a look at how things are going as we aim to put Covid-19 behind us!



## 1) Exploring the different types of vaccinations available around the world
```
map_vaccines = px.choropleth(locations = full_df['country'], 
                             color = full_df['vaccines'],
                             locationmode = "country names",
                             title = "Countries using each set of vaccinations",
                             height = 800
                             )
map_vaccines.update_layout({'legend_orientation':'h', 'legend_title':'Set of vaccinations'})
map_vaccines.show()
```

![Fig 1](/Figs/Fig_1.png)

```
count_vacc_sets = {}
for vacc_set in full_df['vaccines'].unique():
    vacc_df = full_df[full_df['vaccines'] == vacc_set]
    list_countries = list(vacc_df['country'].unique())
    n_countries = len(list_countries)
    count_vacc_sets[vacc_set] = {
        'count': n_countries,
        'countries': list_countries
    }
    
vacc_set_df = pd.DataFrame(count_vacc_sets).transpose().reset_index().rename(columns = {'index': 'vaccine_set'})

vacc_tm = px.treemap(vacc_set_df,
                 path = ['vaccine_set'],
                 values = 'count',
                 title = 'Number of countries each unique set of vaccines can be found in',
                 height = 600, width = 800)
vacc_tm.data[0].textinfo = 'label+text+value'
vacc_tm.show()
```

![Fig 2](/Figs/Fig_2.png)

```
unique_vaccines = []
for total_vacc in list(full_df.vaccines.unique()):
    split_vaccs = total_vacc.split(', ')
    for comp in split_vaccs:
        if comp not in unique_vaccines:
            unique_vaccines.append(comp)

vacc_all_countries = {}
for vacc_comp in unique_vaccines:
    countries = full_df[full_df.vaccines.str.contains(vacc_comp)]['country'].unique().tolist()
    vacc_all_countries[vacc_comp] = {
        'number': len(countries),
        'list_countries': countries
    }

def binary_vacc(country, vaccine):
    if country in vacc_all_countries[vaccine]['list_countries']:
        return True
    else:
        return False

for vacc in vacc_all_countries.keys():
    full_df[vacc] = full_df['country'].apply(binary_vacc, vaccine = vacc)

cols_to_ffill = ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated', 'total_vaccinations_per_hundred', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred']

def vaccine_map(vaccine_name = None):
    if (vaccine_name is None):
        print('Error must input a vaccine type')
    else: 
        filter_df = full_df[full_df[vaccine_name] == True]
        map_vaccines = px.choropleth(locations = filter_df['country'], 
                             color = filter_df[vaccine_name],
                             locationmode = "country names",
                             title = f"Countries using {vaccine_name}",
                             height = 500
                             )
        map_vaccines.update_layout(showlegend=False)
        map_vaccines.show()
        
        lines = []
        for country in filter_df['country'].unique():
            vacc_data = filter_df[filter_df['country'] == country]
            
            for col in cols_to_ffill:
                vacc_data[col] = vacc_data[col].replace(to_replace = 0, method = 'ffill')
            
            lines.append(
                go.Scatter(
                    name = country,
                    x = vacc_data['date'],
                    mode = 'lines+markers',
                    y = vacc_data['total_vaccinations_per_hundred']
                )
            )

        vaccine_line_plot = go.Figure(lines)
        vaccine_line_plot.update_layout(
            title = f'Vaccination progress per country using {vaccine_name} as one of its vaccination suppliers',
            yaxis_title = "Vaccinations Per Hundred People",
            hovermode = 'x',
            legend_orientation = 'h',
            height = 800
        )

        vaccine_line_plot.show()
```

```
vaccine_map('Pfizer/BioNTech')
```

![Fig 3](/Figs/Fig_3.png)
![Fig 4](/Figs/Fig_4.png)

```
vaccine_map('Moderna')
```

![Fig 5](/Figs/Fig_5.png)
![Fig 6](/Figs/Fig_6.png)

```
vaccine_map('Oxford/AstraZeneca')
```

![Fig 7](/Figs/Fig_7.png)
![Fig 8](/Figs/Fig_8.png)

```
vaccine_map('Sputnik V')
```

![Fig 9](/Figs/Fig_9.png)
![Fig 10](/Figs/Fig_10.png)

```
vaccine_map('Sinopharm/Beijing')
```

![Fig 11](/Figs/Fig_11.png)
![Fig 12](/Figs/Fig_12.png)

```
vaccine_map('Sinovac')
```

![Fig 13](/Figs/Fig_13.png)
![Fig 14](/Figs/Fig_14.png)

```
unique_vaccines_countries = pd.DataFrame(vacc_all_countries).transpose().reset_index().rename(columns = {'index': 'vaccine_company'}).sort_values(by = 'number', ascending = False)

vacc_bar = px.bar(unique_vaccines_countries,
             x = 'vaccine_company', y = 'number',
             labels = {'vaccine_company': 'Vaccination Company', 'number': 'Number of Countries Available'})
vacc_bar.show()
```
![Fig 15](/Figs/Fig_15.png)



## 2) Comparing country vaccination rollout progression

```
all_countries = full_df['country'].unique().tolist()
def days_since_start(date, first_date):
    if (date <= first_date):
        return 0
    else:
        delta = date - first_date
        return delta.days
        
adjusted_df = full_df[full_df['country'] == all_countries[0]]
a_first_vaccination = min(adjusted_df['date'])
a_total_vaccinations = max(adjusted_df['total_vaccinations'])
a_total_people_vaccinated = max(adjusted_df['people_vaccinated'])

cols_to_ffill = ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated', 'total_vaccinations_per_hundred', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred']

for col in cols_to_ffill:
    adjusted_df[col] = adjusted_df[col].replace(to_replace = 0, method = 'ffill')
adjusted_df['vaccination_day_number'] = adjusted_df['date'].apply(days_since_start, first_date = a_first_vaccination)
adjusted_df['percent_total_vaccinations'] = adjusted_df['total_vaccinations'] / a_total_vaccinations
adjusted_df['percent_people_vaccinated'] = adjusted_df['people_vaccinated'] / a_total_people_vaccinated

all_countries_left = all_countries[1:]

for country in all_countries_left:
    country_df = full_df[full_df['country'] == country]
    c_first_vaccination = min(country_df['date'])
    c_total_vaccinations = max(country_df['total_vaccinations'])
    c_total_people_vaccinated = max(country_df['people_vaccinated'])
    
    for col in cols_to_ffill:
        country_df[col] = country_df[col].replace(to_replace = 0, method = 'ffill')
    
    country_df['vaccination_day_number'] = country_df['date'].apply(days_since_start, first_date = c_first_vaccination)
    country_df['percent_total_vaccinations'] = country_df['total_vaccinations'] / c_total_vaccinations
    country_df['percent_people_vaccinated'] = country_df['people_vaccinated'] / c_total_people_vaccinated
    
    adjusted_df = pd.concat([adjusted_df, country_df], axis = 0)
```

```
lines = []
for vacc in vacc_all_countries.keys():
    vacc_df = adjusted_df[adjusted_df[vacc] == True]    
    grouped = pd.DataFrame(vacc_df.groupby('date').sum()).reset_index()
    lines.append(
            go.Scatter(
            name = vacc,
            x = grouped['date'],
            mode = 'lines+markers',
            y = grouped['total_vaccinations'],
        )
    )    
vacc_lp = go.Figure(lines)
vacc_lp.update_layout(
    title = 'Vaccination progress for the countries each vaccine can be found in',
    yaxis_title = "Count",
    hovermode = 'x',
    legend_orientation = 'h',
    height = 800
)
vaccp_lp.show()
```

![Fig 16](/Figs/Fig_16.png)

```
lines = []
for vacc_set in adjusted_df['vaccines'].unique():
    vacc_df = adjusted_df[adjusted_df['vaccines'] == vacc_set]
    grouped = pd.DataFrame(vacc_df.groupby('date').sum()).reset_index()
    lines.append(
            go.Scatter(
            name = vacc_set,
            x = grouped['date'],
            mode = 'lines+markers',
            y = grouped['total_vaccinations'],
        )
    )
unique_vacc_lp = go.Figure(lines)
unique_vacc_lp.update_layout(
    title = 'Vaccination progress per set of vaccine present in each country',
    yaxis_title = "Number of vaccines administered",
    hovermode = 'x',
    legend_orientation = 'h',
    height = 1000
)
unique_vacc_lp.show()
```

![Fig 17](/Figs/Fig_17.png)

```
max_vacc = {}
for c in all_countries:
    country_df = adjusted_df[adjusted_df['country'] == c]
    max_total_vaccinations = max(country_df['total_vaccinations'])
    max_total_vaccinations_per_hundred = max(country_df['total_vaccinations_per_hundred'])
    day_started_vaccinating = min(country_df['date'])
    days_spent_vaccinating = max(country_df['vaccination_day_number'])
    max_vacc[c] = {
        'total_vaccinations': max_total_vaccinations,
        'total_per_hundred': max_total_vaccinations_per_hundred,
        'day_started': day_started_vaccinating,
        'days_since_starting': days_spent_vaccinating
    }
    
total_vacc_df = pd.DataFrame(max_vacc).transpose().reset_index()\
    .rename(columns = {'index': 'country'}).sort_values(by = 'total_vaccinations', ascending = False)\
    .merge(pop_dict, how = 'left', left_on = 'country', right_on = 'Country').drop('Country', axis = 1)\
    .merge(continents, how = 'left', left_on = 'country', right_on = 'Country').drop('Country', axis = 1)\
    .rename(columns = {'Population': 'population', 'Continent': 'continent'})
```

```
def top_countries_chart(n = 25, time_period = 'date', pop_adjusted = True):
    sorted_df = total_vacc_df.sort_values(by = 'total_vaccinations', ascending = False)
    countries = sorted_df.iloc[0 : n, ]['country'].tolist()    
    if (time_period != 'date' and time_period != 'vaccination_day_number'):
        print('must have different time period entry')
    elif time_period == 'date':
        title = 'Vaccination progress per country by date'
    elif time_period == 'vaccination_day_number':
        title = 'Vaccination progress per country from the start of their vaccination rollout'
    if pop_adjusted == True:
        y_title = 'Vaccinations per hundred'
        y_metric = 'total_vaccinations_per_hundred'
    elif pop_adjusted == False:
        y_title = 'Vaccinations'
        y_metric = 'total_vaccinations'
    else:
        print('must have different pop adjusted entry')        
    lines = []
    for country in countries:
        vacc_data = adjusted_df[adjusted_df['country'] == country]
        lines.append(
            go.Scatter(
                name = country,
                x = vacc_data[time_period],
                mode = 'lines+markers',
                y = vacc_data[y_metric],
            )
        )
    fig = go.Figure(lines)
    fig.update_layout(
        title = title,
        yaxis_title = y_title,
        hovermode = 'x',
        legend_orientation = 'h',
        height = 800
    )
    fig.show()
```

```
top_countries_chart(n = 50, time_period = 'date', pop_adjusted = False)
```

![Fig 18](/Figs/Fig_18.png)

```
top_countries_chart(n = 50, time_period = 'vaccination_day_number', pop_adjusted = False)
```
![Fig 19](/Figs/Fig_19.png)

```
top_countries_chart(n = 30, time_period = 'date', pop_adjusted = True)
```

![Fig 20](/Figs/Fig_20.png)

```
top_countries_chart(n = 30, time_period = 'vaccination_day_number', pop_adjusted = True)
```

![Fig 21](/Figs/Fig_21.png)

```
n = 25
raw_adjusted_comparison = px.scatter(total_vacc_df.iloc[0:n, ],
           x = 'total_vaccinations',
           y = 'total_per_hundred',
           size = 'population',
           hover_name = 'country',
           color = 'continent',
           size_max = 80,
           height = 800,
           title = 'Comparing country progress for total vaccinations and total vaccinations per hundred people',
           labels = dict(total_per_hundred = "Total Vaccinations per Hundred People", total_vaccinations = "Total Vaccinations (raw)"))

raw_adjusted_comparison.show()
```

![Fig 22](/Figs/Fig_22.png)



## 3) Adjusted vaccination progress and projecting the end of Covid!
![Fig 23](/Figs/Fig_23.png)
![Fig 24](/Figs/Fig_24.png)
![Fig 25](/Figs/Fig_25.png)
![Fig 26](/Figs/Fig_26.png)
![Fig 27](/Figs/Fig_27.png)
![Fig 28](/Figs/Fig_28.png)
![Fig 29](/Figs/Fig_29.png)
![Fig 30](/Figs/Fig_30.png)
