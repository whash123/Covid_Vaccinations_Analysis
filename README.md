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
vaccine_map('Pfizer/BioNTech')
```

![Fig 5](/Figs/Fig_5.png)
![Fig 6](/Figs/Fig_6.png)

```
vaccine_map('Pfizer/BioNTech')
```

![Fig 7](/Figs/Fig_7.png)
![Fig 8](/Figs/Fig_8.png)

```
vaccine_map('Pfizer/BioNTech')
```

![Fig 9](/Figs/Fig_9.png)
![Fig 10](/Figs/Fig_10.png)

```
vaccine_map('Pfizer/BioNTech')
```

![Fig 11](/Figs/Fig_11.png)
![Fig 12](/Figs/Fig_12.png)

```
vaccine_map('Pfizer/BioNTech')
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
![Fig 16](/Figs/Fig_16.png)
![Fig 17](/Figs/Fig_17.png)
![Fig 18](/Figs/Fig_18.png)
![Fig 19](/Figs/Fig_19.png)
![Fig 20](/Figs/Fig_20.png)
![Fig 21](/Figs/Fig_21.png)
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
