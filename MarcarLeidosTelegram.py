from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import ReadHistoryRequest
from telethon.tl.types import User, Chat, Channel

# --- Configuración personal ---
api_id = 24351399  # Reemplaza sin comillas, ejemplo: 123456
api_hash = '91cf8453d5e8a19b11b2784a74f5fba0'  # Entre comillas
phone = '+593990137896'  # Número en formato internacional

# --- Crear cliente y conectarse ---
client = TelegramClient('mark_as_read_session', api_id, api_hash)
client.connect()

if not client.is_user_authorized():
    client.send_code_request(phone)
    code = input('📲 Ingresa el código de verificación recibido en Telegram: ')
    try:
        client.sign_in(phone, code)
    except SessionPasswordNeededError:
        password = input('🔐 Ingresa tu contraseña de Telegram (2FA): ')
        client.sign_in(password=password)

# --- Marcar como leídos solo chats válidos ---
dialogs = client.get_dialogs()

for dialog in dialogs:
    entidad = dialog.entity
    if dialog.unread_count > 0:
        if isinstance(entidad, (User, Chat)):  # Excluye Channel (canales tipo difusión)
            try:
                print(f"✅ Marcando como leídos: {dialog.name}")
                client(ReadHistoryRequest(peer=entidad, max_id=0))
            except Exception as e:
                print(f"⚠️ No se pudo marcar como leído: {dialog.name} → {e}")

print("🎉 Todos los mensajes válidos han sido marcados como leídos.")
client.disconnect()
