## source = https://www.kaggle.com/gpreda/covid-world-vaccination-progress/code?datasetId=1093816&sortBy=voteCount
## this dataset gets updated each and every day with new vaccination data! check it out!

## standard data processing and analysis packages
import pandas as pd
import numpy as np


## packages for visualization, i will be using both plotly express here
import plotly.express as px
import plotly.graph_objects as go


## to predict completed vaccinations date
from scipy.optimize import curve_fit


import datetime
import warnings; warnings.simplefilter('ignore')


## ---------------------------------------------------------------------------------------------------------
## --------------------------- Initial Data Exploration ----------------------------------------------------
## ---------------------------------------------------------------------------------------------------------

## reading in the daily country vaccinations file
## note, with the link cited above, this file gets re-uploaded each day with new daily data
df = pd.read_csv('country_vaccinations.csv')
df.head()

df.describe()

## here i have brought in a mapping file that maps countries to their respective continents
## this will be helpful for tree maps, coloring, etc.
continents = pd.read_csv('country_continents.csv')
continents.head()

## here we are merging vaccination data with the continent data
full_df = df.drop(['source_name', 'source_website'], axis = 1) \
    .merge(right = continents, how = 'left', left_on = 'country', right_on = 'Country') \
    .drop('Country', axis = 1)

## some issues with numpy NaN values will cause issues with our initial charts
## note, we will be forward filling the progression variables soon
full_df = full_df.replace(np.nan, 0)

## making date a datetime variable instead of string will help with charting and time manipulation later
full_df['date'] = pd.to_datetime(full_df['date'])

full_df.dtypes



## ---------------------------------------------------------------------------------------------------------
## --------------------------- Exploring Types of Vaccines -------------------------------------------------
## ---------------------------------------------------------------------------------------------------------

## here this is a basic map of which countries are using which sets of vaccinations
## these are pretty region-dependent, based on which companies each country can get vaccines from
map_vaccines = px.choropleth(locations = full_df['country'], 
                             color = full_df['vaccines'],
                             locationmode = "country names",
                             title = "Countries using each set of vaccinations",
                             height = 800
                             )
map_vaccines.update_layout({'legend_orientation':'h', 'legend_title':'Set of vaccinations'})
map_vaccines.show()

## this will just give us a simple dictionary for each unique set of vaccinations that are mapped above
## we will now have the number of countries each set can be found in, along with the list of countries
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

## here we can find the df version of this dictionary, which will be useful to chart
vacc_set_df.head()

## using a treemap instead of a bar chart for aesthetics, you can see just how prevalent the more popular vaccinations are
## some region-specific ones can only be found in a handful of countries
fig = px.treemap(vacc_set_df,
                 path = ['vaccine_set'],
                 values = 'count',
                 title = 'Number of countries each unique set of vaccines can be found in',
                 height = 600, width = 800)
fig.data[0].textinfo = 'label+text+value'
fig.show()

## since there is overlap of vaccines in each country, let's make a map for each one of the vaccines
## this will get us a list of all of the individual vaccinations available in this dataset
unique_vaccines = []
for total_vacc in list(full_df.vaccines.unique()):
    split_vaccs = total_vacc.split(', ')
    for comp in split_vaccs:
        if comp not in unique_vaccines:
            unique_vaccines.append(comp)
            
print(unique_vaccines)

## using the above unique list, we can make a similar dictionary to our previous one
## here, instead of each key being a unique "set" of multiple vaccines, we have each individual vaccine
## this will be helpful to build individual-vaccine-specific maps and plots that can highlight their rollout
vacc_all_countries = {}
for vacc_comp in unique_vaccines:
    countries = full_df[full_df.vaccines.str.contains(vacc_comp)]['country'].unique().tolist()
    vacc_all_countries[vacc_comp] = {
        'number': len(countries),
        'list_countries': countries
    }

print(vacc_all_countries)

## an easy way to be able to filter down the big dataframe to only include countries that have a certain vaccine available
## is to make a new boolean or binary True/False column for each vaccine, where True represents if the country has access to that vaccine
def binary_vacc(country, vaccine):
    if country in vacc_all_countries[vaccine]['list_countries']:
        return True
    else:
        return False

for vacc in vacc_all_countries.keys():
    full_df[vacc] = full_df['country'].apply(binary_vacc, vaccine = vacc)
    
full_df.head()

## these are our progression variables
## these all represent the progress a country is making, but the df resets to 0 for every day these aren't updated / there is no more progress
## so, to rectify this, we can forward fill each of these. so in the event of a "0", we fill in the previous day's value
cols_to_ffill = ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated', 'total_vaccinations_per_hundred', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred']

## this function will allow us to see a full map of each country that each individual vaccine can be found in
## it will also show a line chart with a line for each country, showing their vaccination progress
## NOTE: this is NOT how the vaccination progress in that country for the specific vaccine, but progress in total for that country
## it's currently impossible to distribute a country's vaccinations across the vaccines they have access to, so we have to keep them bundled
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
        
## we will look at the bigger vaccines, omitting vaccines that can only be found in one or two countries
## pfizer progress
vaccine_map('Pfizer/BioNTech')

## moderna progress
vaccine_map('Moderna')

## astrazeneca progress
vaccine_map('Oxford/AstraZeneca')

## sputnik progress
vaccine_map('Sputnik V')

## sinopharm beijing progress
vaccine_map('Sinopharm/Beijing')

## sinovac progress
vaccine_map('Sinovac')

## here we are just building a df version of our previous dictionary
## we are also sorting by number of countries accessible, so we can make a bar chart shortly after
unique_vaccines_countries = pd.DataFrame(vacc_all_countries).transpose().reset_index().rename(columns = {'index': 'vaccine_company'}).sort_values(by = 'number', ascending = False)

unique_vaccines_countries.head()

## quick and easy bar chart showing how many countries each vaccination can be found in
fig = px.bar(unique_vaccines_countries,
             x = 'vaccine_company', y = 'number',
             labels = {'vaccine_company': 'Vaccination Company', 'number': 'Number of Countries Available'})
fig.show()

all_countries = full_df['country'].unique().tolist()
print(all_countries[0:10])
print(f'We have: {len(all_countries)} countries in the dataset')

## since each country started vaccinating citizens on different days, sometimes it is helpful to look at how their progress is going while comparing from their initial start date
## using this function, we will be able to add a column for which # day each country is on in vaccinating its citizens
def days_since_start(date, first_date):
    if (date <= first_date):
        return 0
    else:
        delta = date - first_date
        return delta.days
    
## in this cell we are doing a lot of adjustments to create new columns that detail some country-specific progress information
## that is why we need to slice the dataframe for each country and create columns based on their own progress then stitch it all back together again
adjusted_df = full_df[full_df['country'] == all_countries[0]]
a_first_vaccination = min(adjusted_df['date'])
a_total_vaccinations = max(adjusted_df['total_vaccinations'])
a_total_people_vaccinated = max(adjusted_df['people_vaccinated'])

cols_to_ffill = ['total_vaccinations', 'people_vaccinated', 'people_fully_vaccinated', 'total_vaccinations_per_hundred', 'people_vaccinated_per_hundred', 'people_fully_vaccinated_per_hundred']

for col in cols_to_ffill:
    adjusted_df[col] = adjusted_df[col].replace(to_replace = 0, method = 'ffill')

## here we are creating a new column for each country that shows how many days since they started vaccinating
adjusted_df['vaccination_day_number'] = adjusted_df['date'].apply(days_since_start, first_date = a_first_vaccination)

## this column will be for what percent of a country's total / final vaccinations (as of today) they have vaccinated
## that way, we can compare progress as a function of how many vaccinations each country was able to administer
adjusted_df['percent_total_vaccinations'] = adjusted_df['total_vaccinations'] / a_total_vaccinations

## this is the same function, but for people vaccinated. this will be useful in comparing the rate at which countries were able to efficiently administer vaccines to new people
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

## now we have our final adjusted dataframe, where we have new columns at the end that help compare progress for each country
adjusted_df.head()

## here we are comparing each the vaccination progress for each country that a vaccination can be found in
## again, NOTE this is NOT saying this is how many vaccinations have been rolled out for each vaccine type
## rather, saying that for each country a vaccination can be found in, here is the total progress of those countries
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
    
fig = go.Figure(lines)
fig.update_layout(
    title = 'Vaccination progress for the countries each vaccine can be found in',
    yaxis_title = "Count",
    hovermode = 'x',
    legend_orientation = 'h',
    height = 800
)

fig.show()

## also unideal, but since we can't attribute a country's vaccinations to individual types within the country
## we can just plot the same analysis as above, but for unique vaccination sets
## so now we will have a line for each country that has the total set of vaccinations present
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
    
fig = go.Figure(lines)
fig.update_layout(
    title = 'Vaccination progress per set of vaccine present in each country',
    yaxis_title = "Number of vaccines administered",
    hovermode = 'x',
    legend_orientation = 'h',
    height = 1000
)

fig.show()



## ---------------------------------------------------------------------------------------------------------
## --------------------------- Country Progression ---------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------

## here we are loading in another auxiliary dataframe, giving population for each country
## this will be helpful in some visualizations as metadata attached to it
pop_dict = pd.read_csv('population_by_country_2020.csv')[['Country (or dependency)', 'Population (2020)']] \
    .rename(columns = {'Country (or dependency)': 'Country', 'Population (2020)': 'Population'})
pop_dict.head()

continents.head()

## here we are building one big "current progress" dataframe, giving one row per country
## detailing how they fare as of today
## whereas the original dataframe is a tall file listing individual days of progress,
## we will use this to compare how countries have done up until this point in time
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

total_vacc_df.head()

## this is another country function that you can play around with
## here you can pass the top n number of countries you want to see, the time period you want to compare their progress, and whether or not to adjust vaccination progress for population
## feel free to try out a couple, but i have shown some examples below
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
    
## here we see the top 50 countries, comparing by raw date, and showing raw total vaccinations
top_countries_chart(n = 50, time_period = 'date', pop_adjusted = False)

## here we see the top 50 countries, comparing by day number since starting vaccinating, and showing raw total vaccinations
top_countries_chart(n = 50, time_period = 'vaccination_day_number', pop_adjusted = False)

## here we see the top 50 countries, comparing by raw date, and showing vaccinations per hundred people
top_countries_chart(n = 30, time_period = 'date', pop_adjusted = True)

## here we see the top 50 countries, comparing by day number since starting vaccinating, and showing vaccinations per hundred people
top_countries_chart(n = 30, time_period = 'vaccination_day_number', pop_adjusted = True)

## here we can plot the total progress of the top 25 countries as of today
## it shows countries with the top 25 number of total vaccinations, compared to how they are doing adjusted for their population (per hundred)
## feel free to change the n down below to see more or fewer countries
n = 25
fig = px.scatter(total_vacc_df.iloc[0:n, ],
           x = 'total_vaccinations',
           y = 'total_per_hundred',
           size = 'population',
           hover_name = 'country',
           color = 'continent',
           size_max = 80,
           height = 800,
           title = 'Comparing country progress for total vaccinations and total vaccinations per hundred people',
           labels = dict(total_per_hundred = "Total Vaccinations per Hundred People", total_vaccinations = "Total Vaccinations (raw)"))

fig.show()



## ---------------------------------------------------------------------------------------------------------
## --------------------------- Average Progression and Predicting Future Success ---------------------------
## ---------------------------------------------------------------------------------------------------------

total_vacc_df.head()
total_vacc_df.dtypes

## just some cleaning for some division later
total_vacc_df['days_since_starting'] = total_vacc_df['days_since_starting'].astype('float64')
total_vacc_df['total_per_hundred'] = total_vacc_df['total_per_hundred'].astype('float64')
total_vacc_df = total_vacc_df[total_vacc_df['days_since_starting'] > 0]

## this, while not the most informative variable, will show us the straightline average percent of the population each country is vaccinating *per day* since they started vaccinating
total_vacc_df['average_daily_percent_vaccinated'] = round(total_vacc_df['total_per_hundred'] / total_vacc_df['days_since_starting'], 4)

## adding in a plain text column just as a parent for our treemap
total_vacc_df['world'] = 'world'

total_vacc_df.head()

total_vacc_df = total_vacc_df.replace(np.inf, np.nan)

## this is another plotting function that you can play with
## you can pass one of two vals, if you want to see current total vaccinations per hundred or average vaccinations per hundred *per day
## you can also put in a minimum population for a country to be included
## this is because, since each value you can pass is adjusted for population, countries with super low populations find their way to the top of the list
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
    
## here we can see the top countries per continent in terms of total vaccinations per hundred
## only showing countries with 10M + population
avg_vaccination_progress(min_pop = 10000000, vals = 'total')

## now we can see the same chart, but showing average population percent vaccinated per day
## and showing countries with above 1M population
avg_vaccination_progress(min_pop = 1000000, vals = 'average')

## here we have a bar chart for the countries within each continent
## showing the most efficient countries at vaccinating their population
## the color is showing total vaccinations per hundred people, darker color meaning more vaccinations administered
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
    
## now let's do something fun - predict when each country will finish vaccinating their entire population!
## first we need to find each country that has enough data to actually fit a curve
countries_to_predict = []
for country in adjusted_df['country'].unique():
    check_df = adjusted_df[adjusted_df['country'] == country]
    if max(check_df['people_vaccinated_per_hundred']) > 0:
         countries_to_predict.append(country)
len(countries_to_predict)

## slow down - this is NOT going to be a robust machine learning project aimed at making precise predictions
## this is just a fun quick and dirty scipy curve_fit application to show when each country will finish vaccinating its citizens, if it keeps on its current progress
## note - this simplistic, prone-to-overfitting, parabola-based curve_fit has flaws
## the biggest of which is that, for almost every country where vaccinations (adjusted for population) has slowed down in recent times, this will say it keeps slowing down until inevitably there's no more progress!
## which obviously isn't true, but that does mean it will think those countries never successfully finish vaccinating their citizens
## for now, as this is a simple example exercise for a final visualization, we will omit those!
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
            
## and here we have it! this dictionary tells us, for each country that will finish vaccinating its citizens, how many days after starting it will take them
## with this data, using our country-adjusted dataframe, we can add this number to each country's first vaccination date to find their final vaccination date!
country_results

## the above few cells are doing just that, using this dictionary and our summary datafile to find our "predicted" end date for each country to be fully vaccinated!
country_results_df = pd.DataFrame(country_results, index = ['days_until_fully_vaccinated']).transpose()\
    .reset_index().rename(columns = {'index': 'country'})

country_results_df = country_results_df.merge(total_vacc_df, on = 'country')
country_results_df.head()

country_results_df['final_date'] = country_results_df['day_started'] + pd.to_timedelta(country_results_df['days_until_fully_vaccinated'], unit = 'd')

country_results_df.sort_values(by = 'days_until_fully_vaccinated').head(10)
country_results_df.sort_values(by = 'final_date')

## now that we have the final date for each country, let's plot!
## here are the "predictions" for which day each country will finish vaccinating, along with their current progress as of today
## as you can see, which makes fairly intuitive sense, there is a negative correlation between the two
## saying that - the more progress already done for a country, the earlier they will be done vaccinating their citizens - makes sense right?
fig = px.scatter(country_results_df,
           x = 'final_date',
           y = 'total_per_hundred',
           size = 'population',
           hover_name = 'country',
           color = 'continent',
           size_max = 80,
           height = 800,
           title = 'Comparing current country vaccination progress with estimated final vaccination date',
           labels = dict(total_per_hundred = 'Total Vaccinations per Hundred (as of today)', final_date = 'Rough Estimate for Country to be Fully Vaccinated'))

fig.show()