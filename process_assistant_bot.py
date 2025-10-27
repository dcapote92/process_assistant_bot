import asyncio
import re
from textwrap import dedent
from pyrogram import Client, filters, idle
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto
from pyrogram.enums import ParseMode
from branch import branchs
from utils import find_branch, branch_rows


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

escaped_branchs = [re.escape(b) for b in branchs]
regex_pattern = '^(' + '|'.join(escaped_branchs) + ')$'
USER_DATA = {}


@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
 
    user_name = message.from_user.first_name if message.from_user else "usuário"
    initial_markup = ReplyKeyboardMarkup(
        [
            [KeyboardButton('Abertura 🌕'), KeyboardButton('Fechamento 🌑')],
        ],
        resize_keyboard=True
    )

    await message.reply_text(
        dedent(f'''
                Olá, **{user_name}** Bem-vindo!
                Esse bot o ajudará nos processos de **Abertura** e **Fechamento**.
                Para começar selecione o processo a realizar.'''
                ),
        reply_markup = initial_markup
    )

@app.on_message(filters.text & filters.regex('Abertura 🌕'))
async def on_opening(client, message):
    opening_buttons = ReplyKeyboardMarkup(branch_rows, resize_keyboard=True)
    answer = dedent('''
    Bom Dia ☀️!
    Você selecionou Abertura.
    Vamos começar o processo, por favor, selecione sua filial:'''
    )

    await message.reply_text(
        answer,
        reply_markup = opening_buttons
    )

@app.on_message(filters.text & filters.regex(regex_pattern)) # branch selection
async def on_branch_selection(client, message):
    branch = message.text
    user_id = message.from_user.id
    USER_DATA[user_id] = {'branch': branch, 'photos':[]}
    answer = dedent(f'''
    {branch}
    Por favor, anexe todos os prints disponíveis
    ⚠️ Uma vez anexados os prints, pode concluir o processo.'''
    )

    await message.reply_text(
        answer,
        reply_markup = ReplyKeyboardMarkup([
            [KeyboardButton('Concluir Abertura '+ branch)]
        ],
        resize_keyboard=True
        )
    )

@app.on_message(filters.photo & filters.private)
async def on_photo_received(client, message):
    user_id = message.from_user.id
    if user_id in USER_DATA and 'photos' in USER_DATA[user_id]:
        USER_DATA[user_id]['photos'].append(message.photo.file_id)
        await message.reply_text('✅ Foto recebida. Envie mais ou conclua o processo.')
    else:
        await message.reply_text('🛑 Fotos não são permitidas neste estagio! 🛑')

@app.on_message(filters.text & filters.regex('^Concluir Abertura'))
async def on_opening_finalization(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name if message.from_user else "usuário"
    match = re.search(r'Concluir Abertura (.*)', message.text)
    branch = match.group(1).strip() if match else 'Filial Desconhecida'

    loaded_photos = USER_DATA.get(user_id, {}).get('photos', [])

    initial_markup =  ReplyKeyboardMarkup(
                [
                    [KeyboardButton('Abertura 🌕'), KeyboardButton('Fechamento 🌑')],
                ],
                resize_keyboard=True
            )
    
    answer = dedent(f'''
    PROCESSO DE ABERTURA FINALIZADO COM SUCESSO.
    ◾ABERTURA ✅ 
    ◾{branch}
    ◾👨‍💻T.I: {user_name}!
    ÓTIMO DIA, E BOM TRABALHO!'''
    )

    if loaded_photos:
        media_group = [
            InputMediaPhoto(media=file_id, caption=answer) if i == 0
            else InputMediaPhoto(media=file_id)
            for i, file_id in enumerate(loaded_photos)
        ]

        await client.send_media_group(
            chat_id= message.chat.id,
            media= media_group
        )
    else:
        await message.reply_text(
            answer,
            reply_markup = initial_markup
        )

    # cleaning user data    
    if user_id in USER_DATA:
        del USER_DATA[user_id]


    # send initial keyboard 
    if loaded_photos:
        await message.reply_text(
            reply_markup= initial_markup
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
