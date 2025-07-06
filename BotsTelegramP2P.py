import os
import requests
import time

def enviar_mensaje(mensaje):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": mensaje}
    requests.post(url, data=data)

def obtener_precio(pais, moneda, metodo_pago, transaccion):
    url = (
        f"https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    )
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
    global TOKEN, CHAT_ID
    # Leer variables de entorno
    TOKEN = os.environ["TOKEN"]
    CHAT_ID = os.environ["CHAT_ID"]

    UMBRAL_COMPRA_SKRILL = float(os.environ["UMBRAL_COMPRA_SKRILL"])
    UMBRAL_VENTA = float(os.environ["UMBRAL_VENTA"])
    UMBRAL_VENTA_DIRECTA = float(os.environ["UMBRAL_VENTA_DIRECTA"])

    while True:
        try:
            # Alerta 1: Skrill a compra (P2P tipo BUY)
            precio_skrill = obtener_precio("EC", "USD", "Skrill", "BUY")
            if precio_skrill and precio_skrill >= UMBRAL_COMPRA_SKRILL:
                mensaje = f"🔔 *Alerta Skrill a COMPRA*\nPrecio: {precio_skrill} USDT\nUmbral: {UMBRAL_COMPRA_SKRILL} USDT"
                enviar_mensaje(mensaje)

            # Alerta 2: BancoPichincha a venta (P2P tipo SELL)
            precio_pichincha_venta = obtener_precio("EC", "USD", "BancoPichincha", "SELL")
            if precio_pichincha_venta and precio_pichincha_venta <= UMBRAL_VENTA:
                mensaje = f"💰 *Alerta BancoPichincha VENTA*\nPrecio: {precio_pichincha_venta} USDT\nUmbral: {UMBRAL_VENTA} USDT"
                enviar_mensaje(mensaje)

            # Alerta 3: Venta directa (P2P tipo BUY)
            precio_pichincha_compra = obtener_precio("EC", "USD", "BancoPichincha", "BUY")
            if precio_pichincha_compra and precio_pichincha_compra >= UMBRAL_VENTA_DIRECTA:
                mensaje = f"📢 *Alerta VENTA DIRECTA*\nPrecio de compra: {precio_pichincha_compra} USDT\nUmbral: {UMBRAL_VENTA_DIRECTA} USDT"
                enviar_mensaje(mensaje)

        except Exception as e:
            print("Error durante la ejecución:", e)

        time.sleep(60)  # Esperar 60 segundos antes de la siguiente revisión

if __name__ == "__main__":
    main()
