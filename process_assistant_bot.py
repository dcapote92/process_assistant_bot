import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode


# 1. Configuração

# Substitua 'SEU_TOKEN_AQUI' pelo seu token real do BotFather
TOKEN = '7992622235:AAGYKClKWziOIBFI_QkUBaXKT-HLTn_4LNw' 

# Configuração de logging para ver o que o bot está fazendo
logging.basicConfig(level=logging.INFO)

# Inicializa o bot e o dispatcher
# ParseMode.HTML é opcional, permite usar formatação HTML nas mensagens
bot = Bot(token=TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


# 2. Handlers de Mensagem

# Handler para o comando /start e /help
@dp.message(commands=["start", "help"])
async def send_welcome(message: types.Message):
    """
    Este handler será chamado quando o usuário enviar os comandos /start ou /help
    """
    await message.reply(
        "Olá! Eu sou o Bot Eco, alimentado por aiogram. \\n"
        "Envie-me qualquer mensagem e eu a responderei!"
    )


# Handler que responde a *todas* as outras mensagens de texto
@dp.message()
async def echo_handler(message: types.Message):
    """
    Este handler simplesmente responde à mensagem do usuário com o mesmo texto.
    O método 'reply' envia a mensagem como uma resposta direta (citando a mensagem original).
    """
    try:
        # Pega o texto da mensagem original e envia de volta
        await message.reply(f"Você disse: <b>{message.text}</b>")
    except TypeError:
        # Trata casos onde a mensagem pode não ser de texto (ex: sticker, foto)
        # e o atributo 'text' não existe.
        await message.reply("Desculpe, só posso fazer 'echo' de mensagens de texto por enquanto.")


# 3. Execução Principal

async def main():
    # Inicia o bot e o dispatcher para receber atualizações
    # 'skip_updates=True' garante que o bot ignore todas as mensagens que chegaram
    # enquanto ele estava offline.
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    # Roda a função 'main' de forma assíncrona
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Permite parar o bot com Ctrl+C no terminal
        print("Bot Desligado")