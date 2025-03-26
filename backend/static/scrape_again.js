import { determineRowClass } from './utils.js'

// Function to handle "Scrape Again" functionality
export async function handleScrapeAgain (pageUrl, row) {
  const loadingElement = document.getElementById('loading')
  loadingElement.style.display = 'block'

  try {
    const response = await fetch('/add_grant', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: pageUrl,
        date: '',
        status: '',
        recipient: ''
      })
    })

    if (response.ok) {
      const data = await response.json()

      row.className = determineRowClass(data.status)
      row.cells[1].textContent = data.date.replace('T', ' ')
      row.cells[2].textContent = data.status
      const diffRow = row.nextElementSibling
      diffRow.querySelector('td').innerHTML = data.diff
    } else {
      alert(`Failed to scrape URL: ${url}. Please try again.`)
    }
  } catch (error) {
    console.error(`Error scraping URL: ${url}`, error)
    alert(`An error occurred while scraping URL: ${url}. Please try again.`)
  } finally {
    loadingElement.style.display = 'none'
  }
}
