import hashlib


# ──────────────────────────────────────────────
#  Helper Functions
# ──────────────────────────────────────────────


def hash_password(password):
    """Hash a password using SHA-256 (built-in)."""
    return hashlib.sha256(password.encode()).hexdigest()


def get_name():
    """Prompt user for a valid name (letters and spaces only)."""
    while True:
        name = input("Enter your full name: ").strip()

        if name == "":
            print("Name cannot be empty.")

        elif all(c.isalpha() or c.isspace() for c in name):
            print(f"Hi {name}!")
            return name

        else:
            print("Name must contain letters only.")

def get_initial_balance():
    """Prompt user for a valid non-negative starting balance."""
    while True:
        try:
            balance = float(input("Enter your initial balance: "))

            if balance < 0:
                print("Balance cannot be negative.")
            else:
                return balance

        except ValueError:
            print("Please enter a valid number.")


def get_positive_amount(message):
    """Prompt user for a positive number (supports decimals)."""
    while True:
        try:
            amount = float(input(message))

            if amount <= 0:
                print("Amount must be greater than zero.")
            else:
                return amount

        except ValueError:
            print("Please enter a valid number.")


def generate_id(existing_ids):
    """Generate a simple unique numeric ID starting from 100."""
    new_id = 100
    while str(new_id) in existing_ids:
        new_id += 1
    return str(new_id)


def print_divider(title=""):
    """Print a section divider with an optional title."""
    line = "=" * 50

    if title:
        print(line)
        print(title.center(50))
        print(line)
    else:
        print(line)


# ──────────────────────────────────────────────
#  BankAccount Class
# ──────────────────────────────────────────────


class BankAccount:
    def __init__(self, owner, username, password_hash, balance):
        self.owner = owner
        self.username = username
        self._password_hash = password_hash   # stored as hash, never plain text
        self.balance = balance

    def check_password(self, password):
        """Return True if the given password matches the stored hash."""
        return self._password_hash == hash_password(password)

    def show_balance(self):
        """Display account owner and current balance."""
        print(f"  Owner   : {self.owner}")
        print(f"  Balance : {self.balance:,.2f}")

    def deposit(self, amount):
        """Add amount to balance. Returns True on success."""
        if amount <= 0:
            print("Invalid amount to deposit.")
            return False

        self.balance += amount
        print(f"Deposit successful. New balance: {self.balance:,.2f}")
        return True

    def withdraw(self, amount):
        """Subtract amount from balance. Returns True on success."""
        if amount <= 0:
            print("Invalid amount.")
            return False

        if amount > self.balance:
            print("Not enough balance.")
            return False

        self.balance -= amount
        print(f"Withdrawal successful. New balance: {self.balance:,.2f}")
        return True

    def transfer(self, amount, target_account):
        """Transfer amount to another account. Returns True on success."""
        if amount <= 0:
            print("Invalid amount.")
            return False

        if amount > self.balance:
            print("Not enough balance to transfer.")
            return False

        self.balance -= amount
        target_account.balance += amount
        print(f"Transfer successful. New balance: {self.balance:,.2f}")
        return True


# ──────────────────────────────────────────────
#  AccountManager Class
# ──────────────────────────────────────────────

class AccountManager:
    MAX_LOGIN_ATTEMPTS = 3

    def __init__(self):
        self.users = {}   # { account_id: BankAccount }

    # ── Username Validation ──

    def _username_exists(self, username):
        """Check if a username is already taken."""
        return any(acc.username == username for acc in self.users.values())

    def _is_valid_username(self, username):
        """Validate username rules and uniqueness."""
        if username == "":
            print("Username cannot be empty.")
            return False

        if any(c.isspace() for c in username):
            print("Username must not contain spaces.")
            return False

        if not any(c.isalpha() for c in username):
            print("Username must contain at least one letter.")
            return False

        if self._username_exists(username):
            print("This username is already taken.")
            return False

        return True

    def _get_username(self):
        """Keep asking until a valid unique username is entered."""
        while True:
            username = input("Enter username: ").strip()

            if self._is_valid_username(username):
                print(f"Username accepted: {username}")
                return username

    # ── Password Validation ──

    @staticmethod
    def _is_valid_password(password):
        """Validate password strength rules."""
        if password == "":
            print("Password cannot be empty.")
            return False

        if len(password) < 8:
            print("Password must be at least 8 characters.")
            return False

        if any(c.isspace() for c in password):
            print("Password must not contain spaces.")
            return False

        if not any(c.isalpha() for c in password):
            print("Password must contain at least one letter.")
            return False

        if not any(c.isdigit() for c in password):
            print("Password must contain at least one number.")
            return False

        if not any(not c.isalnum() for c in password):
            print("Password must contain at least one symbol.")
            return False

        return True

    def _get_password(self):
        """Keep asking until a valid confirmed password is entered."""
        while True:
            password = input("Enter password: ")

            if not self._is_valid_password(password):
                continue

            confirm = input("Confirm password: ")

            if password == confirm:
                print("Password accepted.")
                return password

            print("Passwords do not match. Try again.")

    # ── Account Creation ──

    def create_account(self):
        """Walk the user through creating a new bank account."""
        print_divider("Create Account")

        owner    = get_name()
        username = self._get_username()
        password = self._get_password()
        balance  = get_initial_balance()

        account_id = generate_id(self.users)
        self.users[account_id] = BankAccount(
            owner, username, hash_password(password), balance
        )

        print(f"\nAccount created successfully! Your ID is: {account_id}")

    # ── Login ──

    def login(self):
        """Authenticate a user and open their account menu."""
        print_divider("Login")

        account_id = input("Enter your account ID: ").strip()

        if account_id not in self.users:
            print("Account ID not found.")
            return

        account = self.users[account_id]

        # Limit login attempts to prevent brute-force guessing
        for attempt in range(1, self.MAX_LOGIN_ATTEMPTS + 1):
            password = input("Enter your password: ")

            if account.check_password(password):
                print(f"\nWelcome back, {account.owner}!")
                self._account_menu(account_id, account)
                return

            remaining = self.MAX_LOGIN_ATTEMPTS - attempt
            if remaining > 0:
                print(f"Wrong password. {remaining} attempt(s) remaining.")

        print("Too many failed attempts. Returning to main menu.")

    # ── Account Operations Menu ──

    def _account_menu(self, account_id, account):
        """Display and handle the logged-in account operations."""
        while True:
            print_divider("Account Menu")
            print("  1. Show Balance")
            print("  2. Deposit")
            print("  3. Withdraw")
            print("  4. Transfer")
            print("  00. Sign Out")

            operation = input("Choose operation: ").strip()

            if operation == "1":
                account.show_balance()

            elif operation == "2":
                amount = get_positive_amount("Enter amount to deposit: ")
                account.deposit(amount)

            elif operation == "3":
                # Keep asking until a valid withdrawal succeeds
                while True:
                    amount = get_positive_amount("Enter amount to withdraw: ")
                    if account.withdraw(amount):
                        break

            elif operation == "4":
                self._handle_transfer(account_id, account)

            elif operation == "00":
                print("Signed out successfully.")
                break

            else:
                print("Invalid operation. Please try again.")

    # ── Transfer Logic ──

    def _handle_transfer(self, sender_id, sender):
        """Handle the full transfer flow including target validation."""
        # Get a valid target account
        while True:
            target_id = input("Enter the ID of the account to transfer to: ").strip()

            if target_id == sender_id:
                print("You cannot transfer to yourself.")
                continue

            if target_id not in self.users:
                print("Account ID not found.")
                continue

            break

        target = self.users[target_id]

        # Keep asking until a valid transfer amount succeeds
        while True:
            amount = get_positive_amount("Enter amount to transfer: ")
            if sender.transfer(amount, target):
                break


# ──────────────────────────────────────────────
#  Main Program
# ──────────────────────────────────────────────

def main():
    manager = AccountManager()

    while True:
        print("=" * 100)
        print("=" * 31,"Hello this is Mohannad's Bank System", "=" * 31)
        print("=" * 100)
        print("1.  Create Account")
        print("2.  Login")
        print("3.  Exit")
        print()

        choice = input(" ==> Choose: ").strip().lower()

        if choice in ("1", "create", "c", "create account"):
            manager.create_account()

        elif choice in ("2", "l", "login"):
            manager.login()

        elif choice in ("3", "exit", "e"):
            print("Have a nice day see you!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()