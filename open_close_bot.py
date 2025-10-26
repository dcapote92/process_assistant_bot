'''
@SystemAberturaCE_bot by: Emanuel Douglas
optimized_by: dcapote92
'''
from textwrap import dedent
from telebot import TeleBot as tbot
from random import randint
from telebot import types
from branch import branchs
import utils

token = '7992622235:AAGYKClKWziOIBFI_QkUBaXKT-HLTn_4LNw'
bot = tbot(token)

album_photos= {}
user_states = {}


# Choose Opening or Closing process
initials_buttons = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
opening_key = types.KeyboardButton('☀️ABERTURA')
closing_key = types.KeyboardButton('🌚FECHAMENTO')
initials_buttons.add(opening_key, closing_key)


# Opening buttons
opening_buttons = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
for branch in branchs:
    btn = types.KeyboardButton(branch)
    opening_buttons.add(btn)

# Closing buttons
closing_buttons = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
for branch in branchs:
    btn = types.KeyboardButton(branch)
    closing_buttons.add(btn)


# Opening conclusion buttons
conclusion_text=[]
opening_conclusion_keyboards={}
for branch in branchs:
    btn_text = f'Concluir Abertura {branch} ✅'
    conclusion_text.append(btn_text)
    btn = types.KeyboardButton(btn_text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btn)
    opening_conclusion_keyboards[branch] = keyboard 


# Fail and consistency buttons
consistency_text=[]
fail_and_consistency_keyboards={}
for branch in branchs:
    btn_consist_ok_text = f'Consistencia {branch} ✅'
    btn_consist_ok = types.KeyboardButton(btn_consist_ok_text)
    btn_consist_fail_text = f'Falha Consistencia {branch} ❌'
    consistency_pair = btn_consist_ok_text, btn_consist_fail_text
    consistency_text.append(consistency_pair)
    btn_consist_fail = types.KeyboardButton(btn_consist_fail_text)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btn_consist_ok, btn_consist_fail)
    fail_and_consistency_keyboards[branch] = keyboard


@bot.message_handler(commands=['iniciar','start'])
def welcome(message):
    user_name = message.from_user.first_name
    answer = f'OLÁ, {user_name}!\nBEM_VINDO AO ASSITENTE DE ABERTURA E FECHAMENTO DA REGIONAL CEARÁ!'
    bot.send_message(message.chat.id,
                     answer,
                     reply_markup=initials_buttons)


@bot.message_handler(func=lambda message: True, content_types=['text'])
def keyboard_answer(message):

    if message.text == '☀️ABERTURA':
        answer = dedent('''
        BOM DIA ☀️!
        VOCÊ SELECIONOU ABERTURA.
        VAMOS COMEÇAR PROCEDIMENTO DE ABERTURA.
        SELECIONE SUA FILIAL PARA INICIAR O PROCESSO ABERTURA DE LOJA
        ''')
        bot.send_message(message.chat.id, answer, reply_markup= opening_buttons)        
        bot.register_next_step_handler(message, lambda msg: process_branch_selection(msg, '☀️ABERTURA' ))


    elif message.text == '🌚FECHAMENTO':
        answer = dedent('''
        ÓTIMA NOITE 🌚!
        VOCÊ SELECIONOU FECHAMENTO.
        VAMOS COMEÇAR PROCEDIMENTO DE FECHAMENTO DA LOJA.
        SELECIONE SUA FILIAL PARA INICIAR O PROCESSO DE FECHAMENTO DA LOJA.
        ''')
        bot.send_message(message.chat.id, answer, reply_markup= closing_buttons)
        bot.register_next_step_handler(message, lambda msg:process_branch_selection(msg, '🌚FECHAMENTO'))

    elif message.text in [text[0] for text in consistency_text]:
        user_name = message.from_user.first_name
        answer = dedent(f'''
        PROCESSO DE FECHAMENTO FINALIZADO COM SUCESSO.
        ◾CONSISTÊNCIA ✅
        ◾ALTERAÇÃO ✅
        ◾PAINEL TERMINAL ✅
        ◾{utils.find_branch(message.text)}
        ◾👨‍💻T.I: {user_name}!
        BOM DESCANSO
        ''')
        bot.send_message(message.chat.id, answer, reply_markup=initials_buttons)
        
    
    elif message.text in [text[1] for text in consistency_text]:
        user_name = message.from_user.first_name
        answer = dedent(f'''
        PROCESSO DE FECHAMENTO FINALIZADO COM SUCESSO.
        ◾CONSISTÊNCIA ❌
        ◾ALTERAÇÃO ✅
        ◾PAINEL TERMINAL ✅
        ◾{utils.find_branch(message.text)}
        ◾👨‍💻T.I: {user_name}!
        BOM DESCANSO!
        ''')
        bot.send_message(message.chat.id, answer, reply_markup=initials_buttons)


    else:
        bot.reply_to(message, 'COMANDO NÃO RECONHECIDO. USE /start PARA RECOMEÇAR.')

@bot.message_handler(content_types=['photo'])
def process_opening_conclusion(message):
    """
    Novo handler para processar fotos e álbuns de fotos, garantindo que
    todas as fotos de um álbum sejam coletadas e enviadas sem repetição.
    """
    media_group_id = message.media_group_id
    user_id = message.from_user.id
    caption_text = message.caption if message.caption else ""
    
    # 1. Recuperar a filial do estado
    selected_branch = user_states.get(user_id)
    if not selected_branch:
        bot.reply_to(message, '⚠️ ERRO: Por favor, inicie o processo de ABERTURA primeiro usando /start e selecionando a filial.')
        return

    expected_text = f'Concluir Abertura {selected_branch} ✅'

    # 2. Lógica para ÁLBUM de Fotos
    if media_group_id:
        if media_group_id not in album_photos:
            album_photos[media_group_id] = []
        
        # Adiciona a mensagem atual à lista do álbum (usando o file_id da maior resolução)
        album_photos[media_group_id].append(message) 

        # Se for o comando de conclusão, processamos o álbum completo
        if caption_text.strip() == expected_text.strip():
            
            # Constrói o grupo de mídia
            media_group = []
            conclusion_answer = dedent(f'''
            PROCESSO DE ABERTURA FINALIZADO COM SUCESSO.
            ABERTURA ✅
            FILIAL: {selected_branch}
            👨‍💻TI: {message.from_user.first_name}!
            ÓTIMO DIA E BOM TRABALHO!
            ''')
            
            # Pega as fotos armazenadas para este grupo de mídia
            photos_in_album = album_photos.pop(media_group_id, [])
            
            if not photos_in_album:
                 bot.reply_to(message, '⚠️ ERRO: Não foi possível processar o álbum de fotos. Tente novamente.')
                 return
            
            # Prepara a mídia para envio
            for i, msg in enumerate(photos_in_album):
                photo_file_id = msg.photo[-1].file_id # Pega a maior resolução
                
                # A legenda só pode ir na primeira foto do álbum.
                caption = conclusion_answer if i == 0 else None
                media_group.append(types.InputMediaPhoto(photo_file_id, caption=caption))
            
            # Remove o estado do usuário
            user_states.pop(user_id, None) 
            
            # 🛑 Envia o álbum de volta para o usuário
            try:
                bot.send_media_group(message.chat.id, media_group)
            except Exception as e:
                print(f'Error on send media group to user: {e}')
                bot.send_message(message.chat.id, "Ocorreu um erro ao enviar o álbum. As fotos foram registradas, mas tente novamente se necessário.")

            # 🛑 Envia o teclado inicial (resolve a questão do reply_markup)
            bot.send_message(message.chat.id, 'Processo concluído. Novo ciclo iniciado.', reply_markup=initials_buttons)
            
            # Lógica para enviar para o grupo de report (MANTENHA ESTE TRECHO SE VOCÊ O USA)
            report_on_chat_id = []
            if report_on_chat_id:
                for chat_id in report_on_chat_id:
                    bot.send_media_group(chat_id, media_group)
                    
            return

        # Se for uma foto do álbum sem o comando de conclusão, apenas armazena e espera.
        else:
            return 
    
    # 3. Lógica para FOTO ÚNICA (Se o usuário enviar apenas uma foto)
    elif caption_text.strip() == expected_text.strip():
        
        conclusion_answer = dedent(f'''
        PROCESSO DE ABERTURA FINALIZADO COM SUCESSO.
        ABERTURA ✅
        FILIAL: {selected_branch}
        👨‍💻TI: {message.from_user.first_name}!
        ÓTIMO DIA E BOM TRABALHO!
        ''')
        
        # Cria um media_group de tamanho 1 para a foto única (opcional, mas mantém a consistência)
        media_group_single = [
            types.InputMediaPhoto(message.photo[-1].file_id, caption=conclusion_answer)
        ]
        
        # Envia a foto (agora via send_media_group)
        bot.send_media_group(message.chat.id, media_group_single)
        
        # Envia o teclado inicial
        bot.send_message(message.chat.id, 'Processo concluído.', reply_markup=initials_buttons)

        # Remove o estado do usuário
        user_states.pop(user_id, None)
        return

    # 4. Outras fotos/erros de legenda
    else:
        # Se for uma foto aleatória ou sem o comando de conclusão esperado.
        error_message = dedent(f"""
        ⚠️ FOTO RECEBIDA.
        Para concluir a abertura de {selected_branch}, você deve **ANEXAR TODOS OS PRINTS**
        e enviar **JUNTO** com o texto de confirmação:
        "{expected_text}"
        """)
        bot.reply_to(message, error_message, reply_markup=opening_conclusion_keyboards.get(selected_branch))

def process_branch_selection(message, process_type):
    selected_branch = message.text
    if selected_branch not in branchs:
        bot.reply_to(message, 'POR FAVOR, SELECIONE UMA FILIAL USANDO *APENAS* OS BOTÕES. INICIE NOVAMENTE COM /start.')
        
        if process_type == '☀️ABERTURA':
            bot.register_next_step_handler(message, lambda msg: process_branch_selection(msg,'☀️ABERTURA'))
        
        elif process_type == '🌚FECHAMENTO':
            bot.register_next_step_handler(message, lambda msg: process_branch_selection(msg, '🌚FECHAMENTO'))

        return
    
    user_states[message.from_user.id] = selected_branch
    
    if process_type == '☀️ABERTURA':
        answer = f'''
⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
{selected_branch}
POR FAVOR ANEXAR TODOS OS PRINTS DA ABERTURA
APÓS ANEXAR AS IMAGENS, ENVIE-AS JUNTO A MENSAGEM DE CONFIRMAÇÃO:
"CONCLUIR ABERTURA {selected_branch} ✅"
⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
        '''
        bot.send_message(message.chat.id, answer, reply_markup=opening_conclusion_keyboards.get(selected_branch))
        return
    
    elif process_type == '🌚FECHAMENTO':
        answer = f'''
LOJA {selected_branch} SELECIONADA ✅ 
⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
FAÇA O ANEXO DOS SEGUINTES PRINTS: PAINEL TERMINAL, ALTERAÇÃO GMCORE, CARGA DAS BALANÇAS E CONSISTÊNCIA.
EM CASOS DE HAVER ALGUM PDV COM ERRO NA CONSISTÊNCIA CLIQUE EM  ERRO CONSISTÊNCIA ❌
OU SE TODOS OBTERAM SUCESSO CLIQUE EM CONSISTÊNCIA OK ✅
⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️⚠️
        '''
        reply_markup = fail_and_consistency_keyboards.get(selected_branch)
    
    else:
        return bot.reply_to(message='ERRO: TIPO DE PROCESSO DESCONHECIDO. USE /start PARA RECOMEÇAR.')
    
    bot.send_message(message.chat.id, answer, reply_markup=reply_markup)



bot.infinity_polling()

