from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import io
import os

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
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = asunto
        msg['From'] = 'noreply@generador.com'
        msg['To'] = email_cliente
        msg['X-Mailer'] = 'Generador de Mensajes'
        
        text_part = MIMEText('Ver versión HTML de este mensaje.', 'plain', 'utf-8')
        msg.attach(text_part)
        
        html_part = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(html_part)
        
        msg_bytes = msg.as_bytes()
        
        safe_filename = asunto.replace('/', '_').replace('\\', '_').replace(':', '_')[:80]
        safe_filename = ''.join(c for c in safe_filename if c.isalnum() or c in ' _-ñáéíóú')
        safe_filename = safe_filename.replace(' ', '_').strip('_')
        
        if not safe_filename:
            safe_filename = 'correo'
        
        file_obj = io.BytesIO(msg_bytes)
        
        return send_file(
            file_obj,
            mimetype='application/vnd.ms-outlook',
            as_attachment=True,
            download_name=f'{safe_filename}.msg'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test', methods=['GET'])
def test():
    return jsonify({'message': 'Backend funcionando correctamente'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
