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
    user_id = message.from_user.id
    USER_DATA[user_id] = {'process': 'opening', 'branch': None, 'photos': [], 'consistency': True}
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

@app.on_message(filters.text & filters.regex('Fechamento 🌑'))
async def on_closing(client, message):
    user_id = message.from_user.id
    USER_DATA[user_id] = {'process': 'closing', 'branch': None, 'photos': [], 'consistency': True}
    opening_buttons = ReplyKeyboardMarkup(branch_rows, resize_keyboard=True)
    answer = dedent('''
    Boa Noite 🌑!
    Você selecionou Fechamento.
    Vamos começar o processo, por favor, selecione sua filial:'''
    )
    await message.reply_text(
        answer,
        reply_markup = opening_buttons
    )

@app.on_message(filters.text & filters.regex(regex_pattern)) # branch selection
async def on_branch_selection(client, message):
    user_id = message.from_user.id
    USER_DATA[user_id]['branch'] =  message.text
    answer = dedent(f'''
    {USER_DATA[user_id]['branch']}
    Por favor, anexe todos os prints disponíveis
    ⚠️ Uma vez anexados os prints, pode concluir o processo.'''
    ) if USER_DATA[user_id]['process'] == 'opening' else dedent(f'''
    {USER_DATA[user_id]['branch']}
    Por favor, anexe todos os prints disponíveis
    e selecione o **status** da Consistência.'''
    )

    await message.reply_text(
        answer,
        reply_markup = ReplyKeyboardMarkup([
            [KeyboardButton('Concluir Processo '+ USER_DATA[user_id]['branch'])]
        ],
        resize_keyboard=True
        ) if USER_DATA[user_id]['process'] == 'opening' else  ReplyKeyboardMarkup([
            [KeyboardButton('Consistência ✅')],
            [KeyboardButton('Consistência ❌')]
        ],
        resize_keyboard=True
        )
    )

@app.on_message(filters.text & filters.regex('Consistência ❌'))
async def on_consistency_fail(client, message):
    user_id = message.from_user.id
    answer = 'Agora pode concluir o processo'
    USER_DATA[user_id]['consistency'] = False
    await message.reply_text(
        answer ,
         reply_markup = ReplyKeyboardMarkup([
            [KeyboardButton('Concluir Processo '+ USER_DATA[user_id]['branch'])]
        ]
        )
    )  

@app.on_message(filters.text & filters.regex('Consistência ✅'))
async def on_consistency(client, message):
    user_id = message.from_user.id
    answer = 'Agora pode concluir o processo'
    await message.reply_text(
        answer ,
         reply_markup = ReplyKeyboardMarkup([
            [KeyboardButton('Concluir Processo '+ USER_DATA[user_id]['branch'])]
        ]
        )
    )  

@app.on_message(filters.photo & filters.private) # waiting for photos
async def on_photo_received(client, message):
    user_id = message.from_user.id
    if user_id in USER_DATA and 'photos' in USER_DATA[user_id]:
        USER_DATA[user_id]['photos'].append(message.photo.file_id)
        await message.reply_text('✅ Foto recebida. Envie mais ou conclua o processo.')
    else:
        await message.reply_text('🛑 Fotos não são permitidas neste estagio! 🛑')

@app.on_message(filters.text & filters.regex('^Concluir Processo'))
async def on_opening_finalization(client, message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name if message.from_user else "usuário"
    answer = ''
    match = re.search(r'Concluir Processo (.*)', message.text)
    branch = match.group(1).strip() if match else 'Filial Desconhecida'
    loaded_photos = USER_DATA.get(user_id, {}).get('photos', [])

    initial_markup =  ReplyKeyboardMarkup(
                [
                    [KeyboardButton('Abertura 🌕'), KeyboardButton('Fechamento 🌑')],
                ],
                resize_keyboard=True
            )
    
    if USER_DATA[user_id]['process'] == 'opening':        
        answer = dedent(f'''
        PROCESSO DE ABERTURA FINALIZADO COM SUCESSO.
        ◾ABERTURA ✅ 
        ◾{USER_DATA[user_id]['branch']}
        ◾👨‍💻T.I: {user_name}!
        ÓTIMO DIA, E BOM TRABALHO!'''
        )

    elif USER_DATA[user_id]['process'] == 'closing':
        if USER_DATA[user_id]['consistency']: 
            answer = dedent(f'''
            PROCESSO DE FECHAMENTO FINALIZADO COM SUCESSO.
            ◾CONSISTÊNCIA ✅
            ◾ALTERAÇÃO ✅
            ◾PAINEL TERMINAL ✅
            ◾{USER_DATA[user_id]['branch']}
            ◾👨‍💻T.I: {user_name}!
            BOM DESCANSO'''
            )
        else:    
            answer = dedent(f'''
            PROCESSO DE FECHAMENTO FINALIZADO COM SUCESSO.
            ◾CONSISTÊNCIA ❌
            ◾ALTERAÇÃO ✅
            ◾PAINEL TERMINAL ✅
            ◾{USER_DATA[user_id]['branch']}
            ◾👨‍💻T.I: {user_name}!
            BOM DESCANSO!'''
            )
    final_answer = answer if answer else 'Proceso finalizado.'

    if loaded_photos:
        media_group = [
            InputMediaPhoto(media=file_id, caption=final_answer) if i == 0
            else InputMediaPhoto(media=file_id)
            for i, file_id in enumerate(loaded_photos)
        ]

        await client.send_media_group(
            chat_id= message.chat.id,
            media= media_group
        )

        await message.reply_text(
            'Selecione um novo processo se desejar.',
            reply_markup= initial_markup
        )

    else:
        await message.reply_text(
            final_answer,
            reply_markup = initial_markup
        )

    # cleaning user data    
    if user_id in USER_DATA:
        del USER_DATA[user_id]



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
