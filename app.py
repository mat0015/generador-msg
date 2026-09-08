from flask import Flask, request, send_file, jsonify

from flask_cors import CORS

import io

import os

import uuid

 

app = Flask(__name__)

CORS(app)

 

@app.route('/health', methods=['GET'])

def health():

    return jsonify({'status': 'ok', 'message': 'Servidor funcionando correctamente'})

 

@app.route('/generate-msg', methods=['POST'])

def generate_msg():

    try:

        data = request.get_json()

       

        asunto = data.get('asunto', 'Sin asunto')

        email_cliente = data.get('email_cliente', 'cliente@dominio.com')

        html_body = data.get('html_body', '<p>Sin contenido</p>')

       

        if not asunto or not email_cliente:

            return jsonify({'error': 'Faltan datos requeridos'}), 400

       

        # Generar MIME manualmente SIN base64

        boundary = f"==============={uuid.uuid4().hex}=="

       

        # Construir el MIME message manualmente

        msg_lines = []

        msg_lines.append(f"From: noreply@generador.com")

        msg_lines.append(f"To: {email_cliente}")

        msg_lines.append(f"Subject: {asunto}")

        msg_lines.append(f"MIME-Version: 1.0")

        msg_lines.append(f"X-Mailer: Generador de Mensajes")

        msg_lines.append(f"X-Priority: 3")

        msg_lines.append(f"Content-Type: multipart/alternative; boundary=\"{boundary}\"")

        msg_lines.append("")

       

        # Parte de texto plano

        msg_lines.append(f"--{boundary}")

        msg_lines.append("Content-Type: text/plain; charset=\"utf-8\"")

        msg_lines.append("Content-Transfer-Encoding: 8bit")

        msg_lines.append("")

        msg_lines.append("Ver versión HTML de este mensaje.")

        msg_lines.append("")

       

        # Parte HTML

        msg_lines.append(f"--{boundary}")

        msg_lines.append("Content-Type: text/html; charset=\"utf-8\"")

        msg_lines.append("Content-Transfer-Encoding: 8bit")

        msg_lines.append("")

        msg_lines.append(html_body)

        msg_lines.append("")

       

        # Cierre

        msg_lines.append(f"--{boundary}--")

       

        # Unir con CRLF (formato correcto para email)

        msg_str = "\r\n".join(msg_lines)

        msg_bytes = msg_str.encode('utf-8')

       

        # Generar nombre seguro

        safe_filename = asunto.replace('/', '_').replace('\\', '_').replace(':', '_')[:80]

        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ' _-ñáéíóú')

        safe_filename = safe_filename.replace(' ', '_').strip('_')

       

        if not safe_filename:

            safe_filename = 'correo'

       

        # Crear archivo en memoria

        file_obj = io.BytesIO(msg_bytes)

       

        # Retornar como .msg

        return send_file(

            file_obj,

            mimetype='application/vnd.ms-outlook',

            as_attachment=True,

            download_name=f'{safe_filename}.msg'

        )

       

    except Exception as e:

        print(f"Error: {str(e)}")

        import traceback

        traceback.print_exc()

        return jsonify({'error': str(e)}), 500

 

@app.route('/test', methods=['GET'])

def test():

    return jsonify({'message': 'Backend funcionando correctamente'})

 

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port, debug=False)