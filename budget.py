# -*- coding: utf-8 -*-

# Importing required libraries
import datetime  # For working with dates
import pandas as pd
import json
import time
import os
import pickle

def clear_console():
    os.system('cls')

def get_validated_float(prompt, current_value):
    while True:
        user_input = input(f"{prompt} [{current_value}]: ")
        if user_input == "":
            return current_value
        try:
            return float(user_input.replace(',', '.'))
        except ValueError:
            print("Invalid input. Please enter a number.")

def get_validated_int(prompt, current_value):
    while True:
        user_input = input(f"{prompt} [{current_value}]: ")
        if user_input == "":
            return current_value
        if user_input.isdigit():
            return int(user_input)
        print("Invalid input. Please enter a whole number.")

def save_to_pickle(budget):
    current_file = "Expenses.pkl"
    filename = input(f"Filename: [{current_file}]") or current_file
    with open(filename, "wb") as f:
        pickle.dump(budget, f)
    print("Expenses saved.")

def load_from_pickle():
    current_file = "Expenses.pkl"
    filename = input(f"Filename: [{current_file}]") or current_file
    
    try:
        with open(filename, "rb") as f:
            data = pickle.load(f)
        print("Expenses loaded.")
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        


"""# Expense class"""

class Expense:
    def __init__(self, name, amount, payments_per_year, first_month, shares):
        self.name = name
        self.amount = amount
        self.payments_per_year = payments_per_year
        self.first_month = first_month
        self.total_per_year = amount * payments_per_year
        self.shares = shares  # e.g. {'Naja': 60, 'David': 40}
        self.payment_months = self.calculate_payment_months()

    def calculate_payment_months(self):
        interval = 12 // self.payments_per_year
        return [((self.first_month - 1) + i * interval) % 12 + 1 for i in range(self.payments_per_year)]

    def to_dict(self):
        temp_dict = {
            "name": self.name,
            "amount": self.amount,
            "payments_per_year": self.payments_per_year,
            "first_month": self.first_month,
            "payment_months": self.payment_months,
            "total_per_year": self.total_per_year
        }
        temp_dict.update(self.shares)
        return temp_dict

    def update(self, name=None, amount=None, payments_per_year=None,
               first_month=None, shares=None):

        if name is not None:
            self.name = name
        if amount is not None:
            self.amount = amount
        if payments_per_year is not None:
            self.payments_per_year = payments_per_year
        if first_month is not None:
            self.first_month = first_month
        if any(v is not None for v in [amount, payments_per_year]):
            self.total_per_year = self.amount * self.payments_per_year
        if shares is not None:
            self.shares = shares
        if any(v is not None for v in [payments_per_year, first_month]):
            self.payment_months = self.calculate_payment_months()

"""# Budget class"""

class Budget:
    def __init__(self):
        self.expenses = []
        self.people = self.get_participants()  # e.g. ['Naja', 'David']

    def get_participants(self):
        print("Enter the names of the people sharing expenses (e.g. Naja, David). Leave blank to finish.")
        people = []
        while True:
            name = input("Enter name: ").strip()
            if not name:
                break
            if name in people:
                print("Name already added.")
                continue
            people.append(name)
        if not people:
            print("No names entered. Using default: ['Naja', 'David']")
            return ['Naja', 'David']
        clear_console()
        return people

    def add_expense(self):
        name = input("Enter name of expense: ")
        if any(e.name == name for e in self.expenses):
            print("Expense already exists.")
            return

        amount = get_validated_float("Amount", 0)
        payments = get_validated_int("Payments per year", 0)
        first_month = get_validated_int("First month", 0)

        shares = {}
        total = 0
        print("Enter share percentages. Total must be 100%.")

        for person in self.people:
            while True:
                try:
                    share = int(input(f"{person}'s share (%): "))
                    break
                except ValueError:
                    print("Invalid input. Enter a number.")
            shares[person] = share
            total += share

        if total != 100:
            print(f"Error: Total share is {total}%. Must be 100%.")
            return

        expense = Expense(name, amount, payments, first_month, shares)
        self.expenses.append(expense)
        print("Expense added.")

    def delete_expense(self):
        self.show_expenses()
        name = input("Name of expense: ")
        for e in self.expenses:
            if e.name == name:
                self.expenses.remove(e)
                print("Expense deleted.")
                return
        print("Expense not found.")

    def edit_expense(self):
        name = input("Enter the name of the expense to edit: ")
        for e in self.expenses:
            if e.name == name:
                print(f"Editing '{e.name}' (press Enter to keep current value)")

                new_name = input(f"New name [{e.name}]: ") or e.name
                amount = get_validated_float("New amount", e.amount)
                payments = get_validated_int("Payments per year", e.payments_per_year)
                first_month = get_validated_int("First month", e.first_month)
                
                shares = {}
                total = 0
                print("Enter share percentages. Total must be 100%.")
                
                for person in self.people:
                    share = get_validated_int(person, e.shares[person])
                    shares[person] = share
                    total += share

                if total != 100:
                    print(f"Error: Total share is {total}%. Must be 100%.")
                    return

                e.update(
                    name=new_name,
                    amount=amount,
                    payments_per_year=payments,
                    first_month=first_month,
                    shares = shares
                )


                print("Expense updated.")
                return

        print("Expense not found.")


    def show_shares(self):
        shares ={}
        
        for person in self.people:
            total = sum(e.shares[person] * e.total_per_year / 100 for e in self.expenses)
            shares.update({person:{"total":total, "monthly":total / 12}})
            
        df = pd.DataFrame(shares)
        print(df.to_string(index=True))

    def show_expenses(self):
        if not self.expenses:
            print("No expenses to show.")
            return
        df = pd.DataFrame([e.to_dict() for e in self.expenses])
        df['payment_months'] = df['payment_months'].apply(lambda x: ', '.join(map(str, x)))
        print(df.to_string(index=False))

    def show_expenses_this_month(self):
        current_month = datetime.datetime.now().month
        filtered = [
            {"name": e.name, "amount": e.amount}
            for e in self.expenses if current_month in e.payment_months
        ]
        if not filtered:
            print("No expenses for this month.")
            return
        df = pd.DataFrame(filtered)
        print(df.to_string(index=False))

    


"""# Main function"""

import time

def main():
        
    print("\n--- Menu ---")
    print("1. New budget")
    print("2. Load budget")
    
    choice = input("\nEnter your choice: ")
    
    # Handle user choice
    if choice == '1':
        budget = Budget()
    elif choice == '2':
        budget = load_from_pickle()
    
    while True:
        # Display menu (don't clear yet — avoid input race)
        print("\n--- Menu ---")
        print("1. Add Expense")
        print("2. Show Shares")
        print("3. Show Expenses")
        print("4. Show Expenses This Month")
        print("5. Delete Expense")
        print("6. Edit Expense")
        print("7. Save Expenses")
        print("8. Load Expenses")
        print("9. Exit")

        choice = input("\nEnter your choice: ")

        # Clear screen AFTER input to prevent accidental skipping
        clear_console()

        # Handle user choice
        if choice == '1':
            budget.add_expense()
        elif choice == '2':
            budget.show_shares()
        elif choice == '3':
            budget.show_expenses()
        elif choice == '4':
            budget.show_expenses_this_month()
        elif choice == '5':            
            budget.delete_expense()
        elif choice == '6':
            budget.show_expenses()
            budget.edit_expense()
        elif choice == '7':
            save_to_pickle(budget)
        elif choice == '8':
            budget = load_from_pickle()
        elif choice == '9':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

        # Pause before redisplaying menu
        input("\nPress Enter to return to the menu...")
        clear_console()

main()  
