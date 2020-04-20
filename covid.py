import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

RUNNING_AVG_WINDOW = 7

# https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
def runningAvg(data):
    result = pd.DataFrame(np.convolve(data, np.ones((RUNNING_AVG_WINDOW,))/RUNNING_AVG_WINDOW, mode='valid'))
    return result[0]

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

    def dailyNewCases(self, country):
        return self.byCountry(country)['DailyNewCases']

    def plotTotalCases(self, country, **kwargs):
        plt.xlabel('Days')
        countryData = self.byCountry(country)
        totalCases = countryData['Cases']
        if 'scale_by' in kwargs:
          totalCases = totalCases / countryData[kwargs['scale_by']]
        totalCases *= kwargs.get('factor', 1)
        totalCases.plot(title='Total Cases')

    def plotRecoveries(self, country):
        plt.xlabel('Days')
        self.byCountry(country)['Recovered'].plot(title='Total Cases')

    def plotDeaths(self, country):
        plt.xlabel('Days')
        self.byCountry(country)['Deaths'].plot(title='Total Cases')

    def plotDailyNewCases(self, country):
        plt.xlabel('Days')
        self.dailyNewCases(country).plot(kind='bar', title='Daily New Cases')

    def plotNewCasesAvg(self, country):
        avg = runningAvg(self.dailyNewCases(country))
        avg.index += RUNNING_AVG_WINDOW - 1
        avg.plot(style=['--r'])

    def plotLogDailyAvgByLogTotalCases(self, country):
        total = self.byCountry(country)['Cases']
        dailyAvg = runningAvg(self.dailyNewCases(country))
        plt.title('Avg New Cases vs Total Cases')
        plt.xscale('log')
        plt.xlabel('Total Cases')
        plt.yscale('log')
        plt.ylabel('Avg New Cases')
        plt.plot(total[RUNNING_AVG_WINDOW - 1:], dailyAvg)

    def plotOutcomeOfCases(self, country):
        countryData = self.byCountry(country)
        recoveryRate = (countryData['Recovered'] / countryData['Closed'] * 100)
        deathRate = (countryData['Deaths'] / countryData['Closed'] * 100)
        plt.title('Outcome of Cases')
        plt.xlabel('Days')
        plt.ylabel('Percent')
        recoveryRate.plot()
        deathRate.plot()
        plt.legend(['recovery rate', 'death rate'])

    def plotCountryStatus(self, country):
        fig = plt.figure(figsize=(20,10))
        fig.suptitle(country, fontsize=25)

        plt.subplot(221)
        self.plotTotalCases(country)
        self.plotDeaths(country)
        self.plotRecoveries(country)
        plt.legend(['confirmed', 'deaths', 'recoveries'])

        plt.subplot(222)
        self.plotDailyNewCases(country)
        self.plotNewCasesAvg(country)
        plt.legend(['avg daily cases', 'daily cases'])

        plt.subplot(223)
        self.plotLogDailyAvgByLogTotalCases(country)

        plt.subplot(224)
        self.plotOutcomeOfCases(country)

        plt.show()

    def plotCountriesStatus(self, countries):
        for country in countries:
            self.plotCountryStatus(country)

    def plotAllInOne(self, plotFunc, countries, **kwargs):
        for country in countries:
            plotFunc(country, **kwargs)
        plt.legend(countries)
        plt.show()
