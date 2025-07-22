from datetime import datetime


class VendingMachine:
    def __init__(self, items):
        self.items = items
        self.balance = 0.0
        self.total_spent = 0.0
        self.log = []

    def display(self):
        print("\n💰 Current Balance: ${:.2f}".format(self.balance))
        print("\n📋 Available Items:")
        for category, products in self.items.items():
            print(f"\n--- {category} ---") # Added separators for categories
            # Calculate max product name length for dynamic spacing
            max_name_len = 0
            for p in products.values():
                if len(p['name']) > max_name_len:
                    max_name_len = len(p['name'])
            
            # Adjusted header to use f-string for dynamic spacing
            print(f"Code\tProduct{' ' * (max_name_len - 7)}\tPrice\tQuantity") 
            for code, p in products.items():
                # Adjusted f-string for dynamic spacing of product name
                print(f"{code}\t{p['name']}{' ' * (max_name_len - len(p['name']))}\t${p['price']:.2f}\t{p['quantity']}")

    def choose_payment_method(self):
        while True:
            method = input("\n💳 Choose payment method to add funds (cash/card) or type 'exit' to cancel: ").strip().lower()
            if method == 'exit':
                return None
            elif method in ['cash', 'card']:
                return method
            else:
                print("Invalid choice. Please type 'cash' or 'card'.")

    def process_card_payment(self, amount):
        iban = input("Enter your IBAN number: ").strip()
        if not iban.upper().startswith('IB') or len(iban) < 12:
            print("❌ Invalid IBAN. Card declined.")
            return False
        # The condition 'amount > 50' for card decline seems arbitrary and might not be a real-world scenario.
        # It's kept as per your original code but noted. You might want to remove or adjust this based on actual logic.
        if amount > 50:  
            print("❌ Card declined due to a transactional limit. Please try a smaller amount or use cash.")
            return False
        print(f"✅ Card accepted. ${amount:.2f} added to balance.")
        self.balance += amount
        return True

    def process_cash_payment(self, amount):
        while True:
            try:
                cash_given = float(input(f"Insert cash (${amount:.2f} or more): "))
                if cash_given < amount:
                    print(f"❌ Not enough cash. You inserted ${cash_given:.2f}, but need ${amount:.2f}. Try again.")
                else:
                    change = cash_given - amount
                    if change > 0:
                        print(f"💰 Returning change: ${change:.2f}")
                    print(f"✅ ${amount:.2f} added to balance.")
                    self.balance += amount
                    return True
            except ValueError:
                print("Invalid input. Enter a valid numerical amount.")

    def add_funds(self):
        print(f"\nYour current balance is ${self.balance:.2f}")
        while True:
            try:
                amount = float(input("Enter amount to add: "))
                if amount <= 0:
                    print("Amount must be positive.")
                    continue
                method = self.choose_payment_method()
                if method is None:
                    return False
                if method == 'card':
                    if self.process_card_payment(amount):
                        return True
                elif method == 'cash':
                    if self.process_cash_payment(amount):
                        return True
            except ValueError:
                print("Invalid amount. Please enter a number.")

    def select_item(self):
        code = input("\nEnter the product code (or 'exit' to quit): ").strip().upper()
        if code.lower() == 'exit':
            return False

        found_item = None
        # Iterate through categories to find the item
        for category, products in self.items.items():
            if code in products:
                found_item = products[code]
                break # Item found, exit loop

        if found_item:
            p = found_item
            if p['quantity'] <= 0:
                print("❌ Sorry, this product is out of stock.")
                return True

            amount_due = p['price']
            if self.balance < amount_due:
                print(f"⚠️ Not enough balance (${self.balance:.2f}) for this item (${amount_due:.2f}).")
                add = input("Would you like to add funds? (yes/no): ").strip().lower()
                if add == 'yes':
                    if not self.add_funds():
                        print("Cancelled adding funds.")
                        return True
                    # After adding funds, re-check balance. If still not enough, cancel.
                    if self.balance < amount_due:
                        print(f"Still not enough funds after adding. Current balance: ${self.balance:.2f}")
                        print("Transaction cancelled.")
                        return True
                else:
                    print("Transaction cancelled.")
                    return True

            # Complete transaction
            p['quantity'] -= 1
            self.balance -= amount_due
            self.total_spent += amount_due
            self.log.append({
                'time': datetime.now(),
                'item': p['name'],
                'paid': amount_due,
                'method': 'balance'
            })
            print(f"\n🎁 Dispensing {p['name']}... Thank you!")
            return True
        else:
            print("❌ Invalid product code. Try again.")
            return True

    def finish(self):
        print(f"\n🧾 Total spent: ${self.total_spent:.2f}")
        print(f"💵 Remaining balance: ${self.balance:.2f}")
        if self.balance > 0:
            print(f"💰 Please collect your remaining balance: ${self.balance:.2f}")
        print("\nTransaction log:")
        if not self.log:
            print("No transactions recorded.")
        else:
            for t in self.log:
                time = t['time'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"{time}: {t['item']} - Paid ${t['paid']:.2f} from balance")
        print("\n🙏 Thank you for using the Vending Machine. Goodbye!")

    def run(self):
        print("=== 🤖 Starting Vending Machine ===")
        while True:
            self.display()
            # If select_item returns False, it means the user typed 'exit'
            if not self.select_item():
                self.finish()
                return
            
            # Only ask to buy another item if an item was successfully selected/processed
            # (i.e., select_item didn't return False due to 'exit' and didn't result in an invalid code loop)
            if self.log: # Check if any item was purchased
                more = input("\nWould you like to buy another item? (yes/no): ").strip().lower()
                if more != 'yes':
                    self.finish()
                    return
            else: # If no item was purchased and we are still in the loop, allow exit or continue
                # This handles cases where user enters invalid code repeatedly
                cont = input("\nDo you want to continue shopping or exit? (continue/exit): ").strip().lower()
                if cont == 'exit':
                    self.finish()
                    return


# Inventory stays the same
items = {
    'Snacks': {
        'ORO4': {'name': 'oreo', 'price': 1.00, 'quantity': 10},
        'BUBB5': {'name': 'bubble', 'price': 1.75, 'quantity': 30},
        'LAY3': {'name': 'lays', 'price': 2.11, 'quantity': 22},
        'LOLL2': {'name': 'lollipop', 'price': 0.50, 'quantity': 22},
        'CHP6': {'name': 'potato chips', 'price': 1.50, 'quantity': 15},
        'NUT7': {'name': 'mixed nuts', 'price': 2.75, 'quantity': 20},
        'BRC8': {'name': 'chocolate bar', 'price': 1.25, 'quantity': 18},
        'CRKR9': {'name': 'crackers', 'price': 1.80, 'quantity': 25}
    },
    'Drinks': {
        'DRINK1': {'name': 'Dr.Pep', 'price': 3.11, 'quantity': 22},
        'C2': {'name': 'Coke', 'price': 2.58, 'quantity': 9},
        'P3': {'name': 'Pepsi', 'price': 1.41, 'quantity': 33},
        'W4': {'name': 'water', 'price': 1.00, 'quantity': 25},
        'MS5': {'name': 'mint sprite', 'price': 2.00,'quantity': 25},
        'OJ6': {'name': 'orange juice', 'price': 2.25,'quantity': 20},
        'LT7': {'name': 'lemon tea', 'price': 1.90,'quantity': 18},
        'COF8': {'name': 'coffee', 'price': 2.50, 'quantity': 15},
        'ENRG9': {'name': 'energy drink', 'price': 3.50,'quantity': 12}
    }
}

if __name__ == '__main__':
    vm = VendingMachine(items)
    vm.run()