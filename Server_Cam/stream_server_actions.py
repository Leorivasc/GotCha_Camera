#Based on: https://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

import io
import picamera
import logging
import socketserver
from threading import Condition
from http import server
from classes import GPIO_Out
from classes import Counter
import re
import socket

#Led and relay pins
led = GPIO_Out(21)
relay = GPIO_Out(20)
connections = Counter(0)
isAlert=False
hostname = socket.gethostname()
port=8000

#Resolution
resX=320
resY=240

fps=12


class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()
       

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)



class StreamingHandler(server.BaseHTTPRequestHandler):
        
    

    def do_GET(self):
        
        global isAlert
        global hostname
        global resX
        global resY
        global fps
        global port

        #Regexp to emulate GET parameters: '/command?key=value'
        #It supports multiple key=value separated by '&' 
        command_pat=re.compile(r'^/command\?([^=]+=[^&]+)(&[^=]+=[^&]+)*$')

        #Regexp tp emulate a '/blinkon/<frequency>' route
        freq_pat=re.compile(r'^/blinkon/\d*')

        #Entry route. Redirects to /index.html
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()

            
        #Processes key=value GET query strings (regexp here)
        elif command_pat.match(self.path):
            k,v=self.path.split('?')[1].split('=')
            self.send_html_response(f"Command recieved<br> key={k},  value={v}" )
    


        ###Led business
        #Custom routes to remotely operate the attached LED (default  GPIO 21)

        #Turns led ON
        elif self.path =='/ledon':
            led.turn_on()
            self.send_html_response("Led ON")

        #Turns led OFF
        elif self.path=='/ledoff':
            led.turn_off()
            self.send_html_response("Led OFF")

        #Starts blinking
        elif self.path=='/blinkon':
            led.start_blinking()
            self.send_html_response("Led blink ON")

        #Stops blinking
        elif self.path=='/blinkoff':
            led.stop_blinking()
            self.send_html_response("Led blink OFF")

        #Processes /blinkon/<frequency> routes (regexp here)
        elif freq_pat.match(self.path):
            freq=self.path.split('/')[2]
            led.set_frequency(float(freq))
            led.start_blinking()
            self.send_html_response(f"Frequency set to {freq}")


        ###Reay business
        #Custom routes to operate the attached RELAY (default  GPIO 20)
        
        #Switches relay ON
        elif self.path =='/relayon':
            relay.turn_on()
            self.send_html_response("Relay ON")

        #Turns led OFF
        elif self.path=='/relayoff':
            relay.turn_off()
            self.send_html_response("Relay OFF")



        #Trigger alarm mode
        elif self.path=='/alarm':
            relay.turn_on()       #Turn relay on (lights?)
            led.set_frequency(10) #Set blinking freq
            led.start_blinking()  #Starts led blinking
            self.send_html_response("ALARM!")
            isAlert=True

        #Clears alarm mode
        elif self.path=='/clear':
            relay.turn_off()       #Turn relay on (lights?)
            #Restarts blinking frequency depending on 
            if connections.get()==0:
                led.set_frequency(0.25)
            else:
                led.set_frequency(0.5) #Set blinking freq    
            led.start_blinking()  #Starts led blinking
            self.send_html_response("ALL CLEAR!")
            isAlert=False

        #Returns Index.html
        elif self.path == '/index.html':
            self.send_html_response("""
                               <html>
                                <head>
                                    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
                                    <style>
                                    table, td, th {
                                    border: 1px solid;
                                    }

                                    table {
                                    width:320px;
                                    border-collapse: collapse;
                                    }
                                    </style>

                                    <title>picamera MJPEG streaming</title>
                                </head>
                                <body>
                                <h1>GotCha! Cam</h1>
                                    <div>
                                        <div>
                                        <img src="/video_feed" width="320" height="240" alt="Loading..." />
                                        </div>
                                        <div id="status_table">Loading...</div>
                                    </div>

                                <!-- Refresh status table every 5 seconds -->
                                <script>
                                    $(function () {
                                        setInterval(function () {
                                            $.get("/htmlstatus", function (data) {
                                                $("#status_table").html(data);
                                            });
                                        }, 5000);
                                    });
                                </script>

                                </body>
                                </html>
                                """)
            
        #Returns an html table with the current status of the server
        elif self.path == '/htmlstatus':
            content = f"""
                    <table>
                        <tr>
                            <th>Connections</th>
                            <th>Led</th>
                            <th>Relay</th>
                            <th>Alert</th>
                        </tr>
                        <tr>
                            <td>{connections.get()}</td>
                            <td>{led.get_status()}</td>
                            <td>{relay.get_status()}</td>
                            <td>{isAlert}</td>  
                        </tr>
                    </table>
                    """
            self.send_html_response(content)    
        
        #Returns a JSON with the current status of the server
        elif self.path == '/status':
            content = '{'+\
                    '"hostname":'+'"'+hostname\
                    +'"'+',"connections":'+'"'+str(connections.get())\
                    +'"'+',"led":'+'"'+str(led.get_status())\
                    +'"'+',"relay":'+'"'+str(relay.get_status())\
                    +'"'+',"alert":'+'"'+str(isAlert)\
                    +'"'+'}'
            self.send_json_response(content)


        #Performs the streaming
        elif self.path == '/video_feed':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            connections.inc()
            if led.get_frequency()!=10:#Do not change frequency if alarm is on
                led.set_frequency(0.5) #Connections. blinking.
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:              #Disconnection
                connections.dec()
                logging.warning(
                    'Removed streaming client %s: %s, clients: %d',
                    self.client_address, str(e), connections.get())
                if connections.get()==0 and led.get_frequency()!=10: #Do not change frequency if alarm is on
                    led.set_frequency(0.25) #No connections. Slow blinking

        
        #Route given nonexistent
        else:
            self.send_error(404)
            self.end_headers()


    #'Send' helper class functions
    def send_html_response(self,content):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))
    
    def send_json_response(self,content):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content.encode("utf-8"))



class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


#Camera config
with picamera.PiCamera(resolution=f'{resX}x{resY}', framerate=fps) as camera:
    output = StreamingOutput()
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', port)
        server = StreamingServer(address, StreamingHandler)
        led.start_blinking()
        server.serve_forever()
        
    finally:
        camera.stop_recording()
        led.cleanup()
        relay.cleanup()