from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder="../frontend")

# Initialize storage and business logic
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)


# ---------- Frontend ----------
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)


# ---------- API: Add Order ----------
@app.route("/api/orders", methods=["POST"])
def add_order_api():
    data = request.get_json()

    try:
        order = order_tracker.add_order(
            order_id=data.get("order_id"),
            item_name=data.get("item_name"),
            quantity=data.get("quantity"),
            customer_id=data.get("customer_id"),
            status=data.get("status", "pending"),
        )
        return jsonify(order), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ---------- API: Get Order by ID ----------
@app.route("/api/orders/<string:order_id>", methods=["GET"])
def get_order_api(order_id):
    order = order_tracker.get_order_by_id(order_id)

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    return jsonify(order), 200


# ---------- API: Update Order Status ----------
@app.route("/api/orders/<string:order_id>/status", methods=["PUT"])
def update_order_status_api(order_id):
    data = request.get_json()

    try:
        updated_order = order_tracker.update_order_status(
            order_id=order_id,
            new_status=data.get("new_status"),
        )
        return jsonify(updated_order), 200
    except ValueError as e:
        # Distinguish not-found vs invalid input based on message
        message = str(e)
        if "does not exist" in message or "not exist" in message:
            return jsonify({"error": message}), 404
        return jsonify({"error": message}), 400


# ---------- API: List Orders (all / by status) ----------
@app.route("/api/orders", methods=["GET"])
def list_orders_api():
    status = request.args.get("status")

    try:
        if status:
            orders = order_tracker.list_orders_by_status(status)
        else:
            orders = order_tracker.list_all_orders()
        return jsonify(orders), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


# ---------- App Entry ----------
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)