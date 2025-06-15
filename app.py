from flask import Flask, Response
from flask_cors import CORS
from dotenv import load_dotenv

import boto3
import os
import json


app = Flask(__name__)
CORS(app)  # Permite todas las rutas y orígenes

@app.route('/api/obtieneEventos', methods=['GET'])
def obtener_datos():
    load_dotenv()

    s3 = boto3.client('s3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    obj = s3.get_object(Bucket=os.getenv("BUCKET_NAME"), Key="info_paginas.json")
    contenido = obj['Body'].read().decode('utf-8')
    datos = json.loads(contenido)
    json_pretty = json.dumps(datos, indent=4, ensure_ascii=False)

    return Response(json_pretty, mimetype='application/json')

if __name__ == '__main__':
    app.run()