import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def ourWorldInData():
    data = pd.read_csv('data/our-world-in-data.csv')
    return data.rename(columns={
        'Total confirmed cases of COVID-19 (cases)': 'Cases',
        'Entity':'Country'})

def kaggle():
    covidData = pd.read_csv('data/covid_19_data.csv')
    covidData = covidData.drop(columns=['Province/State'])
    covidData = covidData.rename(columns={'Country/Region':'Country', 'Confirmed':'Cases'})
    covidData['Open'] = covidData['Cases'] - (covidData['Deaths'] + covidData['Recovered'])
    covidData['Closed'] = covidData['Cases'] - covidData['Open']

    populationData = pd.read_csv('data/population.csv')
    populationData = populationData[populationData['Year'] == 2018]
    populationData = populationData.rename(columns={'Country Name':'Country', 'Value':'Population'})
    populationData = populationData.drop(columns=['Year', 'Country Code'])

    return pd.merge(covidData, populationData, how='inner', on='Country')

class Covid:
    def __init__(self, data, runningAvgWindow):
        self.data = data
        self.runningAvgWindow = runningAvgWindow

    def findCountry(self, term):
        countries = self.data['Country'].unique()
        return pd.Series(filter(lambda country: term in country, countries))

    def byCountry(self, country):
        return self.data[self.data['Country'] == country].reset_index(drop=True)

    def dailyNewCasesByCountry(self, country):
        total = self.byCountry(country)['Cases']
        startingDay0 = total[:-1].reset_index(drop=True)
        startingDay1 = total[1:].reset_index(drop=True)
        return (startingDay1 - startingDay0)

    # https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
    def runningAvg(self, x):
        result = pd.DataFrame(np.convolve(x, np.ones((self.runningAvgWindow,))/self.runningAvgWindow, mode='valid'))
        return result[0]

    def plotTotalCases(self, country, **kwargs):
        plt.xlabel('Days')
        countryData = self.byCountry(country)
        totalCases = countryData['Cases']
        if kwargs.get('scale_by', '') == "Population":
          totalCases = totalCases / countryData['Population'] * 1000000
        totalCases.plot(title='Total Cases')

    def plotRecoveries(self, country):
        plt.xlabel('Days')
        self.byCountry(country)['Recovered'].plot(title='Total Cases')

    def plotDeaths(self, country):
        plt.xlabel('Days')
        self.byCountry(country)['Deaths'].plot(title='Total Cases')

    def plotDailyNewCases(self, country):
        plt.xlabel('Days')
        self.dailyNewCasesByCountry(country).plot(kind='bar', title='Daily New Cases')

    def plotNewCasesAvg(self, country):
        avg = self.runningAvg(self.dailyNewCasesByCountry(country))
        avg.index += self.runningAvgWindow - 1
        avg.plot(style=['--r'])

    def plotLogDailyAvgByLogTotalCases(self, country):
        total = self.byCountry(country)['Cases']
        dailyAvg = self.runningAvg(self.dailyNewCasesByCountry(country))
        plt.title('Avg New Cases vs Total Cases')
        plt.xscale('log')
        plt.xlabel('Total Cases')
        plt.yscale('log')
        plt.ylabel('Avg New Cases')
        plt.plot(total[self.runningAvgWindow:], dailyAvg)

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