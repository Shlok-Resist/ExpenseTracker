import csv
import datetime
import os
import sqlite3
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox as mb
from tkinter import ttk
import matplotlib.pyplot as plt
import pandas as pd
from fpdf import FPDF
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkcalendar import DateEntry


# Custom date adapter for SQLite
def adapt_date(date):
    return date.strftime("%Y-%m-%d")


# Remove Time from DateTime
def convert_date(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d")


# Sqlite3 adapter
sqlite3.register_adapter(datetime.date, adapt_date)
sqlite3.register_converter("DATE", convert_date)


# Function to list all the expenses
def listAllExpenses():
    global dbconnector, data_table
    data_table.delete(*data_table.get_children())
    all_data = dbconnector.execute('SELECT * FROM ExpenseTracker')
    data = all_data.fetchall()
    for val in data:
        data_table.insert('', END, values=val)


# Function to view an expense information
def viewExpenseInfo():
    global data_table
    global dateField, payee, description, amount, modeOfPayment
    if not data_table.selection():
        mb.showerror('No expense selected', 'Please select an expense from the table to view its details')
        return
    currentSelectedExpense = data_table.item(data_table.focus())
    val = currentSelectedExpense['values']
    expenditureDate = datetime.date(int(val[1][:4]), int(val[1][5:7]), int(val[1][8:]))
    dateField.set_date(expenditureDate)
    payee.set(val[2])
    description.set(val[3])
    amount.set(val[4])
    modeOfPayment.set(val[5])


# Function to clear the entries from the entry fields
def clearFields():
    global description, payee, amount, modeOfPayment, dateField, data_table
    todayDate = datetime.datetime.now().date()
    description.set('')
    payee.set('')
    amount.set(0.0)
    modeOfPayment.set('Cash')
    dateField.set_date(todayDate)
    data_table.selection_remove(*data_table.selection())


# Function to delete the selected record
def removeExpense():
    if not data_table.selection():
        mb.showerror('No record selected!', 'Please select a record to delete!')
        return
    currentSelectedExpense = data_table.item(data_table.focus())
    valuesSelected = currentSelectedExpense['values']
    confirmation = mb.askyesno('Are you sure?',
                               f'Are you sure that you want to delete the record of {valuesSelected[2]}')
    if confirmation:
        dbconnector.execute('DELETE FROM ExpenseTracker WHERE ID=%d' % valuesSelected[0])
        dbconnector.commit()
        listAllExpenses()
        mb.showinfo('Record deleted successfully!', 'The record you wanted to delete has been deleted successfully')


# Function to delete all the entries
def removeAllExpenses():
    confirmation = mb.askyesno('Are you sure?',
                               'Are you sure that you want to delete all the expense items from the database?',
                               icon='warning')
    if confirmation:
        data_table.delete(*data_table.get_children())
        dbconnector.execute('DELETE FROM ExpenseTracker')
        dbconnector.commit()
        clearFields()
        listAllExpenses()
        mb.showinfo('All Expenses deleted', 'All the expenses were successfully deleted')
    else:
        mb.showinfo('Ok then', 'The task was aborted and no expense was deleted!')


# Function to add another expense
def addAnotherExpense():
    global dateField, payee, description, amount, modeOfPayment, dbconnector
    if not dateField.get() or not payee.get() or not description.get() or not amount.get() or not modeOfPayment.get():
        mb.showerror('Fields empty!', "Please fill all the missing fields before pressing the add button!")
        return
    try:
        float(amount.get())
    except ValueError:
        mb.showerror('Invalid Amount', 'Please enter a valid amount')
        return
    if float(amount.get()) <= 0:
        mb.showerror('Invalid Amount', 'Please enter a positive amount')
        return
    dbconnector.execute(
        'INSERT INTO ExpenseTracker (Date, Payee, Description, Amount, ModeOfPayment) VALUES (?, ?, ?, ?, ?)',
        (dateField.get_date(), payee.get(), description.get(), amount.get(), modeOfPayment.get())
    )
    dbconnector.commit()
    clearFields()
    listAllExpenses()
    mb.showinfo('Expense added', 'The expense whose details you just entered has been added to the database')


# function to edit the details of an expense
def editExpense():
    def editExistingExpense():
        global dateField, amount, description, payee, modeOfPayment
        global dbconnector, data_table
        currentSelectedExpense = data_table.item(data_table.focus())
        content = currentSelectedExpense['values']
        dbconnector.execute(
            'UPDATE ExpenseTracker SET Date = ?, Payee = ?, Description = ?, Amount = ?, ModeOfPayment = ? WHERE ID = ?',
            (dateField.get_date(), payee.get(), description.get(), amount.get(), modeOfPayment.get(), content[0])
        )
        dbconnector.commit()
        clearFields()
        listAllExpenses()
        mb.showinfo('Data edited', 'We have updated the data and stored in the database as you wanted')
        editSelectedButton.destroy()

    if not data_table.selection():
        mb.showerror('No expense selected!',
                     'You have not selected any expense in the table for us to edit; please do that!')
        return
    viewExpenseInfo()
    editSelectedButton = Button(
        frameL3,
        text="Edit Expense",
        font=("Bahnschrift Condensed", "13"),
        width=30,
        bg="#90EE90",
        fg="#000000",
        relief=GROOVE,
        activebackground="#008000",
        activeforeground="#FF0000",
        command=editExistingExpense
    )
    editSelectedButton.grid(row=0, column=0, sticky=W, padx=50, pady=10)


# function to display the details of selected expense into words
def selectedExpenseToWords():
    global data_table
    if not data_table.selection():
        mb.showerror('No expense selected!', 'Please select an expense from the table for us to read')
        return
    currentSelectedExpense = data_table.item(data_table.focus())
    val = currentSelectedExpense['values']
    msg = f'Your expense can be read like: \n"You paid {val[4]} to {val[2]} for {val[3]} on {val[1]} via {val[5]}"'
    mb.showinfo('Here\'s how to read your expense', msg)


# function to display the expense details into words before adding it to the table
def expenseToWordsBeforeAdding():
    global dateField, description, amount, payee, modeOfPayment

    msg = (f'Your expense can be read like: \n"You paid {amount.get()} to {payee.get()} '
           f'for {description.get()} on '
           f'{dateField.get()} via {modeOfPayment.get()}"')
    mb.showinfo('Here\'s how to read your expense', msg)


# Export Expense
def exportExpenses():
    global dbconnector
    all_data = dbconnector.execute('SELECT * FROM ExpenseTracker')
    data = all_data.fetchall()

    # Excel
    def export_to_excel():
        df = pd.DataFrame(data, columns=['ID', 'Date', 'Payee', 'Description', 'Amount', 'ModeOfPayment'])
        file_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[('Excel files', '*.xlsx')])
        if file_path:
            df.to_excel(file_path, index=False)
            mb.showinfo('Exported to Excel', f'The expense data has been exported to {file_path}')

    # CSV
    def export_to_csv():
        file_path = filedialog.asksaveasfilename(defaultextension='.csv', filetypes=[('CSV files', '*.csv')])
        if file_path:
            with open(file_path, mode='w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['ID', 'Date', 'Payee', 'Description', 'Amount', 'ModeOfPayment'])
                writer.writerows(data)
            mb.showinfo('Exported to CSV', f'The expense data has been exported to {file_path}')

    # PDF
    def export_to_pdf():
        pdf = FPDF(orientation='L')  # Set orientation to Landscape
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(200, 10, 'Expense Tracker', 0, 1, 'C')
        pdf.cell(200, 10, '', 0, 1)  # Add empty line
        for row in data:
            pdf.cell(40, 10, str(row[0]), 1)
            pdf.cell(30, 10, row[1], 1)
            pdf.cell(50, 10, row[2], 1)
            pdf.cell(50, 10, row[3], 1)
            pdf.cell(30, 10, str(row[4]), 1)
            pdf.cell(40, 10, row[5], 1)
            pdf.cell(200, 10, '', 0, 1)  # Add empty line
        file_path = filedialog.asksaveasfilename(defaultextension='.pdf', filetypes=[('PDF files', '*.pdf')])
        if file_path:
            pdf.output(file_path)
            mb.showinfo('Exported to PDF', f'The expense data has been exported to {file_path}')

    export_dialog = Toplevel()
    export_dialog.title("Export Format")
    export_dialog.geometry("300x150")
    Button(export_dialog, text="Export to Excel", command=export_to_excel).pack(pady=5)
    Button(export_dialog, text="Export to CSV", command=export_to_csv).pack(pady=5)
    Button(export_dialog, text="Export to PDF", command=export_to_pdf).pack(pady=5)

    # Function to destroy the export dialog when closed
    def on_closing():
        export_dialog.destroy()

    export_dialog.protocol("WM_DELETE_WINDOW", on_closing)


# -----------------------
# Graph Function
# -----------------------


# Function to save the graph as an image
def displayGraph():
    global dbconnector
    all_data = dbconnector.execute('SELECT * FROM ExpenseTracker')
    data = all_data.fetchall()

    # Create a new window for the graph
    graphWindow = Toplevel()
    graphWindow.title("Amount Spent Graph")

    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(10, 6))

    # Choose the type of graph based on the selected option
    if graphOption.get() == "Total Amount Spent per Mode of Payment":
        modeOfPayment_amount = {}
        for row in data:
            if row[5] not in modeOfPayment_amount:
                modeOfPayment_amount[row[5]] = 0
            modeOfPayment_amount[row[5]] += row[4]
        labels = modeOfPayment_amount.keys()
        values = modeOfPayment_amount.values()
        ax.bar(labels, values, color='skyblue')
        ax.set_xlabel('Mode of Payment')
        ax.set_ylabel('Total Amount Spent')

    elif graphOption.get() == "Total Amount Spent per Payee":
        payee_amount = {}
        for row in data:
            if row[2] not in payee_amount:
                payee_amount[row[2]] = 0
            payee_amount[row[2]] += row[4]
        labels = payee_amount.keys()
        values = payee_amount.values()
        ax.bar(labels, values, color='lightgreen')
        ax.set_xlabel('Payee')
        ax.set_ylabel('Total Amount Spent')

    elif graphOption.get() == "Total Amount Spent per Month":
        month_amount = {}
        for row in data:
            month = row[1].split('-')[1]
            if month not in month_amount:
                month_amount[month] = 0
            month_amount[month] += row[4]
        labels = month_amount.keys()
        values = month_amount.values()
        ax.bar(labels, values, color='salmon')
        ax.set_xlabel('Month')
        ax.set_ylabel('Total Amount Spent')

    ax.set_title('Amount Spent Graph')
    plt.xticks(rotation=45)
    plt.tight_layout()

    # Display the graph in the new window
    canvas = FigureCanvasTkAgg(fig, master=graphWindow)
    canvas.draw()
    canvas.get_tk_widget().pack()

    # Add a 'Save Graph' button
    Button(graphWindow, text="Save Graph", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90",
           fg="#000000", relief=GROOVE, activebackground="#008000", activeforeground="#FF0000",
           command=lambda: saveGraph(fig)).pack(pady=10)


# Graph Saving
def saveGraph(fig):
    file_path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG files', '*.png')])
    if file_path:
        fig.savefig(file_path)
        mb.showinfo('Graph Saved', f'The graph has been saved to {file_path}')


# function to search expenses
def searchExpenses():
    keyword = searchEntry.get()
    query = ("SELECT * FROM ExpenseTracker WHERE Date LIKE ? OR Payee LIKE ? OR Description LIKE ? OR Amount LIKE ? OR "
             "ModeOfPayment LIKE ?")
    data = dbconnector.execute(query, (
        '%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%', '%' + keyword + '%'))
    data_table.delete(*data_table.get_children())
    for val in data:
        data_table.insert('', END, values=val)


# function to clear all the entries
def clearFields():
    global description, payee, amount, modeOfPayment, dateField, data_table
    todayDate = datetime.datetime.now().date()
    description.set('')
    payee.set('')
    amount.set(0.0)
    modeOfPayment.set('Cash')
    dateField.set_date(todayDate)
    data_table.selection_remove(*data_table.selection())


# Main Window
mainWindow = Tk()
mainWindow.geometry("1920x1080")
mainWindow.title("Expense Tracker")

# Styling
style = ttk.Style()
style.configure('TButton', font=('Bahnschrift Condensed', 13), background='#90EE90', foreground='#000000',
                relief=GROOVE, padding=5)
style.configure('TLabel', font=('Bahnschrift Condensed', 15))
style.configure('Treeview.Heading', font=('Bahnschrift Condensed', 15))

# Title
titleLabel = Label(mainWindow, text="Expense Tracker", font=("Bahnschrift Condensed", 20))
titleLabel.pack(pady=10)

# add a search bar to GUI
searchFrame = Frame(mainWindow)
searchFrame.pack()

searchLabel = Label(searchFrame, text="Search Expense:", font=("Bahnschrift Condensed", "13"))
searchLabel.pack(side=LEFT, padx=10, pady=10)

searchEntry = Entry(searchFrame, font=("Bahnschrift Condensed", "13"))
searchEntry.pack(side=LEFT, padx=10, pady=10)

searchButton = Button(searchFrame, text="Search", font=("Bahnschrift Condensed", "13"), width=10, bg="#90EE90",
                      fg="#000000", relief=GROOVE, activebackground="#008000", activeforeground="#FF0000",
                      command=searchExpenses)
searchButton.pack(side=LEFT, padx=10, pady=10)

# Main Frame
mainFrame = Frame(mainWindow)
mainFrame.pack(fill=BOTH, expand=True)

# Get the root directory of the project
root_dir = os.path.dirname(os.path.abspath(__file__))

# Define the path for the database file in the root directory
db_path = os.path.join(root_dir, 'ExpenseTracker.db')

# Database connection
dbconnector = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
dbconnector.execute('''CREATE TABLE IF NOT EXISTS ExpenseTracker (
                       ID INTEGER PRIMARY KEY AUTOINCREMENT,
                       Date TEXT NOT NULL,
                       Payee TEXT NOT NULL,
                       Description TEXT NOT NULL,
                       Amount REAL NOT NULL,
                       ModeOfPayment TEXT NOT NULL
                   )''')
dbconnector.commit()

# Creating a treeview to display expenses
data_table = ttk.Treeview(mainFrame, columns=('ID', 'Date', 'Payee', 'Description', 'Amount', 'ModeOfPayment'),
                          show='headings')
for col in ('ID', 'Date', 'Payee', 'Description', 'Amount', 'ModeOfPayment'):
    data_table.heading(col, text=col)
data_table.pack(fill=BOTH, expand=True)

# frame for adding an expense
frameL1 = Frame(mainWindow, padx=10, pady=10)
frameL1.pack(side=LEFT, anchor=NW)

Label(frameL1, text="Date:", font=("Bahnschrift Condensed", "15")).grid(row=1, column=0, sticky=W, padx=50, pady=10)
dateField = DateEntry(frameL1, width=20, background='darkblue', foreground='white', borderwidth=2)
dateField.grid(row=1, column=1, sticky=W, padx=10, pady=10)

Label(frameL1, text="Payee:", font=("Bahnschrift Condensed", "15")).grid(row=2, column=0, sticky=W, padx=50, pady=10)
payee = StringVar()
Entry(frameL1, textvariable=payee, font=("Bahnschrift Condensed", "15")).grid(row=2, column=1, sticky=W, padx=10,
                                                                              pady=10)

Label(frameL1, text="Description:", font=("Bahnschrift Condensed", "15")).grid(row=3, column=0, sticky=W, padx=50,
                                                                               pady=10)
description = StringVar()
Entry(frameL1, textvariable=description, font=("Bahnschrift Condensed", "15")).grid(row=3, column=1, sticky=W, padx=10,
                                                                                    pady=10)

Label(frameL1, text="Amount:", font=("Bahnschrift Condensed", "15")).grid(row=4, column=0, sticky=W, padx=50, pady=10)
amount = DoubleVar()
Entry(frameL1, textvariable=amount, font=("Bahnschrift Condensed", "15")).grid(row=4, column=1, sticky=W, padx=10,
                                                                               pady=10)

Label(frameL1, text="Mode of Payment:", font=("Bahnschrift Condensed", "15")).grid(row=5, column=0, sticky=W, padx=50,
                                                                                   pady=10)
modeOfPayment = StringVar()
paymentOptions = ['Cash', 'Credit Card', 'Debit Card', 'Net Banking', 'UPI', 'Others']
modeOfPayment.set('Cash')
# Create the OptionMenu
option_menu = OptionMenu(frameL1, modeOfPayment, *paymentOptions)
option_menu.grid(row=5, column=1, sticky=W, padx=10, pady=10)

# Set the width of the entry widget inside the OptionMenu
option_menu.config(width=18)

# Add a 'Clear Fields' button
Button(frameL1, text="Clear Fields", font=("Bahnschrift Condensed", "13"), width=20, bg="#90EE90", fg="#000000",
       relief=GROOVE, activebackground="#008000", activeforeground="#FF0000", command=clearFields).grid(row=6,
                                                                                                        column=0,
                                                                                                        sticky=W,
                                                                                                        padx=50,
                                                                                                        pady=10)

Button(frameL1, text="Add", font=("Bahnschrift Condensed", "13"), width=20, bg="#90EE90", fg="#000000", relief=GROOVE,
       activebackground="#008000", activeforeground="#FF0000", command=addAnotherExpense).grid(row=6, column=1,
                                                                                               sticky=W, padx=10,
                                                                                               pady=10)
# frame for listing all the expenses
frameL2 = Frame(mainWindow, padx=10, pady=10)
frameL2.pack(side=LEFT, anchor=NW)

listAllExpenses()

# move buttons to frameL2

Button(frameL2, text="View Expense Info", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000",
       relief=GROOVE, activebackground="#008000", activeforeground="#FF0000", command=viewExpenseInfo).grid(row=1,
                                                                                                            column=0,
                                                                                                            sticky=W,
                                                                                                            padx=50,
                                                                                                            pady=10)

Button(frameL2, text="Edit Expense", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000",
       relief=GROOVE, activebackground="#008000", activeforeground="#FF0000", command=editExpense).grid(row=2,
                                                                                                        column=0,
                                                                                                        sticky=W,
                                                                                                        padx=50,
                                                                                                        pady=10)

Button(frameL2, text="Delete Expense", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000",
       relief=GROOVE, activebackground="#008000", activeforeground="#FF0000", command=removeExpense).grid(row=3,
                                                                                                          column=0,
                                                                                                          sticky=W,
                                                                                                          padx=50,
                                                                                                          pady=10)

Button(frameL2, text="Delete All Expenses", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000",
       relief=GROOVE, activebackground="#008000", activeforeground="#FF0000", command=removeAllExpenses).grid(row=4,
                                                                                                              column=0,
                                                                                                              sticky=W,
                                                                                                              padx=50,
                                                                                                              pady=10)

Button(frameL2, text="Read Selected Expense", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90",
       fg="#000000", relief=GROOVE, activebackground="#008000", activeforeground="#FF0000",
       command=selectedExpenseToWords).grid(row=5, column=0, sticky=W, padx=50, pady=10)

Button(frameL2, text="Read Expense before Adding", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90",
       fg="#000000", relief=GROOVE, activebackground="#008000", activeforeground="#FF0000",
       command=expenseToWordsBeforeAdding).grid(row=6, column=0, sticky=W, padx=50, pady=10)

# frame for buttons
frameL3 = Frame(mainWindow, padx=10, pady=10)
frameL3.pack(side=LEFT, anchor=NW)

Button(frameL3, text="Export Expenses", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000",
       relief=GROOVE, activebackground="#008000", activeforeground="#FF0000", command=exportExpenses).grid(row=1,
                                                                                                           column=0,
                                                                                                           sticky=W,
                                                                                                           padx=50,
                                                                                                           pady=10)

# --------------------------------
# GRAPH
# --------------------------------

# Create a button to view the graph
# Add a 'View Graph' button
Button(frameL3, text="View Graph", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000",
       relief=GROOVE, activebackground="#008000", activeforeground="#FF0000", command=displayGraph).grid(row=3,
                                                                                                         column=0,
                                                                                                         sticky=W,
                                                                                                         padx=50,
                                                                                                         pady=10)

# Add a drop-down menu to choose the graph option
graphOption = StringVar()
graphOption.set("Total Amount Spent per Mode of Payment")
# Create the OptionMenu
graph_option_menu = OptionMenu(frameL3, graphOption,
                               "Total Amount Spent per Mode of Payment",
                               "Total Amount Spent per Payee",
                               "Total Amount Spent per Month")
graph_option_menu.grid(row=2, column=0, sticky=W, padx=50, pady=10)

# Set the width of the entry widget inside the OptionMenu
graph_option_menu.config(width=29)

Button(frameL3, text="Exit", font=("Bahnschrift Condensed", "13"), width=30, bg="#90EE90", fg="#000000", relief=GROOVE,
       activebackground="#008000", activeforeground="#FF0000", command=mainWindow.quit).grid(row=4,
                                                                                             column=0,
                                                                                             sticky=W,
                                                                                             padx=50,
                                                                                             pady=10)

# to start the GUI
mainWindow.mainloop()
