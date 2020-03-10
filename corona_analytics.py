from time import sleep
import os
import requests
from requests.exceptions import ConnectionError
from colorama import Fore, Style
import csv

#### SETTINGS #####

target_countries = ["Switzerland", "Mainland China"]

###################

c_red = Fore.RED
c_green = Fore.GREEN
c_yellow = Fore.YELLOW
c_magenta = Fore.MAGENTA
c_reset = Style.RESET_ALL


base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

confirmed_url = "time_series_19-covid-Confirmed.csv"
deaths_url = "time_series_19-covid-Deaths.csv"
recovered_url = "time_series_19-covid-Recovered.csv"

population_url = "https://raw.githubusercontent.com/SwissCorePy/corona_analytics/master/World_population.csv"

class Country:

    def __init__(self, country):
        self.country = country

    def set_properties(self, properties):
        self.properties = properties
        self.confirmed, self.deaths, self.recovered = properties
        self.perc_confirmed_deaths = 0 if (self.deaths == 0) else self.deaths/self.confirmed*100
        self.perc_confirmed_recovered = 0 if (self.recovered == 0) else self.recovered/self.confirmed*100

    def set_population(self, population):
        self.population = population
        self.perc_population_confirmed = 0 if (self.confirmed == 0) else self.confirmed/self.population*100
        self.perc_population_deaths = 0 if (self.deaths == 0) else self.deaths/self.population*100
        self.perc_population_recovered = 0 if (self.recovered == 0) else self.recovered/self.population*100

    

def main():

    confirmed_csv = None

    try:
        confirmed_csv = requests.get(base_url + confirmed_url, stream=True).content.decode("utf-8")
    except ConnectionError:
        print (red("Please check internet connection and try again later..."))
        exit(1)
    confirmed_data = read_all_to_dict (confirmed_csv)

    deaths_csv = requests.get(base_url + deaths_url, stream=True).content.decode("utf-8")
    deaths_data = read_all_to_dict (deaths_csv)

    recovered_csv = requests.get(base_url + recovered_url, stream=True).content.decode("utf-8")
    recovered_data = read_all_to_dict(recovered_csv)

    population_csv = requests.get(population_url, stream=True).content.decode("utf-8")
    population_data = read_population(population_csv)

    last_percs = {}
    for date in confirmed_data:
        print ("\nDate: " + magenta(date))
        for country in confirmed_data[date]:
            if (country in target_countries):
                print ("  " + magenta(country) + ":")
                if not (country in last_percs):
                    last_percs[country] = 0.0
                population = population_data[country]
                confirmed = confirmed_data[date][country]
                deaths = deaths_data[date][country]
                recovered = recovered_data[date][country]
                perc = (confirmed/population*100) # TODO PERCENT CALCULATION
                increased_perc = 0.0 if (last_percs[country] == 0.0) else (perc/last_percs[country]*100)-100
                print ("    Population: " + magenta(f"{population:,}"))
                print ("    Confirmed : " + red(f"{confirmed:,}") + " | " + red(str("%.4f" % perc) + "%"))
                print ("    Death     : " + red(f"{deaths:,}"))
                print ("    Recovered : " + green(f"{recovered:,}"))
                last_percs[country] = perc

def merge_data(dicts):
    confirmed, deaths, recovered = dicts
    final_dict = {}

    for date in confirmed:
        final_dict[date] = confirmed[date]

def read_population(csv_file):
    raw_data = csv.DictReader(csv_file.split("\r\n"))
    data = []

    final_dict = {}

    for row in raw_data:
        del row["World Development Indicators"]
        data.append(row)

    data.remove(data[0])

    for row in data[1:]:
        country, population = None, None
        for key in row:
            if (key == ""):
                continue
            if (key == None):
                populations = row[key]
                while ("" in populations):
                    populations.remove("")
                population = populations[-1]
            else:
                if (row[key] == "China"):
                    country = "Mainland China"
                else:
                    country = row[key]

        #print (country + ": " + population)
        final_dict[country] = 0 if (population == None or population == " " or population == "SP.POP.TOTL") else int(population)

    for country in final_dict:
        #print (magenta(country) + ": " + green(final_dict[country]))
        pass   

    return final_dict



def read_all_to_dict (csv_file):
    raw_data = csv.DictReader(csv_file.split("\r\n"))
    data = []
    for row in raw_data:
        del row["Lat"]
        del row["Long"]
        data.append(row)
    
    dates = []
    for key in data[0]:
        if ("/20" in key):
            dates.append(key)

    dates_dict = {}
    for date in dates:
        countries = {}
        for row in data:
            country = row["Country/Region"]
            value = int(row[date])

            if not (country in countries):
                countries[country] = value
            else:
                countries[country] += value

        dates_dict[date] = countries
    return dates_dict

def red (msg):
    return c_red + str(msg) + c_reset
def green (msg):
    return c_green + str(msg) + c_reset
def yellow (msg):
    return c_yellow + str(msg) + c_reset
def magenta (msg):
    return c_magenta + str(msg) + c_reset

if (__name__ == "__main__"):
    main()
