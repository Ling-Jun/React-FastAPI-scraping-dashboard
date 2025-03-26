export function markAsReviewed (button) {
  // Get the row containing the clicked button
  var row = button.closest('tr')
  row.classList.add('reviewed')
  var reviewDate = row.cells[2].querySelector('.review-timestamp') // Index 1 corresponds to the 2nd cell

  // modify the front-end
  if (reviewDate) {
    // Get the current date and time in Ottawa's time zone
    var now = new Date()
    var options = {
      timeZone: 'America/Toronto', // Ottawa's time zone
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: false // Use 24-hour time format
    }
    var formatter = new Intl.DateTimeFormat([], options)
    var formattedDateTime = formatter.format(now)
    reviewDate.textContent = `Reviewed at ${formattedDateTime}`
  }

  // button.disabled = true;
  var data = {
    url: row.cells[0].textContent, // Assuming the first cell contains the URL
    date: '',
    status: `Reviewed at ${formattedDateTime}`,
    recipient: ''
  }
  console.log('markAsReviewed data is ', data)
  // modify the backend
  fetch('/mark_reviewed', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response error')
      }
      return response.json()
    })
    .then(result => {
      console.log('Success:', result)
    })
    .catch(error => {
      console.error('Error:', error)
    })
}
