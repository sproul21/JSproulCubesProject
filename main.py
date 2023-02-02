# import sys
# import requests
# import sqlite3
# from secrets import wufoo_key
# from requests.auth import HTTPBasicAuth
#
#
# def get_wufoo_data() -> dict:
#     url = "https://jsproul.wufoo.com/api/v3/forms/cubes-project-proposal-submission/entries/json"
#     response = requests.get(url, auth=HTTPBasicAuth(wufoo_key, 'pass'))
#
#     if response.status_code != 200:
#         print(f"Failed to get data, response code:{response.status_code} and error message: {response.reason} ")
#         sys.exit(-1)
#     jsonresponse = response.json()
#     return jsonresponse['Entries']
#
#
# def write_wufoo_data():
#     # create a database connection
#     conn = sqlite3.connect('wufoo_data.db')
#     c = conn.cursor()
#
#     # create the table if it doesn't already exist
#     c.execute('''CREATE TABLE IF NOT EXISTS entries
#                  (Entry_Id text, Title text, First_Name text, Last_Name text,
#                  Org_Title text, Organization text, Email text, Org_Website text,
#                  Phone_Number text, Time_Period text, Permission text,
#                  Opportunities text, Date_Created text, Created_By text,
#                  Date_Updated text, Updated_By text)''')
#
#     # retrieve the data from Wufoo
#     data = get_wufoo_data()
#
#     # insert the data into the table
#     for item in data:
#         opportunities = ', '.join([item[f'Field112'], item[f'Field113'], item[f'Field114'],
#                                   item[f'Field115'], item[f'Field116'], item[f'Field117'],
#                                   item[f'Field118']])
#
#         c.execute("INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
#                   (item['EntryId'], item['Field214'], item['Field1'], item['Field2'], item['Field8'],
#                    item['Field9'], item['Field5'], item['Field6'], item['Field7'],
#                    ', '.join([item[f'Field12'], item[f'Field13'], item[f'Field14'],
#                              item[f'Field15'], item[f'Field16']]), item['Field212'],
#                    opportunities, item['DateCreated'], item['CreatedBy'], item['DateUpdated'], item['UpdatedBy']))
#
#     # commit the changes to the database and close the connection
#     conn.commit()
#     conn.close()
#
#
# if __name__ == "__main__":
#     write_wufoo_data()

import sys
import requests
import sqlite3
from secrets import wufoo_key
from requests.auth import HTTPBasicAuth


def get_wufoo_data() -> dict:
    url = "https://jsproul.wufoo.com/api/v3/forms/cubes-project-proposal-submission/entries/json"
    response = requests.get(url, auth=HTTPBasicAuth(wufoo_key, 'pass'))

    if response.status_code != 200:
        print(f"Failed to get data, response code: {response.status_code} and error message: {response.reason}")
        sys.exit(-1)

    jsonresponse = response.json()
    return jsonresponse['Entries']


def write_wufoo_data():
    # create a database connection
    conn = sqlite3.connect('wufoo_data.db')
    c = conn.cursor()

    # create the table if it doesn't already exist
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (Entry_Id text,
                  Title text,
                  First_Name text,
                  Last_Name text,
                  Org_Title text,
                  Organization text,
                  Email text,
                  Org_Website text,
                  Phone_Number text,
                  Time_Period text,
                  Permission text,
                  Opportunities text,
                  Date_Created text,
                  Created_By text,
                  Date_Updated text,
                  Updated_By text)''')

    # retrieve the data from Wufoo
    data = get_wufoo_data()

    # insert the data into the table
    for item in data:
        opportunities = ', '.join([item.get('Field112', ''), item.get('Field113', ''), item.get('Field114', ''),
                                  item.get('Field115', ''), item.get('Field116', ''), item.get('Field117', ''),
                                  item.get('Field118', '')])

        c.execute("INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (item['EntryId'],
                   item.get('Field214', ''),
                   item.get('Field1', ''),
                   item.get('Field2', ''),
                   item.get('Field8', ''),
                   item.get('Field9', ''),
                   item.get('Field5', ''),
                   item.get('Field6', ''),
                   item.get('Field7', ''),
                   ', '.join([item.get('Field12', ''),
                              item.get('Field13', ''),
                              item.get('Field14', ''),
                              item.get('Field15', ''),
                              item.get('Field16', '')]),
                   item.get('Field212', ''),
                   opportunities,
                   item.get('DateCreated', ''),
                   item.get('CreatedBy', ''),
                   item.get('DateUpdated', ''), item.get('UpdatedBy', '')))

    # commit the changes to the database and close the connection
    conn.commit()
    conn.close()


if __name__ == "__main__":
    write_wufoo_data()
