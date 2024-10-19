// Create a floating box to display selected text
let floatingBox = document.createElement('div');
floatingBox.id = 'floatingTextBox';
floatingBox.style.position = 'fixed';
floatingBox.style.bottom = '20px';
floatingBox.style.right = '20px';
floatingBox.style.padding = '10px';
floatingBox.style.backgroundColor = '#f0f0f0';
floatingBox.style.border = '1px solid #ccc';
floatingBox.style.borderRadius = '5px';
floatingBox.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
floatingBox.style.maxWidth = '300px';
floatingBox.style.whiteSpace = 'pre-wrap';
floatingBox.style.zIndex = '9999';
floatingBox.innerText = 'No text selected';

// Add the floating box to the webpage
document.body.appendChild(floatingBox);

// Function to update the box with selected text
async function updateSelectedText() {
  let selectedText = window.getSelection().toString().trim();
  if (selectedText) {
    floatingBox.innerText = `Checking fact...`;
    console.log("Selected text:", selectedText);

    // Fetch content from the Flask API
    let summary = await fetchUrlContent(selectedText);
    console.log("Fact-check result:", summary);

    // Update the floating box with the fact-check result
    if (summary) {
      floatingBox.innerText = `${selectedText}\n\nFact-check: ${summary}`;
    } else {
      floatingBox.innerText = `${selectedText}\n\nCould not retrieve fact-check information.`;
    }
  } else {
    floatingBox.innerText = 'No text selected';
  }
}

// Function to fetch content from the Flask API
async function fetchUrlContent(url) {
  try {
    //let paragraph = "The war between china and africa is leading.";  // Modify or replace with dynamic claim

    // Call the Flask API with the selected URL and claim
    const response = await fetch('http://localhost:5000/api/fetch-url', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({url })  // Send the paragraph and selected URL as JSON
    });

    // Check if the response is ok (status code 200-299)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const data = await response.json();
    return data.valid ? data.summary : null;
  } catch (error) {
    console.error('Error fetching the URL:', error);
    return null;
  }
}


// Listen for text selection changes
document.addEventListener('mouseup', updateSelectedText);
document.addEventListener('keyup', updateSelectedText);
