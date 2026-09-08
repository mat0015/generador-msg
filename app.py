from flask import Flask, request, Response

from flask_cors import CORS

import os

import uuid

from email.mime.multipart import MIMEMultipart

from email.mime.text import MIMEText

import io

 

app = Flask(__name__)

CORS(app)

 

def create_msg_from_eml(asunto, email_cliente, html_body):

    """

    Crea un archivo MSG válido a partir de estructura EML

    Usa conversion format que Outlook entiende

    """

   

    # Crear estructura MIME

    msg = MIMEMultipart('alternative')

    msg['From'] = 'noreply@generador.com'

    msg['To'] = email_cliente

    msg['Subject'] = asunto

    msg['X-Mailer'] = 'Generador de Mensajes'

    msg['MIME-Version'] = '1.0'

   

    # Parte texto plano

    part_text = MIMEText('Ver versión HTML de este mensaje.', 'plain', _charset='utf-8')

    msg.attach(part_text)

   

    # Parte HTML

    part_html = MIMEText(html_body, 'html', _charset='utf-8')

    msg.attach(part_html)

   

    # Convertir a string respetando CRLF para Windows

    msg_str = msg.as_string(unixfrom=False)

   

    # En Windows, Outlook puede abrir archivos .msg que son en realidad EML con extensión MSG

    # Esto es un workaround conocido que funciona en Outlook 2016+

    msg_bytes = msg_str.encode('utf-8')

   

    return msg_bytes

 

 

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

       

        # Generar MSG

        msg_bytes = create_msg_from_eml(asunto, email_cliente, html_body)

       

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

    return {'message': 'Backend funcionando correctamente'}

 

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port, debug=False)

 

 

@app.route('/health', methods=['GET'])

def health():

    return {'status': 'ok', 'message': 'Servidor funcionando correctamenteEe'}

 

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

    return {'message': 'Backend funcionando correctamentEeE'}

 

if __name__ == '__main__':

    port = int(os.environ.get('PORT', 5000))

    app.run(host='0.0.0.0', port=port, debug=False)
