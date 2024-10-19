// document.addEventListener('DOMContentLoaded', function() {
//     const contentBox = document.getElementById('content-box');
//     const selectTextButton = document.getElementById('select-text-button');
  
//     selectTextButton.addEventListener('click', function() {
//       chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
//         chrome.tabs.sendMessage(tabs[0].id,   
//    {action: "getSelectedText"}, function(response)   
//    {
//           contentBox.textContent = response.selectedText;
//         });
//       });
//     });
//   });

// document.addEventListener('DOMContentLoaded', function () {
//     chrome.tabs.executeScript(
//       { code: 'window.getSelection().toString();' },
//       function (selection) {
//         document.getElementById('selectedText').innerText = selection[0] || 'No text selected';
//       }
//     );
//   }
// );

document.addEventListener('DOMContentLoaded', function () {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.scripting.executeScript(
        {
          target: { tabId: tabs[0].id },
          func: () => window.getSelection().toString(),
        },
        (result) => {
          const selectedText = result[0].result || 'No text selected';
          document.getElementById('selectedText').innerText = selectedText;
        }
      );
    });
  });
  