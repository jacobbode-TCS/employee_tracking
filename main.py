from flask import Flask, jsonify, request, render_template
import sqlite3
from pathlib import Path

app = Flask(__name__, static_folder='static', template_folder='templates')
DB_FILE = Path(__file__).with_name('employee_data.db')


def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


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


def fetch_employees():
    with get_db_connection() as conn:
        rows = conn.execute(
            'SELECT name, title, email, department, hiring_date, salary, phone_number, office_location FROM employees ORDER BY id'
        ).fetchall()
        return [dict(row) for row in rows]


def fetch_employee_by_name(name):
    with get_db_connection() as conn:
        row = conn.execute(
            'SELECT name, title, email, department, hiring_date, salary, phone_number, office_location FROM employees WHERE lower(name) = lower(?)',
            (name.strip(),),
        ).fetchone()
        return dict(row) if row else None


def update_employee_by_name(name, updates):
    columns = []
    values = []

    if updates.get('new_name'):
        columns.append('name = ?')
        values.append(updates['new_name'].strip())

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


def delete_employee_by_name(name):
    with get_db_connection() as conn:
        cursor = conn.execute(
            'DELETE FROM employees WHERE lower(name) = lower(?)',
            (name.strip(),),
        )
        conn.commit()
        return cursor.rowcount


init_db()


@app.route('/')
def index():
    return render_template('index.html', employees=fetch_employees())


@app.route('/api/employees', methods=['GET'])
def get_employees():
    return jsonify(fetch_employees())


@app.route('/api/employees', methods=['POST'])
def add_employee():
    new_employee = request.get_json(force=True) or {}

    if not new_employee.get('name') or not new_employee['name'].strip():
        return jsonify({'error': 'Employee name is required.'}), 400

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


@app.route('/api/employees', methods=['DELETE'])
def delete_employee():
    payload = request.get_json(force=True) or {}
    name = payload.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Employee name is required for deletion.'}), 400

    removed = delete_employee_by_name(name)
    if removed == 0:
        return jsonify({'error': f'No employee found with name "{name}".'}), 404

    return jsonify({
        'message': f'Removed {removed} employee(s) with the name "{name}".',
        'removed': removed,
    }), 200


@app.route('/api/employees', methods=['PUT'])
def modify_employee():
    payload = request.get_json(force=True) or {}
    name = payload.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Existing employee name is required for modification.'}), 400

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
    updates = {key: value for key, value in updates.items() if value}

    if not updates:
        return jsonify({'error': 'Provide at least one field to update.'}), 400

    updated = update_employee_by_name(name, updates)
    if updated == 0:
        return jsonify({'error': f'No employee found with name "{name}".'}), 404

    target_name = updates.get('new_name', name)
    employee = fetch_employee_by_name(target_name)

    return jsonify({
        'message': f'Updated employee "{name}".',
        'employee': employee,
    }), 200


if __name__ == "__main__":
    app.run(debug=True)
