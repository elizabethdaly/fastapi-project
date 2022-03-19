import pytest
from app.calculations import add, subtract, multiply, divide, BankAccount, InsufficientFunds

# Fixture for code that's run in loads of tests to avoid repetition
# empty bank account
@pytest.fixture
def zero_bank_account():
    return BankAccount()

# bank ac with 50
@pytest.fixture
def bank_account():
    return BankAccount(50)

# Provide lists to test the add function
@pytest.mark.parametrize("a, b, result", [
    (3, 2, 5), # 3+2=5
    (7, 1, 8),
    (12, 4, 16)
])

def test_add(a, b, result):
    print("Testing add function")
    assert add(a, b) == result

def test_subtract():
    print("Testing subtract function")
    assert subtract(3, 2) == 1

def test_multiply():
    print("Testing multiply function")
    assert multiply(4, 3) == 12

def test_divide():
    print("Testing divide function")
    assert divide(9, 3) == 3

# Test BankAccount balance 
def test_bank_set_initial_amount(bank_account):
    assert bank_account.balance == 50

# test default starting value = 0 if none passed
# def test_bank_default_amount():
#     bank_account = BankAccount() # instance of BankAccount
#     assert bank_account.balance == 0

# OR use fixtures to test starting balance
# fixture = an arg to test function
def test_bank_default_amount(zero_bank_account):
    assert zero_bank_account.balance == 0

# test withdraw method
def test_withdraw(bank_account):
    bank_account.withdraw(20)
    assert bank_account.balance == 30

# test deposit method
def test_deposit(bank_account):
    bank_account.deposit(21)
    assert bank_account.balance == 71

# test collect interest method
def test_collect_interest(bank_account):
    bank_account.collect_interest()
    assert round(bank_account.balance, 3) == 55

@pytest.mark.parametrize("deposited, withdrew, result", [
    (200, 100, 100),
    (50, 10, 40),
    (1200, 200, 1000),
])

# Test more than one transaction
def test_bank_transaction(zero_bank_account, deposited, withdrew, result):
    zero_bank_account.deposit(deposited)
    zero_bank_account.withdraw(withdrew)
    assert zero_bank_account.balance == result

# Test that an Exception is raised when we expect it
def test_insufficient_funds(bank_account):
    with pytest.raises(InsufficientFunds): # tell pytest which exception is expected
        bank_account.withdraw(200)

