"""
File: fetch_updates.py
Description: Uses the GitHub API to locate information on the selected bug-contributing commit 
Language: Python3
"""

import os
import csv
import time
import requests

TOKEN = os.environ[''] #Configure with a github token environmental variable 
USERNAME = '' # The GitHub username to use

def run_api(data):
    """
    Runs the API to collect details on the bug-contributing commit
    :param data: the existing dictionary of issue data
    :return None:
    """
    count = 0
    for key in data:
        data[key]['source_author'] = ''
        data[key]['source_author_id'] = ''
        data[key]['source_time'] = ''
        data[key]['source_link'] = ''
        data[key]['source_html'] = ''
        if data[key]['source_commit'] != '':
            count += 1
            if count > 4990:
                print("Cap reached!")
                time.sleep(3601)
                print("Process resuming")
                count = 0
            try:
                url = data[key]['url'].split("/commits/")[0] + "/commits/" + str(data[key]['source_commit'])
                response = requests.get(url, auth=(USERNAME, TOKEN))
                res = response.json()
                data[key]['source_author'] = res['commit']['author']['name']
                data[key]['source_author_id'] = res['commit']['author']['email']
                data[key]['source_time'] = res['commit']['author']['date']
                data[key]['source_link'] = res['url']
                data[key]['source_html'] = res['html_url']
            except:
                continue


def write_commits(data, of):
    """
    Writes the dictionary to a specified file
    :param data: the dictionary to write to the CSV
    :param of: The file to write to
    :return: None 
    """
    with open(of, 'w+') as write_file:
        if len(data) > 0:
            writer = csv.DictWriter(write_file,fieldnames=data[list(data.keys())[0]].keys() ,dialect="excel")
            writer.writeheader()
            for entry in data:
                writer.writerow(data[entry])
    data.clear()


def read_file(filename):
    """
    Reads the specified file
    :param filename: the file to read from
    :return: data - the dictionary of acquired CSV data
    """
    data = {}
    with open(filename) as file:
        reader = csv.DictReader(file)
        for line in reader:
            data[line['id']] = line
    return data


def main():
    data = read_file("combined_all_source.csv")
    # print("Waiting") Can be configured to wait out a rate-limit block
    # time.sleep(3600)
    # print("Starting")
    run_api(data)
    write_commits(data, 'final.csv')


if __name__ == '__main__':
    main()
