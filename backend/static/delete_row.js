export function deleteRow (button) {
  // Find the parent row of the button and remove it
  var row = button.closest('tr')
  row.parentNode.removeChild(row)
  // please remember to add const keyword, this is NOT PYTHON!
  const rowURL = row.cells[0].textContent
  // console.log("Removing row with status: ", row.cells[2].textContent);

  // modify the backend
  if (!row.cells[2].textContent.includes('Invalid')) {
    console.log('Calling endpoint /delete_row!')
    fetch('/delete_row', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: rowURL, date: '', status: '', recipient: '' })
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
}
