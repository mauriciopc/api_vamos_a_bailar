import os
import json
import logging
import boto3
import botocore.exceptions

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")

BUCKET = os.environ["BUCKET"]              # p.ej. "mi-bucket-privado"
ALLOW_ORIGIN = os.environ.get("ALLOW_ORIGIN", "*")  # pon tu dominio de Amplify
DEFAULT_KEY = os.environ.get("KEY")        # opcional: clave por defecto

def _resp(status, body=None):
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": ALLOW_ORIGIN,
        "Access-Control-Allow-Credentials": "true",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
        "Cache-Control": "no-store",
    }

    return {
        "statusCode": status,
        "headers": headers,
        "body": "" if body is None else json.dumps(body, ensure_ascii=False),
    }

def handler(event, context):
    print("esto es lo que tiene event -> ",event)

    try:
        obj = s3.get_object(Bucket=BUCKET, Key=DEFAULT_KEY)
        text = obj["Body"].read().decode("utf-8")

        # Si es JSON válido, devuélvelo como objeto; si no, como texto crudo.
        try:
            data = json.loads(text)
            return _resp(200, data)
        except json.JSONDecodeError:
            return _resp(200, {"raw": text})
    except botocore.exceptions.ClientError as e:
        code = e.response.get("Error", {}).get("Code")
        if code == "NoSuchKey":
            return _resp(404, {"message": "Objeto no encontrado"})
        if code == "AccessDenied":
            return _resp(403, {"message": "Acceso denegado"})
        logger.exception("Error S3 inesperado")
        return _resp(500, {"message": "Error interno"})
    except Exception:
        logger.exception("Error inesperado")
        return _resp(500, {"message": "Error interno"})

lambda_handler = handler