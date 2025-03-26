// Function to populate the select element with emails
function populateEmails (emails, emailDiv) {
  const select = emailDiv.querySelector('#email-select')
  select.innerHTML = '' // Clear existing options

  emails.forEach(email => {
    const option = document.createElement('option')
    option.value = email
    option.text = email
    select.add(option)
  })
}

function showDialog (content, onConfirm) {
  const dialog = document.createElement('dialog')
  dialog.innerHTML = content
  document.body.appendChild(dialog)
  // ======================================================
  const confirmButton = document.createElement('button')
  confirmButton.textContent = 'Confirm Sending email'
  confirmButton.addEventListener('click', async () => {
    await onConfirm()
    dialog.close()
    dialog.remove() // Remove from DOM after closing
  })
  // ======================================================
  const cancelButton = document.createElement('button')
  cancelButton.textContent = 'Cancel'
  cancelButton.addEventListener('click', () => {
    dialog.close()
    dialog.remove() // Remove from DOM after closing
  })

  dialog.appendChild(confirmButton)
  dialog.appendChild(cancelButton)

  dialog.showModal()
}

export async function promptEmail (button) {
  const row = button.parentNode.parentNode

  const emailDiv = document.createElement('div')
  emailDiv.innerHTML = `
    <div style="display: flex; gap: 20px;">
      <div style="flex: 1;">
        <label for="email-select">Select Recipients:</label><br>
        <select id="email-select" multiple></select>
      </div>
      <div style="display: flex; flex-direction: column; gap: 10px; align-items: flex-start">
          <button id="add-email">Add Email</button>
          <button id="delete-email">Delete Selected</button>
      </div>
    </div>
  `

  // *** IMPORTANT: Show the dialog FIRST, THEN attach listeners! ***
  showDialog(emailDiv.outerHTML, async () => {
    const dialogEmailDiv = document.querySelector('dialog div')
    const selectedEmails = Array.from(
      dialogEmailDiv.querySelector('#email-select').selectedOptions
    )
      .map(option => option.value)
      .join(', ') // Join with comma and space

    if (selectedEmails.length === 0) {
      alert('Please select at least one recipient.')
      return // Prevent dialog close
    }

    // please match with Grant class in config.py
    const data = {
      url: row.cells[0].innerText,
      date: '',
      status: row.cells[2].innerText,
      recipient: selectedEmails
    }

    try {
      const response = await fetch('/send_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
      console.log('data....', data)
      const result = await response.text()
      alert(result)
    } catch (error) {
      console.error('Error:', error)
      alert('Error sending emails.')
    }
  })

  const dialogEmailDiv = document.querySelector('dialog div') // Get the div *inside* the dialog

  // Initial population of the email list (inside the dialog)
  fetch('/get_emails')
    .then(response => response.json())
    .then(emails => {
      populateEmails(emails, dialogEmailDiv) // Populate the select in the *dialog*
    })
    .catch(error => {
      console.error('Error fetching emails:', error)
      populateEmails([], dialogEmailDiv)
    })

  dialogEmailDiv.querySelector('#add-email').addEventListener('click', () => {
    const newEmailsInput = prompt('Enter new emails (comma-separated):')
    if (newEmailsInput) {
      const newEmails = newEmailsInput
        .split(',')
        .map(email => email.trim())
        .filter(email => email !== '') // Split, trim, and remove empty

      if (newEmails.length === 0) {
        // Handle if input was just commas or whitespace
        alert(' Please enter email addresses (comma-separated)!')
      }

      Promise.all(
        newEmails.map(
          (
            email // Send multiple requests concurrently if needed
          ) =>
            fetch('/add_email', {
              // Send individual requests for each email
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ email: email }) // Send one email per request
            })

          // console.log('All emails added!!!!!!!!')
        )
      )
        .then(responses => {
          // Check all responses
          if (responses.every(response => response.ok)) {
            populateEmails(
              [...dialogEmailDiv.querySelector('#email-select').options]
                .map(o => o.value)
                .concat(newEmails),
              dialogEmailDiv
            )
          } else {
            // console.error('Some emails could not be added.')
            alert('Some emails already exist!!')
          }
        })
        .catch(error => console.error('Error adding emails:', error))
    }
  })

  dialogEmailDiv
    .querySelector('#delete-email')
    .addEventListener('click', () => {
      const select = dialogEmailDiv.querySelector('#email-select') // Use dialogEmailDiv here too
      const selectedOptions = Array.from(select.selectedOptions)

      selectedOptions.forEach(option => select.remove(option.index))
      console.log(
        'emails: selectedOptions.map(o => o.value)',
        selectedOptions.map(o => o.value)
      )
      fetch('/delete_emails', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emails: selectedOptions.map(o => o.value) })
      }).catch(error => console.error('Error deleting emails:', error))
    })
}
