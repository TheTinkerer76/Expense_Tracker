# Import necessary libraries and modules:
import tkinter as tk # The main module for creating graphical user interfaces (GUIs).
from tkinter import ttk, messagebox # ttk provides themed widgets for a more native look and feel; messagebox is used for showing standard dialog boxes (like errors or info).
import matplotlib.pyplot as plt # A comprehensive library for creating static, interactive, and animated visualizations in Python.
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg # This backend allows embedding matplotlib plots within Tkinter applications.
from datetime import datetime # Used to work with dates and times, specifically for stamping expenses with the current date.
import json # Provides functions for working with JSON data, used here for saving and loading expense data to/from a file.
import os # Provides a way of using operating system dependent functionality, used here to check if the expenses data file exists.

# This class manages the core logic of storing, retrieving, and calculating expenses.
class ExpenseManager:
    # The constructor initializes the ExpenseManager.
    def __init__(self):
        self.expenses = [] # A list to hold dictionaries, where each dictionary represents a single expense.
        # Define the standard categories available for classifying expenses.
        self.categories = ["Food", "Transportation", "Entertainment", "Bills", "Shopping", "Other"]
        self.load_expenses() # Attempt to load any previously saved expenses when the manager is created.

    # This method adds a new expense to the list of expenses.
    # It validates the input and handles saving the updated list.
    def add_expense(self, amount, category, description, date):
        try:
            # Convert the amount input to a floating-point number.
            amount = float(amount)
            # Check if the amount is a positive value.
            if amount <= 0:
                # If not positive, raise a ValueError with a descriptive message.
                raise ValueError("Amount must be positive")

            # Create a dictionary to represent the new expense with its details.
            expense = {
                "amount": amount,
                "category": category,
                "description": description,
                "date": date
            }
            self.expenses.append(expense) # Add the newly created expense dictionary to the expenses list.
            self.save_expenses() # Call the method to save the current list of expenses to persistent storage.
            return True # Return True to indicate that the expense was successfully added.
        except ValueError as e:
            # If a ValueError occurs during the process (e.g., invalid amount), show an error message box.
            messagebox.showerror("Error", str(e))
            return False # Return False to indicate that adding the expense failed.

    # This method returns the complete list of all recorded expenses.
    def get_expenses(self):
        return self.expenses

    # This method calculates and returns the total amount of all expenses.
    def get_total_expenses(self):
        # Use a generator expression within sum() to sum up the 'amount' value of each expense dictionary in the list.
        return sum(expense["amount"] for expense in self.expenses)

    # This method calculates the total expense amount for each category.
    # Returns a dictionary where keys are categories and values are the total amounts for those categories.
    def get_expenses_by_category(self):
        # Initialize a dictionary to store totals for each predefined category, starting with zero.
        category_totals = {category: 0 for category in self.categories}
        # Iterate through each expense in the expenses list.
        for expense in self.expenses:
            # Add the amount of the current expense to the total for its corresponding category.
            # Assumes expense["category"] will always be one of the predefined categories.
            category_totals[expense["category"]] += expense["amount"]
        return category_totals # Return the dictionary containing the total expenses per category.

    # This method saves the current list of expenses to a JSON file.
    def save_expenses(self):
        # Open a file named 'expenses.json' in write mode ('w'). This will create the file if it doesn't exist or overwrite it if it does.
        # 'with' statement ensures the file is properly closed after the operation.
        with open("expenses.json", "w") as f:
            # Use json.dump() to serialize the self.expenses list into a JSON formatted string and write it to the file.
            json.dump(self.expenses, f) # Dump expenses list to JSON file

    # This method loads expenses from a JSON file into the expense list.
    # Handles cases where the file doesn't exist or loading fails.
    def load_expenses(self):
        try:
            # Check if the 'expenses.json' file exists in the current directory.
            if os.path.exists("expenses.json"):
                # Open the 'expenses.json' file in read mode ('r').
                with open("expenses.json", "r") as f:
                    # Use json.load() to deserialize the JSON data from the file back into a Python list and assign it to self.expenses.
                    self.expenses = json.load(f)
        except Exception as e:
            # If any exception occurs during the file reading or JSON parsing process, show an error message.
            messagebox.showerror("Error", f"Failed to load expenses: {str(e)}")

# This class is responsible for creating and managing the visual charts based on expense data.
class ExpenseCharts:
    # The constructor takes an instance of ExpenseManager to access the expense data.
    def __init__(self, expense_manager):
        self.expense_manager = expense_manager

    # This method generates a pie chart showing the distribution of expenses across different categories.
    # The chart is embedded within the provided Tkinter frame.
    def create_category_pie_chart(self, frame):
        # Create a new matplotlib figure and an axes object. The figsize sets the size of the figure.
        fig, ax = plt.subplots(figsize=(6, 4))
        # Retrieve the total expenses for each category from the expense manager.
        category_totals = self.expense_manager.get_expenses_by_category()

        # Filter out categories that have a total expense of zero, as they won't appear on the pie chart.
        categories = [cat for cat, total in category_totals.items() if total > 0]
        totals = [total for total in category_totals.values() if total > 0]

        # Check if there are any expenses with a total greater than zero to display on the chart.
        if not categories:
            # If no expenses with positive totals, display a message in the center of the axes.
            ax.text(0.5, 0.5, "No expenses to display",
                   horizontalalignment='center', verticalalignment='center', transform=ax.transAxes) # Use transform for relative positioning
        else:
            # If there are expenses, create the pie chart.
            # 'totals' provides the size of each wedge, 'labels' provides the labels for each wedge, and 'autopct' formats the percentage displayed on each wedge.
            ax.pie(totals, labels=categories, autopct='%1.1f%%')
            ax.set_title("Expenses by Category") # Set the title of the pie chart.

        # Create a FigureCanvasTkAgg object to embed the matplotlib figure ('fig') into the specified Tkinter frame ('master=frame').
        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw() # Draw the canvas, which renders the matplotlib figure.
        # Get the Tkinter widget representation of the canvas and pack it into the frame.
        # fill=tk.BOTH makes the widget expand to fill both horizontal and vertical space.
        # expand=True allows the widget to take up extra space when the parent frame is resized.
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# This is the main application class that sets up the Tkinter GUI and integrates the ExpenseManager and ExpenseCharts.
class ExpenseApp:
    # The constructor initializes the main application window and its components.
    def __init__(self, root):
        self.root = root # Store the root Tkinter window object.
        self.root.title("Personal Expense Tracker") # Set the title that appears in the window's title bar.
        self.root.geometry("800x600") # Set the initial size of the main window (width x height).

        self.expense_manager = ExpenseManager() # Create an instance of the ExpenseManager to handle data.
        self.charts = ExpenseCharts(self.expense_manager) # Create an instance of ExpenseCharts, passing the expense manager to it.

        # Create a notebook widget, which provides a tabbed interface.
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True) # Pack the notebook to make it fill the main window and expand with it.

        # Build the GUI for the 'Add Expense' tab.
        self.build_add_expense_tab()
        # Initialize the charts tab frame and add it to the notebook before building the view expenses tab.
        # This is important because refresh_expenses (called by build_view_expense_tab) updates the charts tab.
        self.charts_tab = ttk.Frame(self.notebook) # Create the frame that will contain the charts.
        self.notebook.add(self.charts_tab, text="Charts") # Add the charts frame to the notebook with the label "Charts".
        # Build the GUI for the 'View Expenses' tab.
        self.build_view_expense_tab()
        # Build the initial content of the 'Charts' tab (the pie chart).
        self.build_charts_tab()

    # This method sets up the graphical user interface elements for adding a new expense.
    def build_add_expense_tab(self):
        tab = ttk.Frame(self.notebook) # Create a new frame specifically for the 'Add Expense' tab.
        self.notebook.add(tab, text="Add Expense") # Add this new frame to the notebook with the corresponding tab text.

        # --- Amount Input Section ---
        # Label for the amount input field.
        ttk.Label(tab, text="Amount ($):").grid(row=0, column=0, padx=5, pady=5) # Place label in grid at row 0, column 0 with some padding.
        self.amount_var = tk.StringVar() # A special Tkinter variable that holds a string; linked to the amount entry field to easily get/set its value.
        # Entry field for the user to type the expense amount.
        ttk.Entry(tab, textvariable=self.amount_var).grid(row=0, column=1, padx=5, pady=5) # Place entry field in grid at row 0, column 1.

        # --- Category Selection Section ---
        # Label for the category selection combobox.
        ttk.Label(tab, text="Category:").grid(row=1, column=0, padx=5, pady=5) # Place label in grid at row 1, column 0.
        self.category_var = tk.StringVar() # A Tkinter variable to hold the currently selected category string.
        # Combobox (dropdown) for selecting an expense category.
        category_combo = ttk.Combobox(tab, textvariable=self.category_var,
                                    values=self.expense_manager.categories, state="readonly") # Use predefined categories as values and make it read-only to prevent typing custom categories.
        category_combo.grid(row=1, column=1, padx=5, pady=5) # Place combobox in grid at row 1, column 1.
        category_combo.set(self.expense_manager.categories[0]) # Set the default selected category to the first one in the list.

        # --- Description Input Section ---
        # Label for the description input field.
        ttk.Label(tab, text="Description:").grid(row=2, column=0, padx=5, pady=5) # Place label in grid at row 2, column 0.
        self.description_var = tk.StringVar() # A Tkinter variable to hold the description string.
        # Entry field for the user to type a description of the expense.
        ttk.Entry(tab, textvariable=self.description_var).grid(row=2, column=1, padx=5, pady=5) # Place entry field in grid at row 2, column 1.

        # --- Date Input Section ---
        # Label for the date input field.
        ttk.Label(tab, text="Date:").grid(row=3, column=0, padx=5, pady=5) # Place label in grid at row 3, column 0.
        # A Tkinter variable for the date string, initialized with the current date in YYYY-MM-DD format.
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d")) # Variable for date, default to today
        # Entry field for the user to input or view the expense date.
        ttk.Entry(tab, textvariable=self.date_var).grid(row=3, column=1, padx=5, pady=5) # Place entry field in grid at row 3, column 1.

        # --- Add Expense Button ---
        # Button to trigger the addition of the expense.
        ttk.Button(tab, text="Add Expense",
                  command=self.add_expense).grid(row=4, column=0, columnspan=2, pady=20) # Place button in grid, spanning columns 0 and 1, with vertical padding.

    # This method builds the graphical user interface for viewing the list of expenses.
    def build_view_expense_tab(self):
        tab = ttk.Frame(self.notebook) # Create a new frame for the 'View Expenses' tab.
        self.notebook.add(tab, text="View Expenses") # Add this frame to the notebook with the tab text.

        # --- Expense List Display (Treeview) ---
        # Define the column identifiers for the Treeview widget.
        columns = ("Date", "Category", "Description", "Amount") # Define columns for Treeview
        # Create a Treeview widget to display data in a tabular format.
        # 'show="headings"' means only the column headings will be visible, not the tree structure itself.
        self.tree = ttk.Treeview(tab, columns=columns, show="headings") # Create Treeview widget

        # Configure the heading and properties for each column in the Treeview.
        for col in columns:
            self.tree.heading(col, text=col) # Set the text that appears in the column heading.
            # Set the width of the column and anchor the text within the column to the west (left).
            # A width of 150 pixels is set initially.
            self.tree.column(col, width=150, anchor=tk.W) # Set column width and left alignment

        # --- Scrollbar for Treeview ---
        # Create a vertical scrollbar.
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.tree.yview) # Link the scrollbar's movement to the Treeview's vertical view.
        # Configure the Treeview to use this scrollbar for vertical scrolling.
        self.tree.configure(yscrollcommand=scrollbar.set) # Link Treeview's vertical scroll to the scrollbar.

        # --- Layout using Grid Geometry Manager ---
        # Place the Treeview in the grid at row 0, column 0.
        # 'sticky' determines how the widget expands if the grid cell is larger than the widget. (N, S, E, W) means it will expand in all directions (North, South, East, West) to fill the cell.
        self.tree.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.E, tk.W)) # Place Treeview, make it expandable
        # Place the scrollbar in the grid at row 0, column 1.
        # 'sticky=(tk.N, tk.S)' makes the scrollbar expand vertically to fill its cell.
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S)) # Place scrollbar, make it vertically expandable

        # --- Refresh Button ---
        # Create a button to refresh the list of expenses displayed in the Treeview.
        ttk.Button(tab, text="Refresh",
                  command=self.refresh_expenses).grid(row=1, column=0, columnspan=2, pady=10) # Place button in grid at row 1, spanning two columns, with vertical padding.

        # --- Configure Grid Weights for Resizing ---
        # Configure column 0 of the grid to absorb extra horizontal space when the window is resized.
        tab.grid_columnconfigure(0, weight=1) # Column 0 expands horizontally
        # Configure row 0 of the grid to absorb extra vertical space, allowing the Treeview to expand.
        tab.grid_rowconfigure(0, weight=1) # Row 0 expands vertically

        # Load and display the initial set of expenses in the Treeview when the tab is built.
        self.refresh_expenses()

    # This method builds and updates the content of the 'Charts' tab, displaying the expense category pie chart.
    def build_charts_tab(self):
        # Clear any existing widgets from the charts tab frame before drawing the new chart.
        # This prevents multiple charts from being drawn on top of each other when data is refreshed.
        for widget in self.charts_tab.winfo_children():
            widget.destroy() # Destroy each child widget in the frame.

        # Call the create_category_pie_chart method from the ExpenseCharts instance to generate and display the chart within the charts tab frame.
        self.charts.create_category_pie_chart(self.charts_tab)

    # This method is called when the 'Add Expense' button is clicked.
    # It retrieves input, validates it, adds the expense, and updates the display.
    def add_expense(self):
        # Get the values entered by the user from the Tkinter StringVars linked to the input fields.
        amount = self.amount_var.get()
        category = self.category_var.get()
        description = self.description_var.get()
        date = self.date_var.get()

        # --- Input Validation ---
        # Check if any of the required input fields are empty.
        if not all([amount, category, description, date]):
            # If any field is empty, show an error message box and stop the method execution.
            messagebox.showerror("Error", "All fields are required")
            return # Stop if any field is empty

        # --- Add Expense and Update Display ---
        # Call the add_expense method of the expense_manager to add the new expense.
        # This method handles the actual data addition and saving to the file.
        if self.expense_manager.add_expense(amount, category, description, date):
            # If the expense was successfully added (add_expense returned True):
            # Clear the input fields in the 'Add Expense' tab for the next entry.
            self.amount_var.set("")
            self.description_var.set("")
            self.refresh_expenses() # Call refresh_expenses to update the data displayed in the 'View Expenses' tab and the charts.
            # self.build_charts_tab() # This call is redundant as refresh_expenses already calls build_charts_tab()
            messagebox.showinfo("Success", "Expense added successfully") # Show a success message box to the user.

    # This method updates the display of expenses in the Treeview on the 'View Expenses' tab
    # and also triggers an update of the charts.
    def refresh_expenses(self):
        # --- Clear Current Display ---
        # Get a list of all items currently displayed in the Treeview.
        for item in self.tree.get_children():
            self.tree.delete(item) # Delete each item from the Treeview.

        # --- Populate Treeview with Updated Data ---
        # Retrieve the latest list of expenses from the expense manager.
        for expense in self.expense_manager.get_expenses():
            # Insert each expense as a new row in the Treeview.
            # "" indicates that the new item should be a top-level item.
            # tk.END indicates that the new item should be inserted at the end of the list.
            # 'values' is a tuple containing the data for each column of the new row.
            self.tree.insert("", tk.END, values=(
                expense["date"], # Value for the 'Date' column.
                expense["category"], # Value for the 'Category' column.
                expense["description"], # Value for the 'Description' column.
                f"${expense['amount']:.2f}" # Value for the 'Amount' column, formatted as currency with 2 decimal places.
            ))

        # --- Update Charts ---
        # Call build_charts_tab to regenerate and display the charts with the updated expense data.
        self.build_charts_tab()

# This is the standard Python entry point for the script.
# The code within this block will only run when the script is executed directly (not when imported as a module).
if __name__ == "__main__":
    root = tk.Tk() # Create the main application window object.
    app = ExpenseApp(root) # Create an instance of the ExpenseApp class, passing the root window.
    root.mainloop() # Start the Tkinter event loop. This makes the window visible and responsive to user interactions until it is closed. 