""" main module. export json data """
import csv
import class_eval
import json
import analyze_daily_members as adm
import pandas as pd
import re

df_eval = None

def solve_rate(course_code):
    """ solve the evaluation rate of the course from df_eval """
    df = df_eval[df_eval['Course Name'].str.contains(course_code, na=False)]
    # solve average of the evaluation rate
    len_df = len(df)
    rate = 0
    for row in df.itertuples(index=False):
        # overall evaluation rate
        overall_rate = row[-1]
        # overall_rate is str
        # it is possible value is ' - '
        # check if the variable is float and convert to float by regex
        if re.match(r'^-?\d+(?:\.\d+)$', str(overall_rate)) is None:
            len_df -= 1
        else:
            rate += float(overall_rate)
    if len_df == 0:
        return -1
    else :
        return rate / len_df

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
        dict_data['information']['eval_overall'] = solve_rate(course_code)
        json_data.append(dict_data)
    return json.dumps(json_data, ensure_ascii=False, indent=4)


def main():
    """ main function """

    files = [(ay, (sem%2)+1, pages) for ay, sem, pages in zip([2019,2019,2020,2020,2021,2021]
                                                            , [sem for sem in range(0,6)]
                                                            , ['2-10','2-10','2-11','2-8','2-15','2-10'])]
    global df_eval

    # _class_evaluate directory is ignored by git
    for ay, sem, pages in files:
        df = class_eval.pdf2pd(f"../_class_evaluate/FDclassevaluation{ay}-{sem}_je.pdf", pages)
        if df_eval is None:
            df_eval = df
        else:
            df_eval = pd.concat([df_eval, df], axis=0)

    date = [(2021, 4), (2022, 1), (2022, 2), (2022, 3)]

    for ay , q in date:
        new_df = adm.analyze_ml_data('../data/', ay, q, csv_cache_dir_path='./_csv_cache')
        new_df.to_csv(f'./_csv_cache/combined_{ay}_{q}_ml.csv', index=False, encoding='utf-8-sig', quoting=csv.QUOTE_ALL)
        json_data = convert_df2json(new_df)
        #write json
        with open(f"./json_data/{ay}_q{q}.json", "w") as f:
            f.write(json_data)

if __name__ == '__main__':
    main()
