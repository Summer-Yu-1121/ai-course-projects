# Personal Finance Manager — Design Patterns Project

This folder contains the completed project implementation using four classic object-oriented design patterns in Python.

## Reflection

A full written reflection explaining all four patterns, the rationale behind each choice, and trade-offs encountered during implementation is in:

**[REFLECTION.md](REFLECTION.md)**

## Running the Application

From this `starter/` directory:

```bash
/usr/local/bin/python3 main.py
```

## Running the Tests

```bash
/usr/local/bin/python3 -m unittest balance/test_balance.py balance/test_balance_observer.py transaction/test_transaction.py transaction/test_transaction_adapter.py transaction/test_transaction_processing_strategy.py
```

Expected result: `Ran 15 tests ... OK`

## Patterns Implemented

| # | Pattern   | Location                                        |
|---|-----------|--------------------------------------------------|
| 1 | Singleton | `balance/balance.py`                            |
| 2 | Adapter   | `transaction/transaction_adapter.py`            |
| 3 | Observer  | `balance/balance_observer.py`                   |
| 4 | Strategy  | `transaction/transaction_processing_strategy.py`|
