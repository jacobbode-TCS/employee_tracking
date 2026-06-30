from flask import Flask, jsonify, request, render_template
import sqlite3
from pathlib import Path

# Build the app with the static folder and template folder, then define database file path.
app = Flask(__name__, static_folder='static', template_folder='templates')
DB_FILE = Path(__file__).with_name('employee_data.db')


# function to connect to sqllite database
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


# function to initialize the database with the features below
def init_db():
    with get_db_connection() as conn:
        conn.execute(
            '''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                title TEXT,
                email TEXT,
                department TEXT,
                hiring_date TEXT,
                salary TEXT,
                phone_number TEXT,
                office_location TEXT
            )
            '''
        )
        conn.commit()

# function to fetch all employee details from the database
def fetch_employees():
    with get_db_connection() as conn:
        rows = conn.execute(
            'SELECT name, title, email, department, hiring_date, salary, phone_number, office_location FROM employees ORDER BY id'
        ).fetchall()
        return [dict(row) for row in rows]


# function to fetch individual employee details by name
def fetch_employee_by_name(name):
    with get_db_connection() as conn:
        row = conn.execute(
            'SELECT name, title, email, department, hiring_date, salary, phone_number, office_location FROM employees WHERE lower(name) = lower(?)',
            (name.strip(),),
        ).fetchone()
        return dict(row) if row else None


# function to update individual employee details by name, returns the number of rows updated
def update_employee_by_name(name, updates):
    # Updating done by building up a dynamic SQL query based on the fields the user gave us. The columns to update goes in columns, and the values associated with each updated column
    columns = []
    values = []

    # If the user wants to update the name, we have to handle it separately since it is also the primary key of the database.
    if updates.get('new_name'):
        columns.append('name = ?')
        values.append(updates['new_name'].strip())

    # For each feature (aside from name), if there is a new value provided by the user, we queue it up for updating in the database
    for field in ['title', 'email', 'department', 'hiring_date', 'salary', 'phone_number', 'office_location']:
        if updates.get(field):
            columns.append(f'{field} = ?')
            values.append(updates[field].strip())

    if not columns:
        return 0

    values.append(name.strip())
    with get_db_connection() as conn:
        cursor = conn.execute(
            f'UPDATE employees SET {", ".join(columns)} WHERE lower(name) = lower(?)',
            values,
        )
        conn.commit()
        return cursor.rowcount


# function to insert employee into the database (Note that empty fields are allowed)
def insert_employee(employee):
    with get_db_connection() as conn:
        conn.execute(
            'INSERT INTO employees (name, title, email, department, hiring_date, salary, phone_number, office_location) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
            (
                employee.get('name', '').strip(),
                employee.get('title', '').strip(),
                employee.get('email', '').strip(),
                employee.get('department', '').strip(),
                employee.get('hiring_date', '').strip(),
                employee.get('salary', '').strip(),
                employee.get('phone_number', '').strip(),
                employee.get('office_location', '').strip(),
            ),
        )
        conn.commit()


# function to delete employee by name, returns the number of rows deleted
def delete_employee_by_name(name):
    with get_db_connection() as conn:
        cursor = conn.execute(
            'DELETE FROM employees WHERE lower(name) = lower(?)',
            (name.strip(),),
        )
        conn.commit()
        return cursor.rowcount


# Make the database in sqllite
init_db()


# Route the landing page to the index.html template and pass employee data for rendering
@app.route('/')
def index():
    return render_template('index.html', employees=fetch_employees())


# Get method to fetch employee details 
@app.route('/api/employees', methods=['GET'])
def get_employees():
    return jsonify(fetch_employees())


# use POST method of api/employees to add the employee details
@app.route('/api/employees', methods=['POST'])
def add_employee():
    # Get the json information
    new_employee = request.get_json(force=True) or {}

    # Ensure the employee name is actually given and not just whitespace; if not, return 400 error
    if not new_employee.get('name') or not new_employee['name'].strip():
        return jsonify({'error': 'Employee name is required.'}), 400

    # Put the employee into the database
    insert_employee(new_employee)

    return jsonify({
        'message': 'Employee added successfully!',
        'employee': {
            'name': new_employee.get('name', '').strip(),
            'title': new_employee.get('title', '').strip(),
            'email': new_employee.get('email', '').strip(),
            'department': new_employee.get('department', '').strip(),
            'hiring_date': new_employee.get('hiring_date', '').strip(),
            'salary': new_employee.get('salary', '').strip(),
            'phone_number': new_employee.get('phone_number', '').strip(),
            'office_location': new_employee.get('office_location', '').strip(),
        },
    }), 201


# Use DELETE method of api/employees to delete the employee details
@app.route('/api/employees', methods=['DELETE'])
def delete_employee():
    # Get the json information and retrieve the name
    payload = request.get_json(force=True) or {}
    name = payload.get('name', '').strip()

    # If the name is not given, return 400 error
    if not name:
        return jsonify({'error': 'Employee name is required for deletion.'}), 400

    # Delete the employee by name and check if there was any employees by that name, if not, return 404 error
    removed = delete_employee_by_name(name)
    if removed == 0:
        return jsonify({'error': f'No employee found with name "{name}".'}), 404

    return jsonify({
        'message': f'Removed {removed} employee(s) with the name "{name}".',
        'removed': removed,
    }), 200


# Use PUT method of api/employees to modify the employee details
@app.route('/api/employees', methods=['PUT'])
def modify_employee():
    # Get the json information and retrieve the name
    payload = request.get_json(force=True) or {}
    name = payload.get('name', '').strip()

    # If the name is not given, return 400 error
    if not name:
        return jsonify({'error': 'Existing employee name is required for modification.'}), 400

    # Get the modified information from json
    updates = {
        'new_name': payload.get('new_name', '').strip(),
        'title': payload.get('title', '').strip(),
        'email': payload.get('email', '').strip(),
        'department': payload.get('department', '').strip(),
        'hiring_date': payload.get('hiring_date', '').strip(),
        'salary': payload.get('salary', '').strip(),
        'phone_number': payload.get('phone_number', '').strip(),
        'office_location': payload.get('office_location', '').strip(),
    }
    # Take out any field left empty since that means the user wants to keep the original value
    updates = {key: value for key, value in updates.items() if value}

    # If the user did not include any field to update, return 400 error
    if not updates:
        return jsonify({'error': 'Provide at least one field to update.'}), 400

    # Search for the employee by name and update the accompanying fields.
    updated = update_employee_by_name(name, updates)

    # If no employee was found with the given name, return 404 error
    if updated == 0:
        return jsonify({'error': f'No employee found with name "{name}".'}), 404

    # If the name of the employee was updated, fetch the employee by the new name; otherwise, fetch by the original name.
    target_name = updates.get('new_name', name)
    employee = fetch_employee_by_name(target_name)

    return jsonify({
        'message': f'Updated employee "{name}".',
        'employee': employee,
    }), 200


# Only run if this script is called directly
if __name__ == "__main__":
    app.run()
