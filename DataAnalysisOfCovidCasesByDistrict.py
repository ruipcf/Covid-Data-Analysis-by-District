import os
import requests
import json
import numpy as np
import datetime
from base64 import b64encode
import matplotlib.pyplot as plt


def getCounties(district):
    # get list of counties from Portugal from GEO-PT-API
    geoPTAPI_url = "https://geoptapi.org/municipio?"
    r = requests.get(geoPTAPI_url)
    portugalCounties = r.json()

    # check all the counties from Portugal if they are from the district of 'district'
    countiesTMP = []
    for countie in portugalCounties:
        geoPTAPI_url = f'https://geoptapi.org/municipio?nome={countie}'
        r = requests.get(geoPTAPI_url)
        auxCountie = r.json()

        if "distrito" in auxCountie:
            if auxCountie['distrito'] == district.upper():
                countiesTMP.append(auxCountie['localidade'].upper())
    return countiesTMP


def updateEntries(counties):
    # date intervals to search
    startDate = "01-01-2021"
    endDate = "31-12-2021"
    #endDate = datetime.datetime.today().strftime('%d-%m-%Y')

    startDateAux = datetime.datetime.strptime(startDate, "%d-%m-%Y")
    endDateAux = datetime.datetime.strptime(endDate, "%d-%m-%Y")

    data = dict()
    noEntries = dict()

    # API authentication header
    userAndPass = b64encode(b"alunos.ipca.pt:*U,+z7:[(!-Xwku3").decode("ascii")
    headers = {'Authorization': 'Basic %s' % userAndPass}

    totalNoEntries = 0
    for county in counties:
        api_url = f'https://covid19-api.vost.pt/Requests/get_entry_county/{startDate}_until_{endDate}_{county}'
        r = requests.get(api_url, headers=headers)

        data[county] = []
        for x in r.json():
            currentDate = datetime.datetime.strptime(x['data'], "%d-%m-%Y")
            if startDateAux < currentDate < endDateAux and x not in data[county]:
                data[county].append(x)

        noEntries[county] = (len(data[county]))
        print("County: " + county + " has total of: " +
              str(noEntries[county]) + " entries.")
        totalNoEntries += noEntries[county]

    with open(os.path.join("SituaçãoCOVID2021.json"), "w") as fp:
        json.dump(data, fp)

    #print("Total number of entries: " + str(totalNoEntries))
    return data


def showResults(data):
    # for each county get the data (dates and number of COVID cases)
    for county in counties:
        listConty = data[county]

        dates = list()
        numberOfPositives = np.empty(len(listConty))

        for entry in listConty:
            dates.append(entry["data"])
            numberOfPositives[listConty.index(entry)] = entry["confirmados_1"]

        plt.plot(dates, numberOfPositives, 'g', label='Nº de confirmados')

        # calculus of the polinomial function
        xaxis = range(len(listConty))
        coefficients = np.polyfit(xaxis, numberOfPositives, 6)
        numberOfPositivesEstimative = np.poly1d(coefficients)

        # predict covid cases for x samples
        samplesToPredict = 6

        # calculus of the following dates for 'samplesToPredict' number of dates
        i = 0
        lastDate = datetime.datetime.strptime(dates[-2], "%d-%m-%Y")
        lastDate2 = datetime.datetime.strptime(dates[-1], "%d-%m-%Y")
        while i < samplesToPredict/2:
            newDate = lastDate + datetime.timedelta(days=30)
            newDate2 = lastDate2 + datetime.timedelta(days=30)
            dates.append(newDate.strftime("%d/%m/%Y"))
            dates.append(newDate2.strftime("%d/%m/%Y"))
            lastDate = newDate
            lastDate2 = newDate2
            i += 1

        xaxisPredicted = range(0, (len(listConty)+samplesToPredict))

        plt.plot(xaxisPredicted, numberOfPositivesEstimative(
            xaxisPredicted), 'r', label='Curva preditiva de evolução de casos')
        plt.xticks(xaxisPredicted, dates, rotation=90)
        plt.title("Nº de casos confirmados p/dia de COVID em " + county)
        plt.xlabel("Dias do ano")
        plt.ylabel("Nº de confirmados")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    # choose if user wants to update data choosing the district and get recent data from covid cases
    updateData = True
    updateCounties = False
    district = "Braga"

    if(updateCounties):
        counties = getCounties(district)
        print(counties)
    else:
        # list of default counties from Braga
        counties = ["AMARES", "BARCELOS", "BRAGA", "CABECEIRAS DE BASTO", "CELORICO DE BASTO", "ESPOSENDE", "FAFE",
                    "GUIMARÃES", "PÓVOA DE LANHOSO", "TERRAS DE BOURO", "VIEIRA DO MINHO", "VILA NOVA DE FAMALICÃO", "VILA VERDE",
                    "VIZELA"]

    if(not updateData):
        with open(os.path.join("SituaçãoCOVID2021.json"), "r") as data_file:
            data = json.load(data_file)
    else:
        data = updateEntries(counties)

    showResults(data)
