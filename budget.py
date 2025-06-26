# -*- coding: utf-8 -*-

# Importing required libraries
import datetime  # For working with dates
import pandas as pd
import json
import time
import os

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

"""# Expense class"""

class Expense:
    def __init__(self, name, amount, payments_per_year, first_month, naja_share_pct, david_share_pct):
        self.name = name
        self.amount = amount
        self.payments_per_year = payments_per_year
        self.first_month = first_month
        self.total_per_year = amount * payments_per_year
        self.naja_share = naja_share_pct / 100 * self.total_per_year
        self.david_share = david_share_pct / 100 * self.total_per_year
        self.payment_months = self.calculate_payment_months()

    def calculate_payment_months(self):
        interval = 12 // self.payments_per_year
        return [((self.first_month - 1) + i * interval) % 12 + 1 for i in range(self.payments_per_year)]

    def to_dict(self):
        return {
            "name": self.name,
            "amount": self.amount,
            "payments_per_year": self.payments_per_year,
            "first_month": self.first_month,
            "naja_share": self.naja_share,
            "david_share": self.david_share,
            "payment_months": self.payment_months,
            "total_per_year": self.total_per_year
        }

    def update(self, name=None, amount=None, payments_per_year=None,
               first_month=None, naja_share_pct=None, david_share_pct=None):

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
        if naja_share_pct is not None:
            self.naja_share = naja_share_pct / 100 * self.total_per_year
        if david_share_pct is not None:
            self.david_share = david_share_pct / 100 * self.total_per_year
        if any(v is not None for v in [payments_per_year, first_month]):
            self.payment_months = self.calculate_payment_months()

    @classmethod
    def from_dict(cls, data):
        # Reconstruct using stored fields (recalculating shares to avoid rounding issues)
        return cls(
            name=data["name"],
            amount=data["amount"],
            payments_per_year=data["payments_per_year"],
            first_month=data["first_month"],
            naja_share_pct=(data["naja_share"] / data["total_per_year"] * 100),
            david_share_pct=(data["david_share"] / data["total_per_year"] * 100),
        )

"""# Budget class"""

class Budget:
    def __init__(self):
        self.expenses = []

    def add_expense(self):
        name = input("Enter name of expense: ")
        if any(e.name == name for e in self.expenses):
            print("Expense already exists.")
            return
        
        amount = get_validated_float("Amount", 0)
        payments = get_validated_int("Payments per year", 0)
        first_month = get_validated_int("First month", 0)
        naja = get_validated_int("Naja's share (%)", 0)
        david = get_validated_int("David's share (%)", 0)

        expense = Expense(name, amount, payments, first_month, naja, david)
        self.expenses.append(expense)
        print("Expense added.")

    def delete_expense(self, name):
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
                naja = get_validated_int("Naja's share (%)", round(e.naja_share / e.total_per_year * 100))
                david = get_validated_int("David's share (%)", round(e.david_share / e.total_per_year * 100))

                e.update(
                    name=new_name,
                    amount=amount,
                    payments_per_year=payments,
                    first_month=first_month,
                    naja_share_pct=naja,
                    david_share_pct=david
                )


                print("Expense updated.")
                return

        print("Expense not found.")


    def show_shares(self):
        total_naja = sum(e.naja_share for e in self.expenses)
        total_david = sum(e.david_share for e in self.expenses)

        shares = {
            "Naja": {"total": total_naja, "monthly": total_naja / 12},
            "David": {"total": total_david, "monthly": total_david / 12}
        }

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

    def save_to_json(self, filename):
        with open(filename, "w") as f:
            json.dump([e.to_dict() for e in self.expenses], f)
        print("Expenses saved.")

    def load_from_json(self, filename):
        try:
            with open(filename, "r") as f:
                data = json.load(f)
            self.expenses = [Expense.from_dict(e) for e in data]
            print("Expenses loaded.")
        except FileNotFoundError:
            print(f"Error: File '{filename}' not found.")
        except json.JSONDecodeError:
            print(f"Error: File '{filename}' is not a valid JSON file.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


"""# Main function"""

from IPython.display import clear_output
import time

def main():
    budget = Budget()
    current_file = "expenses.json"

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
            budget.show_expenses()
            delete = input("Name of expense: ")
            budget.delete_expense(delete)
        elif choice == '6':
            budget.show_expenses()
            budget.edit_expense()
        elif choice == '7':
            saveto = input(f"Filename: [{current_file}]") or current_file
            budget.save_to_json(saveto)
        elif choice == '8':
            loadfrom = input(f"Filename: [{current_file}]") or current_file
            current_file = loadfrom
            budget.load_from_json(loadfrom)
        elif choice == '9':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

        # Pause before redisplaying menu
        input("\nPress Enter to return to the menu...")
        clear_console()

main()  
