import { determineRowClass } from './utils.js'

export async function scrapeAll () {
  const loadingElement = document.getElementById('loading')
  loadingElement.style.display = 'block'

  const rows = document.querySelectorAll('#grant-table tbody tr')
  // row.cells[2] will fail for diff-rows, we need to select even rows for .textContent.includes("Invalid")
  rows.forEach((row, index) => {
    try {
      if (index % 2 === 0 && row.cells[2].textContent.includes('Invalid')) {
        row.remove()
        rows[index + 1].remove()
      }
    } catch (error) {
      console.error(`Error deleting invalid row ${index}:`, error)
    }
  })
  const urls = Array.from(rows)
    .filter((_, i) => i % 2 === 0)
    .map(row => row.cells[0].textContent.trim())

  try {
    for (const url of urls) {
      const response = await fetch('/add_grant', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url, date: '', status: '', recipient: '' })
      })

      if (response.ok) {
        const data = await response.json()
        const row = document.getElementById(url)
        if (row) {
          row.cells[1].textContent = data.date.replace('T', ' ')
          row.cells[2].textContent = data.status
          row.className = determineRowClass(data.status)
          const diffRow = row.nextElementSibling
          diffRow.querySelector('td').innerHTML = data.diff
        }
      } else {
        console.error(`Failed to scrape URL: ${url}`)
      }
    }
  } catch (error) {
    console.error('Error during scraping:', error)
  }

  loadingElement.style.display = 'none'
}
