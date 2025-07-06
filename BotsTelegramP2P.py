import requests
import time
from datetime import datetime, timedelta
import os
import json

# --- Configuración Binance ---
# Banco Pichincha (venta)
umbral_1 = 0.991
umbral_2 = 0.986
umbral_3 = 0.982
metodo_pago_venta = "BancoPichincha"

# Skrill (compra)
umbral_skrill_1 = 1.020
umbral_skrill_2 = 1.035
umbral_skrill_3 = 1.045
metodo_pago_compra = "SkrillMoneybookers"

moneda = "USD"
cripto = "USDT"
intervalo_espera = 120

# --- Configuración Telegram ---
bot_token = "7725174874:AAHdi1WSIDhgTY7zyCuspbWwqtwdyaW0HYQ"
chat_id = "677169018"

# --- Configuración de Logs ---
log_file = "registro_alertas.txt"
estado_file = "estado_alertas.json"

def loggear(texto):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {texto}\n")

def cargar_estado():
    if os.path.exists(estado_file):
        with open(estado_file, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def guardar_estado(alertas_enviadas):
    with open(estado_file, "w", encoding="utf-8") as f:
        json.dump(list(alertas_enviadas), f)

def enviar_telegram(mensaje):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    params = {"chat_id": chat_id, "text": mensaje}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        print("✅ Mensaje enviado por Telegram.")
        loggear("Mensaje enviado: " + mensaje.replace("\n", " | "))
    else:
        print("⚠️ Error al enviar el mensaje:", response.text)
        loggear("Error al enviar mensaje: " + response.text)

def obtener_info_top(metodo_pago, tipo_transaccion):
    url = "https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search"
    headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
    data = {
        "asset": cripto,
        "fiat": moneda,
        "merchantCheck": False,
        "page": 1,
        "rows": 10,
        "payTypes": [metodo_pago],
        "tradeType": tipo_transaccion
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        anuncios = response.json()["data"]
        if not anuncios:
            loggear(f"Sin anuncios disponibles para {tipo_transaccion} con {metodo_pago}.")
            return None

        anuncio_top = anuncios[0]
        precio = float(anuncio_top["adv"]["price"])
        comerciante = anuncio_top["advertiser"]["nickName"]
        volumen = anuncio_top["adv"]["tradableQuantity"]
        return precio, comerciante, volumen

    except Exception as e:
        loggear(f"❌ Error obteniendo datos para {tipo_transaccion} con {metodo_pago}: {e}")
        return None

def main():
    alertas_enviadas = cargar_estado()
    tiempo_inicio = datetime.now()

    while True:
        if datetime.now() - tiempo_inicio >= timedelta(hours=24):
            alertas_enviadas.clear()
            guardar_estado(alertas_enviadas)
            tiempo_inicio = datetime.now()
            loggear("♻️ Reinicio automático de alertas tras 24 horas")

        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Alerta para venta con Banco Pichincha ---
        resultado_venta = obtener_info_top(metodo_pago_venta, "SELL")
        if resultado_venta:
            precio, comerciante, volumen = resultado_venta
            loggear(f"Venta {metodo_pago_venta}: {precio:.3f} USD por {comerciante} ({volumen} USDT)")

            if precio <= umbral_3 and ("venta3" not in alertas_enviadas):
                mensaje = f"🔴 🔻 Venta Nivel 3 - {metodo_pago_venta}: {precio:.3f} USD\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
                alertas_enviadas.add("venta3")
            elif precio <= umbral_2 and ("venta2" not in alertas_enviadas):
                mensaje = f"🟠 🔻 Venta Nivel 2 - {metodo_pago_venta}: {precio:.3f} USD\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
                alertas_enviadas.add("venta2")
            elif precio <= umbral_1 and ("venta1" not in alertas_enviadas):
                mensaje = f"🟡 🔻 Venta Nivel 1 - {metodo_pago_venta}: {precio:.3f} USD\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
                alertas_enviadas.add("venta1")

        # --- Alerta para compra con Skrill ---
        resultado_compra = obtener_info_top(metodo_pago_compra, "BUY")
        if resultado_compra:
            precio, comerciante, volumen = resultado_compra
            loggear(f"Compra {metodo_pago_compra}: {precio:.3f} USD por {comerciante} ({volumen} USDT)")

            if precio >= umbral_skrill_3 and ("compra3" not in alertas_enviadas):
                mensaje = f"🔴 🟢 Compra Nivel 3 - {metodo_pago_compra}: {precio:.3f} USD\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
                alertas_enviadas.add("compra3")
            elif precio >= umbral_skrill_2 and ("compra2" not in alertas_enviadas):
                mensaje = f"🟠 🟢 Compra Nivel 2 - {metodo_pago_compra}: {precio:.3f} USD\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
                alertas_enviadas.add("compra2")
            elif precio >= umbral_skrill_1 and ("compra1" not in alertas_enviadas):
                mensaje = f"🟡 🟢 Compra Nivel 1 - {metodo_pago_compra}: {precio:.3f} USD\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
                alertas_enviadas.add("compra1")

        guardar_estado(alertas_enviadas)
        time.sleep(intervalo_espera)

if __name__ == "__main__":
    main()
