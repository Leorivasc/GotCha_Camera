



//Opens a popup window with an url
function popupWindow(event,url, width, height) {
    event.preventDefault(); //prevent from scrolling to top of page
    // Center position
    const left = (screen.width - width) / 2;
    const top = (screen.height - height) / 2;

    // Options
    const opciones = `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=no`;

    // Open
    window.open(url, '_blank', opciones);
}

function dragElement(elmnt) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    if (document.getElementById(elmnt.id + "header")) {
        /* if present, the header is where you move the DIV from:*/
        document.getElementById(elmnt.id + "header").onmousedown = dragMouseDown;
    } else {
        /* otherwise, move the DIV from anywhere inside the DIV:*/
        elmnt.onmousedown = dragMouseDown;
    }

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        // get the mouse cursor position at startup:
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        // call a function whenever the cursor moves:
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        // calculate the new cursor position:
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        // set the element's new position:
        elmnt.style.top = (elmnt.offsetTop - pos2) + "px";
        elmnt.style.left = (elmnt.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        /* stop moving when mouse button is released:*/
        document.onmouseup = null;
        document.onmousemove = null;
    }
}       


//UNUSED (local_stream.html) Reads url and show in divdestination
//Promise part of the function. use readAndShow() below
function doGet(url, params) {
   // Construir la URL con los parámetros
   const queryParams = new URLSearchParams(params).toString();
   const fullUrl = `${url}?${queryParams}`;

   // Retornar la promesa de la solicitud GET
   return fetch(fullUrl)
       .then(response => {
           if (!response.ok) {
               throw new Error(`HTTP error! Status: ${response.status}`);
           }
           return response.text();
       });
}

//UNUSED Reads an url and loads into a div
function readAndShow(url, params, divdestination) {
   doGet(url, params, divdestination)
       .then(text => {
           document.getElementById(divdestination).innerHTML = text;
       })
       .catch(err => {
           console.error('Error:', err);
       });
}

//Sends POST data to an url, then calls a callback function
//Will convert data to a URL-encoded string and send as if it was a form
function sendPost(data, url, callback) {
    // Create an instance of XMLHttpRequest
    const xhr = new XMLHttpRequest();

    // Convert the data to a URL-encoded string
    let formData = '';
    for (const key in data) {
        if (data.hasOwnProperty(key)) {
            formData += encodeURIComponent(key) + '=' + encodeURIComponent(data[key]) + '&';
        }
    }
    formData = formData.slice(0, -1); // Remove the trailing '&'

    // Configure the POST request
    xhr.open('POST', url, true);
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Set content type as form data

    // Handle the 'load' event that fires when the request is complete
    xhr.onload = function () {
        if (xhr.status >= 200 && xhr.status < 300) { // Check if the request was successful
            // Execute the callback with a success message
            callback('POST request completed successfully!');
        } else {
            // Execute the callback with an error message
            callback('Error while making the POST request!');
        }
    };

    // Handle the 'error' event that fires when there is an error in the request
    xhr.onerror = function () {
        // Execute the callback with an error message
        callback('Error while making the POST request!');
    };

    // Send the request with the form data
    xhr.send(formData);
}