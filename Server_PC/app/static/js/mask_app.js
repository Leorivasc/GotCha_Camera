// Global Variables
let img;
let mask;

let black;
let brushSize = 20;

let camera_name = ""

function setup() {
  let canvas = createCanvas(320, 240);
  canvas.parent('canvasHolder');
  
  //show canvas
  //canvas.style('display', 'block');
  //canvas.style('margin', 'auto');
  //canvas.style('border', '1px solid black');
  //canvas.style('margin-top', '10px');
  //canvas.style('margin-bottom', '10px');
  //canvas.style('margin-left', 'auto');
 // canvas.style('margin-right', 'auto');


  //document.getElementById('fileInput').addEventListener('change', handleFileSelect, false);
  //document.getElementById('saveLocalButton').addEventListener('click', saveMaskLocally, false);
  document.getElementById('uploadButton').addEventListener('click', uploadMaskToServer, false);
  document.getElementById('loadFromCamera').addEventListener('click', loadFromCamera, false);
  document.getElementById('invertColor').addEventListener('click', invertColor, false);

  //get camera name
  camera_name = document.getElementById('cameraName').value;

  loadFromCamera();
}

function loadFromCamera(){

  //lets make sure to keep the url updated
  var hostname = window.location.hostname;
  var snapshotroute = document.getElementById("snapShotRoute");
  var snapshoturl = document.getElementById("snapShotURL");
  snapshoturl.value = "http://"+ hostname + snapshotroute.value;
  
  img = loadImage(snapshoturl.value, function() {
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

}


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


//Load the image and create the mask image to match the loaded image dimensions
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



//Draw the loaded image, then draw the mask on top of it.
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

//Save and download the mask image locally
function saveMaskLocally() {
  if (img && mask) {
   
    prepareMask()

    mask.save('mask.jpg','jpg');
  }
}


//Upload the mask image to the server
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


//Set transparent pixels to white, dark pixels to black
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


//convert mask to bmp of 0 and 1
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