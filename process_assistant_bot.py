import asyncio
from textwrap import dedent
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
app = Client( SESSION_NAME, api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, parse_mode=ParseMode.MARKDOWN )


# =========================================================
# HANDLERS
# =========================================================

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
 
    user_name = message.from_user.first_name if message.from_user else "usuário"
    initial_markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton('Abertura'), KeyboardButton('Fechamento')],
        ],
        resize_keyboard=True
    )

    await message.reply_text(
        f"Olá, **{user_name}** Bem-vindo! \nEsse bot o ajudará nos processos de abertura e fechamento de loja.",
        reply_markup = initial_markup
    )


# Opening buttons
branch_rows  = [ [KeyboardButton(branch) for branch in branchs[i:i+2]] for i in range(0, len(branchs), 2) ]
opening_buttons = ReplyKeyboardMarkup(branch_rows, resize_keyboard=True)

@app.on_message(filters.text & ~filters.command("start"))
async def keyboard_answer(client: Client, message: Message):
    
    if message.text == 'Abertura':
        answer = dedent('''
        BOM DIA ☀️!
        VOCÊ SELECIONOU ABERTURA.
        VAMOS COMEÇAR O PROCEDIMENTO DE ABERTURA.
        SELECIONE SUA FILIAL PARA INICIAR O PROCESSO ABERTURA DE LOJA.
        ''')

        await message.reply_text(
            answer,
            reply_markup = opening_buttons
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
