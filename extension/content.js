// Create a floating box to display selected text
let floatingBox = document.createElement('div');
floatingBox.id = 'floatingTextBox';

// Create and append the heading
let heading = document.createElement('h2');
heading.innerText = 'Soch Facts';
floatingBox.appendChild(heading);

// Add text content
floatingBox.innerText += '\nNo text selected'; // Append to the heading

// Create resize handle
let resizeHandle = document.createElement('div');
resizeHandle.id = 'resizeHandle';
floatingBox.appendChild(resizeHandle);

// Add the floating box to the webpage
document.body.appendChild(floatingBox);
document.addEventListener('click', function (event) {
  if (!floatingBox.contains(event.target)) {
      // Reset the content only if it is clicked outside
      floatingBox.innerText = heading.innerText + '\nNo text selected';
  }
});

// Prevent clicks inside the floating box from resetting content
floatingBox.addEventListener('click', function(event) {
  event.stopPropagation();
});

// Function to update the box with selected text
// Function to update the box with selected text
// Function to update the box with selected text
async function updateSelectedText() {
  let selectedText = window.getSelection().toString().trim();
  if (selectedText) {
      floatingBox.innerText = 'Validating...';
      
      // Fetch claim validation from the Flask API
      const validationResult = await fetchClaimValidation(selectedText);
      console.log(validationResult);
      if (validationResult) {
          let resultText = '';
          const { valid, support_prob, invalid_urls, citations } = validationResult;

          // Display support probability
          resultText += `Support Probability: ${(support_prob * 100).toFixed(2)}%\n\n`;

          // Process invalid URLs
          if (invalid_urls && invalid_urls.length > 0) {
              invalid_urls.forEach(({ url, score }) => {
                  resultText += `${url} - ${score === null ? 'Invalid URL' : `Only ${(parseFloat(score) * 100).toFixed(2)}% related to context`}\n`;
              });
          } else {
              resultText += 'No invalid URLs found.\n';
          }

          // Process citations
          if (citations && citations.length > 0) {
              resultText += `Citations:\n`;
              citations.forEach(citation => {
                  resultText += `${citation}\n`;
              });
          } else {
              resultText += 'No citations found.\n';
          }

          floatingBox.innerText = resultText;
      } else {
          floatingBox.innerText = 'No validation result received.';
      }
  } else {
      floatingBox.innerText = 'Welcome To Soch Facts\n\nValidate AI thoughts here.....';
  }
}


// Function to fetch content from the URL and get the score, support probability, and citations
// async function isURLPresent(text) {
//   try {
//       const response = await fetch('http://localhost:5000/api/check-url', {
//           method: 'POST',
//           headers: {
//               'Content-Type': 'application/json',
//           },
//           body: JSON.stringify({ text })  // Send the text for processing
//       });

//       const data = await response.json();
//       return data.invalid_urls;
//   } catch (error) {
//       console.error('Error fetching the URLs:', error);
//       return [];
//   }
// }




// Function to fetch claim validation from the Flask API
async function fetchClaimValidation(text) {
  try {
      const response = await fetch('http://localhost:5000/api/check-url', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({ text })  // Send the selected text (context + claim)
      });

      if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;  // Return the API's response (validity, message, support_prob, etc.)
  } catch (error) {
      console.error('Error validating the claim:', error);
      return null;
  }
}

// Listen for text selection changes



// Function to fetch content from a URL
// async function fetchUrlContent(url) {
//   try {
//     let paragraph = "The war between china and africa is leading."
//       const response = await fetch('http://localhost:5000/api/fetch-url', {
//           method: 'POST',
//           headers: {
//               'Content-Type': 'application/json',
//           },
//           body: JSON.stringify({  paragraph, url })  // Send the URL as JSON
//       });

//       // Check if the response is ok (status code 200-299)
//       if (!response.ok) {
//           throw new Error(`HTTP error! status: ${response.status}`);
//       }

//       const data = await response.json();
//       print(data)  
//       return data.valid ? data.summary : null; // Return summary if valid
//   } catch (error) {
//       console.error('Error fetching the URL:', error);
//       return null; 
//   }
// }
async function isURLPresent(text) {
  try {
    
      const response = await fetch('http://localhost:5000/api/check-url', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json',
          },
          body: JSON.stringify({  text })  // Send the URL as JSON
      });

    // Call the Flask API with the selected URL and claim
    // const response = await fetch('http://localhost:5000/api/fetch-url', {
    //   method: 'POST',
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    //   body: JSON.stringify({url })  // Send the paragraph and selected URL as JSON
    // });

      const data = await response.json();
      console.log(data.citation);
      // print(data)  
      return [data.invalid_urls,data.citation];
  } catch (error) {
      console.error('Error fetching the URLs:', error);
      return null; 
  }
  
}


// Listen for text selection changes
document.addEventListener('mouseup', updateSelectedText);
document.addEventListener('keyup', updateSelectedText);
// chrome.commands.onCommand.addListener((command) => {
//   if (command === "open_extension") {
//     // Open the content script functionality or popup
//     chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
//       chrome.scripting.executeScript({
//         target: { tabId: tabs[0].id },
//         function: openContentReader,
//       });
//     });
//   }
// });