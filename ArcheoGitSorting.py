"""
File: ArcheoGitSorting.py 
Description: Sorts issues into a file for each project
Language: Python3
"""

import csv


def sort_by_project(data):
    """
    Sorts entries into project by project entries
    :param data: the dictionary of data
    :return: a new dictionary mapping projects to a list of relevant data entries
    """
    new_data = {}
    # https://github.com/libarchive/libarchive/commit/
    for key in data:
        project_github = data[key]['url'].split("/repos/")[1]
        project_github = project_github.split("/commits/")[0]
        if project_github in new_data:
            new_data[project_github].append(data[key])
        else:
            new_data[project_github] = [data[key]]
    return new_data


def in_moment_processing(data):
    """
    Generates a list of unique crash types
    :param data: the data dictionary
    :return: None
    """
    out = set()
    for key in data:
        out.add(data[key]['crash'])
    print(out)


def limited_set(data):
    """
    Counts the number of entries in the dataset that include a URL compared to the total
    :param data: the dictionary of data
    :return: None
    """
    count_good = 0
    count_total = len(data)
    temp = list(data.keys())
    for key in temp:
        if data[key]['url'] == '':
            data.pop(key)
        else:
            count_good += 1
    print("Total: " + str(count_total))
    print("Good: " + str(count_good))
    print('done')


def write_file(data, outfile):
    """
    Writes the data to a file
    :param data: the data dictionary
    :param outfile: the out filename/path
    :return: None
    """
    with open(outfile, 'w', encoding="utf8", newline='') as writing:
        if len(data) > 0:
            writer = csv.DictWriter(writing, fieldnames=data[list(data.keys())[0]].keys(), dialect="excel")
            writer.writeheader()
            for entry in data:
                writer.writerow(data[entry])


def write_file_list(data, outfile):
    """
    Writes a file when the data is provided as a list instead of a dictionary
    :param data: data in list form
    :param outfile: outfile: the out filename/path
    :return: None
    """
    with open(outfile, 'w', encoding="utf8", newline='') as writing:
        if len(data) > 0:
            writer = csv.DictWriter(writing, fieldnames=list(data[0].keys()), dialect="excel")
            writer.writeheader()
            for entry in data:
                writer.writerow(entry)


def read_file(filename):
    """
    Reads in the provided file to produced by archeogit
    :param filename: the file to read
    :return: the dictionary of data
    """
    data = {}
    with open(filename, encoding="utf8") as file:
        reader = csv.DictReader(file)
        for line in reader:
            data[line['id']] = line
    return data


def main():
    data = read_file("../data/combined_all.csv")
    limited_set(data)
    in_moment_processing(data)
    new_data = sort_by_project(data)
    print(new_data.keys())
    for key in new_data:
        temp_name = key.replace("/", "___", key.count("/"))
        write_file_list(new_data[key], '../out/' + temp_name + '.csv')


if __name__ == '__main__':
    main()
