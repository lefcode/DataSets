import pandas as pd
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import xlrd
import errno


scriptPath = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))
scriptParentPath = os.path.abspath(os.path.join(scriptPath, os.pardir))
IMAGESDIR = scriptParentPath + "/images/"

try:
    os.makedirs(IMAGESDIR)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise


def mergeDatasets(cab_data_file, customer_id_file, transaction_id_file, city_file):

    cab_data =pd.read_csv(cab_data_file)

    string_dates = list()
    # format of date from excel date to string date of format   xxxx-xx-xx
    for cab in cab_data.values:
        datetime_date = xlrd.xldate_as_datetime(cab[1], 0)
        string_date = datetime_date.date().isoformat()
        string_dates.append(string_date)

    cab_data["Date of Travel"] =string_dates

    customer_id = pd.read_csv(customer_id_file)
    transaction_id = pd.read_csv(transaction_id_file)
    city = pd.read_csv(city_file)

    merged = pd.merge(cab_data, transaction_id)
    merged_dataset = pd.merge(merged, customer_id)
    return merged_dataset, city

def lel():
    '''
    city = city.apply(lambda x: x.str.replace(',','.'))
    cities = [c[0] for c in city.values]


     percentages = list()
     for c in city.values:
         #=merged_dataset.groupby(["Company",c[0]]).sum()["Price Charged"]

         pop = int(''.join(filter(str.isdigit, c[1])))
         users =  int(''.join(filter(str.isdigit, c[2])))

         percentages.append(users/pop)



    for city, percent in zip(cities, percentages):
        print("city: "+city+"\n percentage: "+str(percent))
    '''


    #plt.pie(percentages, labels = cities, startangle=90, shadow= True, autopct='%1.1f%%')
    #plt.title('Pie Plot')
    #plt.show()

def totalIncomeTable(merged_dataset):

    columns = ("Cab company","Total income","Total rides","Average price per ride")
    # total income computation
    earnings = merged_dataset.groupby(["Company"]).sum()["Price Charged"]
    expenditures = merged_dataset.groupby(["Company"]).sum()["Cost of Trip"]

    pink_cab_income = int(earnings[0] - expenditures[0])
    yellow_cab_income = int(earnings[1] - expenditures[1])

    # total rides computation
    pink_cab_rides= merged_dataset.groupby(["Company"]).count().values[0][0]
    yellow_cab_rides =  merged_dataset.groupby(["Company"]).count().values[1][0]

    # average income per ride computation
    pink_cab_average = pink_cab_income/pink_cab_rides
    yellow_cab_average = yellow_cab_income/yellow_cab_rides

    pink_cab_list = ["Pink Cab", pink_cab_income, pink_cab_rides, pink_cab_average]
    yellow_cab_list = ["Yellow Cab", yellow_cab_income, yellow_cab_rides, yellow_cab_average]

    fig, ax = plt.subplots()
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    plt.table(cellText=[pink_cab_list,yellow_cab_list],
              colLabels=columns, loc='center')

    fig.tight_layout()
    plt.show()
    plt.savefig(IMAGESDIR + "totalIncomeTable.png")

def cityIncomeHistogram(merged_dataset):
    city_cab = merged_dataset.groupby(["Company", "City"]).sum()["Price Charged"].index
    city_earnings = merged_dataset.groupby(["Company", "City"]).sum()["Price Charged"]
    city_expenditures = merged_dataset.groupby(["Company", "City"]).sum()["Cost of Trip"]
    cities_names = [c_cab[1] for c_cab in city_cab]
    cities=list()

    for city in cities_names:
        if city not in cities:
            cities.append(city)

    pink_cab_cities_incomes = []
    for earn, exp in zip(city_earnings["Pink Cab"], city_expenditures["Pink Cab"]):
        pink_cab_cities_incomes.append(earn-exp)

    yellow_cab_cities_incomes = []
    for earn, exp in zip(city_earnings["Yellow Cab"], city_expenditures["Yellow Cab"]):
        yellow_cab_cities_incomes.append(earn-exp)

    fig, ax = plt.subplots()
    bar_width = 0.35
    X = np.arange(len(cities))

    plt.bar(X, pink_cab_cities_incomes, bar_width, color='pink',label='Pink Cab')

    # The bar of second plot starts where the first bar ends
    plt.bar(X + bar_width, yellow_cab_cities_incomes, bar_width,
                 color='y',
                 label='Yellow Cab')

    plt.xlabel('City/State')
    plt.ylabel('Income')
    plt.title('Income per city')
    plt.xticks(X + (bar_width / 2), cities, rotation='vertical')
    plt.legend()
    plt.tight_layout()
    plt.show()
    plt.savefig(IMAGESDIR + "cityIncome.png")

def yearsIncomes(merged_dataset):
    years_earnings =merged_dataset.groupby(["Company", "Date of Travel"]).sum()["Price Charged"]
    years_expenditures = merged_dataset.groupby(["Company", "Date of Travel"]).sum()["Cost of Trip"]

    years_list = ["2016","2017","2018"]

    pink_cab_annual_income = list()
    for year in years_list:
        years_incomes = 0
        for date, earn, exp in zip(years_earnings["Pink Cab"].index ,years_earnings["Pink Cab"], years_expenditures["Pink Cab"]):
            if date.split("-")[0] == year:
                years_incomes += earn-exp

        pink_cab_annual_income.append(years_incomes)

    yellow_cab_annual_income = list()
    for year in years_list:
        years_incomes = 0
        for date, earn, exp in zip(years_earnings["Yellow Cab"].index ,years_earnings["Yellow Cab"], years_expenditures["Yellow Cab"]):
            if date.split("-")[0] == year:
                years_incomes += earn-exp

        yellow_cab_annual_income.append(years_incomes)


    plt.plot(years_list, pink_cab_annual_income, color='pink')
    plt.plot(years_list, yellow_cab_annual_income, color='yellow')
    plt.title("Income per year")
    plt.xlabel("Years 2016-2018")
    plt.ylabel("Income")
    plt.legend('Arrivals', loc='upper right')
    plt.show()
    plt.savefig(IMAGESDIR + "yearsIncome.png")

if __name__=="__main__":

    cab_data_file = scriptParentPath+"/Cab_Data.csv"
    customer_id_file = scriptParentPath+"/Customer_ID.csv"
    transaction_id_file = scriptParentPath+"/Transaction_ID.csv"
    city_file = scriptParentPath+"/City.csv"

    merged_dataset, city = mergeDatasets(cab_data_file, customer_id_file, transaction_id_file, city_file)

    #totalIncomeTable(merged_dataset)
    #cityIncomeHistogram(merged_dataset)
    #yearsIncomes(merged_dataset)

    #kms =merged_dataset["KM Travelled"].value_counts()
    #print(sorted(kms.index))
