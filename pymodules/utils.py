""" convert html table to csv file """

import csv
import os
from pathlib import Path
from glob import glob
from bs4 import BeautifulSoup

def find_file(dir_path, key_file):
    """ find file in dir_path recursively """
    file_path_list = []
    for path in Path(dir_path).rglob(key_file):
        path_relative = os.path.join(dir_path, path.relative_to(dir_path))
        file_path_list.append(path_relative)
    return file_path_list

def find_dir(dir_path, key_dir):
    """ find directory from name key_dir in dir_path recursively """
    dir_path_list = []
    for root, subdir, _ in os.walk(dir_path):
        for dirs in subdir:
            if key_dir in dirs:
                dir_path_list.append(os.path.join(root, dirs))
    return dir_path_list

def list_subdir(dir_path):
    """ list subdirectories in dir_path """
    return glob(os.path.join(dir_path, "*", ""))

def table2list(file_path):
    """ convert html table to list """

    table_list = []

    soup = BeautifulSoup(open(file_path, encoding='utf-8'), 'html.parser' )

    # get subject name from html file and remove unnecessary rows
    table = soup.find_all("tr")

    # define column name of table
    table_list.append(['ml_name', 'period', 'instructor', 'class_name'])

    # convert html table to list. begin next to the first row
    for row in table[2:]:
        row_list = [elem.text for elem in row.find_all("td")]

        # remove the last element of row_list as it is unnecessary
        row_list.pop()

        # replace \3000 with space in the 3rd element
        row_list[2] = row_list[2].replace("\u3000", " ")

        # remove white space in the first element
        row_list[0] = row_list[0].replace(" ", "")

        table_list.append(row_list)

    return table_list

def list2csv(table_list, file_path):
    """ convert list to csv file and all elements are quoted """
    with open(file_path, 'w', newline='') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_ALL)
        writer.writerows(table_list)

def convert_html2csv(dir_path):
    """ search html file and convert to csv file """

    # search html file
    prefix = dir_path

    for index_dir in find_dir(prefix, "Index"):
        for i in find_file(index_dir, 'mlindex_j.html'):
            table_list = table2list(i)
            list2csv(table_list, i.replace('.html', '.csv'))

if __name__ == '__main__':
    exit()