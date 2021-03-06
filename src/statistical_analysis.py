import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import xlrd
import errno
from collections import Counter

scriptPath = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))
scriptParentPath = os.path.abspath(os.path.join(scriptPath, os.pardir))
IMAGESDIR = scriptParentPath + "/images/"

try:
    os.makedirs(IMAGESDIR)
except OSError as e:
    if e.errno != errno.EEXIST:
        raise

def timeAnalysis(merged_dataset):
    yearsIncomes(merged_dataset)
    monthsIncomes(merged_dataset)

def customerProfileAnalysis(merged_dataset):
    ageAnalysis(merged_dataset)
    incomeAnalysis(merged_dataset)
    genderAnalysis(merged_dataset)


def plotBar(labels, values1, values2, xtitle, ytitle, plot_title, plot_name, rotate="vertical"):

    fig, ax = plt.subplots()
    bar_width = 0.35
    X = np.arange(len(labels))
    plt.bar(X, values1, bar_width, color='pink', label='Pink Cab')

    # The bar of second plot starts where the first bar ends
    plt.bar(X + bar_width, values2, bar_width,
            color='y',
            label='Yellow Cab')

    plt.xlabel(xtitle)
    plt.ylabel(ytitle)
    plt.title(plot_title)
    plt.xticks(X + (bar_width / 2), labels, rotation=rotate)
    plt.legend()
    plt.tight_layout()
    plt.savefig(IMAGESDIR + plot_name + ".png")
    #plt.show()
    

def mergeDatasets(cab_data_file, customer_id_file, transaction_id_file, city_file):

    cab_data =pd.read_csv(cab_data_file)

    string_dates = list()
    # format of date from excel date to string date of format xxxx-xx-xx
    for cab in cab_data.values:
        datetime_date = xlrd.xldate_as_datetime(cab[1], 0)
        string_date = datetime_date.date().isoformat()
        string_dates.append(string_date)

    cab_data["Date of Travel"] = string_dates

    customer_id = pd.read_csv(customer_id_file)
    transaction_id = pd.read_csv(transaction_id_file)
    city = pd.read_csv(city_file)

    merged = pd.merge(cab_data, transaction_id)
    merged_dataset = pd.merge(merged, customer_id)

    if merged_dataset.shape == merged_dataset.drop_duplicates().shape:
        print("No duplicates were found in dataset!")
    else:
        merged_dataset = merged_dataset.drop_duplicates()
        print(str(len(merged_dataset) - len(merged_dataset.drop_duplicates())) +" duplicates found and removed!")

    if str(merged_dataset.isnull().sum().sum())=="0":
        print("No Nan values in entire dataset!")
    else:
        print("Nan values found in the dataset. they must be handled!")

    return merged_dataset, city


def outliersHandling(merged_dataset, feature):
    """ We detect and filter the outliers of Cost of Trip and Price Charged columns"""
    new_dataset = merged_dataset
    new_dataset.sort_values(feature)  # Sorting is must

    # making boolean series for the feature
    filter = new_dataset[feature] > 4

    # filtering data on basis filter
    new_dataset.where(filter, inplace=True)

    return new_dataset


def totalIncomeTable(merged_dataset):
    columns = ("Cab company", "Total income", "Total rides", "Average price per ride")
    # total income computation
    earnings = merged_dataset.groupby(["Company"]).sum()["Price Charged"]
    expenditures = merged_dataset.groupby(["Company"]).sum()["Cost of Trip"]

    pink_cab_income = int(earnings[0] - expenditures[0])
    yellow_cab_income = int(earnings[1] - expenditures[1])

    # total rides computation
    pink_cab_rides = merged_dataset.groupby(["Company"]).count().values[0][0]
    yellow_cab_rides = merged_dataset.groupby(["Company"]).count().values[1][0]

    # average income per ride computation
    pink_cab_average = "%.2f" % (pink_cab_income / pink_cab_rides)
    yellow_cab_average = "%.2f" % (yellow_cab_income / yellow_cab_rides)

    pink_cab_list = ["Pink Cab", pink_cab_income, pink_cab_rides, pink_cab_average]
    yellow_cab_list = ["Yellow Cab", yellow_cab_income, yellow_cab_rides, yellow_cab_average]

    fig, ax = plt.subplots(figsize=((10, 8)))
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    table = plt.table(cellText=[pink_cab_list, yellow_cab_list],
                      colLabels=columns, loc='center')
    table.set_fontsize(24)
    fig.tight_layout()
    plt.savefig(IMAGESDIR + "totalIncomeTable.png")
    #plt.show()

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

    plotBar(cities, pink_cab_cities_incomes, yellow_cab_cities_incomes, 'City/State', 'Income', 'Income per city',
            "cityIncome")


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

        pink_cab_annual_income.append(years_incomes/1e7) #str(years_incomes/1e7)+"M"

    yellow_cab_annual_income = list()
    for year in years_list:
        years_incomes = 0
        for date, earn, exp in zip(years_earnings["Yellow Cab"].index ,years_earnings["Yellow Cab"], years_expenditures["Yellow Cab"]):
            if date.split("-")[0] == year:
                years_incomes += earn-exp

        yellow_cab_annual_income.append(years_incomes/1e7)

    for i in range(3):
        plt.annotate("{:.3f}M".format(pink_cab_annual_income[i]), (i,pink_cab_annual_income[i]), color="red")

    for i in range(3):
        plt.annotate("{:.3f}M".format(yellow_cab_annual_income[i]), (i,yellow_cab_annual_income[i]), color="orange")

    plt.plot(years_list, pink_cab_annual_income, color='pink', label="Pink Cab")
    plt.plot(years_list, yellow_cab_annual_income, color='yellow', label="Yellow Cab")
    plt.title("Company Income per year")
    plt.xlabel("Years 2016-2018")
    plt.ylabel("Company Income")
    plt.legend(loc='upper right')
    plt.savefig(IMAGESDIR + "yearsIncome.png")
    #plt.show()

def monthsIncomes(merged_dataset):

    years_earnings = merged_dataset.groupby(["Company", "Date of Travel"]).sum()["Price Charged"]
    years_expenditures = merged_dataset.groupby(["Company", "Date of Travel"]).sum()["Cost of Trip"]

    years_list = ["2016","2017","2018"]
    months_list = [i for i in range(1,13)]

    labels_list = [y+"-"+str(m) for y in years_list for m in months_list]

    pink_cab_annual_monthly_income = list()
    for year in years_list:
        for month in months_list:
            month_income = 0
            for date, earn, exp in zip(years_earnings["Pink Cab"].index ,years_earnings["Pink Cab"], years_expenditures["Pink Cab"]):
                if int(date.split("-")[1]) == month and date.split("-")[0] == year:
                    month_income += earn-exp
            pink_cab_annual_monthly_income.append(month_income)

    yellow_cab_annual_monthly_income = list()
    for year in years_list:
        for month in months_list:
            month_income = 0
            for date, earn, exp in zip(years_earnings["Yellow Cab"].index ,years_earnings["Yellow Cab"], years_expenditures["Yellow Cab"]):
                if int(date.split("-")[1]) == month and date.split("-")[0] == year:
                    month_income += earn-exp
            yellow_cab_annual_monthly_income.append(month_income)

    plt.plot(labels_list, pink_cab_annual_monthly_income, color='pink', label="Pink Cab")
    plt.plot(labels_list, yellow_cab_annual_monthly_income, color='yellow', label="Yellow Cab")
    plt.title("Company Income per year")
    plt.xlabel("Years 2016-2018")
    plt.ylabel("Company Income")
    plt.legend(loc='upper right')
    plt.xticks(rotation='vertical')
    plt.savefig(IMAGESDIR + "monthsIncome.png")
    #plt.show()

def ageAnalysis(merged_dataset):

    ages = merged_dataset.groupby(["Company", "Age"]).sum()["Price Charged"].index
    ages_earnings = merged_dataset.groupby(["Company", "Age"]).sum()["Price Charged"]
    ages_expenditures = merged_dataset.groupby(["Company", "Age"]).sum()["Cost of Trip"]

    pink_cab_ages_incomes = {}
    for earn, exp, age in zip(ages_earnings["Pink Cab"], ages_expenditures["Pink Cab"], ages):
        pink_cab_ages_incomes[age[1]] = earn-exp
        #pink_cab_ages_incomes.append(earn-exp)

    yellow_cab_ages_incomes = {}
    for earn, exp, age in zip(ages_earnings["Yellow Cab"], ages_expenditures["Yellow Cab"], ages):
        yellow_cab_ages_incomes[age[1]] = earn-exp
        #yellow_cab_ages_incomes.append(earn-exp)

    print("We divide customers' ages into 5 classes: 18-23, 24-30, 31-40, 41-50, 51-65")
    ages_classes = ["18-23", "24-30", "31-40", "41-50", "51-65"]

    pink_cab_ages_classes_incomes = {}
    yellow_cab_ages_classes_incomes={}

    for age_class in ages_classes:
        pink_cab_ages_classes_incomes[age_class] = 0
        yellow_cab_ages_classes_incomes[age_class] = 0

    for key, val in pink_cab_ages_incomes.items():
        if key<=23: pink_cab_ages_classes_incomes["18-23"] += val
        elif key<=30: pink_cab_ages_classes_incomes["24-30"] += val
        elif key<=40: pink_cab_ages_classes_incomes["31-40"] += val
        elif key<=50: pink_cab_ages_classes_incomes["41-50"] += val
        elif key<=65: pink_cab_ages_classes_incomes["51-65"] += val

    for key, val in yellow_cab_ages_incomes.items():
        if key <= 23: yellow_cab_ages_classes_incomes["18-23"] += val
        elif key <= 30: yellow_cab_ages_classes_incomes["24-30"] += val
        elif key <= 40: yellow_cab_ages_classes_incomes["31-40"] += val
        elif key <= 50: yellow_cab_ages_classes_incomes["41-50"] += val
        elif key <= 65: yellow_cab_ages_classes_incomes["51-65"] += val

    # add both dictionaries values
    overall_income = dict(Counter(pink_cab_ages_classes_incomes) + Counter(yellow_cab_ages_classes_incomes))
    plt.pie(overall_income.values(), labels=ages_classes, startangle=90, shadow=True, autopct='%1.1f%%')
    plt.title('Cab Market pie plot')
    plt.savefig("piePlot.png")

    plotBar(ages_classes, pink_cab_ages_classes_incomes.values(), yellow_cab_ages_classes_incomes.values(),
            "Age class", "Company Income", "Company Income per age class", "ageAnalysis", rotate="horizontal")

def incomeAnalysis(merged_dataset):

    company_user_earnings_indices = merged_dataset.groupby(["Company", "Income (USD/Month)"]).sum()["Price Charged"].index
    company_user_earnings = merged_dataset.groupby(["Company", "Income (USD/Month)"]).sum()["Price Charged"]
    company_user_expenditures = merged_dataset.groupby(["Company", "Income (USD/Month)"]).sum()["Cost of Trip"]

    pink_cab_incomes = {}
    for earn, exp, c_us in zip(company_user_earnings["Pink Cab"], company_user_expenditures["Pink Cab"], company_user_earnings_indices):
        pink_cab_incomes[c_us[1]] = earn-exp

    yellow_cab_incomes = {}
    for earn, exp, c_us in zip(company_user_earnings["Yellow Cab"], company_user_expenditures["Yellow Cab"], company_user_earnings_indices):
        yellow_cab_incomes[c_us[1]] = earn-exp

    pink_cab_user_classes_incomes = {}
    yellow_cab_user_classes_incomes={}

    income_levels = ["2000-8250", "8251-16500", "16501-24750", "24751-35000"] # we divided the range of incomes to 4 levels
    for level in income_levels:
        pink_cab_user_classes_incomes[level] = 0
        yellow_cab_user_classes_incomes[level] = 0

    for key, val in pink_cab_incomes.items():
        if int(key)<=8250: pink_cab_user_classes_incomes["2000-8250"] += val
        elif int(key)<=16500: pink_cab_user_classes_incomes["8251-16500"] += val
        elif int(key)<=24750: pink_cab_user_classes_incomes["16501-24750"] += val
        elif int(key)<=35000: pink_cab_user_classes_incomes["24751-35000"] += val

    for key, val in yellow_cab_incomes.items():
        if int(key)<=8250: yellow_cab_user_classes_incomes["2000-8250"] += val
        elif int(key) <= 16500: yellow_cab_user_classes_incomes["8251-16500"] += val
        elif int(key)<=24750: yellow_cab_user_classes_incomes["16501-24750"] += val
        elif int(key) <= 35000: yellow_cab_user_classes_incomes["24751-35000"] += val

    plotBar(income_levels, pink_cab_user_classes_incomes.values(), yellow_cab_user_classes_incomes.values(),
            "User Income", "Company Income", "Company Income per user income", "incomeAnalysis", rotate="horizontal")


def genderAnalysis(merged_dataset):

    company_user_earnings_indices = merged_dataset.groupby(["Company", "Gender"]).sum()["Price Charged"].index
    company_user_earnings = merged_dataset.groupby(["Company", "Gender"]).sum()["Price Charged"]
    company_user_expenditures = merged_dataset.groupby(["Company", "Gender"]).sum()["Cost of Trip"]

    pink_cab_incomes = {}
    for earn, exp, c_us in zip(company_user_earnings["Pink Cab"], company_user_expenditures["Pink Cab"],
                               company_user_earnings_indices):
        pink_cab_incomes[c_us[1]] = earn - exp

    yellow_cab_incomes = {}
    for earn, exp, c_us in zip(company_user_earnings["Yellow Cab"], company_user_expenditures["Yellow Cab"],
                               company_user_earnings_indices):
        yellow_cab_incomes[c_us[1]] = earn - exp


    plotBar(["Female","Male"], pink_cab_incomes.values(), yellow_cab_incomes.values(),
            "Gender", "Company Income", "Company Income per gender", "genderAnalysis", rotate="horizontal")


def kilometersIncome(merged_dataset):

    company_km_earnings_indices = merged_dataset.groupby(["Company", "KM Travelled"]).sum()["Price Charged"].index
    company_km_earnings = merged_dataset.groupby(["Company", "KM Travelled"]).sum()["Price Charged"]
    company_km_expenditures = merged_dataset.groupby(["Company", "KM Travelled"]).sum()["Cost of Trip"]

    print("We divide the ΚΜ Travelled into 5 clusters")
    km_clusters = ["1.9-10","10-20","20-30","30-40","40-50"]

    pink_cab_kms_incomes = {}
    for earn, exp, kms in zip(company_km_earnings["Pink Cab"], company_km_expenditures["Pink Cab"], company_km_earnings_indices):
        pink_cab_kms_incomes[kms[1]] = earn - exp

    yellow_cab_kms_incomes = {}
    for earn, exp, kms in zip(company_km_earnings["Yellow Cab"], company_km_expenditures["Yellow Cab"], company_km_earnings_indices):
        yellow_cab_kms_incomes[kms[1]] = earn - exp

    pink_cab_kms_clusters_incomes = {}
    yellow_cab_kms_clusters_incomes = {}

    for cluster in km_clusters:
        pink_cab_kms_clusters_incomes[cluster] = 0
        yellow_cab_kms_clusters_incomes[cluster] = 0

    pink_cab_kms_averages =list()
    for key, val in pink_cab_kms_incomes.items():
        pink_cab_kms_averages.append(val / key)
        if key <= 10:
            pink_cab_kms_clusters_incomes["1.9-10"] += val
        elif key <= 20:
            pink_cab_kms_clusters_incomes["10-20"] += val
        elif key <= 30:
            pink_cab_kms_clusters_incomes["20-30"] += val
        elif key <= 40:
            pink_cab_kms_clusters_incomes["30-40"] += val
        elif key <= 50:
            pink_cab_kms_clusters_incomes["40-50"] += val

    yellow_cab_kms_averages = list()
    for key, val in yellow_cab_kms_incomes.items():
        yellow_cab_kms_averages.append(val / key)
        if key <= 10:
            yellow_cab_kms_clusters_incomes["1.9-10"] += val
        elif key <= 20:
            yellow_cab_kms_clusters_incomes["10-20"] += val
        elif key <= 30:
            yellow_cab_kms_clusters_incomes["20-30"] += val
        elif key <= 40:
            yellow_cab_kms_clusters_incomes["30-40"] += val
        elif key <= 50:
            yellow_cab_kms_clusters_incomes["40-50"] += val

    pink_total= 0
    for p in pink_cab_kms_averages:
        pink_total+= p
    pink_average = "%.2f" % (pink_total/len(pink_cab_kms_averages))

    yellow_total= 0
    for p in yellow_cab_kms_averages:
        yellow_total+= p

    yellow_average = "%.2f" % (yellow_total/len(yellow_cab_kms_averages))

    pink_cab_list = ["Pink Cab", pink_average]
    yellow_cab_list = ["Yellow Cab", yellow_average]
    columns = ("Cab company", "Average income per ride")
    fig, ax = plt.subplots()
    fig.patch.set_visible(False)
    ax.axis('off')
    ax.axis('tight')

    plt.table(cellText=[pink_cab_list,yellow_cab_list],
              colLabels=columns, loc='center')

    fig.tight_layout()
    plt.savefig(IMAGESDIR + "kmAverage.png")
    #plt.show()

    plotBar(km_clusters, pink_cab_kms_clusters_incomes.values(), yellow_cab_kms_clusters_incomes.values(),
            "Kilometers travelled clusters", "Company Income", "Company Income per Km travelled cluster",
            "kilometersIncome", rotate="horizontal")


if __name__=="__main__":

    cab_data_file = scriptParentPath+"/Cab_Data.csv"
    customer_id_file = scriptParentPath+"/Customer_ID.csv"
    transaction_id_file = scriptParentPath+"/Transaction_ID.csv"
    city_file = scriptParentPath+"/City.csv"

    merged_dataset, city = mergeDatasets(cab_data_file, customer_id_file, transaction_id_file, city_file)
    new_dataset = outliersHandling(merged_dataset, "Price Charged")
    new_dataset = outliersHandling(new_dataset, "Cost of Trip")

    merged_dataset = new_dataset

    totalIncomeTable(merged_dataset)
    cityIncomeHistogram(merged_dataset)
    timeAnalysis(merged_dataset)
    customerProfileAnalysis(merged_dataset)
    kilometersIncome(merged_dataset)