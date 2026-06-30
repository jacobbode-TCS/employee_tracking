# Employee Tracker

A Flask-based employee tracking dashboard with an interactive web UI, SQLite persistence, and live client-side filtering.

## Features

- Add employees with name, title, email, department, hiring date, salary, phone number, and office location.
- Remove employees by name.
- Modify existing employee records using the employee name as the key.
- Live filtering across all employee fields.
- Table rows truncate long values to keep the layout clean, with inline "Show full" toggle.
- Persistent SQLite database stored in `employee_data.db`.
- Modern dashboard-style UI using Jinja2 templates and custom CSS.
- Sortable table columns for better data organization.

## Project Structure

- `main.py` — Flask application and REST endpoints.
- `templates/index.html` — Jinja2 HTML template for the employee tracker page.
- `static/app.js` — Client-side behavior for filtering, adding, removing, truncation, and inline expansion.
- `static/style.css` — Custom styling for the dashboard, forms, and table.
- `pyproject.toml` — Project metadata and dependency configuration.
- `employee_data.db` — Generated SQLite database file containing employee records.

## Requirements

- Python 3.14 or newer
- Flask 3.1.3 or newer

## Installation

This project is designed to be used with uv using 
```powershell
uv sync
```

If you are using python:

1. Create and activate a virtual environment (optional but recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Running Locally

From the project root:

using uv:
```powershell
uv run main.py
```

Using Python:
```powershell
python main.py
```

Then open `http://127.0.0.1:5000` in your browser.

## API Endpoints

- `GET /api/employees`
  - Returns the current list of employees as JSON.
- `POST /api/employees`
  - Adds a new employee.
  - Request body should be JSON with keys: `name`, `title`, `email`, `department`, `hiring_date`, `salary`, `phone_number`, `office_location`.
- `DELETE /api/employees`
  - Removes employee(s) by `name`.
  - Request body should be JSON with key: `name`.
- `PUT /api/employees`
  - Modifies an existing employee record by matching the provided current `name`.
  - Request body should be JSON with keys: `name`, plus any of `new_name`, `title`, `email`, `department`, `hiring_date`, `salary`, `phone_number`, `office_location`.

## Notes

- The SQLite database file is created automatically when the app starts, if it does not already exist.
- Employee names are matched case-insensitively when deleting records.
- The front-end keeps functionality intact while providing a refined visual presentation.

## License

This project is provided as-is.
