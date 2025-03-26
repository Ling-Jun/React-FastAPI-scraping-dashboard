export function determineRowClass (status) {
  if (status.includes('SIGNIFICANT CHANGE!')) {
    return 'significant'
  } else if (status.includes('TRIVIAL CHANGE!')) {
    return 'trivial'
  } else {
    return 'default'
  }
}

export function toggleDiff (button) {
  const diffRow = button.closest('tr').nextElementSibling
  diffRow.style.display =
    diffRow.style.display === 'none' ? 'table-row' : 'none'
}

export function filterTable () {
  const pageFilter = document.getElementById('filter-page').value.toLowerCase()
  const dateFilter = document.getElementById('filter-date').value.toLowerCase()
  const statusFilter = document
    .getElementById('filter-status')
    .value.toLowerCase()

  const rows = document.querySelectorAll('#grant-table tbody tr')

  for (let i = 0; i < rows.length; i += 2) {
    // Skip diff rows
    const row = rows[i]
    const page = row.cells[0].textContent.toLowerCase()
    const date = row.cells[1].textContent.toLowerCase()
    const status = row.cells[2].textContent.toLowerCase()

    if (
      page.includes(pageFilter) &&
      date.includes(dateFilter) &&
      status.includes(statusFilter)
    ) {
      row.style.display = ''
      rows[i + 1].style.display = 'none' // Hide diff row when filtering
    } else {
      row.style.display = 'none'
      rows[i + 1].style.display = 'none' // Hide diff row when filtering
    }
  }
}

export function toggleAllNonSignificantRows () {
  const trivialRows = document.querySelectorAll('.trivial')
  const defaultRows = document.querySelectorAll('.default')
  const globalBtn = document.getElementById('toggleAllRowbtn')

  const areHidden =
    (trivialRows.length > 0 &&
      window.getComputedStyle(trivialRows[0]).display === 'none') ||
    (defaultRows.length > 0 &&
      window.getComputedStyle(defaultRows[0]).display === 'none')

  trivialRows.forEach(
    row => (row.style.display = areHidden ? 'table-row' : 'none')
  )
  defaultRows.forEach(
    row => (row.style.display = areHidden ? 'table-row' : 'none')
  )

  // Update button text
  globalBtn.textContent = areHidden
    ? 'Collapse All Non-significant Rows'
    : 'Show All Non-significant Rows'
}
