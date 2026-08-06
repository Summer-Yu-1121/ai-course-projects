# Design Reflection — Personal Finance Manager

## Overview

This project implements a simplified personal finance manager in Python by applying four classic object-oriented design patterns. The sections below explain what each pattern is, why it was chosen for this specific context, how it improves the design, and any trade-offs or challenges encountered during implementation.

---

## Pattern 1 — Singleton (Balance)

### What it is
The Singleton pattern ensures that only one instance of a class ever exists and provides a global access point to that instance.

### Why it was chosen here
A financial balance is inherently a single shared state. If two separate parts of the application created their own `Balance` objects, they would track different totals and the application would produce incorrect results. The Singleton guarantees one source of truth for the account balance throughout the entire app.

### How it improves the design
- Any module can call `Balance.get_instance()` and always receive the same object.
- No need to pass a balance reference through every function call (dependency injection would work too, but for a small app the singleton is simpler and more transparent).

### Trade-offs and challenges
- Singletons make unit tests harder because state persists across test cases. We solved this by adding a `reset()` method that every `setUp` calls to restore a clean state before each test.
- The `__new__` + `_initialized` guard pattern was needed to prevent `__init__` from re-initializing the instance on repeated calls.

---

## Pattern 2 — Adapter (TransactionAdapter)

### What it is
The Adapter pattern converts the interface of one class into an interface that clients expect, allowing classes with incompatible interfaces to work together.

### Why it was chosen here
External freelance platforms provide income data in their own format (`ExternalFreelanceIncome` with invoice IDs and project descriptions). The rest of the application only understands `Transaction` objects with an `amount` and a `TransactionCategory`. Rather than modifying either class, `TransactionAdapter` acts as the bridge, translating external data without coupling the two systems.

### How it improves the design
- The `Balance` and `Transaction` classes remain completely unaware of any external data formats.
- Adding support for a second external platform (e.g., a payroll service) would only require a new adapter class, with zero changes to existing code (Open/Closed Principle).

### Trade-offs and challenges
- The current adapter always maps external income to `TransactionCategory.INCOME`. If an external source could produce expenses, the adapter logic would need to inspect `typ` dynamically. This is an acceptable simplification for the current requirements.

---

## Pattern 3 — Observer (LowBalanceAlertObserver, PrintObserver)

### What it is
The Observer pattern defines a one-to-many dependency so that when one object (the subject) changes state, all registered dependents (observers) are notified automatically.

### Why it was chosen here
Balance changes are interesting to multiple parts of the system: the UI wants to print every update, and a risk monitor wants to fire an alert when funds run low. Hardcoding both these behaviors inside `Balance.apply_transaction` would violate the Single Responsibility Principle and make the class brittle. Observers let each concern live in its own class.

### How it improves the design
- `Balance` only manages money arithmetic; it does not know or care how observers react.
- New behaviors (e.g., sending an email alert) can be added by registering a new observer class with no changes to `Balance`.
- Observers can also be removed at runtime, which is useful for testing or toggling features.

### Trade-offs and challenges
- The `LowBalanceAlertObserver.alert_triggered` flag tracks whether an alert is currently active to avoid repeated alerts for the same low-balance period. The flag resets when the balance recovers above the threshold. Getting the edge cases right (alert fires once going down, clears on recovery, fires again on next drop) required careful reasoning and an explicit test sequence in `test_balance_observer.py`.

---

## Pattern 4 — Strategy (Transaction Processing Strategy)

### What it is
The Strategy pattern defines a family of algorithms, encapsulates each one in its own class, and makes them interchangeable at runtime without changing the client.

### Why it was chosen (over Command or Decorator)
Transaction processing rules are a natural "algorithm slot": the standard rule (income adds, expense subtracts) is the default, but real finance apps often have variations such as fee deductions on income, rounded amounts, or currency conversions. The Strategy pattern lets `Balance` delegate this logic to a swappable object rather than embedding all variants inside a growing `if/elif` chain.

**Command** was considered but felt like overengineering for a single-step operation with no need for undo history.  
**Decorator** was considered for wrapping `Transaction` objects, but it would have made `apply_transaction` more complex without adding clear benefit at this scale.

### How it improves the design
- `Balance.set_processing_strategy(strategy)` allows callers to swap rules at runtime (e.g., switching to a fee-deducting strategy in tests or for specific account types).
- `StandardTransactionProcessingStrategy` is the safe default, so no existing behavior changes unless a caller explicitly chooses a different strategy.
- The `ITransactionProcessingStrategy` interface makes it easy to validate a custom strategy in tests without touching `Balance` itself.

### Trade-offs and challenges
- Introducing a strategy object adds one extra indirection layer. For simple cases this is slight overhead, but it pays off as soon as a second processing variant is needed.
- The strategy currently lives inside `apply_transaction`, which also raises a `ValueError` for unknown categories. This validation check was kept in `Balance` rather than the strategy so that all strategies benefit from it automatically.

---

## Summary Table

| Pattern   | Class(es)                                   | Benefit                                      |
|-----------|---------------------------------------------|----------------------------------------------|
| Singleton | `Balance`                                   | One shared balance state, no duplication     |
| Adapter   | `TransactionAdapter`, `ExternalFreelanceIncome` | Decouple external data from internal model |
| Observer  | `LowBalanceAlertObserver`, `PrintObserver`  | Separate side-effects from core balance logic|
| Strategy  | `StandardTransactionProcessingStrategy`     | Swap processing rules without modifying Balance |
