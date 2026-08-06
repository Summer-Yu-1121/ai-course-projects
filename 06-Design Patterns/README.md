# Personal Finance Manager — Design Patterns Project

This project is a hands-on exercise in applying Object-Oriented Design Patterns to build a simplified personal finance manager.
You will implement and extend starter code to add functionality such as tracking transactions, adapting external data, observing balance changes, and ensuring proper architectural patterns.

## Getting Started

### Dependencies

Make sure you have python version >= 3.10.x installed on your computer. 


### Installation

1. Clone the repo:

```
bash
git clone https://github.com/udacity/cd14600-project-starter.git
cd cd14600-project-starter/starter
```

2. Run the Program: 
```
python main.py
```

### Workspace-Verified Commands

From the starter folder:

```
cd starter
```

Run the application:

```
/usr/local/bin/python3 main.py
```

Run all project tests used in this submission:

```
/usr/local/bin/python3 -m unittest balance/test_balance.py balance/test_balance_observer.py transaction/test_transaction.py transaction/test_transaction_adapter.py transaction/test_transaction_processing_strategy.py
```

## Testing

This project uses Python’s built-in unittest framework.

To run all tests:

```
python -m unittest discover
```

To run a single test file:
```
python -m unittest balance/test_balance_observer.py
```

### Break Down Tests

- test_balance.py → Verifies correct implementation of the Singleton Balance class.
- test_transaction.py → Confirms transactions update balances correctly.
- test_transaction_adapter.py → Ensures external income data is correctly adapted into Transaction objects.
- test_balance_observer.py → Validates that low-balance alerts are triggered at the correct threshold.

## Project Instructions

1. Implement Singleton Balance Class – Ensure only one balance object exists throughout the app.
2. Complete Transaction Class – Handle income and expense transactions.
3. Implement Adapter Pattern – Adapt external freelance income data into internal Transaction objects.
4. Implement Observer Pattern – Create a low balance observer that triggers an alert when funds drop too low.
5. Add Unit Tests – Write tests for all implemented functionality.
6. Choose and Implement a Fourth Pattern – Pick one additional design pattern (e.g., Strategy, Command, Decorator, etc.) and integrate it into your project.
7. Provide a Reflection – Add a short write-up in your repo (README or separate file) explaining your design choices.

## Reflection

This implementation applies four design patterns to keep the code modular and testable.

1. Singleton (Balance):
The `Balance` class is implemented as a true singleton so every part of the program shares one source of truth for the account state.

2. Adapter (TransactionAdapter):
External freelance income objects are converted into internal `Transaction` objects without changing external models.

3. Observer (LowBalanceAlertObserver, PrintObserver):
Observers react to balance updates after each transaction. This separates side effects (printing and alerts) from the `Balance` domain logic.

4. Strategy (Transaction processing strategy):
`Balance` delegates transaction application rules to a pluggable strategy (`StandardTransactionProcessingStrategy` by default). This makes it easy to swap business rules (for example, adding income fees) without modifying `Balance` itself.

Overall, these choices improve extensibility by reducing coupling: balance tracking, integration, notifications, and transaction rules can evolve independently.

## Built With

* [Python](https://www.python.org/) – Main programming language
* [unittest](https://docs.python.org/3/library/unittest.html) – Testing framework
* [PEP8](https://peps.python.org/pep-0008/) – Style guide for Python code

## License

[License](LICENSE.txt)

