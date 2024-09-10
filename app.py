from flask import Flask, jsonify, render_template, request
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.models.customer_details import CustomerDetails
from cashfree_pg.models.order_meta import OrderMeta
import uuid
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)
X_API_VERSION = "2023-08-01"

# Cashfree API credentials
Cashfree.XClientId = "TEST430329ae80e0f32e41a393d78b923034"
Cashfree.XClientSecret = "TESTaf195616268bd6202eeb3bf8dc458956e7192a85"
Cashfree.XEnvironment = Cashfree.SANDBOX  # Use Cashfree.PRODUCTION for production

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_order', methods=['POST'])
def create_order():
    try:
        # Get data from the frontend request
        data = request.json
        amount = data.get('amount')
        currency = data.get('currency', 'INR')

        # Generate a unique order ID
        order_id = f"order_{uuid.uuid4().hex[:10]}"

        # Create customer details
        customer_details = CustomerDetails(
            customer_id="devstudio_user",
            customer_phone=data.get('customerPhone'),
            customer_email=data.get('customerEmail')
        )

        # Create order request
        create_order_request = CreateOrderRequest(
            order_id=order_id,
            order_amount=amount,
            order_currency=currency,
            customer_details=customer_details
        )

        # Set order meta
        order_meta = OrderMeta()
        order_meta.return_url = f"https://www.cashfree.com/devstudio/preview/pg/web/checkout?order_id={order_id}"
        order_meta.payment_methods = "cc,dc,upi"
        create_order_request.order_meta = order_meta

        # Create the order with Cashfree API
        api_response = Cashfree().PGCreateOrder(X_API_VERSION, create_order_request, None, None)

        # Return the payment session ID if successful
        if api_response and api_response.data and api_response.data.payment_session_id:
            return jsonify({"paymentSessionId": api_response.data.payment_session_id})
        else:
            return jsonify({"error": "Failed to generate payment session ID"}), 500

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8080)
