# Personal Expense Tracker

expenses = []
budget = 0


# Function to add expenses
def add_expense():
    print("\n--- Add Expense ---")

    date = input("Enter date (DD-MM-YYYY): ")

    try:
        number = int(input("How many expenses do you want to add for this date? "))
    except ValueError:
        print("Please enter a valid number.")
        return

    for i in range(number):
        print(f"\nExpense {i + 1}")

        try:
            amount = float(input("Enter expense amount: ₹"))
        except ValueError:
            print("Please enter a valid amount.")
            continue

        category = input("Enter category: ")
        description = input("Enter description: ")

        expense = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description
        }

        expenses.append(expense)

    print("\nExpenses added successfully! 😊")


# Function to view expenses
def view_expenses():
    print("\n--- All Expenses ---")

    if not expenses:
        print("No expenses recorded yet.")
        return

    for i, expense in enumerate(expenses, start=1):
        print(f"\nExpense {i}")
        print("Date:", expense["date"])
        print("Amount: ₹", expense["amount"])
        print("Category:", expense["category"])
        print("Description:", expense["description"])


# Function to calculate total expenses
def total_expenses():
    total = sum(expense["amount"] for expense in expenses)

    print("\n--- Total Expenses ---")
    print(f"Total amount spent: ₹{total:.2f}")


# Function for category-wise summary
def category_summary():
    print("\n--- Category-wise Summary ---")

    if not expenses:
        print("No expenses recorded yet.")
        return

    categories = {}

    for expense in expenses:
        category = expense["category"]
        amount = expense["amount"]

        if category in categories:
            categories[category] += amount
        else:
            categories[category] = amount

    for category, amount in categories.items():
        print(f"{category}: ₹{amount:.2f}")


# Function to set budget
def set_budget():
    global budget

    try:
        budget = float(input("\nEnter your monthly budget: ₹"))
        print(f"Budget set successfully: ₹{budget:.2f}")
    except ValueError:
        print("Please enter a valid budget.")


# Function to check budget
def check_budget():
    print("\n--- Budget Status ---")

    if budget == 0:
        print("Please set your budget first.")
        return

    total = sum(expense["amount"] for expense in expenses)

    print(f"Budget: ₹{budget:.2f}")
    print(f"Spent: ₹{total:.2f}")
    print(f"Remaining: ₹{budget - total:.2f}")

    if total > budget:
        print("⚠️ You have exceeded your budget!")
    else:
        print("✅ You are within your budget.")


# Main program
while True:

    print("\n==============================")
    print("   PERSONAL EXPENSE TRACKER")
    print("==============================")

    print("\n1. Add Expense")
    print("2. View Expenses")
    print("3. Total Expenses")
    print("4. Category-wise Summary")
    print("5. Set Budget")
    print("6. Check Budget")
    print("7. Exit")

    choice = input("\nEnter your choice: ")

    if choice == "1":
        add_expense()

    elif choice == "2":
        view_expenses()

    elif choice == "3":
        total_expenses()

    elif choice == "4":
        category_summary()

    elif choice == "5":
        set_budget()

    elif choice == "6":
        check_budget()

    elif choice == "7":
        print("\nThank you for using Personal Expense Tracker! 😊")
        break

    else:
        print("\nInvalid choice. Please try again.")