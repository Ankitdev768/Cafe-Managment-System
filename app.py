from flask import Flask, render_template, request, jsonify
import json
import datetime

app = Flask(__name__)

# Menu and Combo Offers
menu = {
    'Espresso': 150,
    'Cappuccino': 200,
    'Latte': 180,
    'Mocha': 220,
    'Tea': 100,
    'Sandwich': 120,
    'Burger': 250,
    'Pizza': 400,
    'Pasta': 350,
    'Cake': 180,
}

combo_offers = {
    "Coffee & Cake Combo": {"items": ["Espresso", "Cake"], "discount": 10},
    "Burger & Tea Combo": {"items": ["Burger", "Tea"], "discount": 15},
}

@app.route('/')
def home():
    return render_template('index.html', menu=menu)

@app.route('/place_order', methods=['POST'])
def place_order():
    # Extract order details from the form data
    order_details = request.form.to_dict()

    # Filter out invalid values and convert valid quantities to integers
    try:
        order_details = {key: int(value) for key, value in order_details.items() if value != '0' and key != 'payment_method'}
    except ValueError:
        return "❌ Invalid input in order details. Please try again."

    # If no valid items were selected
    if not order_details:
        return "❌ No items selected! Please add items to your order."

    # Calculate order total
    order_total = sum(menu[item] * order_details[item] for item in order_details)

    # Apply Combo Discounts
    discount_amount = 0
    for combo, details in combo_offers.items():
        if all(item in order_details for item in details["items"]):
            combo_price = sum(menu[item] * order_details[item] for item in details["items"])
            discount = (details["discount"] / 100) * combo_price
            discount_amount += discount

    order_total -= discount_amount

    # Apply GST (5%)
    tax = order_total * 0.05
    order_total += tax

    # Payment Method (string, not converted to int)
    payment_method = request.form['payment_method']

    # Save Order History
    order_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    order_record = {
        "time": order_time, 
        "order": order_details, 
        "total": round(order_total, 2), 
        "payment_method": payment_method,
        "discount": round(discount_amount, 2),  # Save discount value
        "gst": round(tax, 2)  # Save GST value
    }

    # Read and append to order history file
    try:
        with open("cafe_order_history.json", "r") as file:
            order_history = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        order_history = []

    order_history.append(order_record)
    with open("cafe_order_history.json", "w") as file:
        json.dump(order_history, file, indent=4)

    # Return the order summary page with menu data included
    return render_template('order_history.html', order_record=order_record, menu=menu)


@app.route('/order_history')
def order_history():
    try:
        with open("cafe_order_history.json", "r") as file:
            history = json.load(file)
    except FileNotFoundError:
        history = []  # If the file doesn't exist, return an empty list
    except json.JSONDecodeError:
        history = []  # If JSON decoding fails, return an empty list
    
    return render_template('order_history.html', history=history, menu=menu)


if __name__ == '__main__':
    app.run(debug=True)
