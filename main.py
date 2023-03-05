import sys
import requests
import sqlite3
from secrets import wufoo_key
from requests.auth import HTTPBasicAuth
import tkinter as tk
from typing import Tuple


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

        # check if entry already exists in table
        c.execute("SELECT Entry_Id FROM entries WHERE Entry_Id = ?", (item['EntryId'],))
        result = c.fetchone()
        if result is not None:
            continue  # entry already exists, skip insertion

        # insert the entry into the table
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

        # create a frame for the buttons
        self.button_frame = tk.Frame(self.master)
        self.button_frame.pack()

        # create the View Data button
        self.view_button = tk.Button(self.button_frame, text="View Data", command=self.load_data)
        self.view_button.pack(side=tk.LEFT)

        # create the Update Data button
        self.update_button = tk.Button(self.button_frame, text="Update Data", command=self.update_data)
        self.update_button.pack(side=tk.LEFT)

        self.new_user_button = tk.Button(self.button_frame, text="New User", command=self.new_user)
        self.new_user_button.pack(side=tk.LEFT)

        self.paned_window = tk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=1)

        self.listbox = tk.Listbox(self.paned_window)
        self.listbox.bind('<<ListboxSelect>>', lambda event=None: self.show_entry(event))
        self.paned_window.add(self.listbox)

        self.entry_frame = tk.Frame(self.paned_window)
        self.paned_window.add(self.entry_frame)


        # create labels in the entry frame
        self.labels = []
        fields = ["Title", "First Name", "Last Name", "Organization Title", "Organization", "Email",
                  "Organization Website",
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



    def load_data(self):
        # connect to the database and retrieve the data
        conn = sqlite3.connect('wufoo_data.db')
        c = conn.cursor()
        c.execute("SELECT Entry_Id, Title, First_Name, Last_Name, Email FROM entries")
        data = c.fetchall()
        conn.close()

        # clear the listbox and value labels
        self.listbox.delete(0, tk.END)
        for value_label in self.value_labels:
            value_label.config(text="")

        # add the data to the listbox
        for item in data:
            entry = f"{item[1]} {item[2]} {item[3]}"
            self.listbox.insert("end", entry)
            self.listbox.itemconfig("end", fg="blue")

    def show_entry(self, event=None):
        # update the labels
        if event is not None and self.listbox.curselection():
            index = self.listbox.curselection()[0]
            entry = self.listbox.get(index)

            # connect to the database and retrieve the entry
            conn = sqlite3.connect('wufoo_data.db')
            c = conn.cursor()
            c.execute("SELECT * FROM entries WHERE Title || ' ' || First_Name || ' ' || Last_Name = ?", (entry,))
            data = c.fetchone()
            conn.close()

            if data is not None:
                for i, value_label in enumerate(self.value_labels):
                    value_label.config(text=data[i + 1])

    def check_email(self, email_entry):
        email = email_entry.get()

        # check if the email address is already in the database and autofill the rest of the information
        conn = sqlite3.connect('wufoo_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM entries WHERE Email = ?", (email,))
        data = c.fetchone()
        conn.close()

        if data is not None:
            # autofill the rest of the information
            fields = ["Title", "First Name", "Last Name", "Organization Title", "Organization",
                      "Organization Website", "Phone Number", "Time Period", "Permission", "Opportunities"]
            for i, field in enumerate(fields):
                entry_value = tk.StringVar(value=data[i + 2])
                app.new_user_entries[i].config(textvariable=entry_value)

    def new_user(self):
        # create a new window for adding a new user
        new_user_window = tk.Toplevel(self.master)
        new_user_window.title("New User")

        # create a label and entry widget for the email address
        email_label = tk.Label(new_user_window, text="Email")
        email_label.grid(row=0, column=0, sticky="e")

        email_entry_value = tk.StringVar()
        email_entry = tk.Entry(new_user_window, textvariable=email_entry_value)
        email_entry.grid(row=0, column=1, sticky="w")
        email_entry.bind("<KeyRelease>", lambda event: self.check_email(email_entry))


        # create labels and entry widgets for each input
        fields = ["Title", "First Name", "Last Name", "Organization Title", "Organization", "Organization Website",
                  "Phone Number", "Time Period", "Permission", "Opportunities"]
        self.new_user_entries = []
        for i, field in enumerate(fields):
            label = tk.Label(new_user_window, text=field)
            label.grid(row=i + 1, column=0, sticky="e")

            entry_value = tk.StringVar()
            entry = tk.Entry(new_user_window, textvariable=entry_value)
            entry.grid(row=i + 1, column=1, sticky="w")

            self.new_user_entries.append(entry)

        def save_user():
            # get the new user data and insert it into the database
            email = email_entry.get().strip()
            title = self.new_user_entries[0].get().strip()
            first_name = self.new_user_entries[1].get().strip()
            last_name = self.new_user_entries[2].get().strip()
            org_title = self.new_user_entries[3].get().strip()
            organization = self.new_user_entries[4].get().strip()
            org_website = self.new_user_entries[5].get().strip()
            phone_number = self.new_user_entries[6].get().strip()
            time_period = self.new_user_entries[7].get().strip()
            permission = self.new_user_entries[8].get().strip()
            opportunities = self.new_user_entries[9].get().strip()

            full_name = f"{title} {first_name} {last_name}"

            conn = sqlite3.connect('wufoo_data.db')
            c = conn.cursor()

            # check if the email address is already in the database
            c.execute("SELECT * FROM entries WHERE Email = ?", (email,))
            result = c.fetchone()

            # if email already exists, update the existing entry
            if result is not None:
                c.execute(
                    "UPDATE entries SET Title = ?, First_Name = ?, Last_Name = ?, Org_Title = ?, Organization = ?, "
                    "Org_Website = ?, Phone_Number = ?, Time_Period = ?, Permission = ?, Opportunities = ? "
                    "WHERE Email = ?",
                    (title, first_name, last_name, org_title, organization, org_website, phone_number, time_period,
                     permission, opportunities, email))
            # otherwise, insert the new entry
            else:
                c.execute("INSERT INTO entries (Title, First_Name, Last_Name, Org_Title, Organization, Email, "
                          "Org_Website, Phone_Number, Time_Period, Permission, Opportunities) "
                          "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                          (title, first_name, last_name, org_title, organization, email, org_website,
                           phone_number, time_period, permission, opportunities))

            # commit the changes to the database and close the connection
            conn.commit()
            conn.close()

            new_user_window.destroy()

            # load the updated data
            app.load_data()

        save_button = tk.Button(new_user_window, text="Save", command=save_user)
        save_button.grid(row=len(fields) + 1, column=0, columnspan=2)

    def update_data(self):
        # check if an entry is selected
        if not self.listbox.curselection():
            return

        # get the selected entry
        index = self.listbox.curselection()[0]
        entry = self.listbox.get(index)

        # connect to the database and retrieve the entry
        conn = sqlite3.connect('wufoo_data.db')
        c = conn.cursor()
        c.execute("SELECT * FROM entries WHERE Title || ' ' || First_Name || ' ' || Last_Name = ?", (entry,))
        data = c.fetchone()
        conn.close()

        # check if data is None before trying to access its values
        if data is None:
            return

        # create a new window for modifying the entry
        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Entry")

        # create labels and entry widgets for each input
        fields = ["Title", "First Name", "Last Name", "Organization Title", "Organization", "Email",
                  "Organization Website", "Phone Number", "Time Period", "Permission", "Opportunities",
                  "Date Created", "Created By", "Date Updated", "Updated By"]
        entries = []
        for i, field in enumerate(fields):
            label = tk.Label(edit_window, text=field)
            label.grid(row=i, column=0, sticky="e")

            entry_value = tk.StringVar()
            entry_value.set(data[i + 1])
            entry = tk.Entry(edit_window, textvariable=entry_value)
            entry.grid(row=i, column=1, sticky="w")

            entries.append(entry)

        def save_entry():
            new_data = [entry.get() for entry in entries]
            new_data.append(data[0])  # add the Entry_Id to the end of the list

            conn = sqlite3.connect('wufoo_data.db')
            c = conn.cursor()
            c.execute("UPDATE entries SET Title = ?, First_Name = ?, Last_Name = ?, Org_Title = ?, "
                      "Organization = ?, Email = ?, Org_Website = ?, Phone_Number = ?, Time_Period = ?, "
                      "Permission = ?, Opportunities = ?, Date_Created = ?, Created_By = ?, Date_Updated = ?, "
                      "Updated_By = ? WHERE Entry_Id = ?",
                      tuple(new_data))
            conn.commit()
            conn.close()

            edit_window.destroy()

            # load the updated data
            self.load_data()

        def delete_entry():
            conn = sqlite3.connect('wufoo_data.db')
            c = conn.cursor()
            c.execute("DELETE FROM entries WHERE Entry_Id = ?", (data[0],))
            conn.commit()
            conn.close()

            edit_window.destroy()

            # load the updated data
            self.load_data()

        save_button = tk.Button(edit_window, text="Save", command=save_entry)
        save_button.grid(row=len(fields), column=0, columnspan=2)

        delete_button = tk.Button(edit_window, text="Delete", command=delete_entry)
        delete_button.grid(row=len(fields) + 1, column=0, columnspan=2)

        # show the selected entry
        self.show_entry()


if __name__ == "__main__":
        write_wufoo_data()
        root = tk.Tk()
        app = Application(master=root)
        app.mainloop()