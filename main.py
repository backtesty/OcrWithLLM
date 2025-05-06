import base64
import mimetypes
import json
import time
import os
from openai import OpenAI
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)

format_output = """
{
    "company_name": "Nombre de la empresa",
    "company_address": "Dirección de la empresa",
    "receiver_name": "Nombre del receptor",
    "receiver_address": "Dirección del receptor",
    "send_invoice_to": "Enviar factura a",
    "send_invoice_to_address": "Enviar factura a dirección",
    "invoice_number": "Número de factura",
    "invoice_date": "Fecha de la factura",
    "invoice_order": "Orden de la factura",
    "invoice_due_date": "Fecha de vencimiento de la factura",
    "invoice_total": "Total de la factura",
    "invoice_money": "Moneda de la factura",
    "iva_percentaje": "IVA",
    "iva_amount": "Monto del IVA",
    "invoice_items": [
        {
            "item_name": "Nombre del artículo",
            "item_quantity": "Cantidad del artículo",
            "item_price": "Precio unitario del artículo",
            "item_total": "Precio total del artículo"
        }
    ],
}
"""

prompt = f"""
Te envío una factura de venta. Extraer los siguientes datos de la imagen y devolverlos en formato JSON:

{format_output}
"""
time_start = time.time()
data_uri = ""
local_path = "modelo-factura.png"  # Replace with your image path
data_json = None
with open(local_path, "rb") as image_file:
    extension = local_path.split(".")[-1]
    content_type, encoding = mimetypes.guess_type("_dummy" + extension)
    if content_type is None:
        content_type = "image/jpeg"
    image_base64 = base64.b64encode(image_file.read()).decode("utf-8")
    data_uri = f"data:{content_type};base64,{image_base64}"
    messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_uri,
                        },
                    },
                ],
            }
        ]
    response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.7
            )
    content_voucher = response.choices[0].message.content

    data_json = json.loads(content_voucher)
    time_end = time.time()
    print(f"Tiempo de ejecución: {time_end - time_start} segundos")
    print(data_json)

    with open("output.json", "w", encoding="utf-8") as json_file:
        json.dump(data_json, json_file, ensure_ascii=False, indent=4)
    print("JSON guardado en output.json")
