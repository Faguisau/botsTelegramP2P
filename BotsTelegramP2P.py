import requests
import time
from datetime import datetime

# --- Configuración Binance ---
# Banco Pichincha (venta)
umbral_1 = 0.982
umbral_2 = 0.981
umbral_3 = 0.981
metodo_pago_venta = "BancoPichincha"

# Skrill (compra)
umbral_skrill_1 = 1.040
umbral_skrill_2 = 1.048
umbral_skrill_3 = 1.050
metodo_pago_compra = "SkrillMoneybookers"

moneda = "USD"
cripto = "USDT"
intervalo_espera = 120  # 5 minutos

# --- Configuración Telegram ---
bot_token = "7725174874:AAHdi1WSIDhgTY7zyCuspbWwqtwdyaW0HYQ"
chat_id = "677169018"

# --- Configuración de Logs ---
log_file = "registro_alertas.txt"

def loggear(texto):
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {texto}\n")

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
            mensaje = f"⚠️ No hay anuncios disponibles para {tipo_transaccion} con {metodo_pago}"
            loggear(mensaje)
            return None, mensaje

        anuncio_top = anuncios[0]
        precio = float(anuncio_top["adv"]["price"])
        comerciante = anuncio_top["advertiser"]["nickName"]
        volumen = anuncio_top["adv"]["tradableQuantity"]
        return (precio, comerciante, volumen), None

    except Exception as e:
        error_msg = f"❌ Error obteniendo datos para {tipo_transaccion} con {metodo_pago}: {e}"
        loggear(error_msg)
        return None, error_msg

def main():
    ultimo_precio_venta = None
    ultimo_precio_compra = None

    while True:
        hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # --- Venta con Banco Pichincha ---
        resultado_venta, motivo_venta = obtener_info_top(metodo_pago_venta, "SELL")
        if resultado_venta:
            precio, comerciante, volumen = resultado_venta

            if ultimo_precio_venta is not None:
                if precio > ultimo_precio_venta:
                    tendencia = "🔼 Subió"
                elif precio < ultimo_precio_venta:
                    tendencia = "🔽 Bajó"
                else:
                    tendencia = "⏸️ Sin cambio"
            else:
                tendencia = "📌 Primer dato"

            loggear(f"Venta {metodo_pago_venta}: {precio:.3f} USD ({tendencia}) por {comerciante} ({volumen} USDT)")

            if precio <= umbral_3:
                mensaje = f"🔴 🔻 Venta Nivel 3 - {metodo_pago_venta}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
            elif precio <= umbral_2:
                mensaje = f"🟠 🔻 Venta Nivel 2 - {metodo_pago_venta}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
            elif precio <= umbral_1:
                mensaje = f"🟡 🔻 Venta Nivel 1 - {metodo_pago_venta}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)

            ultimo_precio_venta = precio
        elif motivo_venta:
            enviar_telegram(f"{motivo_venta}\n🕒 {hora}")

        # --- Compra con Skrill ---
        resultado_compra, motivo_compra = obtener_info_top(metodo_pago_compra, "BUY")
        if resultado_compra:
            precio, comerciante, volumen = resultado_compra

            if ultimo_precio_compra is not None:
                if precio > ultimo_precio_compra:
                    tendencia = "🔼 Subió"
                elif precio < ultimo_precio_compra:
                    tendencia = "🔽 Bajó"
                else:
                    tendencia = "⏸️ Sin cambio"
            else:
                tendencia = "📌 Primer dato"

            loggear(f"Compra {metodo_pago_compra}: {precio:.3f} USD ({tendencia}) por {comerciante} ({volumen} USDT)")

            if precio >= umbral_skrill_3:
                mensaje = f"🔴 🟢 Compra Nivel 3 - {metodo_pago_compra}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
            elif precio >= umbral_skrill_2:
                mensaje = f"🟠 🟢 Compra Nivel 2 - {metodo_pago_compra}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)
            elif precio >= umbral_skrill_1:
                mensaje = f"🟡 🟢 Compra Nivel 1 - {metodo_pago_compra}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)

            ultimo_precio_compra = precio
        elif motivo_compra:
            enviar_telegram(f"{motivo_compra}\n🕒 {hora}")

        time.sleep(intervalo_espera)

if __name__ == "__main__":
    main()
