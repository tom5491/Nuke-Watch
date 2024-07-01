"""
Imports
"""
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup


"""
Functions
"""
def retrieve_all_power_station_data(nuke_statuses_url='https://www.edfenergy.com/energy/power-station/daily-statuses'):
    r = requests.get(nuke_statuses_url)
    soup = BeautifulSoup(r.content, features='lxml')

    # Updated class and tag selection based on provided HTML
    power_station_soups = soup.find_all('article', class_='reactors-layout-listing')

    all_power_station_data = list()

    for power_station_soup in power_station_soups:
        power_station_data = dict()
        power_station_data['name'] = power_station_soup.find('h3', class_='h4').find('a').text.strip()

        reactor_soups = power_station_soup.find_all('div', class_='reactor')
        power_station_data['reactors'] = list()

        for reactor_soup in reactor_soups:
            reactor_data = dict()
            reactor_name_tag = reactor_soup.find('h3', class_='h5 field-name-field-reactor-name').find('div')
            status_div = reactor_soup.find('div', string='Status')
            status_tag = status_div.find_next('div') if status_div else None
            output_tag = reactor_soup.find('div', class_='generation-amount').find('div')

            reactor_data['name'] = reactor_name_tag.text.strip() if reactor_name_tag else "Unknown"
            reactor_data['status'] = status_tag.text.strip() if status_tag else "Unknown"
            reactor_data['output_MW'] = int(output_tag.text.strip()) if output_tag else 0

            power_station_data['reactors'] += [reactor_data]

        all_power_station_data += [power_station_data]
        
    return all_power_station_data

def update_readme_time(readme_fp, 
                       splitter='Last updated: ', 
                       dt_format='%Y-%m-%d %H:%M'):
    
    with open(readme_fp, 'r') as readme:
        txt = readme.read()
    
    start, end = txt.split(splitter)
    old_date = end[:16]
    end = end.split(old_date)[1]
    new_date = pd.Timestamp.now().strftime(dt_format)
    
    new_txt = start + splitter + new_date + end
    
    with open(readme_fp, 'w') as readme:
        readme.write(new_txt)
        
    return
    
    
"""
Retrieval Process
"""
all_power_station_data = retrieve_all_power_station_data()

with open('data/all_power_station_data.json', 'w') as fp:
    json.dump(all_power_station_data, fp)
    
update_readme_time('README.md')