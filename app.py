from flask import Flask, request, Response

from flask_cors import CORS

import os

import uuid

import io

import struct

from datetime import datetime

 

app = Flask(__name__)

CORS(app)

 

def create_ole2_msg(asunto, email_cliente, html_body):

    """

    Genera un archivo .MSG OLE2 real compatible con Outlook

    Basado en el formato MAPI/OLE2 de Microsoft

    """

   

    # Crear estructura OLE2 mínima

    # Cabecera OLE2 (512 bytes)

    ole_header = bytearray(512)

   

    # Firma OLE2

    ole_header[0:8] = b'\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1'

   

    # CLSID (16 bytes de ceros)

    ole_header[8:24] = b'\x00' * 16

   

    # Minor version, Major version (3 = 512 bytes)

    ole_header[24:26] = b'\x00\x00'

    ole_header[26:28] = b'\x03\x00'

   

    # Byte order (0xFFFE = little endian)

    ole_header[28:30] = b'\xfe\xff'

   

    # Sector size power (9 = 512 bytes)

    ole_header[30:32] = struct.pack('<H', 9)

   

    # Mini sector size power (6 = 64 bytes)

    ole_header[32:34] = struct.pack('<H', 6)

   

    # Reserved

    ole_header[34:40] = b'\x00' * 6

   

    # Total sectors (0 para versión 3)

    ole_header[44:48] = b'\x00\x00\x00\x00'

   

    # FAT sectors

    ole_header[48:52] = struct.pack('<I', 0)

   

    # Directory first sector

    ole_header[52:56] = struct.pack('<I', 0)

   

    # Mini FAT first sector (-2 = no existe)

    ole_header[60:64] = struct.pack('<i', -2)

   

    # Total mini FAT sectors

    ole_header[64:68] = struct.pack('<I', 0)

   

    # First DIFAT sector (-2 = no DIFAT)

    ole_header[68:72] = struct.pack('<i', -2)

   

    # Total DIFAT sectors

    ole_header[72:76] = struct.pack('<I', 0)

   

    # DIFAT array (109 primeras FAT sectors)

    ole_header[76:80] = struct.pack('<I', 0)  # FAT sector 0

    for i in range(80, 512):

        ole_header[i] = 0xfe

   

    # Crear contenido MIME multipart

    boundary = f"==============={uuid.uuid4().hex}=="

   

    msg_lines = []

    msg_lines.append(f"From: noreply@generador.com")

    msg_lines.append(f"To: {email_cliente}")

    msg_lines.append(f"Subject: {asunto}")

    msg_lines.append(f"MIME-Version: 1.0")

    msg_lines.append(f"X-Mailer: Generador de Mensajes")

    msg_lines.append(f"Content-Type: multipart/alternative; boundary=\"{boundary}\"")

    msg_lines.append("")

   

    msg_lines.append(f"--{boundary}")

    msg_lines.append("Content-Type: text/plain; charset=\"utf-8\"")

    msg_lines.append("")

    msg_lines.append("Ver versión HTML de este mensaje.")

    msg_lines.append("")

   

    msg_lines.append(f"--{boundary}")

    msg_lines.append("Content-Type: text/html; charset=\"utf-8\"")

    msg_lines.append("")

    msg_lines.append(html_body)

    msg_lines.append("")

   

    msg_lines.append(f"--{boundary}--")

   

    msg_content = "\r\n".join(msg_lines)

    msg_bytes = msg_content.encode('utf-8')

   

    # Crear FAT (File Allocation Table)

    # Sector 0 = FAT

    # Sector 1 = Directory

    # Sector 2 = Contenido del mensaje

    fat = bytearray(512)

   

    # Marcar sectores: -3 = FAT, -2 = end of chain, -1 = free

    fat[0:4] = struct.pack('<i', -3)      # Sector 0 es FAT

    fat[4:8] = struct.pack('<i', -2)      # Sector 1 fin de cadena (dir)

   

    # Calcular cuántos sectores necesita el contenido

    content_sectors = (len(msg_bytes) + 511) // 512

    for i in range(content_sectors - 1):

        fat[(2 + i) * 4:(2 + i + 1) * 4] = struct.pack('<i', 3 + i)

    fat[(2 + content_sectors - 1) * 4:(2 + content_sectors) * 4] = struct.pack('<i', -2)

   

    # Rellenar resto de FAT con -1 (libre)

    for i in range(2 + content_sectors, 128):

        fat[i * 4:(i + 1) * 4] = struct.pack('<i', -1)

   

    # Crear entry de directorio

    # Root entry

    dir_entry = bytearray(512)

   

    # Nombre del root: "Root Entry"

    root_name = "Root Entry".encode('utf-16-le')

    dir_entry[0:len(root_name)] = root_name

    dir_entry[64:66] = struct.pack('<H', len(root_name) + 2)

   

    # Type: 5 = root storage

    dir_entry[66:67] = b'\x05'

   

    # Color: 1 = black

    dir_entry[67:68] = b'\x01'

   

    # Left sibling: -1

    dir_entry[68:72] = struct.pack('<i', -1)

   

    # Right sibling: -1

    dir_entry[72:76] = struct.pack('<i', -1)

   

    # Child DID: 1 (el contenido)

    dir_entry[76:80] = struct.pack('<I', 1)

   

    # Size: 0

    dir_entry[120:124] = struct.pack('<I', 0)

   

    # Start sector: 0

    dir_entry[116:120] = struct.pack('<I', 0)

   

    # Entry del contenido

    content_name = "Message".encode('utf-16-le')

    dir_entry[128:128 + len(content_name)] = content_name

    dir_entry[192:194] = struct.pack('<H', len(content_name) + 2)

   

    # Type: 2 = stream

    dir_entry[194:195] = b'\x02'

   

    # Color: 1 = black

    dir_entry[195:196] = b'\x01'

   

    # Left sibling: -1

    dir_entry[196:200] = struct.pack('<i', -1)

   

    # Right sibling: -1

    dir_entry[200:204] = struct.pack('<i', -1)

   

    # Child: -1

    dir_entry[204:208] = struct.pack('<i', -1)

   

    # Start sector: 2

    dir_entry[244:248] = struct.pack('<I', 2)

   

    # Size

    dir_entry[248:252] = struct.pack('<I', len(msg_bytes))

   

    # Rellenar contenido a múltiples de 512

    padded_content = bytearray(((len(msg_bytes) + 511) // 512) * 512)

    padded_content[0:len(msg_bytes)] = msg_bytes

   

    # Armar el archivo final

    ole_file = bytearray()

    ole_file.extend(ole_header)

    ole_file.extend(fat)

    ole_file.extend(dir_entry)

    ole_file.extend(padded_content)

   

    return bytes(ole_file)

 

 

@app.route('/health', methods=['GET'])

def health():

    return {'status': 'ok', 'message': 'Servidor funcionando correctamente'}

 

@app.route('/generate-msg', methods=['POST'])

def generate_msg():

    try:

        data = request.get_json()

       

        asunto = data.get('asunto', 'Sin asunto')

        email_cliente = data.get('email_cliente', 'cliente@dominio.com')

        html_body = data.get('html_body', '<p>Sin contenido</p>')

       

        if not asunto or not email_cliente:

            return {'error': 'Faltan datos requeridos'}, 400

       

        # Generar archivo OLE2/MSG

        msg_bytes = create_ole2_msg(asunto, email_cliente, html_body)

       

        safe_filename = asunto.replace('/', '_').replace('\\', '_').replace(':', '_')[:80]

        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ' _-ñáéíóú')

        safe_filename = safe_filename.replace(' ', '_').strip('_')

       

        if not safe_filename:

            safe_filename = 'correo'

       

        response = Response(msg_bytes)

        response.headers['Content-Type'] = 'application/octet-stream'

        response.headers['Content-Disposition'] = f'attachment; filename="{safe_filename}.msg"'

       

        return response

       

    except Exception as e:

        print(f"Error: {str(e)}")

        import traceback

        traceback.print_exc()

        return {'error': str(e)}, 500

 

@app.route('/test', methods=['GET'])

def test():

    return {'message': 'Backend funcionando correctamenteeeeeeeeee'}

 

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port, debug=False)
