# Covid Vaccinations Analysis

This is a Python project analyzing and visualizing the current progress for the Covid vaccination rollout across the world. You can find the link to the dataset here, which is updated each day to include more data:
[Covid data](https://www.kaggle.com/gpreda/covid-world-vaccination-progress)

Note I performed this analysis on vaccination data up until 3/13/21 so things obviously could have changed since then!

Above in the files you can find a Jupyter notebook file and a normal Python .py scipt where you can play around with the analysis and visualizations. You will see many of them are built as functions that you can pass different arguments for and have a look at altered charts from the ones I have produced in this file. Similarly, the plots you will find below are static images; if you download the notebook or script, you will have access to the interactable plotly charts.

Have a look at how things are going as we aim to put Covid-19 behind us!


## Table of Contents
 * [Section 1 - Exploring Different Types of Vaccinations](#1-exploring-the-different-types-of-vaccinations-available-around-the-world)
 * [Section 2 - Looking In-Depth at Country Progression](#2-comparing-country-vaccination-rollout-progression)
 * [Section 3 - Population Adjusted Progress and Projecting the End of Covid!](#3-adjusted-vaccination-progress-and-projecting-the-end-of-covid)
 

## 1) Exploring the different types of vaccinations available around the world

A good place to start with this data is by looking into the different types of vaccinations that exist, where they are being used, and which ones are being used as part of successful vaccination rollouts. Since many of the companies selling vaccines to countries are regionally-specific and came out at different times, it would be good to get a feel for which ones each country is using, and if that has any effect on vaccination progress.

Let's first have a look around the world of which vaccines each country is currently using as part of its vaccination rollout plan against Covid-19:

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

As you can see, there are many different sets of vaccinations being used across the world, but the map doesn't tell us everything we need to know. Let's check and see how widespread each of these groupings of vaccinations are by taking the count of countries they have been used in.

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
```

```
vacc_tm = px.treemap(vacc_set_df,
                 path = ['vaccine_set'],
                 values = 'count',
                 title = 'Number of countries each unique set of vaccines can be found in',
                 height = 600, width = 800)
vacc_tm.data[0].textinfo = 'label+text+value'
vacc_tm.show()
```

![Fig 2](/Figs/Fig_2.png)

It's interesting to note that this dataset bundles the vaccines that a country are using together in one variable named *vaccines*. For each row, the value is a list of all the types of vaccinations a country is using, leading to many different unique sets of vaccines. For example, Guatemala is using only Moderna, whereas Israel is using both Moderna and Pfizer/BioNTech. Even though they have an overlap in Moderna, the lists are not the same and therefore they will be in separate categories for the chart as it groups distinct values.

As you can see, the most popular *sets* of vaccines are countries that just have access to Oxford/AstraZeneca and those that just have access to Pfizer/BioNTech, though you can see some of the more unique sets (like Moderna, Oxford/AstraZeneca, and Pfizer/BioNTech together) are also prevalent. But this doesn't tell us the whole story does it? Let's find out how prevalent each individual vaccine is.

We can use some string splitting to get each unique vaccine and create a dataframe counting the number of countries they appear in.

```
unique_vaccines = []
for total_vacc in list(full_df.vaccines.unique()):
    split_vaccs = total_vacc.split(', ')
    for comp in split_vaccs:
        if comp not in unique_vaccines:
            unique_vaccines.append(comp)
```

```
vacc_all_countries = {}
for vacc_comp in unique_vaccines:
    countries = full_df[full_df.vaccines.str.contains(vacc_comp)]['country'].unique().tolist()
    vacc_all_countries[vacc_comp] = {
        'number': len(countries),
        'list_countries': countries
    }
```

```
unique_vaccines_countries = pd.DataFrame(vacc_all_countries).transpose().reset_index()\
    .rename(columns = {'index': 'vaccine_company'}).sort_values(by = 'number', ascending = False)
```

Now that we have a df portraying the number of countries each *unique* vaccine is, we can compare these on a quick bar chart:

```
vacc_bar = px.bar(unique_vaccines_countries,
             x = 'vaccine_company', y = 'number',
             labels = {'vaccine_company': 'Vaccination Company', 'number': 'Number of Countries Available'})
vacc_bar.show()
```
![Fig 15](/Figs/Fig_15.png)

Ah, this paints a much better picture. We can see that, while Pfizer/BioNTech on its own was prevalent in 26 countries (that did not also have access to any other vaccines), it actually is used in 72 countries overall, some on its own and some as part of a set of offerings by the country. That helps clear things up a bit and makes sense, given we know Pfizer was one of the first manufacturers to distribute their vaccine.

But what if we wanted to learn more about a) where these individual vaccines are being rolled out, and b) how the countries that are using them are faring? We can create a map for each vaccine and a line plot showing the progress of each country that has access to each vaccine below.

Note: the line plots below show the overall vaccination progress for each country that has access to each of the vaccines. Since the data groups vaccines together, it's impossible to estimate the attribution of each vaccine to a country that is using it as part of a set of vaccinations they are offering.

```
def binary_vacc(country, vaccine):
    if country in vacc_all_countries[vaccine]['list_countries']:
        return True
    else:
        return False

for vacc in vacc_all_countries.keys():
    full_df[vacc] = full_df['country'].apply(binary_vacc, vaccine = vacc)
```

```
cols_to_ffill = ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated', 'total_vaccinations_per_hundred', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred']
```

```
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

So this confirms quite a few things for us that we may have already assumed. Firstly, these vaccines are highly regional, which is evident when looking at Sputnik V penetrating Russia, East Asia, and some of South America, while vaccines like Moderna are really limited to only North America and Western Europe.

Similarly, we find that, per-hundred-people, the countries that have access to the vaccines that were shipping earlier, like Pfizer/BioNTech and Oxford/AstraZeneca are in a better situation now than those reliant on more recent vaccinations, like Sinovac. This is likely highly related to how long they were able to roll out their vaccinations, and how much the companies were able to amp up their production and distribution lines.

But let's take a closer look at how some of these countries are doing with their rollouts.

## 2) Comparing country vaccination rollout progression

So, there is a lot of good information in this dataset pertaining to each country's progress with the vaccinations. There is raw vaccine data, population-adjusted data, etc. and it is all listed per day since the first day they were able to successfully vaccinate one of their citizens. This first part, however, I will be building a few more interesting variables I think might help further down the road.

For each of these countries, I am going to do some individual progress adjustments. These adjusted variables will be at the country level and include information for each date like how many days since they started vaccinating (so we can see progress for each country benchmarked to when they started progress) and percent of their own overall vaccinations they have completed up until that date, which can give some interesting insights into the pace at which each country was able to ramp up their vaccine distribution.

```
all_countries = full_df['country'].unique().tolist()
def days_since_start(date, first_date):
    if (date <= first_date):
        return 0
    else:
        delta = date - first_date
        return delta.days
```

```
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

Now that we have our adjusted variables, we can start having a look at how these countries have progressed since they began vaccinating.

First we will just take a quick look at the raw progression information as a baseline, and we will look at the countries grouped together by the individual vaccine they have access to, as well as the vaccine set they have access to, similar to how we did this above in Section 1.

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

As we noted before, these charts are heavily biased by the amount of countries each vaccine and vaccine set are found in, as well as the populations of such countries. This is why Pfizer/BioNTech is leading the way by such a large margin, having been distributed early, to many, large countries.

What if we wanted to look at a similar type of progress chart, but broken out by country rather than by vaccine? Below is some code that will allow us to create a dictionary of some summary statistics for each country that will initially be important so we can choose to plot the performance of the highest vaccinating countries, but we will gather more summary data along the way that will help in Section 3.

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

Now that we have this dictionary ready to be used, let's make a function where you can look at the top *n* number of countries and their progress so far, in raw vaccination numbers and population-adjusted numbers.

This is important for 2 reasons: 1) there are way too many countries to make any chart with all of them readable or useful to use and 2) for the population-adjusted numbers, many of the countries with the lowest populations have the highest progress, biased by their low overall population. Being able to compare the progress of the top 30 or 50 countries, where the numbers are a bit more sensible to look at can give us more insights.

Like all my other chart-building functions, if you download the notebook or script you can play around with them to create your own charts and find some interesting pieces of information yourself!


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

Let's first just look at the top 50 countries in raw vaccinations, setting the timeline to be the date:

```
top_countries_chart(n = 50, time_period = 'date', pop_adjusted = False)
```

![Fig 18](/Figs/Fig_18.png)

While this is interesting and does help paint the picture, what if we wanted to see how each country was doing on their nth day of vaccinations? For this, we can easily set the x-axis to be the "vaccination day number," which adjusts each countries progress to start at their first day of vaccinating. This will help us see some of the countries that may have higher progress than other because they started out earlier, or vice versa.

```
top_countries_chart(n = 50, time_period = 'vaccination_day_number', pop_adjusted = False)
```
![Fig 19](/Figs/Fig_19.png)

This helps as well - giving us some more clues as to how they are doing. But the natural next question is - aren't these numbers heavily skewed towards countries with larger populations? Isn't it reasonable that countries with more people will have higher numbers for vaccines? And yes, that is the case. So below we have similar charts, comparing the progress of each country in how many vaccinations they have administered *per hundred citizens,* which should help. 

```
top_countries_chart(n = 30, time_period = 'date', pop_adjusted = True)
```

![Fig 20](/Figs/Fig_20.png)

```
top_countries_chart(n = 30, time_period = 'vaccination_day_number', pop_adjusted = True)
```

![Fig 21](/Figs/Fig_21.png)

Now we have a much better idea of how they are doing! While it may not have been obvious before, since their populations are too low to be at the top of the raw vaccinations charts, Israel and the United Arab Emirates are actually leading the way in per-hundred vaccinations. Israel actually has administered more than 1 vaccine per person at the time of writing! These countries invested heavily and early, and were able to see some serious progress in beating Covid.

Now that we have seen the progress for each country in raw numbers and in population-adjusted numbers individually, what if we plotted these together on the same chart? This is where our summary dictionary can come in handy. I'll color them by continent and make the sizes the populations, so we can extract a bit more information about how these countries are doing on raw x population-adjusted vaccinations:

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

As you can see, this helps our case. While countries like the USA (far right) and India / China (two large red points) have the most number of vaccinations, that is clearly a function of their massive populations compared to other countries, while countries with smaller populations are doing really well, despite having smaller raw numbers. We could have easily missed this critical piece if we had left our charts to just total vaccinations.

But what if we looked a little more about the rate at which these countries are vaccinating their citizens? And what if we could use that information to inform the future, and have a guess at when these populations will be fully vaccinated?


## 3) Adjusted vaccination progress and projecting the end of Covid!

Now, using our summary chart, we know how many total vaccinations per hundred citizens they have been able to administer, and we know how long they have been vaccinating their citizens for, with the "vaccination_day_number" variable, so we can find the straight-line average number of vaccinations per 100 people for each country per day. As stated before, some countries that started vaccinating early will have higher numbers today than those that were behind, but those same countries could be progressing at a faster rate. Let's have a look.

This function below will allow us to create a treemap, using the new "world" column as a parent to each of the continents where the countries are grouped. You can pass the minimum population to be included in this chart (again, countries with fewer people skew higher on the population adjusted metrics) and whether or not you want to see the per-hundred vaccinations data as total / final-date or average per day they have been vaccinating.

```
total_vacc_df['average_daily_percent_vaccinated'] = round(total_vacc_df['total_per_hundred'] / total_vacc_df['days_since_starting'], 4)
total_vacc_df['world'] = 'world'
total_vacc_df = total_vacc_df.replace(np.inf, np.nan)
```

```
def avg_vaccination_progress(vals, min_pop = 10000000):
    if vals != 'total' and vals != 'average':
        print('must input an appropriate value type')
    elif vals == 'total':
        val_metric = 'total_per_hundred'
    elif vals == 'average':
        val_metric = 'average_daily_percent_vaccinated'
    
    chart_df = total_vacc_df[total_vacc_df['population'] >= min_pop]
    fig = px.treemap(chart_df,
                     path = ['world', 'continent', 'country'],
                     values = val_metric,
                     height = 750)
    fig.data[0].textinfo = 'label+text+value'

    fig.show()
```

Let's first look at which countries ended up in the best place - that is, which countries have performed the most total vaccinations per hundred citizens at the time of writing. I will pass a minimum population of 10M people so we can get some of the more relavent countries with stable data:

```
avg_vaccination_progress(min_pop = 10000000, vals = 'total')
```

![Fig 23](/Figs/Fig_23.png)

As we can see, many of the Western European countries, the USA, and Chile have been able to roll out a good amount of vaccinations per person in their country, coming in around the 30-40 per hundred mark. Not bad!

However, let's see which countries were the most efficient at vaccinating their population since they started vaccinating. We will look at countries with more than 1M people and set the value to "average" so we can see average number of vaccinations per hundred people per day:

```
avg_vaccination_progress(min_pop = 1000000, vals = 'average')
```

![Fig 24](/Figs/Fig_24.png)

Now that tells a different story - here we can see Israel and the UAE are performing the quickest, both performing around 1-1.3 vaccinations for every one hundred people in their country *per day*. This would be the same as the US averaging 3.5M vaccinations a day! That's incredible progress. As you can see, some of our current top performers at the total level, such as Chile, the USA, and England, are still among our most efficient distributors, however they may have started out slow and sped up as production increased.

What we can do now is, instead of giving a population minimum and looking at some countries in each continent, we can have a look at every country in each continent and compare their progression - again, still on a per-day per-hundred people basis. Since many vaccinations are regionally-diverse, it would be interesting to compare countries with those in their own continent that may have access to similar resources.

Below you can find a chart for each continent, where the y-axis is the per-day per-hundred people amount of vaccinations rolled out. The color (darker meaning more) represents the total number of vaccinations rolled out per hundred people, so we can see if some countries are vaccinating quickly, but still not fully rolled out, vs countries that, while slower, have reached more people in total:

```
for cont in total_vacc_df['continent'].unique():
    continent_df = total_vacc_df[total_vacc_df['continent'] == cont]
    sorted_df = continent_df.sort_values(by = 'average_daily_percent_vaccinated', ascending = False)
    
    fig = px.bar(sorted_df.sort_values(by = 'average_daily_percent_vaccinated', ascending = False),
                 x = 'country', y = 'average_daily_percent_vaccinated',
                 color = 'total_per_hundred',
                 color_continuous_scale = 'deep',
                 width = 800,
                 height = 500,
                 title = cont,
                 labels = dict(total_per_hundred = 'Total Vaccinations Per Hundred', average_daily_percent_vaccinated = 'Average % Population Vaccinated Per Day', country = 'Country'))
    fig.show()
```

![Fig 25](/Figs/Fig_25.png)
![Fig 26](/Figs/Fig_26.png)
![Fig 27](/Figs/Fig_27.png)
![Fig 28](/Figs/Fig_28.png)
![Fig 29](/Figs/Fig_29.png)

Now, I hinted at it before, but we actually have a variable for "people vaccinated per hundred" - which slightly differs from number of vaccinations rolled out per hundred, as some vaccines need more than 1 vaccination to complete the job. Thus, we saw how Israel actually administered more than 1 vaccination per person, but less than 100% of the population had been vaccinated.

Using this *people* vaccinated per hundred information, and the date / vaccination day number data, we can project how countries will do going forward to see if we can get an educated guess on when they will be done vaccinating their entire populations.

I want to note before this analysis that this was not the point of this notebook - the main goal was to learn more about how countries are doing and the vaccinations they are using. This is not meant to be a robust machine learning time-series prediction model, nor am I expecting any of these outcomes to be perfectly accurate. This was meant to be an interesting quick exercise to add a little context surrounding where we are as a world in opening back up.

With that being said, the below allows us to iterate over each country and perform a simple SciPy fitted curve to each country's progression in vaccinating its population and, using the parameters it returns, predict the future people vaccinated per hundred. Using this, we can find each country's final end date when they will have vaccinated their entire population!

Again, I understand there are many flaws with this process - that, being highly overfitted to the current curve, any country that has slowed down its production recently is projected to continue slowing down forever, and that it assumes the country continues on the same path it has so far, with no changes. Also, this assumes 100% of the population would take the vaccine, and let's be honest, that's not going to happen...

Obviously these are issues, but it was still a fun quick exercise!

```
countries_to_predict = []
for country in adjusted_df['country'].unique():
    check_df = adjusted_df[adjusted_df['country'] == country]
    if max(check_df['people_vaccinated_per_hundred']) > 0:
         countries_to_predict.append(country)
```

```
def curve_func(x, a, b, c):
    return a * x + b * x**2 + c

country_results = {}

for country in countries_to_predict:
    country_df = adjusted_df[adjusted_df['country'] == country]
    
    if(country_df.shape[0] >= 5):
        xdata = np.array(country_df['vaccination_day_number'])
        ydata = np.array(country_df['people_vaccinated_per_hundred'])

        popt, pcov = curve_fit(curve_func, xdata = xdata, ydata = ydata)

        x = 0
        max_perc_vacc = 0
        day_for_max = 0

        while x < 365:
            pred = popt[0] * x + popt[1]* x**2 + popt[2]
            if max_perc_vacc < 100:
                if pred > max_perc_vacc:
                    max_perc_vacc = pred
                    day_for_max = x

            if pred >= 100:
                max_perc_vacc = pred
                day_for_max = x
                break
            elif pred < 100:
                x = x + 1

        if max_perc_vacc >= 100:
            country_results[country] = day_for_max
```

Now that we have our super accurate predictions for how many days each country needs to vaccinate 100% of its population, we can add that to each country's vaccination start date to get the final date needed for Covid to be knocked out and the world to get back to pre-pandemic days!

```
country_results_df = pd.DataFrame(country_results, index = ['days_until_fully_vaccinated']).transpose()\
    .reset_index().rename(columns = {'index': 'country'})

country_results_df = country_results_df.merge(total_vacc_df, on = 'country')
country_results_df['final_date'] = country_results_df['day_started'] + pd.to_timedelta(country_results_df['days_until_fully_vaccinated'], unit = 'd')
```

```
pred_plot = px.scatter(country_results_df,
           x = 'final_date',
           y = 'total_per_hundred',
           size = 'population',
           hover_name = 'country',
           color = 'continent',
           size_max = 80,
           height = 800,
           title = 'Comparing current country vaccination progress with estimated final vaccination date',
           labels = dict(total_per_hundred = 'Total Vaccinations per Hundred (as of today)', final_date = 'Rough Estimate for Country to be Fully Vaccinated'))

pred_plot.show()
```

![Fig 30](/Figs/Fig_30.png)

And voila there you have it! The 7-8 months between the start of this summer and the middle of next winter will be tough, but it looks to be hopeful as well! And hey, with the rate that vaccinations are progressing and production increasing, maybe we will be past this sooner than we thought!
