import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RUNNING_AVG_WINDOW = 7

# https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
def runningAvg(data):
    result = pd.DataFrame(np.convolve(data, np.ones((RUNNING_AVG_WINDOW,))/RUNNING_AVG_WINDOW, mode='valid'))
    return result[0]

def plot(data, **kwargs):
    plt.xlabel(kwargs.pop('xlabel', ''))
    plt.ylabel(kwargs.pop('ylabel', ''))
    data.plot(**kwargs)

class Covid:
    def __init__(self):
        covidData = pd.read_csv('data/covid_19_data.csv')

        covidData = covidData.drop(columns=['Province/State'])
        covidData = covidData.rename(columns={'Country/Region':'Country', 'Confirmed':'Cases'})
        covidData['Open'] = covidData['Cases'] - (covidData['Deaths'] + covidData['Recovered'])
        covidData['Closed'] = covidData['Cases'] - covidData['Open']

        populationData = pd.read_csv('data/population.csv')
        populationData = populationData[populationData['Year'] == 2018]
        populationData = populationData.rename(columns={'Country Name':'Country', 'Value':'Population'})
        populationData = populationData.drop(columns=['Year', 'Country Code'])

        self.data = pd.merge(covidData, populationData, how='inner', on='Country')

        casesColIdx = self.data.columns.get_loc('Cases')
        self.data.insert(casesColIdx + 1, 'DailyNewCases', np.NaN)
        for country in self.allCountries():
            dailyNewCases = self.__dailyNewCases(country)
            filterByCountry = self.data['Country'] == country
            dailyNewCases.index = self.data.loc[filterByCountry].index
            self.data.loc[filterByCountry, 'DailyNewCases'] = dailyNewCases

    def __dailyNewCases(self, country):
        total = self.byCountry(country)['Cases']
        theDayBefore = pd.concat([pd.Series([0]), total])[:-1].reset_index(drop=True)
        return (total - theDayBefore)

    def getData(self):
        return self.data

    def allCountries(self):
        return self.data['Country'].unique()

    def findCountry(self, term):
        return pd.Series(filter(lambda country: term in country, self.allCountries()))

    def byCountry(self, country):
        return self.data[self.data['Country'] == country].reset_index(drop=True)

    def scale(self, country, column, **kwargs):
        countryData = self.byCountry(country)
        result = countryData[column]
        if 'scale_by' in kwargs:
          result = result / countryData[kwargs['scale_by']]
        result *= kwargs.get('factor', 1)
        return result

    def totalCases(self, country, **kwargs):
        return self.scale(country, 'Cases', **kwargs)

    def dailyNewCases(self, country, **kwargs):
        return self.scale(country, 'DailyNewCases', **kwargs)

    def avgNewCases(self, country, **kwargs):
        avg = runningAvg(self.dailyNewCases(country, **kwargs))
        avg.index += RUNNING_AVG_WINDOW - 1
        return avg

    def recoveries(self, country, **kwargs):
        return self.scale(country, 'Recovered', **kwargs)

    def recoveryRate(self, country):
        return self.scale(country, 'Recovered', scale_by='Closed', factor=100)

    def deaths(self, country, **kwargs):
        return self.scale(country, 'Deaths', **kwargs)

    def deathRate(self, country):
        return self.scale(country, 'Deaths', scale_by='Closed', factor=100)

    def growthOfCases(self, country, **kwargs):
        avg = self.avgNewCases(country, **kwargs)
        total = self.totalCases(country, **kwargs)
        avg.index = total[RUNNING_AVG_WINDOW - 1:]
        return avg

    def plotCountryStatus(self, country):
        fig = plt.figure(figsize=(20,10))
        fig.suptitle(country, fontsize=25)

        plt.subplot(221)
        plot(self.totalCases(country), title='Total Cases', legend=True)
        plot(self.deaths(country), legend=True)
        plot(self.recoveries(country), legend=True)
        plt.xlabel('Days')

        plt.subplot(222)
        plot(self.dailyNewCases(country), title='Daily New Cases', kind='bar', xlabel='Days', label='Daily New Cases')
        plot(self.avgNewCases(country), label='%dd running avg' % RUNNING_AVG_WINDOW, style='--r')
        plt.legend()

        plt.subplot(223)
        plot(self.growthOfCases(country),
                title='Logarithmic Growth of Cases',
                loglog=True, 
                xlabel='Total Cases',
                ylabel='Avg New Cases')

        plt.subplot(224)
        plot(self.recoveryRate(country), title='Outcome of Cases', xlabel='Days', ylabel='Percent', legend=True, label='Recovery Rate')
        plot(self.deathRate(country), legend=True, label='Death Rate')

        plt.show()

    def plotCountriesStatus(self, countries):
        for country in countries:
            self.plotCountryStatus(country)

    def plotAllInOne(self, dataFunc, countries, **kwargs):
        plot_kwargs = {key: value for key, value in kwargs.items() if key not in ['scale_by', 'factor']}
        for country in countries:
            plot(dataFunc(country, **kwargs), **plot_kwargs)
        plt.legend(countries)
        plt.show()
