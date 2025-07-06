import os
import requests
import time

def enviar_mensaje(token, chat_id, mensaje):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {"chat_id": chat_id, "text": mensaje}
    requests.post(url, data=data)

def obtener_precio(moneda, metodo_pago, transaccion):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    data = {
        "asset": "USDT",
        "fiat": moneda,
        "merchantCheck": False,
        "page": 1,
        "payTypes": [metodo_pago],
        "publisherType": None,
        "rows": 1,
        "tradeType": transaccion,
        "proMerchantAds": False,
        "shieldMerchantAds": False
    }
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        r_json = response.json()
        return float(r_json["data"][0]["adv"]["price"])
    else:
        print("Error al consultar API de Binance")
        return None

def main():
    # Leer variables de entorno
    print("🔍 DEBUG ENV VARS:")
    for var in ["TOKEN", "CHAT_ID", "UMBRAL_COMPRA_SKRILL", "UMBRAL_VENTA", "UMBRAL_VENTA_DIRECTA"]:
        print(f"{var} => {os.environ.get(var, 'NO DEFINIDA')}")

    token = os.environ["TOKEN"]
    chat_id = os.environ["CHAT_ID"]

    umbral_compra_skrill = float(os.environ["UMBRAL_COMPRA_SKRILL"])
    umbral_venta = float(os.environ["UMBRAL_VENTA"])
    umbral_venta_directa = float(os.environ["UMBRAL_VENTA_DIRECTA"])

    while True:
        try:
            # Alerta 1: Skrill a compra
            precio_skrill = obtener_precio("USD", "Skrill", "BUY")
            if precio_skrill and precio_skrill >= umbral_compra_skrill:
                mensaje = f"🔔 *Alerta Skrill a COMPRA*\nPrecio: {precio_skrill} USDT\nUmbral: {umbral_compra_skrill} USDT"
                enviar_mensaje(token, chat_id, mensaje)

            # Alerta 2: BancoPichincha a venta
            precio_pichincha_venta = obtener_precio("USD", "BancoPichincha", "SELL")
            if precio_pichincha_venta and precio_pichincha_venta <= umbral_venta:
                mensaje = f"💰 *Alerta BancoPichincha VENTA*\nPrecio: {precio_pichincha_venta} USDT\nUmbral: {umbral_venta} USDT"
                enviar_mensaje(token, chat_id, mensaje)

            # Alerta 3: Venta directa (alguien comprando con Pichincha)
            precio_pichincha_compra = obtener_precio("USD", "BancoPichincha", "BUY")
            if precio_pichincha_compra and precio_pichincha_compra >= umbral_venta_directa:
                mensaje = f"📢 *Alerta VENTA DIRECTA*\nPrecio de compra: {precio_pichincha_compra} USDT\nUmbral: {umbral_venta_directa} USDT"
                enviar_mensaje(token, chat_id, mensaje)

        except Exception as e:
            print("Error durante la ejecución:", e)

        time.sleep(60)

if __name__ == "__main__":
    main()
