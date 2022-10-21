""" convert html table to csv file """

import csv
from gettext import install
import os
import utils
import pandas as pd
from pathlib import Path
from glob import glob
from bs4 import BeautifulSoup

def hasNumbers(inputString):
    return any(char.isdigit() for char in inputString)

def drop_assistants(df):
    """ drop ta and sa from dataframe """
    df = df[~df['name'].str.match(r'^(TA\.|SA\.)', na=False)]
    return df.reset_index(drop=True)

def drop_professors(df):
    """ drop professors from dataframe """
    df = df[df['id'].str.match(r'^[smd]\d{7}', na=False)]
    return df.reset_index(drop=True)

def drop_instructors(df):
    """ drop instructors from dataframe and return dataframe """
    # extract members starts with s OR m OR d in id column
    # and drop beggins with 'TA.' OR 'SA.' in name column
    df = drop_assistants(df)
    df = drop_professors(df)
    return df.reset_index(drop=True)

def memberfile2df(file_path):
    """ load member file and convert to dataframe """
    return pd.read_csv(file_path, encoding='utf_8_sig' ,header=None, names=['id', 'jpn_name', 'name'])

def numof_members(member_file_path):
    """ calculate and return number of members in each class excluding instructors """
    df = memberfile2df(member_file_path)
    return len(drop_instructors(df))

def calc_num_df(prefix_dir_path, quarter):
    """ calculate number of members in each class excluding instructors
        Args:
        prefix_path (str): path to the directory where the data is stored
        e.g. '../../data/2022/s1'
        quarter (int): quarter of the class
        Returns: pandas.dataframe
    """
    quarter = int(quarter)
    if quarter >= 1 and quarter <= 4:
        definitive_dir_path = os.path.join(prefix_dir_path, f'q{quarter}_definitive')
        if quarter == 1:
            data_dir = '04-'
        elif quarter == 2:
            data_dir = '06-'
        elif quarter == 3:
            data_dir = '10-'
        else:
            data_dir = '12-'
    else :
        # error handling
        print('quarter must be 1, 2, 3 or 4')
        return
    path_index_definitive = utils.find_file(definitive_dir_path, 'mlindex_j.html')
    table_list = utils.table2list(path_index_definitive[0])

    # convert list to pandas dataframe
    df = pd.DataFrame(table_list[1:], columns=table_list[0])
    num_df = []
    for ml_name, instructor in zip(df['ml_name'], df['instructor']):
        dirs_list = utils.find_dir(prefix_dir_path, data_dir)
        dirs_list.sort()
        num_list = []
        for subdir in dirs_list:
            # list of the same class name
            member_dir = utils.find_dir(subdir, 'member')

            # as ml_name is changed often so we use instructor name to find the class
            member_file_path_list = utils.find_file(member_dir[0], f'{ml_name[:3] + "????" + ml_name[7:]}.txt')

            # if member_file_path_list is empty, num is 0
            if not member_file_path_list:
                num_list.append(0)
            elif len(member_file_path_list) == 1:
                num_list.append(numof_members(member_file_path_list[0]))
            else:
                number = 0
                prof_set = set(instructor.split(','))
                for member_file_path in member_file_path_list:
                    member_df = memberfile2df(member_file_path)
                    # zenkaku to hankaku
                    member_df = member_df.replace({'jpn_name': {'\u3000': ' '}}, regex=True)
                    member_df_drop_prof = drop_professors(member_df)
                    member_df_prof_set = set(member_df['jpn_name']) - set(member_df_drop_prof['jpn_name'])
                    # compare professor names, if same (i.e. the same class), add number of members
                    if prof_set == member_df_prof_set:
                        number = len(member_df_drop_prof)
                        break
                num_list.append(number)
        # finally add number of definitive members to num_df
        definitive_member_dir = utils.find_dir(definitive_dir_path, 'member')
        num_list.append(numof_members(os.path.join(definitive_member_dir[0], f'{ml_name}.txt')))
        num_df.append(num_list)

    # make colums for num list
    # replacd '-' with '_' in column name
    dirs_list = [l.split('/')[-1].replace('-', '_') for l in dirs_list]
    dirs_list.append('definitive')
    num_df = pd.DataFrame(num_df, columns = dirs_list)

    df = pd.concat([df, num_df], axis=1)
    return df


def main():
    """ main function """
    return



if __name__ == '__main__':
    main()
