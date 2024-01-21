//Used in local_stream.html
//Controls the alert buttons
function setAlert(cameraName,cameraip, cameraport){
    //Set alert button to red and send alert to camera
    //If alert button is red, set it to green and send clear to camera
    var alertButton = document.getElementById("alert_"+cameraName);
    if (alertButton.innerHTML == "Alert"){
        alertButton.innerHTML = "Clear";
        alertButton.classList.replace("buttonblue","buttonred");
        fetch("http://" + cameraip + ":" + cameraport + "/alarm")
    }
    else{
        alertButton.innerHTML = "Alert";
        alertButton.classList.replace("buttonred","buttonblue");
        fetch("http://" + cameraip + ":" + cameraport + "/clear")
    }
}

//Used in local_stream.html
//Controls the alert buttons
function setRecord(cameraName,cameraip, cameraport){
    //Set record button to red and send start recording to camera
    //If record button is red, set it to green and send stop recording to camera
    var recordButton = document.getElementById("record_"+cameraName);
    if (recordButton.innerHTML == "Record"){
        recordButton.innerHTML = "Stop";
        recordButton.classList.replace("buttonblue","buttonred");
        fetch("http://" + cameraip + ":" + cameraport + "/startrecording")
    }
    else{
        recordButton.innerHTML = "Record";
        recordButton.classList.replace("buttonred","buttonblue");
        fetch("http://" + cameraip + ":" + cameraport + "/stoprecording")
    }
}

//Opens a popup window with an url
function popupWindow(url, width, height) {
    // Center position
    const left = (screen.width - width) / 2;
    const top = (screen.height - height) / 2;

    // Options
    const opciones = `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=yes`;

    // Open
    window.open(url, '_blank', opciones);
}


