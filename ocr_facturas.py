import os
import base64
import mimetypes
import json
from openai import OpenAI
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
openai_client = OpenAI(api_key=OPENAI_API_KEY)


data = []
for factura in os.listdir("pdf_parts"):
    if factura.endswith(".jpg"):

        format_output = """
        {
            "fecha_emision": "Fecha de emisión en formato YYYY-MM-DD",
            "hora_emision": "Hora de emisión en formato HH:MM",
            "fecha_validation": "Fecha de validación DAN en formato YYYY-MM-DD",
            "hora_validation": "Hora de validación en formato HH:MM",
            "fecha_vencimiento": "Fecha de vencimiento en formato YYYY-MM-DD",
            "codigo_moneda": "COP o PEN o USD o EUR",
            "cliente_empresa_nombre": "Nombre del cliente empresa o organización",
            "cliente_empresa_nit": "NIT del cliente empresa o organización",
            "cliente_empresa_direccion": "Dirección del cliente empresa o organización",
            "cliente_empresa_telefono": "Teléfono del cliente empresa o organización",
            "cliente_empresa_ciudad": "Ciudad del cliente empresa o organización",
            "nro_factura_venta": "Número de la factura de venta",
            "nro_factura_compra": "Número de la factura de compra",
            "condiciones_pago": "Condiciones de pago",
            "formas_pago": "Formas de pago",
            "iva_porcentaje": "IVA en porcentaje, no incluir el signo %",
            "iva_monto": "IVA en monto",
            "total_factura": "Monto total de la factura",
            "items": [
                {
                    "item_numero": "Número del artículo",
                    "item_referencia": "Referencia o código del artículo",
                    "item_descripcion": "Descripción del artículo",
                    "item_unidad_medida": "Unidad de medida del artículo",
                    "item_cantidad": "Cantidad del artículo",
                    "item_cargos_descuentos": "Cargos o descuentos del artículo",
                    "item_precio_unitario": "Precio unitario del artículo",
                    "item_total": "Importe total del artículo",
                }
            ],
        }
        """

        prompt = f"""
        Te envío una factura. Extraer los siguientes campos de la imagen y devolverlos en formato JSON:

        ```json
        {format_output}
        ```
        """

        data_uri = ""
        local_path = f"pdf_parts/{factura}"
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
                        temperature=0.3
                    )
            content_voucher = response.choices[0].message.content
            data_json = json.loads(content_voucher)
            data.append(data_json)

with open("facturas.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

