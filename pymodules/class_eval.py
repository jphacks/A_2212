""" read pdf of class evaluation and export to csv """
import csv
import os
import pandas as pd
import re
from traceback import print_tb
from numpy import NAN, NaN

# pip install tabula-py
from tabula import read_pdf

"""
def make_new_csv(dfs, usual_columns):
    dfs = dfs.values.tolist()

    dfs = [[l.replace("\r", " ") if type(l) is str else "-" for l in x] for x in dfs]
    df = pd.DataFrame(dfs, columns=usual_columns)

    df = df[df["Class(Course)"] != "-"]

    # drop clean rows
    df = df.drop(df.index[[0]], axis=0)

    return df
"""

def make_new_csv(dfs,usual_columns):
    dfs = dfs.values.tolist()

    new_dfs = []
    for x in dfs:
        list = []
        if not isinstance(x[0], str):
            continue
        if x[0].isdigit():
            x[4:6] = ["-", "-"]

            x.pop(-1)
            x.insert(6, "-")

        for i, l in enumerate(x):
            if type(l) is str and i != 3:
                list.append(l.replace("\r", " "))
            elif type(l) is str and i == 3:
                list.append(l.replace("\r", ""))
            else:
                list.append(l)
        new_dfs.append(list)


    df = pd.DataFrame(new_dfs, columns=usual_columns)

    df = df[df["Class(Course)"] != "-"]

    # drop clean rows
    df = df.drop(df.index[[0]], axis=0)

    return df

def pdf2pd(pdf_file_path, page_range):
    """ convert pdf to pandas dataframe """

    # columns
    usual_columns = ["Class(Course)",
                "Class(SUM)",
                "Code",
                "Course Name jp",
                "Course Name",
                "Professor name jp",
                "Professor Name",
                "Number of Targets",
                "Number of Answers",
                "Ratio",
                "eval 1",
                "eval 2",
                "eval 3",
                "eval 4",
                "eval 5",
                "eval 6",
                "eval 7",
                "eval 8",
                "eval 9",
                "OverallEvaluation"]


    # Read PDF
    dfs = read_pdf(pdf_file_path,       # PDFファイル
                     pages=page_range,    # 抽出ページ
                     guess=False,     # 分析部分の変更有無
                     area="entire",  # ページの部分指定
                     lattice=True,  # 格子区切りがPDF内にある場合の対応
                     stream=False,   # ストリームモード
                    )

    # Convert to CSV
    # dfs = [l.values.tolist() for l in dfs]
    # dfs = [l if not re.match("Sub Total*",l[2]) else [l[:3] + ["-","-"] + l[3:]] for l in dfs]
    #df.columns = usual_columns

    df = make_new_csv(dfs[0], usual_columns)

    for i in range(1, len(dfs)):
        df = pd.concat([df, make_new_csv(dfs[i], usual_columns)])

    return df


def main():
    """ main function """
    files = [(ay, (sem%2)+1, pages) for ay, sem, pages in zip([2019,2019,2020,2020,2021,2021]
                                                            , [sem for sem in range(0,6)]
                                                            , ['2-10','2-10','2-11','2-8','2-15','2-10'])]
    # _class_evaluate directory is ignored by git
    for ay, sem, pages in files:
        print(ay, sem, pages)
        df = pdf2pd(f"../_class_evaluate/FDclassevaluation{ay}-{sem}_je.pdf", pages)
        # save csv
        df.to_csv(f"./_csv_cache/class_eval_{ay}-{sem}.csv", index=False, quoting=csv.QUOTE_ALL, encoding="utf-8-sig", na_rep="NaN")


if __name__ == '__main__':
    main()