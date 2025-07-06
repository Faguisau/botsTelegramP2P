import requests
import time
from datetime import datetime

# --- Configuración Binance ---
metodo_pago_venta = "BancoPichincha"
metodo_pago_compra = "SkrillMoneybookers"

umbral_venta = 0.990
umbral_venta_directa = 0.990
umbral_compra_skrill = 1.010

moneda = "USD"
cripto = "USDT"
intervalo_espera = 120  # 2 minutos

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

        # --- Alerta: Venta con Banco Pichincha ---
        resultado_venta, motivo_venta = obtener_info_top(metodo_pago_venta, "SELL")
        if resultado_venta:
            precio, comerciante, volumen = resultado_venta
            tendencia = "📌 Primer dato" if ultimo_precio_venta is None else (
                "🔼 Subió" if precio > ultimo_precio_venta else
                "🔽 Bajó" if precio < ultimo_precio_venta else "⏸️ Sin cambio"
            )

            loggear(f"Venta {metodo_pago_venta}: {precio:.3f} USD ({tendencia}) por {comerciante} ({volumen} USDT)")

            if precio != ultimo_precio_venta and precio <= umbral_venta:
                mensaje = f"🔻 Alerta Venta PUBLICANDO - {metodo_pago_venta}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)

            ultimo_precio_venta = precio
        elif motivo_venta:
            enviar_telegram(f"{motivo_venta}\n🕒 {hora}")

        # --- Alerta: Venta DIRECTA con Banco Pichincha ---
        resultado_directa, motivo_directa = obtener_info_top(metodo_pago_venta, "BUY")
        if resultado_directa:
            precio, comerciante, volumen = resultado_directa
            tendencia = "📌 Primer dato" if ultimo_precio_venta is None else (
                "🔼 Subió" if precio > ultimo_precio_venta else
                "🔽 Bajó" if precio < ultimo_precio_venta else "⏸️ Sin cambio"
            )

            loggear(f"Venta DIRECTA {metodo_pago_venta}: {precio:.3f} USD ({tendencia}) por {comerciante} ({volumen} USDT)")

            if precio != ultimo_precio_venta and precio <= umbral_venta_directa:
                mensaje = f"⚡ Alerta Venta DIRECTA - {metodo_pago_venta}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)

        elif motivo_directa:
            enviar_telegram(f"📡 Venta DIRECTA - {motivo_directa}\n🕒 {hora}")

        # --- Alerta: Compra con Skrill ---
        resultado_compra, motivo_compra = obtener_info_top(metodo_pago_compra, "BUY")
        if resultado_compra:
            precio, comerciante, volumen = resultado_compra
            tendencia = "📌 Primer dato" if ultimo_precio_compra is None else (
                "🔼 Subió" if precio > ultimo_precio_compra else
                "🔽 Bajó" if precio < ultimo_precio_compra else "⏸️ Sin cambio"
            )

            loggear(f"Compra {metodo_pago_compra}: {precio:.3f} USD ({tendencia}) por {comerciante} ({volumen} USDT)")

            if precio != ultimo_precio_compra and precio >= umbral_compra_skrill:
                mensaje = f"🟢 Alerta Compra PUBLICANDO - {metodo_pago_compra}: {precio:.3f} USD\n{tendencia}\n👤 {comerciante}\n📦 {volumen} USDT\n🕒 {hora}"
                enviar_telegram(mensaje)

            ultimo_precio_compra = precio
        elif motivo_compra:
            enviar_telegram(f"{motivo_compra}\n🕒 {hora}")

        time.sleep(intervalo_espera)

if __name__ == "__main__":
    main()
