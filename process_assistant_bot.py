import asyncio
import re
from os import getenv
from textwrap import dedent
from pyrogram import Client, filters, idle
from pyrogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputMediaPhoto, ReplyKeyboardRemove
from pyrogram.enums import ParseMode
from branch import branchs



# Need to create an app on my.telegram.org in order to receive API_ID and API_HASH 
API_ID = getenv('API_ID') 
API_HASH = getenv('API_HASH')

# Get your token on both father
PA_TOKEN = ('PA_TOKEN') # process_assistant

# this is justo set a session name ( can be anything)
SESSION_NAME = "process_bot_session" 


BRANCH_ROWS  = [ [KeyboardButton(branch) for branch in branchs[i:i+2]] for i in range(0, len(branchs), 2) ]
ESCAPED_BRANCH = [re.escape(b) for b in branchs]
REGEX_PATTERN = '^(' + '|'.join(ESCAPED_BRANCH) + ')$'
USER_DATA = {}
TARGET_GROUP_IDS = [
   -1001933126601, # Suporte T.I Regional Ceará
   # -1002669184395, # Suporte T.I - Lojas
]


# =========================================================
# Get pyrogram client started
# =========================================================
app = Client( SESSION_NAME, api_id=API_ID, api_hash=API_HASH, bot_token=PA_TOKEN, parse_mode=ParseMode.MARKDOWN )


# =========================================================
# HANDLERS
# =========================================================
@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    """Catchs /start command to set bot to run and shows a
    process selection buttons.

    Args:
        client (Client): Pyrogram Client
        message (Message): Message
    """
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

@app.on_message(filters.command(['stop','cancel']) & filters.text)
async def stop_command(client: Client, message: Message):
    """Catchs /stop or /cancel command to stop bot and remove the custom keyboard"""
    user_id = message.from_user.id
    
    # Clean user data if exist
    if user_id in USER_DATA:
        del USER_DATA[user_id]

    await message.reply_text(
        '🛑 **- Processo cancelado.**\n- Teclado ocultado',
        reply_markup=ReplyKeyboardRemove()
    )

@app.on_message(filters.text & filters.regex('Abertura 🌕'))
async def on_opening(client, message):
    """Catchs text message to set bot process as opening and shows 
    a branch selection buttons.

    Args:
        client (Client): Pyrogram Client
        message (Message): Message
    """
    user_id = message.from_user.id
    USER_DATA[user_id] = {'process': 'opening', 'branch': None, 'photos': [], 'consistency': True}
    opening_buttons = ReplyKeyboardMarkup(BRANCH_ROWS, resize_keyboard=True)
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
    opening_buttons = ReplyKeyboardMarkup(BRANCH_ROWS, resize_keyboard=True)
    answer = dedent('''
    Boa Noite 🌑!
    Você selecionou Fechamento.
    Vamos começar o processo, por favor, selecione sua filial:'''
    )
    await message.reply_text(
        answer,
        reply_markup = opening_buttons
    )

@app.on_message(filters.text & filters.regex(REGEX_PATTERN)) # branch selection
async def on_branch_selection(client, message):
    user_id = message.from_user.id

    if user_id not in USER_DATA or not USER_DATA[user_id].get('process'):
        return await message.reply_text("🛑 Por favor, comece selecionando 'Abertura 🌕' ou 'Fechamento 🌑'.")

    user_data = USER_DATA[user_id]
    user_data['branch'] = message.text

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

    media_group = None

    if loaded_photos:
        
        media_group = [
            InputMediaPhoto(media=file_id, caption=final_answer) if i == 0
            else InputMediaPhoto(media=file_id)
            for i, file_id in enumerate(loaded_photos)
        ]

    for target_id in TARGET_GROUP_IDS:
        try:
            if media_group:
                await client.send_media_group(
                    chat_id = target_id,
                    media = media_group
                )
            else:
                await client.send_message(
                    chat_id = target_id,
                    text = final_answer
                )
        except Exception as e:
            print(f'Erro ao enviar relatorio de processo para o chat {target_id}: {e}')

        
    await message.reply_text(
        '✅ Processo concluído e registrado nos canais de monitoramento. Selecione um novo processo para começar:',
        reply_markup= initial_markup
    )

    if media_group:
        await client.send_media_group(
            chat_id=message.chat.id,
            media=media_group
        )
        await message.reply_text(
            '✅ Processo concluído e registrado nos canais de monitoramento. Selecione um novo processo para começar:',
            reply_markup=initial_markup
        )
    else:
        await message.reply_text(
            final_answer + '\n\n✅ Processo concluído e registrado nos canais de monitoramento. Selecione um novo processo para começar:',
            reply_markup=initial_markup
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
