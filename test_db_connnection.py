import mysql.connector

# Replace with your actual database credentials and information
db_config = {
    'host': '34.71.146.71', # Your Cloud SQL Public IP
    'user': 'main',
    'password': 'plz123emt',
    'database': 'ProjectDatabase',
    'port': 3306
}

try:
    # Establish the connection
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Example: Execute a query
    cursor.execute("SELECT VERSION()")
    db_version = cursor.fetchone()
    print(f"Database version: {db_version[0]}")

    # Example: Insert data
    insert_query = "INSERT INTO users (user_id, full_name, email, password_hash, role, phone, address, is_active) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    data_to_insert = ("1", "Max Hilsen", "mlhilsen@gmail.com", "testpassword", "user", "4047862248", "123 street", "1")
    cursor.execute(insert_query, data_to_insert)
    cnx.commit()
    print("Data inserted successfully.")

except mysql.connector.Error as err:
    print(f"Error: {err}")
finally:
    # Close the connection
    if 'cnx' in locals() and cnx.is_connected():
        cursor.close()
        cnx.close()
        print("MySQL connection closed.")
