let streams = []; // Almacena las direcciones IP de los streams
let videos = [];  // Almacena los objetos de video correspondientes

function setup() {
  createCanvas(800, 600);
  
  // Agrega las direcciones IP de los streams
  streams.push("http://192.168.1.17:5000/video_feed");  // Reemplaza con la dirección IP y el puerto del primer stream
  //streams.push("http://direccion_ip_2:puerto/stream");  // Reemplaza con la dirección IP y el puerto del segundo stream
  
  // Crea un objeto de video para cada dirección IP
  for (let i = 0; i < streams.length; i++) {
    let video = createVideo(streams[i]);
    video.hide(); // Oculta el elemento de video predeterminado
    videos.push(video);
  }
}

function draw() {
  background(255);
  
  // Muestra cada video en el lienzo
  let x = 0;
  let y = 0;
  let margin = 10;
  
  for (let i = 0; i < videos.length; i++) {
    image(videos[i], x, y, width / videos.length - margin, height);
    x += width / videos.length;
  }
}

function mousePressed() {
  // Reproduce o pausa los videos al hacer clic en el lienzo
  for (let i = 0; i < videos.length; i++) {
    if (mouseX > i * (width / videos.length) && mouseX < (i + 1) * (width / videos.length)) {
      if (videos[i].playing()) {
        videos[i].pause();
      } else {
        videos[i].loop();
      }
    }
  }
}
