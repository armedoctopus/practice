import json
import time

import matplotlib.pyplot as plt
import omdb
import pandas as pd
import requests
from bs4 import BeautifulSoup

import tweepbotconfig as config

API_KEY = config.data['OMDB_API_KEY']
omdb.set_default('apikey', API_KEY)


def scraping_the_number():
    start_page = 1

    while start_page < 1000:
        scrape_url = "https://www.the-numbers.com/movie/budgets/all/{}".format(
            start_page)
        raw_df = pd.read_html(scrape_url, header=0)[0]
        filtered_df = raw_df.dropna(axis=0, how='all')
        filtered_df.to_csv("page{}.csv".format(
            start_page), sep='\t', header=True)
        print(filtered_df)
        start_page += 100
        time.sleep(3)


def scraping_rotten_tomato():
    base_url = "https://www.rottentomatoes.com/search/?search=avatar"
    res = requests.get(base_url)
    soup = BeautifulSoup(res.content, "html.parser")
    movie_list = soup.find_all('li', {'class': 'bottom divider clearfix'})
    for movie in movie_list:
        print(movie)


def load_csv_and_query(input_file):
    #load csv and iterate through df to get movie names
    master_data = pd.read_csv(input_file, sep='\t')
    #print(movies_list)
    for index, row in master_data.iterrows():
        print("{0} has name: {1}".format(index, row['Movie']))
    movies_list = master_data['Movie'].tolist()
    print(movies_list)
    for movie in movies_list:
        try:
            movie_deets = omdb.title(movie, timeout=5)
            if movie_deets:
                time.sleep(2)
                continue
            else:
                print("Error - {}\n".format(movie))
        except Exception as inst:
            print('Error - {} Movie - {}\n'.format(inst, movie))
    time.sleep(2)


def load_csv_and_query_api(input_file):
    #load csv and iterate through df to get movie names
    master_data = pd.read_csv(input_file, sep='\t')
    #print(movies_list)
    ratings = []
    for row in master_data['Movie']:
        results = omdb_request_api(row)
        ratings.append(results)
    ratings_df = pd.DataFrame(ratings)
    ratings_df.to_csv("ratings{}.csv".format(
        input_file[:-4]), sep='\t', header=True)
    print(ratings_df)
    final_df = master_data.join(ratings_df, how='outer')
    print(final_df)
    final_df.to_csv("movie_ratings{}.csv".format(
        input_file[:-4]), sep='\t', header=True)


def omdb_request_api(movie_name):
    try:
        scrape_url = "http://www.omdbapi.com/"
        #http://docs.python-requests.org/en/master/user/quickstart/
        payload = {'apikey': API_KEY, 't': movie_name}
        res = requests.get(scrape_url, params=payload, timeout=10)
        movie_deets = json.loads(res.text)
    except Exception as inst:
        print("Error - {0} - {1}".format(inst, movie_name))
        ratings = {'IMDB': 0, 'RT': 0, 'METACRITIC': 0}
        time.sleep(3)
        return ratings
    if movie_deets['Response'] == 'True':
        #print(movie_deets['Title'])
        if len(movie_deets['Ratings']) == 1:
            imdb_rating = movie_deets['Ratings'][0]['Value']
            rt_rating = 0
            metacritic = 0
        elif len(movie_deets['Ratings']) == 2:
            rt_rating = movie_deets['Ratings'][1]['Value']
            imdb_rating = movie_deets['Ratings'][0]['Value']
            metacritic = 0
        elif len(movie_deets['Ratings']) == 3:
            rt_rating = movie_deets['Ratings'][1]['Value']
            imdb_rating = movie_deets['Ratings'][0]['Value']
            metacritic = movie_deets['Ratings'][2]['Value']
        else:
            imdb_rating = 0
            rt_rating = 0
            metacritic = 0
        ratings = {'IMDB': imdb_rating,
                   'RT': rt_rating, 'METACRITIC': metacritic}
        time.sleep(3)
        return ratings
    else:
        print("Error: {0} - {1}".format(movie_name, movie_deets['Error']))
        ratings = {'IMDB': 0, 'RT': 0, 'METACRITIC': 0}
        time.sleep(3)
        return ratings


def load_csv_and_plot(input_file):
    master_data = pd.read_csv(input_file, sep='\t')
    master_data['Production Budget'] = master_data['Production Budget'].replace(
        '[\$,]', '', regex=True).astype(float)
    master_data['Production Budget'] = master_data['Production Budget'].divide(
        1000000)
    master_data['Worldwide Gross'] = master_data['Worldwide Gross'].replace(
        '[\$,]', '', regex=True).astype(float)
    master_data['Worldwide Gross'] = master_data['Worldwide Gross'].divide(
        1000000)
    master_data['Domestic Gross'] = master_data['Domestic Gross'].replace(
        '[\$,]', '', regex=True).astype(float)
    master_data['Domestic Gross'] = master_data['Domestic Gross'].divide(
        1000000)
    master_data['IMDB'] = master_data['IMDB'].replace(
        '[\/10,]', '', regex=True)
    master_data['IMDB'] = pd.to_numeric(
        master_data['IMDB'], downcast='float', errors='coerce')
    master_data['Production to Worldwide Ratio'] = master_data['Worldwide Gross'].divide(
        master_data['Production Budget'])
    print(master_data)
    ##https://stackoverflow.com/questions/4270301/matplotlib-multiple-datasets-on-the-same-scatter-plot
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_ylabel('Worldwide Gross over Production Budget Ratio')
    ax1.set_xlabel('IMDB Rating')
    ax1.scatter(y=master_data['Production to Worldwide Ratio'],
                x=master_data['IMDB'], marker='o', c='r')
    #ax1.scatter(y=master_data['Worldwide Gross'], x=master_data['IMDB'], marker='s', c='b', label='Worldwide Gross')
    #plt.legend(loc='upper right')
    plt.show()
    chart_df = pd.concat([master_data['Production to Worldwide Ratio'],
                        master_data['Movie'], master_data['IMDB']], axis=1)
    chart_df.to_csv('d3chart.tsv', sep='\t', header=True)
    print(new_df)