import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)

#
# --- TODO: add test functions below this line ---
#
def test_add_order_successfully(order_tracker, mock_storage):
    """
    Tests adding a new order with default 'pending' status.
    """
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()

    # Verify the saved order content
    saved_order = mock_storage.save_order.call_args[0][0]
    assert saved_order["order_id"] == "ORD001"
    assert saved_order["item_name"] == "Laptop"
    assert saved_order["quantity"] == 1
    assert saved_order["customer_id"] == "CUST001"
    assert saved_order["status"] == "pending"


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")


def test_add_order_raises_error_for_invalid_quantity(order_tracker):
    with pytest.raises(ValueError, match="Quantity must be a positive integer."):
        order_tracker.add_order("ORD002", "Laptop", 0, "CUST001")


def test_get_order_by_id_returns_order_when_exists(order_tracker, mock_storage):
    order = {
        "order_id": "ORD100",
        "item_name": "Keyboard",
        "quantity": 1,
        "customer_id": "CUST100",
        "status": "pending",
    }

    mock_storage.get_order.return_value = order

    result = order_tracker.get_order_by_id("ORD100")

    assert result == order
    mock_storage.get_order.assert_called_once_with("ORD100")

def test_get_order_by_id_returns_none_when_not_exists(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    result = order_tracker.get_order_by_id("NON_EXISTENT")

    assert result is None
    mock_storage.get_order.assert_called_once_with("NON_EXISTENT")


def test_get_order_by_id_raises_for_empty_id(order_tracker):
    with pytest.raises(ValueError, match="Order ID must be provided."):
        order_tracker.get_order_by_id("")

def test_update_order_status_success(order_tracker, mock_storage):
    existing_order = {
        "order_id": "ORD200",
        "item_name": "Mouse",
        "quantity": 1,
        "customer_id": "CUST200",
        "status": "pending",
    }

    mock_storage.get_order.return_value = existing_order

    updated = order_tracker.update_order_status("ORD200", "shipped")

    assert updated["status"] == "shipped"
    mock_storage.save_order.assert_called_once()


def test_update_order_status_raises_for_invalid_status_without_storage_lookup(order_tracker, mock_storage):
    with pytest.raises(ValueError, match="Invalid order status: unknown"):
        order_tracker.update_order_status("ORD200", "unknown")

    mock_storage.get_order.assert_not_called()


def test_update_order_status_raises_if_order_missing(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError, match="Order with ID 'ORD404' does not exist."):
        order_tracker.update_order_status("ORD404", "shipped")

def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    orders = {
        "O1": {"order_id": "O1", "status": "pending"},
        "O2": {"order_id": "O2", "status": "shipped"},
    }

    mock_storage.get_all_orders.return_value = orders

    result = order_tracker.list_all_orders()

    assert isinstance(result, list)
    assert {order["order_id"] for order in result} == {"O1", "O2"}
    mock_storage.get_all_orders.assert_called_once()


def test_list_orders_by_status_returns_matches(order_tracker, mock_storage):
    mock_storage.get_all_orders.return_value = {
        "O1": {"order_id": "O1", "status": "pending"},
        "O2": {"order_id": "O2", "status": "shipped"},
        "O3": {"order_id": "O3", "status": "pending"},
    }

    result = order_tracker.list_orders_by_status("pending")

    assert {order["order_id"] for order in result} == {"O1", "O3"}


def test_list_orders_by_status_raises_for_invalid_status(order_tracker):
    with pytest.raises(ValueError, match="Invalid order status: unknown"):
        order_tracker.list_orders_by_status("unknown")

