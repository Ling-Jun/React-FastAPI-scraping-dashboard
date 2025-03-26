function parseCustomDate (dateString) {
  console.log('dateString', dateString)
  if (
    !dateString ||
    dateString.includes('N/A') ||
    dateString.includes('Reviewed')
  ) {
    console.warn(`Invalid date string: "${dateString}"`)
    return null
  }

  // Don't forget to trim the trailing & starting space with .trim()
  const [datePart, timePart] = dateString.trim().split(' ')
  // console.log("[datePart, timePart]: ", [datePart, timePart]);
  if (!datePart || !timePart) {
    console.warn(`Incomplete date string: "${dateString}"`)
    return null
  }

  const [year, month, day] = datePart.split('-').map(Number)
  const [hour, minute, second] = timePart.split(':').map(Number)
  // console.log("MONTH:", month);
  if (
    isNaN(year) ||
    isNaN(month) ||
    isNaN(day) ||
    isNaN(hour) ||
    isNaN(minute) ||
    isNaN(second)
  ) {
    console.warn(`Invalid date components in: "${dateString}"`)
    return null
  }

  // Date() is 0-based indexing for month, but 1-based for year and other components
  return new Date(year, month - 1, day, hour, minute, second)
}

export function sortTableByDate () {
  const table = document.getElementById('grant-table')
  const tbody = table.querySelector('tbody')
  const rows = Array.from(tbody.querySelectorAll('tr'))

  // Toggle sort direction
  let sortDirection = document.getElementById('sort-icon').textContent
  sortDirection = sortDirection === '▼' ? '▲' : '▼'
  document.getElementById('sort-icon').textContent = sortDirection

  // Group a row and accompanying hidden diff-row into pairs, so that they move together
  const groupedRows = []
  for (let i = 0; i < rows.length; i++) {
    if (!rows[i].classList.contains('diff-row')) {
      groupedRows.push([rows[i], rows[i + 1]])
      i++
    }
  }

  groupedRows.sort((a, b) => {
    const dateA = parseCustomDate(a[0].cells[1].textContent)
    const dateB = parseCustomDate(b[0].cells[1].textContent)
    if (!dateA && !dateB) return 0
    if (!dateA) return 1 // 'N/A' dates are considered greater
    if (!dateB) return -1
    // the difference between two Date objectsis the number of milliseconds between the two
    return sortDirection === '▼' ? dateA - dateB : dateB - dateA
  })

  // Rebuild the table body with sorted rows
  tbody.innerHTML = ''
  groupedRows.forEach(rowPair => {
    tbody.appendChild(rowPair[0])
    tbody.appendChild(rowPair[1])
  })
}
