# Udatracker Starter Code

This directory contains the starter code for the Udatracker project.

## Reflection

- I kept `OrderTracker` framework-agnostic and moved HTTP concerns to `app.py`, which makes unit tests fast and focused while keeping route handlers thin.
- A key trade-off was normalizing order collection shapes in `OrderTracker` (dict-backed storage to list outputs) to keep API behavior predictable without coupling tests to storage internals.
- Test-first development caught a real contract mismatch between `OrderTracker` and `InMemoryStorage` (`save_order` signature), which surfaced immediately through failing integration tests.
- If I continued this project, I would add persistent storage (e.g., SQLite) and a `DELETE /api/orders/<order_id>` endpoint, then extend tests to cover deletion and restart durability.

```
.
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── in_memory_storage.py
│   ├── order_tracker.py
│   ├── requirements.txt
│   └── tests
│       ├── __init__.py
│       ├── test_api.py
│       └── test_order_tracker.py
├── frontend
│   ├── css
│   │   └── style.css
│   ├── index.html
│   └── js
│       └── script.js
├── pytest.ini
└── README.md
```

