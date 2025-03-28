import os
import click
from flask import Flask, render_template, request, redirect, url_for, flash, session, g, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash, safe_join
from werkzeug.utils import secure_filename
from datetime import datetime
import secrets # For generating secret key
import functools # For admin login decorator
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# DATABASE_PATH = os.path.join(BASE_DIR, 'database.db') # No longer needed for SQLite path
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static/images/products')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', secrets.token_hex(16)) # Use env var or generate
# Use DATABASE_URL from environment variables, default to local SQLite for dev if not set
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{os.path.join(BASE_DIR, "database.db")}')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

db = SQLAlchemy(app)

# --- Context Processors ---
# Make cart available globally
@app.context_processor
def inject_cart():
    cart = session.get('cart', {})
    cart_items = []
    total_quantity = 0
    total_price = 0.0
    if cart:
        product_ids = [int(k) for k in cart.keys()]
        products_in_cart = Product.query.filter(Product.id.in_(product_ids)).all()
        product_map = {product.id: product for product in products_in_cart}

        for product_id, item_data in cart.items():
            product = product_map.get(int(product_id))
            if product:
                quantity = item_data.get('quantity', 0)
                total_quantity += quantity
                total_price += quantity * product.price
                cart_items.append({
                    'product': product,
                    'quantity': quantity,
                    'size': item_data.get('size'),
                    'color': item_data.get('color'),
                    'subtotal': quantity * product.price
                })
    return dict(
        cart_items=cart_items,
        cart_total_quantity=total_quantity,
        cart_total_price=total_price
    )

# Inject datetime for footer year
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# --- Database Models ---

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    products = db.relationship('Product', backref='category', lazy=True)

    def __repr__(self):
        return f'<Category {self.name}>'

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=False)
    image_url = db.Column(db.String(300), nullable=True, default='default.jpg') # Path relative to static/images/products
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    available_sizes = db.Column(db.Text, nullable=True) # e.g., "40,41,42"
    available_colors = db.Column(db.Text, nullable=True) # e.g., "Black,White"
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    order_items = db.relationship('OrderItem', backref='product', lazy=True)

    def __repr__(self):
        return f'<Product {self.name}>'

# class User(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128))
#     name = db.Column(db.String(100), nullable=True)
#     address = db.Column(db.Text, nullable=True)
#     phone = db.Column(db.String(20), nullable=True)
#     orders = db.relationship('Order', backref='customer', lazy=True)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)

#     def __repr__(self):
#         return f'<User {self.email}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True) # Nullable for guest checkout
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending') # e.g., pending, processing, shipped, cancelled
    # Shipping details (denormalized for simplicity, especially for guests)
    shipping_address = db.Column(db.Text, nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=True)
    customer_name = db.Column(db.String(100), nullable=False) # Added customer name
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade="all, delete-orphan") # Use lazy='dynamic' for querying items

    def __repr__(self):
        return f'<Order {self.id} - Status: {self.status}>'

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False) # Price when the order was placed
    size_selected = db.Column(db.String(20), nullable=True)
    color_selected = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<OrderItem Order:{self.order_id} Product:{self.product_id} Qty:{self.quantity}>'


# --- Database Initialization Command ---
@app.cli.command('init-db')
def init_db_command():
    """Creates the database tables."""
    with app.app_context():
        db.create_all()
    click.echo('Initialized the database.')

# --- Basic Routes (Placeholder) ---
# --- Frontend Routes ---

@app.route('/')
def index():
    # Fetch a few featured products (e.g., latest 4)
    featured_products = Product.query.order_by(Product.date_added.desc()).limit(4).all()
    return render_template('index.html', featured_products=featured_products)

@app.route('/products')
def products_list():
    # Basic product list - add filtering/sorting later
    page = request.args.get('page', 1, type=int)
    query = Product.query.order_by(Product.name) # Simple ordering

    # TODO: Add filtering by category, size, color
    # TODO: Add sorting options

    products = query.paginate(page=page, per_page=12) # Show 12 products per page
    categories = Category.query.order_by(Category.name).all()
    return render_template('products.html', products=products, categories=categories)

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = Product.query.get_or_404(product_id)
    # Prepare sizes and colors if they exist
    available_sizes = product.available_sizes.split(',') if product.available_sizes else []
    available_colors = product.available_colors.split(',') if product.available_colors else []
    return render_template('product_detail.html',
                           product=product,
                           available_sizes=[s.strip() for s in available_sizes if s.strip()],
                           available_colors=[c.strip() for c in available_colors if c.strip()])

# --- Cart Routes ---

@app.route('/cart/add/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    quantity = request.form.get('quantity', 1, type=int)
    size = request.form.get('size')
    color = request.form.get('color')

    if quantity < 1:
        flash('Invalid quantity.', 'warning')
        return redirect(url_for('product_detail', product_id=product_id))

    # Basic stock check
    if product.stock_quantity < quantity:
         flash(f'Only {product.stock_quantity} items left in stock for {product.name}.', 'warning')
         return redirect(url_for('product_detail', product_id=product_id))

    cart = session.get('cart', {})
    cart_item_key = str(product_id) # Use product ID as key in session dict

    # Simple cart implementation: store product_id and quantity
    # For items with options (size/color), we might need a more complex key or structure
    # For simplicity now, we just overwrite/add based on product ID.
    # A better approach might involve unique keys per product+size+color combo.
    if cart_item_key in cart:
        # Check stock before increasing quantity
        new_quantity = cart[cart_item_key]['quantity'] + quantity
        if product.stock_quantity < new_quantity:
             flash(f'Cannot add {quantity} more. Only {product.stock_quantity - cart[cart_item_key]["quantity"]} additional items available.', 'warning')
             return redirect(url_for('product_detail', product_id=product_id))
        cart[cart_item_key]['quantity'] = new_quantity
    else:
        cart[cart_item_key] = {'quantity': quantity, 'size': size, 'color': color}

    session['cart'] = cart
    flash(f'{product.name} added to cart.', 'success')
    # Redirect back to the product page or the products list
    return redirect(request.referrer or url_for('products_list'))


@app.route('/cart')
def view_cart():
    # The context processor 'inject_cart' already prepares cart_items
    return render_template('cart.html')

@app.route('/cart/update/<int:product_id>', methods=['POST'])
def update_cart(product_id):
    quantity = request.form.get('quantity', type=int)
    cart = session.get('cart', {})
    cart_item_key = str(product_id)

    if cart_item_key not in cart:
        flash('Item not found in cart.', 'danger')
        return redirect(url_for('view_cart'))

    product = Product.query.get(product_id) # Get product for stock check
    if not product:
        # Should not happen if item is in cart, but good practice
        del cart[cart_item_key]
        session['cart'] = cart
        flash('Product not found, removed from cart.', 'warning')
        return redirect(url_for('view_cart'))

    if quantity is not None and quantity > 0:
         # Check stock before updating
        if product.stock_quantity < quantity:
            flash(f'Only {product.stock_quantity} items available for {product.name}. Quantity not updated.', 'warning')
        else:
            cart[cart_item_key]['quantity'] = quantity
            flash('Cart updated.', 'success')
    elif quantity is not None and quantity <= 0:
        # Remove item if quantity is 0 or less
        del cart[cart_item_key]
        flash('Item removed from cart.', 'success')
    else:
        flash('Invalid quantity.', 'warning')

    session['cart'] = cart
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    cart_item_key = str(product_id)

    if cart_item_key in cart:
        del cart[cart_item_key]
        session['cart'] = cart
        flash('Item removed from cart.', 'success')
    else:
        flash('Item not found in cart.', 'warning')

    return redirect(url_for('view_cart'))

# --- Checkout Routes (Placeholders) ---

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    cart = session.get('cart', {})
    if not cart:
        flash('Your cart is empty. Cannot proceed to checkout.', 'warning')
        return redirect(url_for('view_cart'))

    # Use the context processor data for display
    cart_context = inject_cart()
    cart_items = cart_context['cart_items']
    total_price = cart_context['cart_total_price']

    if request.method == 'POST':
        # --- Form Data Retrieval ---
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        address1 = request.form.get('shipping_address_line1')
        address2 = request.form.get('shipping_address_line2')
        city = request.form.get('city')
        state = request.form.get('state')
        zip_code = request.form.get('zip_code')

        # Basic validation (more robust validation can be added)
        if not all([customer_name, customer_email, address1, city, state, zip_code]):
            flash('Please fill in all required shipping details.', 'danger')
            return render_template('checkout.html', cart_items=cart_items, cart_total_price=total_price) # Re-render form

        full_address = f"{address1}\n"
        if address2:
            full_address += f"{address2}\n"
        full_address += f"{city}, {state} {zip_code}"

        # --- Order Creation ---
        try:
            new_order = Order(
                total_amount=total_price,
                status='pending', # Default status
                shipping_address=full_address,
                customer_email=customer_email,
                customer_phone=customer_phone,
                customer_name=customer_name
                # user_id could be added here if users are implemented and logged in
            )
            db.session.add(new_order)
            # We need the order ID for order items, so flush to get it
            db.session.flush()

            # --- Create Order Items & Update Stock ---
            for item in cart_items:
                product = item['product']
                quantity = item['quantity']

                # Double-check stock just before creating order item
                if product.stock_quantity < quantity:
                    db.session.rollback() # Rollback the entire transaction
                    flash(f'Error: Not enough stock for {product.name}. Order cancelled.', 'danger')
                    return redirect(url_for('view_cart'))

                order_item = OrderItem(
                    order_id=new_order.id,
                    product_id=product.id,
                    quantity=quantity,
                    price_at_purchase=product.price,
                    size_selected=item.get('size'),
                    color_selected=item.get('color')
                )
                db.session.add(order_item)

                # Decrease stock quantity
                product.stock_quantity -= quantity

            # Commit all changes (Order, OrderItems, Stock updates)
            db.session.commit()

            # Clear the cart
            session.pop('cart', None)

            flash('Order placed successfully!', 'success')
            return redirect(url_for('order_confirmation', order_id=new_order.id))

        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error placing order: {e}")
            flash(f'An error occurred while placing your order: {e}. Please try again.', 'danger')
            return redirect(url_for('checkout'))


    # GET request: just display the checkout page
    return render_template('checkout.html', cart_items=cart_items, cart_total_price=total_price)


@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    order = Order.query.options(db.joinedload(Order.items).joinedload(OrderItem.product)).get_or_404(order_id)
    # Security check: In a real app with users, ensure the current user owns this order or is admin
    return render_template('order_confirmation.html', order=order) # Need to create this template


# --- Admin Routes (Placeholders/Basic Setup) ---

# Simple hardcoded admin credentials (NOT FOR PRODUCTION)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD_HASH = generate_password_hash('password') # Change 'password'

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session['admin_logged_in'] = True
            session.permanent = True # Keep admin logged in
            flash('Login successful!', 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('admin_dashboard'))
        else:
            flash('Invalid credentials.', 'danger')
    return render_template('admin/login.html') # Need to create this template

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@login_required
def admin_dashboard():
    # Basic dashboard stats (example)
    product_count = Product.query.count()
    order_count = Order.query.count()
    pending_orders = Order.query.filter_by(status='pending').count()
    return render_template('admin/dashboard.html', # Need to create this template
                           product_count=product_count,
                           order_count=order_count,
                           pending_orders=pending_orders)

# --- Admin Product Management Routes ---

@app.route('/admin/products')
@login_required
def admin_products():
    """List all products in the admin panel."""
    page = request.args.get('page', 1, type=int)
    products = Product.query.order_by(Product.date_added.desc()).paginate(page=page, per_page=15)
    return render_template('admin/products_list.html', products=products)

@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def admin_add_product():
    """Add a new product."""
    categories = Category.query.order_by(Category.name).all()
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        category_id = request.form.get('category_id', type=int)
        stock_quantity = request.form.get('stock_quantity', type=int)
        available_sizes = request.form.get('available_sizes')
        available_colors = request.form.get('available_colors')
        image_file = request.files.get('image_file')

        if not all([name, price is not None, category_id is not None, stock_quantity is not None]):
            flash('Please fill in all required fields (Name, Price, Category, Stock).', 'danger')
            return render_template('admin/product_form.html', categories=categories, product=request.form) # Pass back form data

        # Check if category exists
        category = Category.query.get(category_id)
        if not category:
             flash('Invalid category selected.', 'danger')
             return render_template('admin/product_form.html', categories=categories, product=request.form)

        image_filename = None
        if image_file:
            image_filename = save_image(image_file)
            if image_filename is None: # save_image flashes error if needed
                 return render_template('admin/product_form.html', categories=categories, product=request.form)

        try:
            new_product = Product(
                name=name,
                description=description,
                price=price,
                category_id=category_id,
                stock_quantity=stock_quantity,
                available_sizes=available_sizes,
                available_colors=available_colors,
                image_url=image_filename # Will be None if no image uploaded or error
            )
            db.session.add(new_product)
            db.session.commit()
            flash(f'Product "{name}" added successfully!', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error adding product: {e}")
            flash(f'Error adding product: {e}', 'danger')

    # GET request
    return render_template('admin/product_form.html', categories=categories, product=None)


@app.route('/admin/products/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_product(product_id):
    """Edit an existing product."""
    product = Product.query.get_or_404(product_id)
    categories = Category.query.order_by(Category.name).all()

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price', type=float)
        category_id = request.form.get('category_id', type=int)
        stock_quantity = request.form.get('stock_quantity', type=int)
        available_sizes = request.form.get('available_sizes')
        available_colors = request.form.get('available_colors')
        image_file = request.files.get('image_file')

        if not all([name, price is not None, category_id is not None, stock_quantity is not None]):
            flash('Please fill in all required fields (Name, Price, Category, Stock).', 'danger')
            # Pass current product data back to form
            return render_template('admin/product_form.html', categories=categories, product=product)

        category = Category.query.get(category_id)
        if not category:
             flash('Invalid category selected.', 'danger')
             return render_template('admin/product_form.html', categories=categories, product=product)

        image_filename = product.image_url # Keep old image by default
        if image_file:
            # Consider deleting the old image file here if replacing
            new_image_filename = save_image(image_file)
            if new_image_filename:
                image_filename = new_image_filename
            else: # save_image flashes error
                 return render_template('admin/product_form.html', categories=categories, product=product)

        try:
            product.name = name
            product.description = description
            product.price = price
            product.category_id = category_id
            product.stock_quantity = stock_quantity
            product.available_sizes = available_sizes
            product.available_colors = available_colors
            product.image_url = image_filename
            db.session.commit()
            flash(f'Product "{product.name}" updated successfully!', 'success')
            return redirect(url_for('admin_products'))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating product {product_id}: {e}")
            flash(f'Error updating product: {e}', 'danger')

    # GET request
    return render_template('admin/product_form.html', categories=categories, product=product)


@app.route('/admin/products/delete/<int:product_id>', methods=['POST'])
@login_required
def admin_delete_product(product_id):
    """Delete a product."""
    product = Product.query.get_or_404(product_id)
    try:
        # Optional: Delete image file from filesystem first
        # if product.image_url and product.image_url != 'default.jpg':
        #     try:
        #         os.remove(os.path.join(app.config['UPLOAD_FOLDER'], product.image_url))
        #     except OSError as e:
        #         app.logger.error(f"Error deleting image file {product.image_url}: {e}")
        #         # Decide if you want to stop deletion if image removal fails

        db.session.delete(product)
        db.session.commit()
        flash(f'Product "{product.name}" deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting product {product_id}: {e}")
        # Check for foreign key constraints (e.g., if product is in an order)
        if 'FOREIGN KEY constraint failed' in str(e):
             flash(f'Cannot delete product "{product.name}" because it is part of an existing order. Consider disabling it instead.', 'danger')
        else:
            flash(f'Error deleting product: {e}', 'danger')

    return redirect(url_for('admin_products'))


# --- Admin Category Management Routes ---

@app.route('/admin/categories')
@login_required
def admin_categories():
    """List all categories."""
    categories = Category.query.order_by(Category.name).all()
    return render_template('admin/categories_list.html', categories=categories)

@app.route('/admin/categories/add', methods=['GET', 'POST'])
@login_required
def admin_add_category():
    """Add a new category."""
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Category name is required.', 'danger')
        else:
            try:
                # Check if category already exists (case-insensitive check might be better)
                existing_category = Category.query.filter(Category.name.ilike(name)).first()
                if existing_category:
                    flash(f'Category "{name}" already exists.', 'warning')
                else:
                    new_category = Category(name=name)
                    db.session.add(new_category)
                    db.session.commit()
                    flash(f'Category "{name}" added successfully!', 'success')
                    return redirect(url_for('admin_categories'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error adding category: {e}")
                flash(f'Error adding category: {e}', 'danger')
    # GET request or if POST failed
    return render_template('admin/category_form.html', category=None)


@app.route('/admin/categories/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_category(category_id):
    """Edit an existing category."""
    category = Category.query.get_or_404(category_id)
    if request.method == 'POST':
        name = request.form.get('name')
        if not name:
            flash('Category name is required.', 'danger')
        else:
            try:
                 # Check if new name conflicts with another existing category
                existing_category = Category.query.filter(Category.name.ilike(name), Category.id != category_id).first()
                if existing_category:
                     flash(f'Another category named "{name}" already exists.', 'warning')
                else:
                    category.name = name
                    db.session.commit()
                    flash(f'Category updated to "{name}" successfully!', 'success')
                    return redirect(url_for('admin_categories'))
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Error updating category {category_id}: {e}")
                flash(f'Error updating category: {e}', 'danger')
    # GET request or if POST failed
    return render_template('admin/category_form.html', category=category)


@app.route('/admin/categories/delete/<int:category_id>', methods=['POST'])
@login_required
def admin_delete_category(category_id):
    """Delete a category."""
    category = Category.query.get_or_404(category_id)
    # Check if category has associated products
    if category.products:
        flash(f'Cannot delete category "{category.name}" because it has associated products. Reassign products first.', 'danger')
    else:
        try:
            db.session.delete(category)
            db.session.commit()
            flash(f'Category "{category.name}" deleted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error deleting category {category_id}: {e}")
            flash(f'Error deleting category: {e}', 'danger')
    return redirect(url_for('admin_categories'))


# --- Admin Order Management Routes ---

@app.route('/admin/orders')
@login_required
def admin_orders():
    """List all orders, optionally filtered by status."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status')

    query = Order.query.order_by(Order.order_date.desc())
    if status_filter and status_filter != 'all':
        query = query.filter(Order.status == status_filter)

    orders = query.paginate(page=page, per_page=15)
    order_statuses = ['pending', 'processing', 'shipped', 'cancelled'] # Define possible statuses

    return render_template('admin/orders_list.html',
                           orders=orders,
                           order_statuses=order_statuses,
                           current_status=status_filter or 'all')


@app.route('/admin/orders/<int:order_id>')
@login_required
def admin_order_detail(order_id):
    """View details of a specific order."""
    order = Order.query.options(
        db.joinedload(Order.items).joinedload(OrderItem.product)
    ).get_or_404(order_id)
    order_statuses = ['pending', 'processing', 'shipped', 'cancelled']
    return render_template('admin/order_detail.html', order=order, order_statuses=order_statuses)


@app.route('/admin/orders/update_status/<int:order_id>', methods=['POST'])
@login_required
def admin_update_order_status(order_id):
    """Update the status of an order."""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    order_statuses = ['pending', 'processing', 'shipped', 'cancelled']

    if new_status not in order_statuses:
        flash('Invalid status selected.', 'danger')
    else:
        try:
            order.status = new_status
            db.session.commit()
            flash(f'Order #{order.id} status updated to "{new_status}".', 'success')
            # TODO: Optionally trigger email notification to customer about status change
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error updating status for order {order_id}: {e}")
            flash(f'Error updating order status: {e}', 'danger')

    return redirect(url_for('admin_order_detail', order_id=order_id))

# --- Helper Functions ---

def allowed_file(filename):
    """Checks if the filename has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_image(file):
    """Saves an uploaded image file securely."""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # Prevent overwriting: add unique prefix if file exists? Or handle in form logic.
        # For simplicity now, we might overwrite. Consider adding timestamp or UUID.
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(filepath)
            return filename # Return the saved filename
        except Exception as e:
            app.logger.error(f"Failed to save image {filename}: {e}")
            flash(f"Error saving image: {e}", "danger")
            return None
    elif file:
        flash("Invalid file type. Allowed types: png, jpg, jpeg, gif, webp", "warning")
    return None

# --- Main Execution ---
if __name__ == '__main__':
    # Note: Use 'flask run' in the terminal to start the development server
    # The following is only for direct script execution (less common with Flask CLI)
    app.run(debug=True) # debug=True should NOT be used in production
