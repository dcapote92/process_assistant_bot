import asyncio
from pyrogram import Client, filters, idle
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from pyrogram.enums import ParseMode
from branch import branchs
import utils


# Need to create an app on my.telegram.org in order to receive API_ID and API_HASH 
API_ID = 29867141 
API_HASH = 'd5956629151b2ffc1d26a640d99825ef'

# Get your token on both father
BOT_TOKEN = '7992622235:AAGYKClKWziOIBFI_QkUBaXKT-HLTn_4LNw'

# this is justo set a session name ( can be anything)
SESSION_NAME = "process_bot_session" 


# =========================================================
# Get pyrogram client started
# =========================================================
app = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)


# =========================================================
# HANDLERS
# =========================================================

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """
    Responde ao comando /start.
    O modo de análise é definido globalmente para MARKDOWN.
    """
    user_name = message.from_user.first_name if message.from_user else "usuário"
    
    await message.reply_text(
        f"Olá, **{user_name}**! Seu bot Pyrogram está funcionando usando modo MARKDOWN.",
    )

@app.on_message(filters.text & ~filters.command("start"))
async def echo_message(client: Client, message: Message):
    """
    Responde a qualquer texto que não seja um comando.
    O modo de análise é definido globalmente para HTML.
    """
    opcao_a = KeyboardButton("Opção A")
    opcao_b = KeyboardButton("/status") # Pode ser um comando
    
    # 2. Montagem do teclado
    reply_keyboard = ReplyKeyboardMarkup(
        [
            # Linha 1
            [opcao_a, opcao_b], 
            # Linha 2
            [KeyboardButton("Fechar Teclado")]
        ],
        resize_keyboard=True,   # Reduz o tamanho do teclado
        one_time_keyboard=False # Mantém o teclado ativo
    )

    await message.reply_text(
        "<b>Botões de Resposta:</b> Use os botões abaixo para enviar texto rápido.",
        reply_markup=reply_keyboard
    )

    await message.reply_text(
        f"Você disse: __{message.text}__",
    )


# =========================================================
# EXECUÇÃO PRINCIPAL
# =========================================================

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    async def main_pyrogram():
        print("Bot sendo inicializado...")
        await app.start()
        print("Bot rodando. Pressione Ctrl+C para parar.")
        await idle()
        await app.stop()
        print("Bot parou.")

    try:
        loop.run_until_complete(main_pyrogram())
    except KeyboardInterrupt:
        print("\nBot interrompido pelo usuário.")
    except Exception as e:
        print(f"Ocorreu um erro fatal: {e}")
