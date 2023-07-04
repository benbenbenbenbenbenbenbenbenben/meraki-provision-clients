// Convert CSV to JSON
function csvToJson(csvData) {
  const lines = csvData.split("\r\n");
  const headers = lines[0].split(",");
  const jsonData = [];

  for (let i = 1; i < lines.length; i++) {
    const currentLine = lines[i].split(",");
    if (currentLine.length === headers.length) {
      const row = {};
      for (let j = 0; j < headers.length; j++) {
        row[headers[j]] = currentLine[j];
      }
      jsonData.push(row);
    }
  }
  return jsonData;
}

// Display Dissmissable Alert with a give message and type (success, danger etc)
function displayAlert(message, type) {
  var alertContainer = document.getElementById("alert-container");

  // Create the alert message element
  var alertMessage = document.createElement("div");
  alertMessage.className = `alert alert-${type} alert-dismissible fade show`;
  alertMessage.setAttribute("role", "alert");

  // Add the message text
  alertMessage.textContent = message;

  // Create the dismiss button
  var dismissButton = document.createElement("button");
  dismissButton.className = "btn-close";
  dismissButton.setAttribute("type", "button");
  dismissButton.setAttribute("data-bs-dismiss", "alert");
  dismissButton.setAttribute("aria-label", "Close");

  // Append the dismiss button to the alert message
  alertMessage.appendChild(dismissButton);

  // Append the alert message to the alert container
  alertContainer.appendChild(alertMessage);
}
