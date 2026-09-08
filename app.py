from flask import Flask, request, send_file, jsonify

from flask_cors import CORS

import io

import os

from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText

from email import encoders

 

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

       

        # Crear mensaje MIME sin usar base64

        msg = MIMEMultipart('alternative')

        msg['Subject'] = asunto

        msg['From'] = 'noreply@generador.com'

        msg['To'] = email_cliente

        msg['X-Mailer'] = 'Generador de Mensajes'

        msg['X-Priority'] = '3'

        msg['Content-Transfer-Encoding'] = '8bit'

       

        # Parte de texto plano - SIN charset para evitar base64

        text_part = MIMEText('Ver versión HTML de este mensaje.', 'plain')

        text_part['Content-Transfer-Encoding'] = '8bit'

        msg.attach(text_part)

       

        # Parte HTML - SIN base64

        html_part = MIMEText(html_body, 'html')

        html_part['Content-Transfer-Encoding'] = '8bit'

        html_part.replace_header('Content-Type', 'text/html; charset="utf-8"')

        msg.attach(html_part)

       

        # Obtener contenido como string (no bytes) para evitar encoding

        msg_str = msg.as_string()

        msg_bytes = msg_str.encode('utf-8')

       

        # Generar nombre seguro

        safe_filename = asunto.replace('/', '_').replace('\\', '_').replace(':', '_')[:80]

        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ' _-ñáéíóú')

        safe_filename = safe_filename.replace(' ', '_').strip('_')

       

        if not safe_filename:

            safe_filename = 'correo'

       

        # Crear archivo en memoria

        file_obj = io.BytesIO(msg_bytes)

       

        # Retornar con headers que obliguen a descargar

        return send_file(

            file_obj,

            mimetype='application/octet-stream',

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