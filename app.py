from flask import Flask, render_template, request, send_file
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import keyboard
import screen_brightness_control as sbc
import os
import qrcode
import threading
import webbrowser
import socket

app = Flask(__name__, template_folder='templates', static_folder='static')

@app.route('/')
def page():
    return render_template('index.html')

@app.route('/volume', methods=['GET'])
def control_volume():
    try:
        level = float(request.args.get("level")) / 100
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = interface.QueryInterface(IAudioEndpointVolume)
        volume.SetMasterVolumeLevelScalar(level, None)
        return f"Volumen ajustado a {int(level * 100)}%"
    except Exception as e:
        return f"Error en control de volumen: {e}", 500

@app.route("/brightness", methods=["GET"])
def control_brightness():
    try:
        level = int(request.args.get("level"))
        sbc.set_brightness(level, display=0)
        return f"Brillo ajustado a {level}%"
    except Exception as e:
        return f"Error en control de brillo: {e}", 500

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

@app.route("/shutdown", methods=["GET"])
def shutdown_system():
    try:
        os.system("shutdown /s /t 1")
        return "Sistema apagándose..."
    except Exception as e:
        return f"Error al apagar el sistema: {e}", 500

@app.route('/qrcode.png')
def serve_qr_code():
    return send_file('static/qrcode.png', mimetype='image/png')

def generate_qr_code(url, filename="static/qrcode.png"):
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

def get_local_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)

@app.route('/execute-file', methods=['GET'])
def execute_file():
    try:
        # Ruta absoluta del archivo en el escritorio de Windows
        file_path = r"C:\Users\0scar\Desktop\Fortnite.url"

        # Ejecuta el archivo
        os.startfile(file_path)

        return "Archivo ejecutado exitosamente."
    except Exception as e:
        return f"Error al ejecutar el archivo: {e}", 500


def start_flask_server():
    ip = get_local_ip()
    port = 12345
    url = f"http://{ip}:{port}/"
    generate_qr_code(url)
    print(f"Servidor iniciado en {url}")
    webbrowser.open(url)
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    threading.Thread(target=start_flask_server).start()
