import { handleShowPreviousChange } from './show_prior_change.js'
import { handleScrapeAgain } from './scrape_again.js'
import { toggleDiff } from './utils.js'
import { filterTable, toggleAllNonSignificantRows } from './utils.js'
import { sortTableByDate } from './sort_table.js'
import { toggleStatus } from './toggle_status.js'
import { addGrant } from './add_grant.js'
import { scrapeAll } from './scrape_all.js'
import { markAsReviewed } from './mark_as_reviewed.js'
import { promptEmail } from './prompt_email.js'
import { deleteRow } from './delete_row.js'

window.toggleDiff = toggleDiff
window.filterTable = filterTable
window.sortTableByDate = sortTableByDate
window.toggleStatus = toggleStatus
window.promptEmail = promptEmail
window.markAsReviewed = markAsReviewed
window.deleteRow = deleteRow
window.toggleAllNonSignificantRows = toggleAllNonSignificantRows

document.getElementById('add-grant-form').addEventListener('submit', addGrant)

document.getElementById('scrape-all-btn').addEventListener('click', scrapeAll)

// Event delegation for dynamically added "Scrape Again" buttons
document
  .querySelector('#grant-table tbody')
  .addEventListener('click', function (event) {
    const target = event.target
    if (target.classList.contains('scrape-again-btn')) {
      const url = target.getAttribute('data-url')
      const row = target.closest('tr')
      handleScrapeAgain(url, row)
    }
  })

// Event delegation for dynamically added "Show Previous Change" buttons
document
  .querySelector('#grant-table tbody')
  .addEventListener('click', function (event) {
    const target = event.target
    if (target.classList.contains('show-prior-diff-btn')) {
      const url = target.getAttribute('data-url')
      const row = document.getElementById(url)
      handleShowPreviousChange(url, row)
    }
  })

document
  .getElementById('edit-keywords-btn')
  .addEventListener('click', function () {
    var formDiv = document.getElementById('keyword-div')
    if (formDiv.style.display === 'none' || formDiv.style.display === '') {
      formDiv.style.display = 'block'
    } else {
      formDiv.style.display = 'none'
    }
  })

document
  .getElementById('keywords-form')
  .addEventListener('submit', function (event) {
    event.preventDefault()
    var formData = new FormData(this)

    fetch('/update_keywords', {
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        alert(data.message)
        document.getElementById('keyword-div').style.display = 'none'
      })
      .catch(error => {
        console.error('Error:', error)
      })
  })

document
  .getElementById('schedule-form')
  .addEventListener('submit', function (event) {
    event.preventDefault()
    var formData = new FormData(this)
    console.log('formData', formData)
    fetch('/schedule', {
      method: 'POST',
      body: formData
    })
      .then(response => response.json())
      .then(data => {
        alert(data.message)
      })
      .catch(error => {
        console.error('Error:', error)
      })
  })
