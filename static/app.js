const tableBody = document.querySelector('#employee-table tbody');
const addForm = document.querySelector('#employee-form');
const removeForm = document.querySelector('#remove-form');
const modifyForm = document.querySelector('#modify-form');
const filterInputs = Array.from(document.querySelectorAll('.filter-field'));
const sortButtons = Array.from(document.querySelectorAll('.sort-button'));
const feedback = document.querySelector('#form-feedback');

let currentSortField = null;
let currentSortDirection = 'asc';

function truncateText(text) {
  return text.length > 10 ? `${text.slice(0, 10)}...` : text;
}

function setCellValue(cell, fullText) {
  cell.dataset.full = fullText;
  const textSpan = cell.querySelector('.cell-text');
  if (textSpan) {
    textSpan.textContent = truncateText(fullText);
  } else {
    const span = document.createElement('span');
    span.className = 'cell-text';
    span.textContent = truncateText(fullText);
    cell.textContent = '';
    cell.appendChild(span);
  }
}

function getCellValue(cell) {
  return (cell.dataset.full || cell.textContent || '').trim().toLowerCase();
}

function updateRowDisplay(row, fullMode) {
  row.classList.toggle('full-mode', fullMode);

  row.querySelectorAll('td').forEach((cell) => {
    if (cell.classList.contains('action-cell')) {
      return;
    }
    const fullText = cell.dataset.full || '';
    const textSpan = cell.querySelector('.cell-text');
    if (textSpan) {
      textSpan.textContent = fullMode ? fullText : truncateText(fullText);
    }
  });

  const button = row.querySelector('.full-toggle');
  if (button) {
    button.textContent = fullMode ? 'Hide full' : 'Show full';
  }
}

function toggleRowFull(row) {
  const fullMode = row.dataset.fullExpanded !== 'true';
  row.dataset.fullExpanded = fullMode ? 'true' : 'false';
  updateRowDisplay(row, fullMode);
}

function initializeRow(row) {
  row.querySelectorAll('td').forEach((cell) => {
    if (cell.classList.contains('action-cell')) {
      return;
    }
    const fullText = cell.dataset.full || cell.textContent.trim();
    setCellValue(cell, fullText);
  });

  const button = row.querySelector('.full-toggle');
  if (button) {
    button.addEventListener('click', () => toggleRowFull(row));
  }
}

function initializeRows() {
  const rows = Array.from(tableBody.querySelectorAll('tr.employee-row'));
  rows.forEach(initializeRow);
}

initializeRows();

function clearEmptyState() {
  const emptyRow = tableBody.querySelector('.empty-state-row');
  if (emptyRow) {
    emptyRow.remove();
  }
}

function createEmptyStateRow(message = 'No employees have been added yet.') {
  const row = document.createElement('tr');
  row.classList.add('empty-state-row');
  row.innerHTML = `
    <td colspan="9" class="empty-state">${message}</td>
  `;
  tableBody.appendChild(row);
}

function getFilterValues() {
  return filterInputs.reduce((filters, input) => {
    filters[input.name] = input.value.trim().toLowerCase();
    return filters;
  }, {});
}

function rowMatchesFilters(row, filters) {
  const cells = row.querySelectorAll('td');
  const values = {
    name: getCellValue(cells[0]),
    title: getCellValue(cells[1]),
    email: getCellValue(cells[2]),
    department: getCellValue(cells[3]),
    hiring_date: getCellValue(cells[4]),
    salary: getCellValue(cells[5]),
    phone_number: getCellValue(cells[6]),
    office_location: getCellValue(cells[7]),
  };

  return Object.entries(filters).every(([field, term]) => {
    return !term || values[field].includes(term);
  });
}

function applyFilters() {
  const filters = getFilterValues();
  const rows = Array.from(tableBody.querySelectorAll('tr.employee-row'));
  let visibleCount = 0;

  rows.forEach((row) => {
    const match = rowMatchesFilters(row, filters);
    row.hidden = !match;
    if (match) {
      visibleCount += 1;
    }
  });

  const emptyRow = tableBody.querySelector('.empty-state-row');
  const message = rows.length > 0 ? 'No employees match the current filters.' : 'No employees have been added yet.';

  if (visibleCount === 0) {
    if (emptyRow) {
      emptyRow.querySelector('td').textContent = message;
    } else {
      createEmptyStateRow(message);
    }
  } else if (emptyRow) {
    emptyRow.remove();
  }
}

function compareCellValues(a, b) {
  const dateA = Date.parse(a);
  const dateB = Date.parse(b);

  if (!Number.isNaN(dateA) && !Number.isNaN(dateB)) {
    return dateA - dateB;
  }

  const numA = parseFloat(a.replace(/[^0-9.-]+/g, ''));
  const numB = parseFloat(b.replace(/[^0-9.-]+/g, ''));

  if (!Number.isNaN(numA) && !Number.isNaN(numB)) {
    return numA - numB;
  }

  return a.localeCompare(b, undefined, { numeric: true, sensitivity: 'base' });
}

function sortRows(field) {
  const columnIndex = {
    name: 0,
    title: 1,
    email: 2,
    department: 3,
    hiring_date: 4,
    salary: 5,
    phone_number: 6,
    office_location: 7,
  }[field];

  if (currentSortField === field) {
    currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
  } else {
    currentSortField = field;
    currentSortDirection = 'asc';
  }

  sortButtons.forEach((button) => {
    const icon = button.querySelector('.sort-icon');
    const isActive = button.dataset.field === field;
    button.classList.toggle('active', isActive);
    if (icon) {
      icon.textContent = isActive
        ? currentSortDirection === 'asc' ? '▲' : '▼'
        : '⇅';
    }
  });

  const rows = Array.from(tableBody.querySelectorAll('tr.employee-row'));
  rows.sort((a, b) => {
    const aValue = getCellValue(a.querySelectorAll('td')[columnIndex]);
    const bValue = getCellValue(b.querySelectorAll('td')[columnIndex]);
    const result = compareCellValues(aValue, bValue);
    return currentSortDirection === 'asc' ? result : -result;
  });

  rows.forEach((row) => tableBody.appendChild(row));
}

function addRow(employee) {
  clearEmptyState();

  const row = document.createElement('tr');
  row.classList.add('employee-row');
  row.innerHTML = `
    <td>${employee.name || ''}</td>
    <td>${employee.title || ''}</td>
    <td>${employee.email || ''}</td>
    <td>${employee.department || ''}</td>
    <td>${employee.hiring_date || ''}</td>
    <td>${employee.salary || ''}</td>
    <td>${employee.phone_number || ''}</td>
    <td>${employee.office_location || ''}</td>
    <td class="action-cell"><button type="button" class="full-toggle">Show full</button></td>
  `;
  tableBody.appendChild(row);
  initializeRow(row);
  applyFilters();
}

function getRowsByName(name) {
  const lowerName = name.trim().toLowerCase();
  return Array.from(tableBody.querySelectorAll('tr.employee-row')).filter((row) => {
    const cell = row.querySelector('td');
    return cell && getCellValue(cell) === lowerName;
  });
}

function updateRowWithEmployee(row, employee) {
  const fullMode = row.dataset.fullExpanded === 'true';
  row.innerHTML = `
    <td>${employee.name || ''}</td>
    <td>${employee.title || ''}</td>
    <td>${employee.email || ''}</td>
    <td>${employee.department || ''}</td>
    <td>${employee.hiring_date || ''}</td>
    <td>${employee.salary || ''}</td>
    <td>${employee.phone_number || ''}</td>
    <td>${employee.office_location || ''}</td>
    <td class="action-cell"><button type="button" class="full-toggle">${fullMode ? 'Hide full' : 'Show full'}</button></td>
  `;
  initializeRow(row);
  updateRowDisplay(row, fullMode);
}

function removeRowsByName(name) {
  const lowerName = name.trim().toLowerCase();
  const rows = Array.from(tableBody.querySelectorAll('tr.employee-row'));
  let removed = 0;

  rows.forEach((row) => {
    const cell = row.querySelector('td');
    if (!cell) {
      return;
    }

    if (getCellValue(cell) === lowerName) {
      row.remove();
      removed += 1;
    }
  });

  return removed;
}

function showMessage(message, isError = false) {
  feedback.textContent = message;
  feedback.classList.toggle('error', isError);
}

filterInputs.forEach((input) => {
  input.addEventListener('input', applyFilters);
});

sortButtons.forEach((button) => {
  button.addEventListener('click', () => sortRows(button.dataset.field));
});

addForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(addForm);
  const employee = {
    name: formData.get('name').trim(),
    title: formData.get('title').trim(),
    email: formData.get('email').trim(),
    department: formData.get('department').trim(),
    hiring_date: formData.get('hiring_date').trim(),
    salary: formData.get('salary').trim(),
    phone_number: formData.get('phone_number').trim(),
    office_location: formData.get('office_location').trim(),
  };

  if (!employee.name) {
    showMessage('Name is required.', true);
    return;
  }

  try {
    const response = await fetch('/api/employees', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(employee),
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || 'Unable to add employee.', true);
      return;
    }

    addRow(data.employee);
    addForm.reset();
    showMessage('Employee added successfully!');
  } catch (error) {
    showMessage('Network error. Please try again.', true);
    console.error(error);
  }
});

removeForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(removeForm);
  const name = formData.get('name').trim();

  if (!name) {
    showMessage('Name is required to remove an employee.', true);
    return;
  }

  try {
    const response = await fetch('/api/employees', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ name }),
    });

    const data = await response.json();

    if (!response.ok) {
      showMessage(data.error || 'Unable to remove employee.', true);
      return;
    }

    const removed = removeRowsByName(name);
    if (removed === 0) {
      createEmptyStateRow();
    }

    removeForm.reset();
    showMessage(data.message);
  } catch (error) {
    showMessage('Network error. Please try again.', true);
    console.error(error);
  }
});

modifyForm.addEventListener('submit', async (event) => {
  event.preventDefault();
  const formData = new FormData(modifyForm);
  const payload = {
    name: formData.get('existing_name').trim(),
    new_name: formData.get('new_name').trim(),
    title: formData.get('title').trim(),
    email: formData.get('email').trim(),
    department: formData.get('department').trim(),
    hiring_date: formData.get('hiring_date').trim(),
    salary: formData.get('salary').trim(),
    phone_number: formData.get('phone_number').trim(),
    office_location: formData.get('office_location').trim(),
  };

  if (!payload.name) {
    showMessage('Existing employee name is required.', true);
    return;
  }

  try {
    const response = await fetch('/api/employees', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    const data = await response.json();
    if (!response.ok) {
      showMessage(data.error || 'Unable to modify employee.', true);
      return;
    }

    const rows = getRowsByName(payload.name);
    if (rows.length > 0) {
      rows.forEach((row) => updateRowWithEmployee(row, data.employee));
      if (payload.new_name) {
        const updatedRows = getRowsByName(payload.new_name);
        if (updatedRows.length === 0 && rows.length > 0) {
          updateRowWithEmployee(rows[0], data.employee);
        }
      }
    }

    modifyForm.reset();
    showMessage(data.message);
  } catch (error) {
    showMessage('Network error. Please try again.', true);
    console.error(error);
  }
});
