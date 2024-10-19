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
function updateSelectedText() {
  let selectedText = window.getSelection().toString().trim();
  if (selectedText) {
    floatingBox.innerText = selectedText;
  } else {
    floatingBox.innerText = 'No text selected';
  }
}

// Listen for text selection changes
document.addEventListener('mouseup', updateSelectedText);
document.addEventListener('keyup', updateSelectedText);

