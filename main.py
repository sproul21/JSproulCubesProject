#
# import sys
# import requests
# from secrets import wufoo_key
# from requests.auth import HTTPBasicAuth
#
#
# def get_wufoo_data() -> dict:
#     url = "https://jsproul.wufoo.com/api/v3/forms/cubes-project-proposal-submission/entries/json"
#     response = requests.get(url, auth=HTTPBasicAuth(wufoo_key, 'pass'))
#
#     if response.status_code != 200:  # if we don't get an ok response we have trouble
#         print(f"Failed to get data, response code:{response.status_code} and error message: {response.reason} ")
#         sys.exit(-1)
#     jsonresponse = response.json()
#     return jsonresponse  # json response will be either a dictionary or a list of dictionaries
#
#
# # each dictionary represents a json object
# def write_wufoo_data():
#     # JSON data
#     data = get_wufoo_data()['Entries']
#
#     # open a file for writing
#     with open("data.txt", "w") as outfile:
#         # write the JSON key-value pairs to the file
#         for item in data:
#             for key, value in item.items():
#                 outfile.write(f"{key}: {value}\n")
#
#     # print the file
#     print_file("data.txt")
#
#
# def print_file(file_name):
#     with open(file_name) as f:
#         print(f.read())
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
        print(f"Failed to get data, response code:{response.status_code} and error message: {response.reason} ")
        sys.exit(-1)
    jsonresponse = response.json()
    return jsonresponse['Entries']

def write_wufoo_data():
    # create a database connection
    conn = sqlite3.connect('wufoo_data.db')
    c = conn.cursor()

    # create the table if it doesn't already exist
    c.execute('''CREATE TABLE IF NOT EXISTS entries
                 (Entry_Id text, Title text, First_Name text, Last_Name text,
                 Org_Title text, Organization text, Email text, Org_Website text,
                 Phone_Number text, Time_Period text, Permission text,
                 Opportunities text, Date_Created text, Created_By text, 
                 Date_Updated text, Updated_By text)''')

    # retrieve the data from Wufoo
    data = get_wufoo_data()

    # insert the data into the table
    for item in data:
        opportunities = ', '.join([item[f'Field112'], item[f'Field113'], item[f'Field114'],
                                  item[f'Field115'], item[f'Field116'], item[f'Field117'],
                                  item[f'Field118']])

        c.execute("INSERT INTO entries VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                  (item['EntryId'], item['Field214'], item['Field1'], item['Field2'], item['Field8'],
                   item['Field9'], item['Field5'], item['Field6'], item['Field7'],
                   ', '.join([item[f'Field12'], item[f'Field13'], item[f'Field14'],
                             item[f'Field15'], item[f'Field16']]), item['Field212'],
                   opportunities, item['DateCreated'], item['CreatedBy'], item['DateUpdated'], item['UpdatedBy']))

    # commit the changes to the database and close the connection
    conn.commit()
    conn.close()

if __name__ == "__main__":
    write_wufoo_data()


