import csv
import sys
import os
import sqlite3
import openpyxl


def xlsx2csv(file_name):
    wb = openpyxl.load_workbook(filename=file_name, data_only=True)

    ws = wb[wb.worksheets[0].title]
    ans = []
    for r in ws.rows:
        sub = []
        for cel in r:
            sub.append(cel.value)
        ans.append(sub)
    with open('./files/file.csv', encoding='UTF-8', mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=';', quotechar='"')
        for elem in ans:
            writer.writerow(elem)


def csv2sql(data):
    con = sqlite3.connect("./files/db.sqlite")
    cur = con.cursor()
    heads = list(next(data).keys())
    cur.execute("""
    DROP TABLE IF EXISTS Data""")
    cur.execute(f"""CREATE TABLE Data (
        [{heads[0]}] TEXT)""")
    for elem in heads[1:]:
        cur.execute(f"ALTER TABLE Data ADD COLUMN [{elem}] TEXT")
    for elem in data:
        elem.values()
        vals = '", "'.join(elem.values())
        cur.execute(f'INSERT INTO Data ([{"], [".join(heads)}]) VALUES("{vals}")')
    con.commit()


def dict_factory(cursor, row):
    d = {}  # Создаем пустой словарь
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]  # Заполняем его значениями
    return d