import { determineRowClass } from './utils.js'

export async function addGrant (event) {
  event.preventDefault()
  const urlInput = document.getElementById('grant-urls')
  const urls = urlInput.value.split(',').map(url => url.trim())

  const loadingElement = document.getElementById('loading')
  loadingElement.style.display = 'block'

  try {
    for (const url of urls) {
      if (url) {
        const response = await fetch('/add_grant', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url, date: '', status: '', recipient: '' })
        })

        if (response.ok) {
          const data = await response.json()
          const existingRow = document.getElementById(url)

          const isDisabled = data.status === 'Invalid' ? 'disabled' : ''
          const newRowContent = `
                        <td>${data.page}</td>
                        <td>
                            ${data.date.replace('T', ' ')} 
                        </td>
                        <td>
                            ${data.status}<br>
                            <span class="review-timestamp"></span>
                        </td>
                        <td>
                            <button onclick="toggleDiff(this)">View Details</button>
                            <button class="scrape-again-btn" data-url="${
                              data.page
                            }" ${isDisabled}>Scrape Again</button>
                            <button class="show-prior-diff-btn" data-url="${
                              data.page
                            }" ${isDisabled}>Show Previous Change</button>
                            <button onclick="toggleStatus(this, ${
                              data.page
                            })">Flag as SIGNIFICANT/TRIVIAL</button>
                            <button id="email-button" onclick="promptEmail(this)" ${isDisabled}>Email This</button>
                            <button onclick="markAsReviewed(this)" ${isDisabled}>Mark as Reviewed</button>
                            <button onclick="deleteRow(this)">Delete Row</button>
                        </td>
                    `

          if (existingRow) {
            existingRow.className = determineRowClass(data.status)
            existingRow.innerHTML = newRowContent
          } else {
            const table = document
              .getElementById('grant-table')
              .querySelector('tbody')
            const newRow = document.createElement('tr')

            newRow.id = url
            newRow.className = determineRowClass(data.status)
            newRow.innerHTML = newRowContent
            table.appendChild(newRow)

            const diffRow = document.createElement('tr')
            diffRow.className = 'diff-row'
            diffRow.style.display = 'none'
            diffRow.innerHTML = `<td colspan="4">${data.diff}</td>`
            table.appendChild(diffRow)
          }
        } else {
          alert(`Failed to add URL: ${url}.`)
        }
      }
    }
  } catch (error) {
    console.error(`Error adding URL: ${url}`, error)
  } finally {
    loadingElement.style.display = 'none'
    urlInput.value = ''
  }
}
