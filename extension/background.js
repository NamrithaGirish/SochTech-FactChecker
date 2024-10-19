// chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
//     if (request.action === "getContent") {
//       chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
//         chrome.tabs.executeScript(tabs[0].id, {code: `
//           document.body.innerText;
//         `}, function(results) {
//           sendResponse({content: results[0]});
//         });
//       });
//     }
//     return true; // Indicates asynchronous response
//   }
// );

// chrome.action.onClicked.addListener((tab) => {
//     chrome.scripting.executeScript({
//       target: { tabId: tab.id },
//       func: () => {
//         const selectedText = window.getSelection().toString();
//         console.log(selectedText);
//       }
//     });
//   });

chrome.runtime.onInstalled.addListener(() => {
    console.log("Extension Installed");
  });
  
  