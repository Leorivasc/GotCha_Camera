// MASK APP
// This script is used to create a mask image for the camera. 
// The mask image is used to define the area of the image that will be used for motion detection. 
// The mask image is created by drawing on top of the camera image. 
// The resulting mask image is then uploaded to the server to be used by the motion detection algorithm.
// Requires p5.js library for drawing on the canvas and image manipulation.
// This script works only when loaded from 'mask_app.html' because it requires the buttons to be present in the DOM.

// Global Variables
let img;
let mask;

let black;
let brushSize = 20;

let camera_name = ""

/**
 * P5.js setup() function
 * Create the canvas and set up event listeners for the buttons
 * (this is only to be loaded from 'mask_app.html')
 */
function setup() {
  let canvas = createCanvas(320, 240);
  canvas.parent('canvasHolder');
  
  // Add event listeners to the buttons
  document.getElementById('uploadButton').addEventListener('click', uploadMaskToServer, false);
  document.getElementById('loadFromCamera').addEventListener('click', loadFromCamera, false);
  document.getElementById('invertColor').addEventListener('click', invertColor, false);

  //get camera name from the template
  camera_name = document.getElementById('cameraName').value;

  loadFromCamera();
}

/**
 * Load an image from the camera to be used as background where the drawing will be done
 */
function loadFromCamera(){

  //lets make sure to keep the url updated
  var hostname = window.location.hostname;
  var snapshotroute = document.getElementById("snapShotRoute");
  var snapshoturl = document.getElementById("snapShotURL");
  snapshoturl.value = "http://"+ hostname + snapshotroute.value;
  
  //Load the image
  img = loadImage(snapshoturl.value, function() {
                    //resize the canvas to match the image dimensions (future use may allow different dimensions for mask and image)
                    resizeCanvas(img.width, img.height);
                    mask = createImage(img.width, img.height);

                    //Position the image on the canvas
                    image(img, 0, 0);

                    // Create the mask image. It is all white, opaque, and the same size as the loaded image
                    mask.loadPixels();
                    for (let i = 0; i < mask.width * mask.height * 4; i += 4) {
                      mask.pixels[i] = 255;
                      mask.pixels[i + 1] = 255;
                      mask.pixels[i + 2] = 255;
                      mask.pixels[i + 3] = 1; // 1 to pass the if
                    }
                    mask.updatePixels();


                    // Create a black image to use as copy source
                    black = createImage(img.width, img.height);
                    black.loadPixels();
                    for (let i = 0; i < black.width * black.height * 4; i += 4) {
                      black.pixels[i] = 0;
                      black.pixels[i + 1] = 0;
                      black.pixels[i + 2] = 0;
                      black.pixels[i + 3] = 255; // 0 = transparent, 255 = opaque
                    }
                    black.updatePixels();

                }, function(e) {
                      console.log('Error loading image:', e);
                      });

}


/**
 * Invert the color of the mask. Useful to flip the mask from black to white and vice versa
 */
function invertColor(){
//Will invert the color of the mask
  if (img && mask) {
    mask.loadPixels();
    for (let i = 0; i < width * height * 4; i += 4) {
      if (mask.pixels[i] === 0 && mask.pixels[i + 1] === 0 && mask.pixels[i + 2] === 0) {
        mask.pixels[i] = 255;
        mask.pixels[i + 1] = 255;
        mask.pixels[i + 2] = 255;
        mask.pixels[i + 3] = 1; //255 = opaque
      } else {
        mask.pixels[i] = 0;
        mask.pixels[i + 1] = 0;
        mask.pixels[i + 2] = 0;
        mask.pixels[i + 3] = 155;//255 = opaque
      }
    }
    mask.updatePixels();
  }

}


/**
 * Load the image from file selector and create the mask image to match the loaded image dimensions
 * (Not used anymore, replaced by loadFromCamera), but kept for reference
 * @param {*} event 
 */
function handleFileSelect(event) {
  //Load the image
  let file = event.target.files[0];
  if (file.type.match('image.*')) {
    let reader = new FileReader();
   
    reader.onload = function() {
      img = loadImage(reader.result, function() {
        resizeCanvas(img.width, img.height);
        mask = createImage(img.width, img.height);
       
        image(img, 0, 0);

        // Create the mask image. It is all white, opaque, and the same size as the loaded image
        mask.loadPixels();
        for (let i = 0; i < mask.width * mask.height * 4; i += 4) {
          mask.pixels[i] = 255;
          mask.pixels[i + 1] = 255;
          mask.pixels[i + 2] = 255;
          mask.pixels[i + 3] = 1; // 1 to pass the if
        }
        mask.updatePixels();


        // Create a black image to use as copy source
        black = createImage(img.width, img.height);
        black.loadPixels();
        for (let i = 0; i < black.width * black.height * 4; i += 4) {
          black.pixels[i] = 0;
          black.pixels[i + 1] = 0;
          black.pixels[i + 2] = 0;
          black.pixels[i + 3] = 255; // 0 = transparent, 255 = opaque
        }
        black.updatePixels();

      }, function(e) {
        console.log('Error loading image:', e);
      });
    };
    reader.readAsDataURL(file);
    
  }
}



/**
 * P5.js draw() function
 * Draw the loaded image, then draw the mask on top of it.
 */
function draw() {
  //The mask is drawn semi-transparently, so that the image underneath can be seen.
  if (img) {
    image(img, 0, 0);
    if (mouseIsPressed && mouseX >= 0 && mouseX < width && mouseY >= 0 && mouseY < height) {
      let x = mouseX - brushSize / 2;
      let y = mouseY - brushSize / 2;
      mask.copy(black, x, y, brushSize, brushSize, x, y, brushSize, brushSize);
      mask.loadPixels();
      for (let i = 0; i < width * height * 4; i += 4) {
        if (mask.pixels[i] === 0 && mask.pixels[i + 1] === 0 && mask.pixels[i + 2] === 0) {
          mask.pixels[i] = 0;
          mask.pixels[i + 1] = 0;
          mask.pixels[i + 2] = 0;
          mask.pixels[i + 3] = 155;//semi opaque
        } else {
          mask.pixels[i] = 255;
          mask.pixels[i + 1] = 255;
          mask.pixels[i + 2] = 255;
          mask.pixels[i + 3] = 1; // 1 to pass the if
        }
      }
      mask.updatePixels();
      //image(mask,0,0);
    }
  }

  //Draw the mask image on top of the loaded image. Since it is semi-transparent, the image underneath will be visible.
  if(mask){
    image(mask,0,0);
  }
}

/**
 * Save and download the mask image locally
 * (Not used anymore, replaced by uploadMaskToServer), but kept for reference
 */
function saveMaskLocally() {
  if (img && mask) {
   
    prepareMask()

    mask.save('mask.jpg','jpg');
  }
}


/**
 * Upload the mask image to the server
 * Modified from:https://stackoverflow.com/questions/3012566/how-to-upload-string-as-file-with-jquery-or-other-js-framework
 */
function uploadMaskToServer() {
  if (img && mask) {
    //prepareMask();
    mask2onezeros();
    mask.canvas.toBlob(function(blob) {
      let formData = new FormData();
      formData.append('mask', blob, 'mask_'+camera_name+'.jpg');
      fetch('/upload_mask', {
        method: 'POST',
        body: formData
      })
      .then(response => {
        if (response.ok) {
          console.log('Mask image uploaded successfully');
        } else {
          console.error('Failed to upload mask image');
        }
      })
      .catch(error => {
        console.error('Error uploading mask image:', error);
      });
    }, 'image/jpeg');
  }
}


/**
 * Set transparent pixels to white, dark pixels to black
 * so that it can be used as a mask
 */
function prepareMask(){
  mask.loadPixels();
  for (let i = 0; i < width * height * 4; i += 4) {
    if (mask.pixels[i] === 0 && mask.pixels[i + 1] === 0 && mask.pixels[i + 2] === 0) {
      mask.pixels[i] = 0;
      mask.pixels[i + 1] = 0;
      mask.pixels[i + 2] = 0;
      mask.pixels[i + 3] = 255; //255 = opaque
    } else {
      mask.pixels[i] = 255;
      mask.pixels[i + 1] = 255;
      mask.pixels[i + 2] = 255;
      mask.pixels[i + 3] = 255;//255 = opaque
    }
  }
  mask.updatePixels();
}

/**
 * Convert to binary mask
 * @returns bmp
 */
function mask2onezeros(){
  mask.loadPixels();
  bmp=[];
  for (let i=0; i<width*height*4; i+=4){
    byte = (mask.pixels[i]+mask.pixels[i+1]+mask.pixels[i+2])/3; //average of RGB
    if (byte>2){
      bmp.push(1);  
    }else{
      bmp.push(0);
    }
  }

  mask.updatePixels();
  return bmp;
}


/**
 * convert mask to bmp of 0 and 1
 * @returns bmp
 */
function convertMaskToBMP(){
  let bmp = [];
  mask.loadPixels();
  for (let i = 0; i < width * height * 4; i += 4) {
    if (mask.pixels[i] === 0 && mask.pixels[i + 1] === 0 && mask.pixels[i + 2] === 0) {
      bmp.push(0);
    } else {
      bmp.push(1);
    }
  }
  mask.updatePixels();
  return bmp;
}