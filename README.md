# ShoeStore - E-commerce Prototype

Welcome to ShoeStore! This is a simple prototype of an e-commerce website for selling shoes, built with Python (Flask) and SQLite. It's designed to be easy to set up and manage, especially for users with limited technical experience.

**Features:**

*   **Frontend:** Homepage, Product Catalog (Grid View), Product Detail Page, Shopping Cart, Simulated Checkout, Order Confirmation.
*   **Backend:** Built with Flask, using SQLite for simple database management.
*   **Admin Panel:** Secure login, Product Management (Add, Edit, Delete, Image Upload), Category Management (Add, Edit, Delete), Order Viewing & Status Updates.

---

## Table of Contents

1.  [Prerequisites](#prerequisites)
2.  [Installation](#installation)
3.  [Database Setup](#database-setup)
4.  [Running the Application](#running-the-application)
5.  [Accessing the Site](#accessing-the-site)
6.  [Database Management (for Beginners)](#database-management-for-beginners)
7.  [Using the Admin Panel](#using-the-admin-panel)
8.  [Basic E-commerce Concepts](#basic-e-commerce-concepts)
9.  [Project Structure](#project-structure)

---

## 1. Prerequisites

Before you start, make sure you have the following installed on your computer:

*   **Python 3:** This project requires Python version 3.6 or newer. You can download it from [python.org](https://www.python.org/downloads/). During installation, make sure to check the box that says "Add Python to PATH" (or similar).
*   **pip:** This is Python's package installer. It usually comes bundled with Python 3. You can check if it's installed by opening your terminal or command prompt and typing `pip --version`.

---

## 2. Installation

Follow these steps to set up the project on your computer:

1.  **Get the Code:**
    *   If you received the code as a folder (e.g., `esempio_ecommerce`), you already have it.
    *   If it's a Git repository, you would typically use `git clone <repository_url>`.

2.  **Open a Terminal or Command Prompt:**
    *   Navigate to the project directory. This is the folder containing the `app.py` file (e.g., `esempio_ecommerce`). You can usually do this using the `cd` command. For example:
        ```bash
        cd path/to/esempio_ecommerce
        ```
        (Replace `path/to/esempio_ecommerce` with the actual path on your computer).

3.  **Create a Virtual Environment (Recommended):**
    *   A virtual environment keeps the project's dependencies separate from other Python projects on your system. It's good practice!
    *   Run the following command in your terminal (inside the project folder):
        ```bash
        python3 -m venv venv
        ```
        (On some systems, you might just use `python` instead of `python3`).
    *   This creates a folder named `venv` in your project directory.

4.  **Activate the Virtual Environment:**
    *   **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    *   **On Windows (Command Prompt):**
        ```bash
        venv\Scripts\activate.bat
        ```
    *   **On Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate.ps1
        ```
        (If you get an error on PowerShell about execution policies, you might need to run `Set-ExecutionPolicy Unrestricted -Scope Process` first, then try activating again).
    *   You'll know the environment is active because your terminal prompt will usually change to show `(venv)` at the beginning.

5.  **Install Dependencies:**
    *   While the virtual environment is active, run this command to install all the necessary Python packages listed in `requirements.txt`:
        ```bash
        pip install -r requirements.txt
        ```
    *   This will download and install Flask, Flask-SQLAlchemy, and other needed tools into your `venv`.

---

## 3. Database Setup

This application uses SQLite, which stores the entire database in a single file named `database.db`. You need to create this file and set up the necessary tables the first time.

1.  **Make sure your virtual environment is active** (see step 4 in Installation).
2.  **Make sure you are in the project directory** in your terminal.
3.  **Run the initialization command:**
    ```bash
    flask init-db
    ```
4.  You should see a message like `Initialized the database.`. This command creates the `database.db` file in your project folder and sets up the tables (`products`, `categories`, `orders`, `order_items`).

You only need to run `flask init-db` **once** when setting up the project for the first time.

---

## 4. Running the Application

To start the website development server:

1.  **Make sure your virtual environment is active.**
2.  **Make sure you are in the project directory** in your terminal.
3.  **Run the Flask development server:**
    ```bash
    flask run
    ```
4.  You should see output similar to this:
    ```
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: xxx-xxx-xxx
    ```
5.  The website is now running locally on your computer! Keep the terminal window open while you are using the site. To stop the server, go back to the terminal and press `CTRL + C`.

---

## 5. Accessing the Site

While the server is running (after `flask run`):

*   **Main Website:** Open your web browser (like Chrome, Firefox, Safari, Edge) and go to:
    [http://127.0.0.1:5000/](http://127.0.0.1:5000/)
    or
    [http://localhost:5000/](http://localhost:5000/)

*   **Admin Panel:** To access the administration area, go to:
    [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)

    You will be asked to log in. Use the following default credentials:
    *   **Username:** `admin`
    *   **Password:** `password`

    **(Security Note:** These are default credentials for the prototype ONLY. For a real website, you would need a much more secure way to manage admin access.)*

---

## 6. Database Management (for Beginners)

*   **What is SQLite?**
    *   Think of SQLite as a simple database contained entirely within a single file. Unlike bigger databases (like MySQL or PostgreSQL), it doesn't require a separate server program to be running.
    *   This makes it very easy to manage for small projects or prototypes like this one.

*   **Where is the Database File?**
    *   The database file for this project is named `database.db`.
    *   It is located in the main project folder (the same folder as `app.py`).
    *   You can easily back up your data just by copying this `database.db` file somewhere safe.

*   **How to View or Edit Data (If Necessary):**
    *   The **recommended** way to manage products, categories, and view orders is through the **Admin Panel** ([http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin)).
    *   However, if you ever need to look directly at the data tables or make manual changes (e.g., for troubleshooting or bulk editing), you can use a free graphical tool. A popular choice is **DB Browser for SQLite**: [https://sqlitebrowser.org/](https://sqlitebrowser.org/)
    *   **Using DB Browser for SQLite:**
        1.  Download and install it from their website.
        2.  Open the application.
        3.  Click "Open Database".
        4.  Navigate to your project folder (`esempio_ecommerce`) and select the `database.db` file.
        5.  You can now click on the "Browse Data" tab.
        6.  Select a table (like `products`, `categories`, `orders`) from the dropdown menu to view its contents.
        7.  You can edit cells directly or add/delete rows using the buttons.
    *   **WARNING:** Be very careful when editing the database directly! You could accidentally break the website if you enter incorrect data or delete something important. **Always prefer using the Admin Panel when possible.**

*   **Understanding the Main Tables:**
    *   `categories`: Stores the different types of shoes (e.g., "Running Shoes", "Formal Shoes", "Sneakers"). Each product belongs to one category.
    *   `products`: This is the main table holding information about each shoe: its name, description, price, which category it belongs to, the filename of its image, how many are in stock (`stock_quantity`), and available sizes/colors.
    *   `orders`: When a customer completes the checkout, a record is created here storing the order date, total amount, customer's shipping details (name, email, address), and the order status (like 'pending', 'shipped').
    *   `order_items`: This table links the `orders` and `products` tables. For each product included in an order, a row is added here specifying which order it belongs to, which product it is, the quantity ordered, and the price at the time of purchase.

---

## 7. Using the Admin Panel

Access the admin panel at [http://127.0.0.1:5000/admin](http://127.0.0.1:5000/admin) (login with `admin` / `password`).

*   **Dashboard:** Shows a quick overview (total products, orders, pending orders).
*   **Products:**
    *   View a list of all products.
    *   Click "Add New Product" to create a new shoe listing. Fill in the details (name, description, price, category, stock). You can also upload an image here.
    *   Click "Edit" next to a product to modify its details or change its image.
    *   Click "Delete" to remove a product (you'll be asked for confirmation). Note: You usually cannot delete a product if it's part of an existing order.
*   **Categories:**
    *   View existing categories.
    *   Click "Add New Category" to create one (e.g., "Sandals").
    *   Click "Edit" to rename a category.
    *   Click "Delete" to remove a category (only possible if no products are assigned to it).
*   **Orders:**
    *   View a list of all customer orders, sorted by date.
    *   You can filter orders by status (e.g., view only 'pending' orders).
    *   Click "Details" next to an order to see the customer's information, the items they ordered, and the total amount.
    *   On the Order Detail page, you can update the order status (e.g., change from 'pending' to 'shipped') using the dropdown menu and clicking "Update".

---

## 8. Basic E-commerce Concepts

*   **Order:** An order represents a customer's request to purchase items. In this system, an order is created when the customer fills out the checkout form and clicks "Place Order". It contains the customer's details and a list of the items they bought.
*   **Inventory Management:** The `stock_quantity` field in the `products` table tracks how many units of a specific shoe are available. When an order is placed, the system automatically reduces the stock quantity for the purchased items. The "Add to Cart" button is disabled if stock is zero.
*   **Simulated Payments:** This prototype **does not** handle real money or connect to payment gateways (like Stripe or PayPal). The checkout process only collects shipping information and records the order with a 'pending' status. Integrating actual payments is a more complex step required for a live store.

---

## 9. Project Structure

Here's a brief overview of the main files and folders:

*   `app.py`: The main Flask application file containing the server logic, routes (URL handling), database models, and connections.
*   `database.db`: The SQLite database file (created by `flask init-db`). **Contains all your data!**
*   `requirements.txt`: Lists the Python packages needed for the project.
*   `README.md`: This file!
*   `templates/`: Contains all the HTML files used to display the website pages.
    *   `base.html`: The main layout template (header, footer, navigation).
    *   `index.html`, `products.html`, `product_detail.html`, etc.: Templates for specific frontend pages.
    *   `admin/`: Contains templates specifically for the Admin Panel (`admin_base.html`, `login.html`, `products_list.html`, etc.).
*   `static/`: Contains files that are served directly by the web server (CSS, JavaScript, Images).
    *   `css/style.css`: Custom styles for the website.
    *   `js/script.js`: Custom JavaScript for interactivity.
    *   `images/`: Folder for storing images.
        *   `products/`: Product images uploaded via the admin panel are saved here.
        *   `logo_placeholder.png`, `hero_placeholder.png`: Placeholder images used in the templates.
*   `venv/`: The virtual environment folder (created during installation). Contains the installed Python packages for this project only. You generally don't need to modify anything inside this folder.

---

Enjoy using your ShoeStore prototype!
