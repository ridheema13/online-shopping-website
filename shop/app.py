from flask import Flask, render_template ,request, redirect, url_for ,session,json
from flask import flash

import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="shop"
)

cursor = db.cursor(dictionary=True)

@app.route('/')
def home():
    login_success = session.pop('login_success', None)  # gets and removes the session value
    name = session.get('name')  
    return render_template('home.html', login_success=login_success,name=name)

  # Make sure cart.h
# Dummy admin credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'

@app.route('/admin_login2', methods=['GET', 'POST'])
def admin_login2():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('admin_login.html', error="Invalid Credentials")
    return render_template('admin_login2.html')

@app.route('/admin')
def admin_dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin_login2'))
    return render_template('admin.html')

@app.route('/menu')
def menu():
    return "<h2>Menu page coming soon!</h2>"
@app.route('/cart')
def cart():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('cart.html', cart=cart, total=total)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')


@app.route('/login', methods=['GET' ,'POST'])
def login():
   if request.method == 'POST':
    
    email = request.form['email']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        session['email'] = email
        session['name'] = user['name']
        session['login_success'] = True  # store temporary message
        return redirect(url_for('home'))
       # flash("Login Successful!", "success")
    else:
        flash("Invalid email or password.", "danger")
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        # Check for existing user
        cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cursor.fetchone()
        if existing_user:
            return '''
                <div style="text-align: center; font-family: Poppins, sans-serif; padding: 40px;">
                    <h3 style="color: red;">❌ Username or Email already exists! </h3>
                    <a href="/register" style="color: #1976d2; font-weight: bold;">Try Again</a>
                </div>
            '''

        # Insert into database
        cursor.execute("INSERT INTO users (name, email, username, password) VALUES (%s, %s, %s, %s)",
                       (name, email, username, password))
        db.commit()

        # Show success message (no redirect)
        return '''
            <div style="text-align: center; font-family: Poppins, sans-serif; padding: 50px;">
                <h2 style="color: green;">🎉 Registration Successful!</h2>
                <p style="margin-bottom: 25px;">You have successfully created your account.</p>
           
                <a href="/" style="padding: 10px 20px; background: #1976d2; color: white; text-decoration: none; border-radius: 6px;">Back to Home</a>
            </div>
        '''

    return render_template('register.html')

#for addtocart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    item_id = request.form['id']
    name = request.form['name']
    price = float(request.form['price'])
    image_url = request.form['image_url']

    # Get existing cart from session or make a new one
    cart = session.get('cart', {})

    if item_id in cart:
        cart[item_id]['quantity'] += 1
    else:
        cart[item_id] = {
            'name': name,
            'price': price,
            'quantity': 1,
            'image_url': image_url
        }

    session['cart'] = cart
    flash(f"'{name}' added to cart!", 'success')
    return redirect(request.referrer)

#update cart
@app.route('/update_cart', methods=['POST'])
def update_cart():
    item_id = request.form['id']
    action = request.form['action']
    
    cart = session.get('cart', {})

    if item_id in cart:
        if action == 'increase':
            cart[item_id]['quantity'] += 1
        elif action == 'decrease':
            cart[item_id]['quantity'] -= 1
            if cart[item_id]['quantity'] <= 0:
                del cart[item_id]  # Remove item from cart

    session['cart'] = cart
    return redirect(url_for('cart'))
#remove whole cart
@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    item_id = request.form['id']
    cart = session.get('cart', {})

    if item_id in cart:
        del cart[item_id]

    session['cart'] = cart
    return redirect(url_for('cart'))




@app.route("/confirm_order", methods=["POST"])
def confirm_order():
    if "cart" not in session or not session["cart"]:
        return "Cart is empty!"

    name = request.form["full_name"]
    email = request.form["email"]
    address = request.form["address"]
    payment = request.form["payment_method"]

    cart = session["cart"]
    total = sum(item["price"] * item["quantity"] for item in cart.values())

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO orders (customer_name, email, address, payment_method, items, total)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, email, address, payment, json.dumps(cart), total))
    db.commit()

    # Clear cart after confirming order
    session["cart"] = {}

    return render_template("order_success.html", name=name, total=total)

   
@app.route("/admin_orders")
def admin_orders():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
    orders = cursor.fetchall()
    return render_template("admin_orders.html", orders=orders)
@app.route("/cancel_order/<int:order_id>", methods=["POST"])
def cancel_order(order_id):
    reason = request.form["reason"]
    cursor = db.cursor()
    cursor.execute("""
        UPDATE orders SET status=%s, cancel_reason=%s WHERE id=%s
    """, ("Cancelled", reason, order_id))
    db.commit()
    return redirect(url_for("order_status"))


@app.route("/update_status/<int:order_id>", methods=["POST"])
def update_status(order_id):
    new_status = request.form["status"]
    cursor = db.cursor()
    cursor.execute("UPDATE orders SET status=%s WHERE id=%s", (new_status, order_id))
    db.commit()
    return redirect(url_for("admin_orders"))


@app.route("/order_status")
def order_status():
    email = session.get("email")

    if not email:
        return redirect(url_for("login"))   # if not logged in

    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM orders WHERE email=%s ORDER BY created_at DESC", (email,))
    orders = cursor.fetchall()

    # make sure 'items' column is parsed
    for order in orders:
        try:
            order["parsed_items"] = json.loads(order["items"])
        except Exception:
            order["parsed_items"] = {}

    return render_template("order_status.html", orders=orders)

#skirt collection

@app.route("/skirt_collection")
def skirt_collection():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM skirts")
    skirts = cursor.fetchall()
    return render_template("skirt_collection.html", items=skirts)

@app.route("/admin_skirtdashboard")
def admin_skirtdashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM skirts")
    skirts = cursor.fetchall()
    return render_template("admin_skirtdashboard.html", skirts=skirts)

@app.route("/add_skirt", methods=["POST"])
def add_skirt():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image_url = request.form['image_url']
    cursor = db.cursor()
    cursor.execute("INSERT INTO skirts (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
                   (name, description, price, image_url))
    db.commit()
    return redirect("/admin_skirtdashboard")

@app.route("/delete_skirt/<int:id>")
def delete_skirt(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM skirts WHERE id = %s", (id,))
    db.commit()
    return redirect("/admin_skirtdashboard")

@app.route("/edit_skirt/<int:id>", methods=["GET", "POST"])
def edit_skirt(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        cursor.execute("UPDATE skirts SET name=%s, description=%s, price=%s, image_url=%s WHERE id=%s",
                       (name, description, price, image_url, id))
        db.commit()
        return redirect("/admin_skirtdashboard")
    else:
        cursor.execute("SELECT * FROM skirts WHERE id = %s", (id,))
        skirt = cursor.fetchone()
        return render_template("edit_skirt.html", skirt=skirt)


@app.route('/jeans_collection')
def jeans_collection():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jeans_collection")
    items = cursor.fetchall()
    return render_template('jeans_collection.html', items=items)

@app.route('/admin_jeansdashboard', methods=['GET', 'POST'])
def admin_jeansdashboard():
    if request.method == 'POST':
        image_url = request.form['image_url']
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        cursor.execute("INSERT INTO jeans_collection (image_url, name, description, price) VALUES (%s, %s, %s, %s)",
                       (image_url, name, description, price))
        db.commit()
        return redirect(url_for('admin_jeansdashboard'))

    cursor.execute("SELECT * FROM jeans_collection")
    jeans = cursor.fetchall()
    return render_template("admin_jeansdashboard.html", jeans=jeans)

if __name__ == "__main__":
    app.run(debug=True)

# -------------------- DRESSES COLLECTION -------------------

# --------------------------- CUSTOMER SIDE --------------------------- #

# Show Dresses to Customers
@app.route('/dresses_collection')
def dresses_collection():
    cursor.execute("SELECT * FROM dresses")
    items = cursor.fetchall()
    return render_template('dresses_collection.html', items=items, category='dresses')


# 
# --------------------------- ADMIN SIDE --------------------------- #

# Admin Dashboard for Dresses
@app.route('/admin_dressesdashboard')
def admin_dressesdashboard():
    cursor.execute("SELECT * FROM dresses")
    dresses = cursor.fetchall()
    return render_template('admin_dressesdashboard.html', dresses=dresses)

# Add Dress Item
@app.route('/add_dress', methods=['POST'])
def add_dress():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image_url = request.form['image_url']
    cursor.execute("INSERT INTO dresses (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
                   (name, description, price, image_url))
    db.commit()
    return redirect(url_for('admin_dressesdashboard'))

# Edit Dress Item
@app.route('/edit_dress/<int:id>', methods=['GET', 'POST'])
def edit_dress(id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        cursor.execute("""UPDATE dresses SET name=%s, description=%s, price=%s, image_url=%s WHERE id=%s""",
                       (name, description, price, image_url, id))
        db.commit()
        return redirect(url_for('admin_dressesdashboard'))
    else:
        cursor.execute("SELECT * FROM dresses WHERE id = %s", (id,))
        dress = cursor.fetchone()
        return render_template('edit_dress.html', dress=dress)

# Delete Dress Item
@app.route('/delete_dress/<int:id>')
def delete_dress(id):
    cursor.execute("DELETE FROM dresses WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for('admin_dressesdashboard'))




# Flask Routes for Indian Wear (add to app.py)

@app.route("/indianwear_collection")
def indianwear_collection():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM indianwear")
    indianwears = cursor.fetchall()
    return render_template("indianwear_collection.html", items=indianwears)

@app.route("/admin_indianwear_dashboard")
def admin_indianwear_dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM indianwear")
    indianwears = cursor.fetchall()
    return render_template("admin_indianwear_dashboard.html", indianwears=indianwears)

@app.route("/add_indianwear", methods=["POST"])
def add_indianwear():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image_url = request.form['image_url']
    cursor = db.cursor()
    cursor.execute("INSERT INTO indianwear (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
                   (name, description, price, image_url))
    db.commit()
    return redirect("/admin_indianwear_dashboard")

@app.route("/delete_indianwear/<int:id>")
def delete_indianwear(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM indianwear WHERE id = %s", (id,))
    db.commit()
    return redirect("/admin_indianwear_dashboard")

@app.route("/edit_indianwear/<int:id>", methods=["GET", "POST"])
def edit_indianwear(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']
        cursor.execute("UPDATE indianwear SET name=%s, description=%s, price=%s, image_url=%s WHERE id=%s",
                       (name, description, price, image_url, id))
        db.commit()
        return redirect("/admin_indianwear_dashboard")
    else:
        cursor.execute("SELECT * FROM indianwear WHERE id = %s", (id,))
        item = cursor.fetchone()
        return render_template("edit_indianwear.html", item=item)
    

# ---------------- SHOES COLLECTION (Customer Side) ---------------- #

@app.route("/shoes_collection")
def shoes_collection():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shoes")
    shoes = cursor.fetchall()
    return render_template("shoes_collection.html", items=shoes)


# ---------------- ADMIN SHOES DASHBOARD ---------------- #

@app.route("/admin_shoes_dashboard")
def admin_shoes_dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM shoes")
    shoes = cursor.fetchall()
    return render_template("admin_shoes_dashboard.html", shoes=shoes)


# ---------------- ADD SHOES ---------------- #

@app.route("/add_shoes", methods=["POST"])
def add_shoes():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image_url = request.form['image_url']

    cursor = db.cursor()
    cursor.execute("INSERT INTO shoes (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
                   (name, description, price, image_url))
    db.commit()
    return redirect("/admin_shoes_dashboard")


# ---------------- DELETE SHOES ---------------- #

@app.route("/delete_shoes/<int:id>")
def delete_shoes(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM shoes WHERE id = %s", (id,))
    db.commit()
    return redirect("/admin_shoes_dashboard")


# ---------------- EDIT SHOES ---------------- #

@app.route("/edit_shoes/<int:id>", methods=["GET", "POST"])
def edit_shoes(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        cursor.execute("UPDATE shoes SET name=%s, description=%s, price=%s, image_url=%s WHERE id=%s",
                       (name, description, price, image_url, id))
        db.commit()
        return redirect("/admin_shoes_dashboard")
    else:
        cursor.execute("SELECT * FROM shoes WHERE id = %s", (id,))
        item = cursor.fetchone()
        return render_template("edit_shoes.html", item=item)


# ---------------- HEELS COLLECTION (Customer Side) ---------------- #
@app.route("/heels_collection")
def heels_collection():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM heels")
    heels = cursor.fetchall()
    return render_template("heels_collection.html", items=heels)


# ---------------- ADMIN HEELS DASHBOARD ---------------- #
@app.route("/admin_heels_dashboard")
def admin_heels_dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM heels")
    heels = cursor.fetchall()
    return render_template("admin_heels_dashboard.html", heels=heels)


# ---------------- ADD HEELS ---------------- #
@app.route("/add_heels", methods=["POST"])
def add_heels():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image_url = request.form['image_url']

    cursor = db.cursor()
    cursor.execute("INSERT INTO heels (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
                   (name, description, price, image_url))
    db.commit()
    return redirect("/admin_heels_dashboard")


# ---------------- DELETE HEELS ---------------- #
@app.route("/delete_heels/<int:id>")
def delete_heels(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM heels WHERE id = %s", (id,))
    db.commit()
    return redirect("/admin_heels_dashboard")


# ---------------- EDIT HEELS ---------------- #
@app.route("/edit_heels/<int:id>", methods=["GET", "POST"])
def edit_heels(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        cursor.execute("UPDATE heels SET name=%s, description=%s, price=%s, image_url=%s WHERE id=%s",
                       (name, description, price, image_url, id))
        db.commit()
        return redirect("/admin_heels_dashboard")
    else:
        cursor.execute("SELECT * FROM heels WHERE id = %s", (id,))
        item = cursor.fetchone()
        return render_template("edit_heels.html", item=item)

# ---------------- JACKETS COLLECTION (Customer Side) ---------------- #
@app.route("/jacket_collection")
def jacket_collection():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jackets")
    jackets = cursor.fetchall()
    return render_template("jacket_collection.html", items=jackets)


# ---------------- ADMIN JACKETS DASHBOARD ---------------- #
@app.route("/admin_jacket_dashboard")
def admin_jacket_dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM jackets")
    jackets = cursor.fetchall()
    return render_template("admin_jacket_dashboard.html", jackets=jackets)


# ---------------- ADD JACKETS ---------------- #
@app.route("/add_jacket", methods=["POST"])
def add_jacket():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image_url = request.form['image_url']

    cursor = db.cursor()
    cursor.execute("INSERT INTO jackets (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
                   (name, description, price, image_url))
    db.commit()
    return redirect("/admin_jacket_dashboard")


# ---------------- DELETE JACKETS ---------------- #
@app.route("/delete_jacket/<int:id>")
def delete_jacket(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM jackets WHERE id = %s", (id,))
    db.commit()
    return redirect("/admin_jacket_dashboard")


# ---------------- EDIT JACKETS ---------------- #
@app.route("/edit_jacket/<int:id>", methods=["GET", "POST"])
def edit_jacket(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        cursor.execute("UPDATE jackets SET name=%s, description=%s, price=%s, image_url=%s WHERE id=%s",
                       (name, description, price, image_url, id))
        db.commit()
        return redirect("/admin_jacket_dashboard")
    else:
        cursor.execute("SELECT * FROM jackets WHERE id = %s", (id,))
        item = cursor.fetchone()
        return render_template("edit_jacket.html", item=item)

# ---------------- PURSES COLLECTION (Customer Side) ---------------- #
@app.route("/purses_collection")
def purses_collection():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM purses")
    purses = cursor.fetchall()
    return render_template("purses_collection.html", items=purses)


# ---------------- ADMIN PURSES DASHBOARD ---------------- #
@app.route("/admin_purses_dashboard")
def admin_purses_dashboard():
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM purses")
    purses = cursor.fetchall()
    return render_template("admin_purses_dashboard.html", purses=purses)


# ---------------- ADD PURSE ---------------- #
@app.route("/add_purses", methods=["POST"])
def add_purses():
    name = request.form['name']
    description = request.form['description']
    price = request.form['price']
    image_url = request.form['image_url']

    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO purses (name, description, price, image_url) VALUES (%s, %s, %s, %s)",
        (name, description, price, image_url)
    )
    db.commit()
    return redirect("/admin_purses_dashboard")


# ---------------- DELETE PURSE ---------------- #
@app.route("/delete_purses/<int:id>")
def delete_purse(id):
    cursor = db.cursor()
    cursor.execute("DELETE FROM purses WHERE id = %s", (id,))
    db.commit()
    return redirect("/admin_purses_dashboard")


# ---------------- EDIT PURSE ---------------- #
@app.route("/edit_purse/<int:id>", methods=["GET", "POST"])
def edit_purse(id):
    cursor = db.cursor(dictionary=True)
    if request.method == "POST":
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        image_url = request.form['image_url']

        cursor.execute(
            "UPDATE purses SET name=%s, description=%s, price=%s, image_url=%s WHERE id=%s",
            (name, description, price, image_url, id)
        )
        db.commit()
        return redirect("/admin_purses_dashboard")
    else:
        cursor.execute("SELECT * FROM purses WHERE id = %s", (id,))
        item = cursor.fetchone()
        return render_template("edit_purse.html", item=item)

# ✅ app.run should always be the LAST line
if __name__ == '__main__':
    app.run(debug=True)
