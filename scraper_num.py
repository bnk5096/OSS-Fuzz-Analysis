"""
File: scraper_num.py
Description: Performs web scraping on Monorail to acquire OSS-Fuzz issue data and stores data in a numerical set of files.
Language: Python3 
"""


import argparse
import copy
import csv
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


def arg_handle():
    """
    handles the start page argument
    returns: the Parser instance
    """
    parser = argparse.ArgumentParser(description="Scrapes a Monoral Issue Tracker Page for OSS-Fuzz")
    parser.add_argument("start", type=int, help="the start page (zero indexed)")
    return parser


def scrape_main_page(driver, start_iter, data):
    """
    Reads from the main page of the Monorial Issue collection
    :param driver: the driver instance to use
    :param start_iter: the starting iteration for the execution
    :param data: the dictionary to store data in
    :return: None 
    """
    wait = WebDriverWait(driver, 20)
    driver.get("https://bugs.chromium.org/p/oss-fuzz/issues/list?q=-status%3ADuplicate%20-component%3AInfra&can=1&start=0")
    main_dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-list-page")))
    main_dom = main_dom.shadow_root
    current_iter = 0
    while True:
        try:
            if current_iter < start_iter:
                current_iter += 1
            else:
                time.sleep(5)
                table_wait = WebDriverWait(main_dom, 20)
                entries_master = table_wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-issue-list")))
                entries_master = entries_master.shadow_root
                entries = entries_master.find_element(By.CSS_SELECTOR, "tbody")
                entries = entries.find_elements(By.CSS_SELECTOR, "mr-issue-link")

                # Get Project list
                project_list = []
                projects = entries_master.find_elements(By.CSS_SELECTOR, "td")
                for i in range(5, len(projects), 10):
                    project_list.append(projects[i].text)

                print(len(entries))
                scrape_issue_pages(entries, driver, data, project_list)
                write_data(data, "Numerical/" + str(current_iter) + ".csv")
                current_iter += 1

        except Exception as e:
            print(e)
            break
        try:
            driver.refresh()
            time.sleep(15)
            wait = WebDriverWait(driver, 20)
            main_dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-list-page")))
            main_dom = main_dom.shadow_root
            wait2 = WebDriverWait(main_dom, 20)
            next_button = wait2.until(presence_of_element_located((By.CSS_SELECTOR, "a")))
            time.sleep(5)
            buttons = main_dom.find_elements(By.CSS_SELECTOR, "a")
            flag = False
            for element in buttons:
                if element.text.split()[0].strip() == "Next":
                    element.send_keys(Keys.RETURN)
                    print("Turning the page")
                    flag = True
                    break
            if not flag:
                break
        except Exception as e:
            print(e)
            break


    print("DONE")


def scrape_issue_pages(entries, driver, data, project_list):
    """
    Runs the process of reading from each of the collected
    :param entires: the entries acquired from the issue listing
    :param driver: the driver to use 
    :param data: the dictionary to store data in 
    :param project_list: the list of projects corresponding to the issues read
    :return: None 
    """
    home_window = driver.window_handles[0]
    iter_counter = 0
    for entry in entries:
        project = project_list[iter_counter]
        iter_counter += 1
        driver.switch_to.window(home_window)
        entry_shadow = entry.shadow_root
        anchor = entry_shadow.find_element(By.CSS_SELECTOR, "a")
        anchor.send_keys(Keys.CONTROL + Keys.RETURN)
        window = driver.window_handles[-1]
        counter = 0
        while True:
            try:
                scrape_issue_page(window, driver, data, project)
                break
            except Exception as e:
                print(e)
                counter += 1
                if counter > 20:
                    break
                continue
    driver.switch_to.window(home_window)


def scrape_issue_page(window, driver, data, project):
    """
    Scrapes a single issue page for details
    :param window: the window to scrape
    :param driver: the webdriver in use
    :param data: the dictionary to store scraped data in 
    :param project: The project the issue relates to 
    :return: None 
    """
    driver.switch_to.window(window)
    driver.refresh()
    time.sleep(2)
    # type
    wait = WebDriverWait(driver, 20)
    dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-issue-metadata")))
    dom = dom.shadow_root
    dom = dom.find_element(By.CSS_SELECTOR, "mr-metadata")
    dom = dom.shadow_root
    wait = WebDriverWait(dom, 20)
    dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-field-values")))
    dom = dom.shadow_root
    dom = dom.find_element(By.CSS_SELECTOR, "a")
    entry_type = dom.get_attribute("text").strip()

    # Status
    wait = WebDriverWait(driver, 20)
    dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-issue-metadata")))
    dom = dom.shadow_root
    dom = dom.find_element(By.CSS_SELECTOR, "mr-metadata")
    dom = dom.shadow_root
    wait = WebDriverWait(dom, 20)
    dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "tr.row-status")))
    dom = dom.find_element(By.CSS_SELECTOR, "td")
    status = dom.text.strip()
    

    #label & time of detection
    wait = WebDriverWait(driver, 20)
    dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-issue-header")))
    dom = dom.shadow_root
    dom_temp = dom.find_element(By.CSS_SELECTOR, "h1")
    label = dom_temp.text.split()[1].strip().strip(":")
    dom = dom.find_element(By.CSS_SELECTOR, "chops-timestamp")
    tod = dom.get_attribute("title")
    regressed = ""
    fixed = ""
    crash_type = ""
    crash_state = ""
    
    
    # Check the description 
    wait = WebDriverWait(driver, 20)
    dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-description")))
    dom = dom.shadow_root
    dom  = dom.find_element(By.CSS_SELECTOR, "mr-comment-content")
    dom = dom.shadow_root
    elements = dom.find_elements(By.CSS_SELECTOR, "*")
    for i in range(len(elements)):
        el = elements[i]
        try:
            if el.text.strip() == "Regressed:" or el.text.strip() == "Crash Revision:":
                regressed = elements[i+1].get_attribute("text")
        except Exception as e:
            print(e)
        try:
            if "Crash Type" in el.text.strip():
                crash_type = elements[i].text.split(":")[1]
        except Exception as e:
            print(e)
        try:
            if "Crash State" in el.text.strip():
                temp = []
                max = 8
                if len(elements[i:]) < 8:
                    max = len(elements[i:])
                for j in range(2, max, 2):
                    try:
                        if "  " in  elements[i+j].text:
                            temp.append(elements[i+j].text.strip())
                    except Exception as e:
                        print(e)
                for e in temp:
                    crash_state += e + "--"
                crash_state = crash_state[:-2]
        except Exception as e:
            print(e)


    wait = WebDriverWait(driver, 20)
    dom = wait.until(presence_of_element_located((By.CSS_SELECTOR, "mr-comment-list")))
    dom = dom.shadow_root
    comments = dom.find_elements(By.CSS_SELECTOR, "mr-comment")
   
    tof = ""
    for comment in comments:
        try:
            temp_comment = comment.shadow_root
            temp_header = temp_comment.find_element(By.CSS_SELECTOR, "chops-timestamp")
            
            temp_comment = temp_comment.find_element(By.CSS_SELECTOR, "mr-comment-content")
            temp_comment = temp_comment.shadow_root
            links = temp_comment.find_elements(By.CSS_SELECTOR, "a")
            temp_list = []
            #Check for fixed and regressed
            elements = temp_comment.find_elements(By.CSS_SELECTOR, "*")
            for i in range(len(elements)):
                el = elements[i]
                try:
                    if el.text.strip() == "Regressed:" or el.text.strip() == "Crash Revision:":
                        regressed = elements[i+1].get_attribute("text")
                    if el.text.strip() == "Fixed:" or "verified as fixed in" in el.text.strip():
                        fixed = elements[i+1].get_attribute("text")
                        tof = temp_header.get_attribute("title")
                except Exception as e:
                    print(e)
                    continue
                if regressed != "" and fixed != "":
                    break
            if regressed != "" and fixed != "":
                break
        except Exception as e:
            print(e)
            continue

    data[label] = {}
    data[label]["id"] = label
    data[label]["project"] = project
    data[label]["type"] = entry_type
    data[label]["Status"] = status
    data[label]["crash"] = crash_type
    if len(crash_state) >= 2 and crash_state[-1] == "-" and crash_state[-2] == "-":
        crash_state = crash_state[:-2]
    data[label]["state"] = crash_state
    tod = tod.split(",")
    tod = " ".join(tod)
    tof = tof.split(",")
    tof = " ".join(tof)
    data[label]["tod"] = tod
    data[label]["regressed"] = regressed
    data[label]["tof"] = tof
    data[label]["fixed"] = fixed
    driver.close()


def write_data(data, filename):
    """
    Writes the data dictionary to a file 
    :param data: the dictionary to write
    :param filename: the filename to write to
    :return: None
    """
    with open(filename, 'w+') as write_file:
        if len(data) > 0:
            writer = csv.DictWriter(write_file,fieldnames=data[list(data.keys())[0]].keys() ,dialect="excel")
            writer.writeheader()
            for entry in data:
                writer.writerow(data[entry])
    data.clear()


def alt_main():
    """
    Runs the scraping operations without utilizing command line arguments
    """
    parser = arg_handle()
    args = parser.parse_args()
    driver_loc = Service("") # Include the path to the Chrome websriver for selenium to use
    # for project in projects:
    data = {}
    with webdriver.Chrome(service=driver_loc) as driver:
        scrape_main_page(driver, args.start, data)
        driver.quit()
    

def main():
    """
    Main function that utilizes command line arguments
    """
    parser = arg_handle()
    args = parser.parse_args()
    driver_loc = Service("") # Include the path to the Chrome websriver for selenium to use
    data = {}
    with webdriver.Chrome(service=driver_loc) as driver:
            scrape_main_page(driver, args.num, data)
    write_data(data, "data/output.csv")


if __name__ == '__main__':
    alt_main() # to run without arguments
    # main() to run with arguments
