from flask import Flask, render_template, request, redirect, url_for
import mysql.connector

app = Flask(__name__)

# Consolidated low-level database engine configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Anant@22',
    'database': 'salespulse'
}

@app.route("/", methods=["GET", "POST"])
def dashboard():
    connection = None
    try:
        # 1. Open direct connection channel lifecycle
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # HANDLE INGESTION (POST)
        if request.method == "POST":
            product_name = request.form.get("product_name")
            amount = request.form.get("amount")

            if product_name and amount:
                # Parameterized raw SQL query fundamentals
                insert_query = "INSERT INTO sales (product_name, amount) VALUES (%s, %s);"
                cursor.execute(insert_query, (product_name, int(amount)))
                
                # Manual transaction boundary commit control
                connection.commit()
            
            cursor.close()
            return redirect(url_for("dashboard"))

        # HANDLE DATA FETCH (GET)
        # Fetch grouped unique products
        cursor.execute("""
             SELECT product_name, MAX(amount)
             FROM sales
             GROUP BY product_name
             ORDER BY MAX(amount) DESC;
        """)

        sales_data = cursor.fetchall()

        # Safely computing aggregation with a fallback check
        cursor.execute("SELECT SUM(amount) FROM sales;")
        revenue_row = cursor.fetchone()
        total_revenue = revenue_row[0] if revenue_row and revenue_row[0] is not None else 0

        # Clean cursor allocation teardown
        cursor.close()
        
        return render_template(
            "dashboard.html",
            sales=sales_data,
            total_revenue=total_revenue
        )

    except mysql.connector.Error as err:
        return f"Database Connection/Query Error: {str(err)}", 500

    finally:
        # 2. Strict cleanup block ensuring sockets close regardless of app failures
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    app.run(debug=True)