import calc_members
import csv
import json
import os
import pandas as pd
import numpy as np

def make_new_df_list(dfs):

    #the dict to bring the same lessons together.
    name_dict = {}

    new_df_list = []

    for df in dfs.values:

        # for dict keys
        name = df[2].split(" ")

        last_value = ""
        if "[演]" in name[-1]:
            last_value = "[演]"
            # Remove exercise classes for subjects that also have exercises.
            if name[0] in name_dict:
                continue
        name = name[0] + last_value


        # Remove retaking class or Graduation thesis
        if "[再]" in df[2] or "GT01" in df[2]:
            continue

        # bring the same lessons together.
        if name in name_dict: # if the same lesson is already in the dict
            for i, value in enumerate(df[3:-1]):
                new_df_list[name_dict[name]][3+i] += value

        else: # if the same lesson is not in the dict

            # Modify the name
            last_value = ""
            if "[演]" in df[2]:
                last_value = "[演]"

            df[2] = df[2].split("[")[0] + last_value

            # Add to dict and list
            new_df_list.append(df)
            name_dict[name] = len(new_df_list)-1

    # Stores index of unwanted rows.
    delete_index_list = []
    for name in name_dict:
        if "[演]" in name and name.replace("[演]","") in name_dict:
            delete_index_list.append(name_dict[name])

    # delete
    new_df_list = np.delete(new_df_list, delete_index_list, axis=0)

    return new_df_list

def convert_df2json(df):
    """ make json data"""
    json_data = []
    for row in df.itertuples(index=False):
        dict_data = {}
        course_code = row.class_name.split(" ")[0]
        dict_data['course_code'] = course_code

        # number of member element begins from 3rd column
        # chooze the first value that is not 0
        for num in row[4:]:
            if num != 0:
                num_members_before = num
                break

        num_members_after = row[-1]
        dict_data['information'] = {}
        dict_data['information']['withdrawal_rate'] = (num_members_before - num_members_after) / num_members_before
        dict_data['information']['class_name'] = row.class_name
        json_data.append(dict_data)

    return json.dumps(json_data, ensure_ascii=False, indent=4)

def analyze_ml_data(prefix, academic_year, quarter, csv_cache_dir_path=None):
    """ analyze from mailing list data.
    Args:
        prefix (str): path to the directory containing the data
        e.g. ../../data/
        academic_year (int): academic year
        quarter (int): quarter
    Returns:
        df (pd.DataFrame): pandas dataframe containing the data
    """

    if quarter == 1 or quarter == 2:
        semester = 's1'
    else:
        semester = 's2'

    dir_path = os.path.join(prefix, str(academic_year), semester)
    if csv_cache_dir_path is not None:
        csv_file_name = f'{academic_year}_{quarter}_ml.csv'
        csv_file_path = os.path.join(csv_cache_dir_path, csv_file_name)
        if not os.path.exists(csv_file_path):
            df = calc_members.calc_num_df(dir_path, quarter)
            # convert df to csv
            df.to_csv(csv_file_path, index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
        df = pd.read_csv(os.path.join(csv_cache_dir_path, csv_file_name), encoding="utf-8-sig", quoting=csv.QUOTE_ALL)
    else:
        df = calc_members.calc_num_df(dir_path, quarter)

    # remove day of week column
    dfs = df.drop(df.columns[[1]],axis = 1)

    # pd dataframe to list
    columns_list = dfs.columns.tolist()

    new_df_list = make_new_df_list(dfs)
    # to pd dataframe and then save
    new_df = pd.DataFrame(new_df_list, columns=columns_list)

    return new_df

def main():
    """ main function """
    return

if __name__ == '__main__':
    main()