# Expense Tracker Application

## Introduction

Managing personal finances is crucial for maintaining a balanced budget and achieving financial goals. The Expense Tracker application serves as a tool to help individuals keep track of their expenses efficiently. It offers a user-friendly interface to record, view, edit, and analyze expenses, providing insights into spending patterns and aiding in financial planning.

The Expense Tracker application is a GUI-based program built using Python. It allows users to keep track of their expenses by recording details such as date, payee, description, amount, and mode of payment. Users can perform various operations like adding new expenses, editing existing ones, deleting expenses, searching for specific expenses, exporting data to different formats (Excel, CSV, PDF), and visualizing expense data through graphs.

## Features

1. **Add Expense**: Users can add new expenses by entering details like date, payee, description, amount, and mode of payment.
2. **Edit Expense**: Edit existing expenses to update details such as date, payee, description, amount, and mode of payment.
3. **Delete Expense**: Delete individual expenses from the database.
4. **Delete All Expenses**: Delete all expenses from the database at once.
5. **Search Expenses**: Search for specific expenses using keywords.
6. **Export Expenses**: Export expense data to different formats like Excel, CSV, and PDF.
7. **View Graph**: Visualize expense data through various types of graphs such as total amount spent per mode of payment, per payee, or per month.
8. **Read Expense Details**: Read selected expense details in words before adding or after selection.
9. **Date Picker**: Use a date picker widget to select dates conveniently.
10. **Responsive UI**: The GUI is designed using Tkinter, providing an intuitive and user-friendly interface.

## Technology Used

1. **Python**: The application is developed using the Python programming language, known for its simplicity and versatility.
2. **Tkinter**: Tkinter is used for creating the graphical user interface (GUI) of the application. It provides a set of tools and widgets for building desktop applications in Python.
3. **SQLite**: SQLite is used as the database management system for storing and managing expense data. It is lightweight, easy to set up, and perfect for small-scale applications.
4. **Pandas**: Pandas is a Python library used for data manipulation and analysis. It is utilized here for exporting expense data to Excel format.
5. **Matplotlib**: Matplotlib is a plotting library for Python used to create visualizations such as bar charts for graphical analysis of expense data.
6. **FPDF**: FPDF is a Python library for generating PDF documents. It is employed here to export expense data to PDF format.
7. **tkcalendar**: tkcalendar is a Python library used for creating date entry widgets with a calendar pop-up. It enhances the user experience when entering dates for expenses.
8. **PIL (Python Imaging Library)**: PIL is used for saving the generated graphs as image files (PNG format) for later reference.

## Installation

To run the Expense Tracker application, you need to install the following Python packages:

```bash
pip install tkinter
pip install pandas
pip install matplotlib
pip install fpdf
pip install tkcalendar
pip install pillow
```

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Screenshots

<img width="436" alt="image" src="https://github.com/Shlok-Resist/expenseTracker/assets/60575417/6c4f21f9-0afd-4687-93ee-d57950959a37">
<img width="435" alt="image" src="https://github.com/Shlok-Resist/expenseTracker/assets/60575417/b9dc31bd-e48f-47c6-84e0-5813c7a2b02b">
<img width="427" alt="image" src="https://github.com/Shlok-Resist/expenseTracker/assets/60575417/ec175511-37fa-46c3-955b-70c0b999ed5c">
<img width="423" alt="image" src="https://github.com/Shlok-Resist/expenseTracker/assets/60575417/e0366c38-61e6-48fa-a36f-dc53e3616d64">




## Conclusion

The Expense Tracker application provides a convenient way for users to manage their expenses effectively. With its intuitive interface and comprehensive features, users can easily track, analyze, and visualize their spending habits, thereby helping them make informed financial decisions.

---

Feel free to contribute, raise issues, or fork the repository to make your own enhancements. Your feedback is highly appreciated!

---

### How to Contribute

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Make your changes.
4. Commit your changes (`git commit -m 'Add some feature'`).
5. Push to the branch (`git push origin feature-branch`).
6. Open a Pull Request.

Happy Coding!
