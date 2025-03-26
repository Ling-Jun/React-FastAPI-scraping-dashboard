export async function toggleStatus (button, pageUrl) {
  // console.log("Clicked toggleStatus button!")
  var row = button.closest('tr')
  var statusCell = row.cells[2] // Assuming the status is in the third column
  var currentStatus = statusCell.textContent.trim()
  var newStatus
  if (currentStatus.includes('TRIVIAL CHANGE!')) {
    newStatus = 'SIGNIFICANT CHANGE!'
    row.classList.remove('trivial')
    row.classList.add('significant')
  } else if (currentStatus.includes('SIGNIFICANT CHANGE!')) {
    newStatus = 'TRIVIAL CHANGE!'
    row.classList.remove('significant')
    row.classList.add('trivial')
  } else {
    console.log('currentStatus is: ', currentStatus)
    return
  }

  // Update the status cell in the frontend
  statusCell.textContent = newStatus

  //update the backend;
  // The data must have the form of Grant class from config.py
  var data = {
    url: pageUrl,
    date: '',
    status: newStatus,
    recipient: ''
  }
  console.log('toggleStatus data is ', data)
  try {
    const response = await fetch('/toggle_status', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    })

    if (!response.ok) {
      throw new Error(`Server error: ${response.statusText}`)
    }

    const result = await response.json()
    console.log('Status update successful:', result)
  } catch (error) {
    console.error('Error updating status:', error)
    // Optionally, revert the status change in the frontend if the backend update fails
    statusCell.textContent = currentStatus
    row.classList.toggle('trivial')
    row.classList.toggle('significant')
  }
}
