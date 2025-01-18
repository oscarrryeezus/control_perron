import socket
import threading
from flask import Flask, request, send_file
from comtypes import CLSCTX_ALL
import keyboard
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import qrcode.constants
import screen_brightness_control as sbc 
import os
import webbrowser
import qrcode

# Configuración del servidor Flask
app = Flask(__name__)

# Ruta para mostrar la imagen
@app.route('/')
def page():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Control Remoto</title>
    <style>
        body {
            text-align: center;
            margin: 20px;
            font-family: Arial, sans-serif;
        }
        h1 {
            font-size: 1.8em;
            margin-bottom: 20px;
        }
        h3 {
            font-size: 1.2em;
            margin-bottom: 15px;
        }
        .section {
            margin-bottom: 30px;
        }
        .button-group {
            display: flex;
            justify-content: center;
            gap: 10px;
            flex-wrap: wrap;
        }
        button {
            padding: 10px 20px;
            font-size: 1em;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover {
            opacity: 0.9;
        }
        .shutdown {
            background-color: red;
            color: white;
        }
        img {
            max-width: 100%;
            height: auto;
        }

        /* Responsiveness */
        @media (max-width: 600px) {
            h1 {
                font-size: 1.5em;
            }
            button {
                padding: 8px 15px;
                font-size: 0.9em;
            }
        }
    </style>
</head>
<body>
    <h1>Control Remoto</h1>

    <div class="section">
        <h3>Control de Música</h3>
        <div class="button-group">
            <button onclick="fetch('/music?control=play')">Play/Pause</button>
            <button onclick="fetch('/music?control=next')">Siguiente</button>
            <button onclick="fetch('/music?control=previous')">Anterior</button>
        </div>
    </div>
    
    <div class="section">
        <h3>Control de Brillo</h3>
        <div class="button-group">
            <button onclick="fetch('/brightness?level=up')">Subir Brillo</button>
            <button onclick="fetch('/brightness?level=down')">Bajar Brillo</button>
        </div>
    </div>
    
    <div class="section">
        <h3>Control de Volumen</h3>
        <div class="button-group">
            <button onclick="fetch('/volume?level=up')">Subir Volumen</button>
            <button onclick="fetch('/volume?level=down')">Bajar Volumen</button>
        </div>
    </div>
    
    <div class="section">
        <h3>Apagar Sistema</h3>
        <button class="shutdown" onclick="fetch('/shutdown')">Apagar</button>
    </div>
    
    <div class="section">
        <h3>Escanea este código QR para conectarte:</h3>
        <img src='/qrcode.png' alt="Código QR">
    </div>
</body>
</html>

    '''
# Ruta para controlar el olumen
@app.route('/volume', methods=['GET'])
def control_volume():
    level = request.args.get('level')
    devices = AudioUtilities.GetSpeakers()
    interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    volume = interface.QueryInterface(IAudioEndpointVolume)
    if level == 'up':
        volume.SetMasterVolumeLevelScalar(min(volume.GetMasterVolumeLevelScalar() + 0.1, 1.0), None)
        return "Subiste volumen pa"
    elif level == "down":
        volume.SetMasterVolumeLevelScalar(max(volume.GetMasterVolumeLevelScalar() - 0.1, 0.0), None)
        return "Subiste volumen pa"
    else:
        return "sepa la verga que hiciste", 400
    
@app.route("/music", methods=["GET"])
def control_music():
    action = request.args.get("control")
    try:
        if action == "play":
            keyboard.press_and_release("play/pause media")
            return "Reproducción/Pausa activada"
        elif action == "next":
            keyboard.press_and_release("next track")
            return "Siguiente canción activada"
        elif action == "previous":
            keyboard.press_and_release("previous track")
            return "Canción anterior activada"
        else:
            return "Acción no válida", 400
    except Exception as e:
        return f"Error en control de música: {e}", 500

@app.route("/brightness", methods=["GET"])
def control_brightness():
    level = request.args.get("level")
    try:
        current_brightness = sbc.get_brightness(display=0)[0]
        if level == "up":
            sbc.set_brightness(min(current_brightness + 10, 100), display=0)
            return "Brillo subido"
        elif level == "down":
            sbc.set_brightness(max(current_brightness - 10, 0), display=0)
            return "Brillo bajado"
        else:
            return "Acción no válida", 400
    except Exception as e:
        return f"Error en control de brillo: {e}", 500

@app.route("/shutdown", methods=["GET"])
def shutdown_system():
    try:
        os.system("shutdown /s /t 1")  # Comando para apagar Windows
        return "Sistema apagándose..."
    except Exception as e:
        return f"Error al apagar el sistema: {e}", 500
    
# Función para iniciar el servidor Flask
def start_flask_server():
    ip = get_local_ip()
    port = 12345
    url = f"http://{ip}:{port}"
    app.run(host="0.0.0.0", port=12345)

# Función para iniciar el servidor WiFi
def start_wifi_server(host="0.0.0.0", port=12346):
    try:
        wifi_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        wifi_server.bind((host, port))
        wifi_server.listen(5)
        print(f"WiFi server listening on {host}:{port}")
        
        while True:
            client_socket, client_address = wifi_server.accept()
            print(f"WiFi connection established with {client_address}")
            client_socket.sendall(b"Welcome to the WiFi server!")
            data = client_socket.recv(1024)
            print(f"Received WiFi data: {data.decode()}")
            client_socket.close()
    except Exception as e:
        print(f"WiFi Server Error: {e}")

def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

def generate_qr_code(url, filename="qrcode.png"):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)
    return filename

# Iniciar el servidor Flask
def start_flask_server():
    ip = get_local_ip()
    port = 12345
    url = f"http://{ip}:{port}/"

    # Generar el código QR
    generate_qr_code(url)

    print(f"Servidor iniciado en {url}")
    webbrowser.open(url)

    # Iniciar servidor Flask
    app.run(host="0.0.0.0", port=port)
    
@app.route('/qrcode.png')
def serve_qr_code():
    return send_file('qrcode.png', mimetype='image/png')

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask_server)
    flask_thread.start()
    flask_thread.join()
