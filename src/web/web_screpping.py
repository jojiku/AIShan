import requests
from bs4 import BeautifulSoup
import csv
import os

# ЗДЕСЬ ИЗМЕНИТЬ
url = 'https://dostavka24.pro/goryachaya-liniya-ashan/'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')


data = []

    # Extract text from <h2> tags
h2_tags = soup.find_all('h2')
for h2_tag in h2_tags:
    h2_text = h2_tag.get_text()
    data.append(['<h2>', h2_text])

    # Extract text from <p> tags
p_tags = soup.find_all('p')
for p_tag in p_tags:
    p_text = p_tag.get_text()
    data.append(['<p>', p_text])

# ЗДЕСЬ ИЗМЕНИТЬ
folder_path = 'C:/Users/Tseh/Desktop/Hackaton'  
csv_file_name = 'parsed_data.csv'


full_file_path = os.path.join(folder_path, csv_file_name)


with open(full_file_path, 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    

    # csv_writer.writerow(['Tag', 'Text'])
    
 
    csv_writer.writerows(data)

print(f'Data has been written to {full_file_path}')
