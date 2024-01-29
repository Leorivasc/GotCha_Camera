//Used in local_stream.html
//Controls the alert buttons
function setAlarm(event,cameraName,cameraip, cameraport,seconds){
    //Set alert button to red and send alert to camera
    //If alert button is red, set it to green and send clear to camera

    event.preventDefault(); //prevent from scrolling to top of page

    var alertButton = document.getElementById("alert_"+cameraName);
    if (alertButton.innerHTML == "Alarm"){
        alertButton.innerHTML = "Clear";
        alertButton.classList.replace("button","buttonred");
        fetch("http://" + cameraip + ":" + cameraport + "/alarm/" + seconds)
        
        
    }
    else{
        alertButton.innerHTML = "Alarm";
        alertButton.classList.replace("buttonred","button");
        fetch("http://" + cameraip + ":" + cameraport + "/clear")
        
    }
}

//Used in local_stream.html
//Controls the alert buttons
function setRecord(event,cameraName,cameraip, cameraport){
    //Set record button to red and send start recording to camera
    //If record button is red, set it to green and send stop recording to camera

    event.preventDefault(); //prevent from scrolling to top of page

    var recordButton = document.getElementById("record_"+cameraName);
    if (recordButton.innerHTML == "Record"){
        recordButton.innerHTML = "Stop";
        recordButton.classList.replace("button","buttonred");
        fetch("http://" + cameraip + ":" + cameraport + "/startrecording")
    }
    else{
        recordButton.innerHTML = "Record";
        recordButton.classList.replace("buttonred","button");
        fetch("http://" + cameraip + ":" + cameraport + "/stoprecording")
    }
}

//Used in local_stream.html
//Controls the alert buttons
function sendRestart(event, cameraName,cameraip, cameraport){
    //Set record button to red and send start recording to camera
    //When return is completed, set record button to normal

    event.preventDefault(); //prevent from scrolling to top of page
    
    var recordButton = document.getElementById("restart_"+cameraName);
    recordButton.classList.replace("button","buttonred");
    fetch("http://" + cameraip + ":" + cameraport + "/restart")
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            recordButton.classList.replace("buttonred","button");
        });
   
}




//Opens a popup window with an url
function popupWindow(url, width, height) {
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

