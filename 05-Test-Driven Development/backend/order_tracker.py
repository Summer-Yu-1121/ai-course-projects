# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """

    VALID_STATUSES = {
        "pending",
        "processing",
        "shipped",
        "delivered",
        "cancelled",
    }

    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(
                    f"Storage object must implement a callable '{method}' method."
                )
        self.storage = storage

    def add_order(
        self,
        order_id: str,
        item_name: str,
        quantity: int,
        customer_id: str,
        status: str = "pending",
    ):
        # Basic validation
        if not order_id:
            raise ValueError("Order ID must be provided.")
        if not item_name:
            raise ValueError("Item name must be provided.")
        if not customer_id:
            raise ValueError("Customer ID must be provided.")
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid order status: {status}")

        # Uniqueness check
        if self.storage.get_order(order_id) is not None:
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }

        self.storage.save_order(order)
        return order

    def get_order_by_id(self, order_id: str):
        if not order_id:
            raise ValueError("Order ID must be provided.")
        return self.storage.get_order(order_id)

    def update_order_status(self, order_id: str, new_status: str):
        if not order_id:
            raise ValueError("Order ID must be provided.")
        if new_status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid order status: {new_status}")

        order = self.storage.get_order(order_id)
        if order is None:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")

        # Copy to avoid mutating original object directly
        updated_order = dict(order)
        updated_order["status"] = new_status

        self.storage.save_order(updated_order)
        return updated_order

    def list_all_orders(self):
        all_orders = self.storage.get_all_orders()
        return list(all_orders.values()) if isinstance(all_orders, dict) else list(all_orders)

    def list_orders_by_status(self, status: str):
        if not status:
            raise ValueError("Status must be provided.")
        if status not in self.VALID_STATUSES:
            raise ValueError(f"Invalid order status: {status}")

        all_orders = self.storage.get_all_orders()
        orders_iterable = all_orders.values() if isinstance(all_orders, dict) else all_orders

        return [
            order
            for order in orders_iterable
            if order.get("status") == status
        ]