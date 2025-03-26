// Function to handle "Show Previous Change" functionality
import { determineRowClass } from './utils.js'

export async function handleShowPreviousChange (url, row) {
  const loadingElement = document.getElementById('loading')
  loadingElement.style.display = 'block'

  try {
    const response = await fetch('/show_prior_diff', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, date: '', status: '', recipient: '' })
    })
    if (response.ok) {
      const data = await response.json()
      // console.log("data is", data)
      row.className = determineRowClass(data.status)
      row.cells[1].textContent = data.date
      row.cells[2].textContent = data.status
      const diffRow = row.nextElementSibling
      diffRow.querySelector('td').innerHTML = data.diff
    } else {
      alert(`Failed to show prior change for URL: ${url}. Please try again.`)
    }
  } catch (error) {
    console.error(`Error showing prior change for URL: ${url}`, error)
    alert(
      `An error occurred while showing prior change for URL: ${url}. Please try again.`
    )
  } finally {
    loadingElement.style.display = 'none'
  }
}
