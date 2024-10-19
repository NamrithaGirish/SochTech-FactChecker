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
    floatingBox.innerText = 'Welcome To Soch Facts\n\nValidate AI thoughts here.....';
    let pairs = await isURLPresent(selectedText);
    let resultText = "";

// Loop through the URL-score pairs
    pairs.forEach(pair => {
        const { url, score } = pair;
        if (score==null){
          resultText += `${url} -\n Invalid URL\n`;
        }
        else{
          const scorePercentage = parseFloat(score) * 100;
          resultText += `${url} - Only\n${scorePercentage.toFixed(2)}% related to context\n`;
        }
        
        // Check if the score is valid (you can define your own criteria)
        // if (score < 0.5) {
            
        // } else {
        //     resultText += `${url} \n ${scorePercentage.toFixed(2)}%\n`;
        // }
    });

    console.log("hello");
    floatingBox.innerText = resultText;
    // Fetch content from the selected URL
    // let summary = await fetchUrlContent(selectedText);
    // console.log(summary);
    //     if (summary) {
    //         floatingBox.innerText = `${selectedText}\n\nSummary: ${summary}`;
    //     } else {
    //         floatingBox.innerText = selectedText;
    //     }
    // floatingBox.innerText = content ? `Content: ${content.substring(0, 200)}...` : 'Failed to retrieve content.';
  } else {
    floatingBox.innerText = 'Welcome To Soch Facts\n\nValidate AI thoughts here.....';
  }
}

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
      print(data)  
      return data.invalid_urls;
  } catch (error) {
      console.error('Error fetching the URLs:', error);
      return null; 
  }
  
}


// Listen for text selection changes
document.addEventListener('mouseup', updateSelectedText);
document.addEventListener('keyup', updateSelectedText);
