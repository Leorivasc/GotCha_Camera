



//Opens a popup window with an url. New browser window
function popupWindow_new(event,url, width, height) {
    event.preventDefault(); //prevent from scrolling to top of page
    // Center position
    const left = (screen.width - width) / 2;
    const top = (screen.height - height) / 2;

    // Options
    const opciones = `width=${width},height=${height},left=${left},top=${top},resizable=yes,scrollbars=no`;

    // Open
    window.open(url, '_blank', opciones);
}

//Opens an url in a W2UI popup
function popupWindow(event, url, width, height, head_title) {
    w2popup.open({
        title: head_title,
        body: '<iframe src="' + url + '" width="100%" height="99%" frameborder=0 style="overflow:hidden"></iframe>',
        width: width,
        height: height
    });
}


//open webm videos in a w2ui popup
function popupVideo(event, url, width, height) {
    event.preventDefault(); //prevent from scrolling to top of page
    w2popup.open({
        title: 'Video Player',
        body: '<video width="100%" height="100%" controls><source src="' + url + '" type="video/webm"></video>',
        width: width,
        height: height
    });
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
            callback(this.responseText);  //Will return the response text
        } else {
            // Execute the callback with an error message
            callback('Error');
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


function loginPopup(event){
    event.preventDefault();
    w2popup.open({
        title: 'Login',
        body:   '<div class="w2ui-centered">' +
                    '<form class="w2ui-reset w2ui-login-form">' +
                        '<div class="w2ui-field">' +
                            '<label>Username:</label>' +
                            '<div><input id="user" type="text" style="width: 100%;"></div>' +
                        '</div>' +
                        '<div class="w2ui-field">' +
                            '<label>Password:</label>' +
                            '<div><input id="password" type="password" style="width: 100%;"></div>' +
                        '</div>' +
                    '</form>' +
                '</div>',


        actions: ['Ok'],
        width: 320,
        height: 200,
        modal: true,
        showClose: true,
       
        
    })
    .close(evt => {
        console.log('popup clsoed')
    })
    .ok((evt) => {
        var name = document.getElementById('user').value ;
        var pass = document.getElementById('password').value ;
        
        sendPost({user: name, password: pass}, '/login', 
                    function(response){
                        if (response=="Ok"){
                            w2popup.close()
                            location.reload()
                        }else{
                            w2popup.open({
                                title: 'Error',
                                text: response,
                                width: 350,
                                height: 150,
                            })
                        }
                    })

        w2popup.close()
    })



}