from time import sleep
import os
import requests
from requests.exceptions import ConnectionError
from colorama import Fore, Style
from colorama import init as colorama_init
import csv

#### SETTINGS #####
all_countries = False
target_countries = ["Switzerland", "Poland", "Mainland China", "Italy"]

# "M.d.yy"
target_date = ""

work_offline = True

###################

c_red = Fore.RED
c_green = Fore.GREEN
c_yellow = Fore.YELLOW
c_magenta = Fore.MAGENTA
c_reset = Style.RESET_ALL
colorama_init(convert=True)

file_path = "/".join(__file__.split("/")[:-1]) + "/" + "csv_files/"

if not (os.path.exists(file_path)):
    os.mkdir(file_path)



base_url = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"

confirmed_url = "time_series_19-covid-Confirmed.csv"
deaths_url = "time_series_19-covid-Deaths.csv"
recovered_url = "time_series_19-covid-Recovered.csv"
population_url = "https://raw.githubusercontent.com/SwissCorePy/corona_analytics/master/csv_files/World_population.csv"

class Country:

    def __init__(self, country, population):
        self.country = country
        self.population = population
        self.history = {}

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

    confirmed_csv, deaths_csv, recovered_csv = None, None, None

    try:
        if not (work_offline):
            print ("fetch files...")
            confirmed_csv = requests.get(base_url + confirmed_url, stream=True).content.decode("utf-8")
            deaths_csv = requests.get(base_url + deaths_url, stream=True).content.decode("utf-8")
            recovered_csv = requests.get(base_url + recovered_url, stream=True).content.decode("utf-8")

            if not (os.path.exists(file_path + "World_Population.csv")):
                population_csv = requests.get(population_url, stream=True).content.decode("utf-8")
            population_csv = str(open(file_path + "World_Population.csv", "r", newline="\r\n").read())

            with open (file_path + "Confirmed.csv", "w", encoding="utf-8") as f:
                f.write(confirmed_csv)
            with open (file_path + "Deaths.csv", "w", encoding="utf-8") as f:
                f.write(deaths_csv)
            with open (file_path + "Recovered.csv", "w", encoding="utf-8") as f:
                f.write(recovered_csv)
        else:
            confirmed_csv = str(open(file_path + "Confirmed.csv", "r", newline="\r\n").read())
            deaths_csv = str(open(file_path + "Deaths.csv", "r", newline="\r\n").read())
            recovered_csv = str(open(file_path + "Recovered.csv", "r", newline="\r\n").read())
            population_csv = str(open(file_path + "World_Population.csv", "r", newline="\r\n").read())

    except ConnectionError:
        print (red("Please check your internet connection..."))
        exit(1)

    confirmed_data = read_all_to_dict (confirmed_csv)
    deaths_data = read_all_to_dict (deaths_csv)
    recovered_data = read_all_to_dict(recovered_csv)
    population_data = read_population(population_csv)
    
    last_percs = {}
    for date in confirmed_data:
        print ("\nDate: " + magenta(date))
        for country in confirmed_data[date]:
            if (country in target_countries or all_countries==True):
                print ("  " + magenta(country) + ":")
                if not (country in last_percs):
                    last_percs[country] = 0.0
                    
                population = population_data[country]
                confirmed = confirmed_data[date][country]
                deaths = deaths_data[date][country]
                recovered = recovered_data[date][country]
                perc = (confirmed/population*100)
                print ("    Population: " + magenta(f"{population:,}"))
                print ("    Confirmed : " + red(f"{confirmed:,}") + " | " + red(str("%.4f" % perc) + "%"))
                print ("    Death     : " + red(f"{deaths:,}"))
                print ("    Recovered : " + green(f"{recovered:,}"))
                last_percs[country] = perc

def percent (val, total):
    return 0.0 if (val == 0.0) else total/val*100

def add(dates, name="World"):
    output_data = { name : [] }
    for date in dates:
        counter = 0
        for country in dates[date]:
            if (country in target_countries or all_countries==True):
                counter += dates[date][country]
        output_data[name] = counter

    print (output_data)
                


def str_percent (val, total, decimals):
    val, total, decimals = float(val), float(total), int(decimals)
    if (val == 0.0):
        return "0." + ("0" * decimals) + "%"
    return str(f"%.{decimals}f" % (val/total*100) + "%")

def bake_dataset(dicts, populations):
    confirmed, deaths, recovered = dicts
    output_data = {}

    for date in confirmed:
        output_data[date] = confirmed[date]

def read_population(csv_file):
    raw_data = csv.DictReader(csv_file.split("\r\n"))
    data = []

    output_data = {}

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
        output_data[country] = 0 if (population == None or population == " " or population == "SP.POP.TOTL") else int(population)

    for country in output_data:
        #print (magenta(country) + ": " + green(output_data[country]))
        pass   

    return output_data



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