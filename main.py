import sys
import requests
import sqlite3
from secrets import wufoo_key
from requests.auth import HTTPBasicAuth
import tkinter as tk


def get_wufoo_data() -> dict:  # comment to test workflow
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

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Wufoo Data Viewer")
        self.create_widgets()

    def create_widgets(self):
        # create a PanedWindow with two panes
        self.paned_window = tk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        # create a listbox in the first pane
        self.listbox = tk.Listbox(self.paned_window)
        self.listbox.bind('<<ListboxSelect>>', self.show_entry)
        self.paned_window.add(self.listbox)

        # create a frame in the second pane
        self.entry_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.entry_frame)

        # create labels in the entry frame
        self.labels = []
        fields = ["Title", "First Name", "Last Name", "Organization Title", "Organization", "Email", "Organization Website",
                  "Phone Number", "Time Period", "Permission", "Opportunities", "Date Created", "Created By",
                  "Date Updated", "Updated By"]
        for i, field in enumerate(fields):
            label = tk.Label(self.entry_frame, text=field)
            label.grid(row=i, column=0, sticky="e")
            self.labels.append(label)

        # create labels for the values in the entry frame
        self.value_labels = []
        for i in range(len(fields)):
            value_label = tk.Label(self.entry_frame, text="")
            value_label.grid(row=i, column=1, sticky="w")
            self.value_labels.append(value_label)

        # create a scrollbar
        self.scrollbar = tk.Scrollbar(self.master)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # configure the listbox and scrollbar
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        # load the data
        self.load_data()

    def load_data(self):
        # connect to the database and retrieve the data
        conn = sqlite3.connect('wufoo_data.db')
        c = conn.cursor()
        c.execute("SELECT Entry_Id, Title, First_Name, Last_Name, Email FROM entries")
        data = c.fetchall()
        conn.close()

        # add the data to the listbox
        for item in data:
            entry = f"{item[1]} {item[2]} {item[3]}"
            self.listbox.insert("end", entry)
            self.listbox.itemconfig("end", fg="blue")

    def show_entry(self, event):
        # get the selected item from the listbox
        index = self.listbox.curselection()[0]
        entry = self.listbox.get(index)

        # connect to the database and retrieve the full entry
        conn = sqlite3.connect('wufoo_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM entries WHERE Title || ' ' || First_Name || ' ' || Last_Name = ?", (entry,))
        data = c.fetchone()
        conn.close()

        # update the labels in the entry frame
        for i, value_label in enumerate(self.value_labels):
            value_label.config(text=data[i+1])

root = tk.Tk()
app = Application(master=root)
app.mainloop()

if __name__ == "__main__":
    write_wufoo_data()
