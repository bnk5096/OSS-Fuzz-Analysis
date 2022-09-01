"""
File: search.py 
Description: Runs GitHub API lookups for determining the bug-fixing commit 
Language: Python3
"""

import json
from pickle import NONE
import requests
import argparse
import csv
import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

START = 0 #File to start at
END = 441 # File to end at 
TOKEN = os.environ[''] #Configure with a github token environmental variable 

count = [0]

def fetch_from_csv(filename):
    """
    Reads from the specified file and populates the data dictionary
    :param filename: the filename to read from
    :return: data - a dictionary of all CSV data
    """
    data = {}
    with open(filename) as file:
        reader = csv.DictReader(file)
        for line in reader:
            data[line['id']] = line
    return data



def convert_to_github(data):
    """
    Converts the Monorail-provided commit ranges into their GitHub equivelants where possible
    :param data: the dictionary to load from 
    :return: links - dictionary of IDs to valid GitHub links
    """
    driver_loc = Service("/WebDrivers/chromedriver") # configure with path to the webdriver for selenium to use
    prev = NONE
    links = {}
    with webdriver.Chrome(service=driver_loc) as driver:
        for key in data:
            temp_list = []
            links[key] = ""
            if data[key]['fixed'] == '':
                continue
            try:
                time.sleep(2)
                wait = WebDriverWait(driver, 10)
                driver.get(data[key]["fixed"])
                dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "revisions-info")))
                dom = dom.shadow_root
                found_links = dom.find_elements(By.CSS_SELECTOR, "if-else")
                # dom = dom.shadow_root
                for edom in found_links:
                    link = edom.find_element(By.CSS_SELECTOR, "a")
                    if link.get_attribute("href").strip() and "github" in link.get_attribute("href").strip().lower():
                        temp_list.append(link.get_attribute("href").strip())
                for item in temp_list:
                    links[key] += item + "*SEP*"
                links[key] = links[key][:-5]
            except:
                continue
    return links


def run_api(data, links):
    """
    Runs the API to acquire the data for the bug fixing commit
    :param data: the dictionary of currently acquired data
    :param links: the dictionary of a data entry to public GitHub repository links
    :return: None 
    """
    print(count[0])
    for key in links:
        if links[key] == "":
            continue
        username = '' # Insert github username
        url = "https://api.github.com/repos/" + links[key].split(".com/")[1]
        response = requests.get(url, auth=(username, TOKEN))
        json_data = response.json()
        count[0] += 1
        possible_commits = {'mention':[], 'first': [], 'second': [], 'third': []}
        for commit in json_data['commits']:
            ts = data[key]['state'].split("--")
            lookup_url = commit['url']
            temp_response = requests.get(lookup_url, auth=(username, TOKEN))
            temp_json = temp_response.json()

            if count[0] > 4950:
                print("Resting the API...")
                time.sleep(3600)
                print("Restarting the API...")
                count[0] = 0
            count += 1
            for f in temp_json['files']:
                if key in temp_json['commit']['message']:
                    possible_commits['mention'].append(temp_json)
                if len(ts) > 0 and "patch" in f and ts[0].strip() in f['patch']:
                    possible_commits['first'].append(temp_json)
                elif len(ts) > 1 and "patch" in f and ts[1].strip() in f['patch']:
                    possible_commits['second'].append(temp_json)
                elif len(ts) > 2 and "patch" in f and ts[2].strip() in f['patch']:
                    possible_commits['third'].append(temp_json)
        print(possible_commits)
            

def write_links(data, links, of):
    """
    Writes the acquired links to a specified CSV 
    :param data: the dictionary of scraped data
    :param links: the map of Data entry keys to new links 
    :param of: the destination file to write to
    :return: None 
    """
    for entry in data:
        to_fill = ''
        if entry in links:
            to_fill = links[entry]
        data[entry]["new_link"] = to_fill
    with open(of, 'w+') as write_file:
        if len(data) > 0:
            writer = csv.DictWriter(write_file,fieldnames=data[list(data.keys())[0]].keys() ,dialect="excel")
            writer.writeheader()
            for entry in data:
                writer.writerow(data[entry])
    data.clear()
    links.clear()

     


def convert_all():
    """
    Processes the conversion process for all located issues.
    :return: None 
    """
    for i in range(START,END +1):
        data = fetch_from_csv("Numerical/" + str(i) + ".csv")
        links = convert_to_github(data)
        write_links(data, links, "out/new_" + str(i) + ".csv")


def github_run(data):
    """
    Runs the GitHub API search and determines the most likely commit 
    :param data: the dictionary of scarped data
    :return: None 
    """
    counter_talley = 0
    for key in data:
        data[key]['source'] = ""
        data[key]['url'] = ""
        data[key]['html'] = ""
        data[key]['commit_author'] = ""
        data[key]['commit_author_id'] = ""
        data[key]['commit_time'] = ""
        try:
            if data[key]["new_link"] == "":
                continue
            possible_commits = {'mention':[], 'first': [], 'second': [], 'third': [], 'oss_fuzz_error': [], 'sole_commit': []}
            for temp_link_value in data[key]["new_link"].split("*SEP*"):
                username = '' # Specify GitHub username to use 
                url = "https://api.github.com/repos/" + temp_link_value.split(".com/")[1]
                try:
                    response = requests.get(url, auth=(username, TOKEN))
                    json_data = response.json()
                    count[0] += 1
                except:
                    continue
                if "commits" not in json_data:
                    continue
                for commit in json_data['commits']:
                    ts = data[key]['state'].split("--")
                    lookup_url = commit['url']
                    temp_response = requests.get(lookup_url, auth=(username, TOKEN))
                    temp_json = temp_response.json()
                    if count[0] > 4950:
                        print("Resting the API...")
                        time.sleep(3600)
                        print("Restarting the API...")
                        count[0] = 0
                    count[0] += 1
                    for f in temp_json['files']:
                        if key in temp_json['commit']['message']:
                            possible_commits['mention'].append(temp_json)
                        if len(ts) > 0 and "patch" in f and ts[0].strip() in f['patch']:
                            possible_commits['first'].append(temp_json)
                        elif len(ts) > 1 and "patch" in f and ts[1].strip() in f['patch']:
                            possible_commits['second'].append(temp_json)
                        elif len(ts) > 2 and "patch" in f and ts[2].strip() in f['patch']:
                            possible_commits['third'].append(temp_json)
                        elif 'timeout' in data[key]['crash'].lower() and 'libFuzzer' in temp_json['commit']['message']:
                            possible_commits['oss_fuzz_error'].append(temp_json)
                    if len(json_data['commits']) == 1:
                        possible_commits['sole_commit'].append(temp_json)
                most_likely = ""
            try:
                for subkey in possible_commits:
                    for item in possible_commits[subkey]:
                        if most_likely == "":
                            most_likely = item
                            data[key]['source'] = subkey
                if most_likely != "":
                    data[key]['url'] = most_likely['url']
                    data[key]['html'] = most_likely['html_url']
                    data[key]['commit_author'] = most_likely['commit']['author']['name']
                    data[key]['commit_author_id'] = most_likely['commit']['author']['email']
                    data[key]['commit_time'] = most_likely['commit']['author']['date']
                    counter_talley += 1
                    
            except:
                continue
        except:
            continue


def write_commits(data, of):
    """
    Writes commit data to the given file 
    :param data: the data to write
    :param of: the filename to use for output 
    :return: None 
    """
    with open(of, 'w+') as write_file:
        if len(data) > 0:
            writer = csv.DictWriter(write_file,fieldnames=data[list(data.keys())[0]].keys() ,dialect="excel")
            writer.writeheader()
            for entry in data:
                writer.writerow(data[entry])
    data.clear()

def fetch_all():
    """
    Orchestrates GitHub lookup operations
    :return: None 
    """
    for i in range(START,END +1):
        data = fetch_from_csv("out/new_" + str(i) + ".csv")
        github_run(data)
        write_commits(data, "out/commit_link_" + str(i) + ".csv")

if __name__ == '__main__':
    # print("Starting Timer") this sleep can be enabled to wait out a rate-limit period 
    # time.sleep(3600)
    # print("Beginning Run")
    fetch_all()
