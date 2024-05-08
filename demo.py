class Account:
    def __init__(self, account_number, balance=0):
        self.account_number = account_number
        self.balance = balance

    def deposit(self, amount):
        self.balance += amount
        print(f"Deposited ${amount}. New balance: ${self.balance}")

    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            print(f"Withdrew ${amount}. New balance: ${self.balance}")
        else:
            print("Insufficient funds")

    def display_balance(self):
        print(f"Account Balance: ${self.balance}")

# Creating accounts
account1 = Account("123456789")
account2 = Account("987654321", 1000)

# Depositing and withdrawing from accounts
account1.deposit(500)
account2.withdraw(200)

# Displaying account balances
account1.display_balance()
account2.display_balance()
