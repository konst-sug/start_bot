import logging
import asyncio
import Config
import aiogram.utils.markdown as fmt

from aiogram.types.message import ContentType
from sqlighter import SQLighter
from aiogram import types
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.storage import FSMContext
from aiogram.utils import executor
from loader import dp, bot


logging.basicConfig(level=logging.INFO)

db = SQLighter('db.db')

admin = dict()

PRICE = types.LabeledPrice(label="Подписка на 1 месяц", amount=80*100)  # в копейках (руб)



inline_btn_1 = InlineKeyboardButton('Провести оплату!', callback_data='button1')
inline_btn_2 = InlineKeyboardButton('Отправить письмо ☎️', callback_data='button2')
inline_btn_3 = InlineKeyboardButton('Отправить', callback_data='button3')
menu = InlineKeyboardMarkup().add(inline_btn_1).add(inline_btn_2)
menu2 = InlineKeyboardMarkup().row(inline_btn_1,inline_btn_2)
send_menu  = types.ReplyKeyboardMarkup(resize_keyboard=True).add(inline_btn_3)




@dp.message_handler(CommandStart())
async def bot_start(message: types.Message, state: FSMContext):
    await message.answer('Главное меню')
    await state.set_state("admin")
    

# ----------------------старт\\\стоп---------------------------------

@dp.message_handler(commands='start', state='admin')
@dp.message_handler(commands='start', state='payload')
@dp.message_handler(commands='start', state='mail')
@dp.message_handler(commands='start', state='add_mail')
async def start_menu_repeat(message: types.Message,state='admin'):
   
	if(not db.user_exists(message.from_user.id)):
		# если юзера нет в базе, добавляем его
		db.add_user(message.from_user.id, message.from_user.username,True)
            
	else:
		# если он уже есть, то просто обновляем ему статус подписки
		db.update_user(message.from_user.id, True)
        
	await message.answer("Бот  уже запущен",reply_markup=menu2)
       
    
@dp.message_handler(commands="cancel", state='*')
async def back_to_admin_menu(message: types.Message, state: FSMContext):
    text = "Выход в начало/ Cancelled."
    logging.info('Cancelling state %r')
    await message.answer(text, reply_markup=types.ReplyKeyboardRemove())
    await state.reset_state()
    await bot_start(message, state)


#-----------------перевод на страницу оплаты-----------------------
@dp.callback_query_handler(Text(equals='button1'),state='admin')
async def sleep_call(call: types.CallbackQuery, state: FSMContext):
    #keyboard = await podbor_key()
    await call.message.edit_text('У вас есть деньги?')
    await call.message.delete()
    await state.set_state("payload")


@dp.message_handler(state="payload", content_types=["text"])
@dp.message_handler(commands=['buy'],state ='payload')
async def buy(message: types.Message):

    if Config.PAYMENTS_TOKEN.split(':')[1] == 'TEST':
        await bot.send_message(message.chat.id, "Тестовый платеж!!!")

    await bot.send_invoice(message.chat.id,
                           title="Проверка платежа",
                           description="Активация платежной системыЁ",
                           provider_token=Config.PAYMENTS_TOKEN,
                           currency="rub",
                           photo_url="https://www.aroged.com/wp-content/uploads/2022/06/Telegram-has-a-premium-subscription.jpg",
                           photo_width=416,
                           photo_height=234,
                           photo_size=416,
                           is_flexible=False,
                           prices=[PRICE],
                           start_parameter="one-month-subscription",
                           payload="test-invoice-payload")


# pre checkout  (must be answered in 10 seconds)
@dp.pre_checkout_query_handler(lambda query: True)
async def pre_checkout_query(pre_checkout_q: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


# successful payment
@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(message: types.Message):
    print("SUCCESSFUL PAYMENT:")
    payment_info = message.successful_payment.to_python()
    for k, v in payment_info.items():
        print(f"{k} = {v}")

    await bot.send_message(message.chat.id,
                           f"Платеж на сумму {message.successful_payment.total_amount // 100} {message.successful_payment.currency} прошел успешно!!!")

 
#------------------обработка отправки сообщения админам -------------------
@dp.callback_query_handler(Text(equals='button2'),state='admin')
async def sleep_call(call: types.CallbackQuery, state: FSMContext):
    #keyboard = await podbor_key()
    await call.message.edit_text('Отправка сообщения админам')
    await call.message.answer('Введите сообщение')
    await state.update_data(admin=call.message.text)
    await state.set_state("mail")    


@dp.message_handler(state="mail", content_types=["text"])
async def mail_to_admins(message:types.Message, state: FSMContext):
    await message.answer('Сообщение записано, Отправить?')
   
    await state.update_data(mail=message.text)
    await message.answer(
        fmt.text(
            fmt.text(fmt.hunderline("Уведомление")),
            fmt.text(fmt.hbold("Прожать button для отправки")),
            fmt.text(fmt.hbold("cancel для выхода")),
            sep="\n" ),reply_markup=send_menu)
    await state.set_state("mailadmins")    
    data = await state.get_data()


@dp.message_handler(state="mailadmins", regexp="Отправить")
async def send_admins(message:types.Message, state: FSMContext):
     data = await state.get_data()
     admin = db.get_admins()
     offers = [x[0] for x in admin]
     if offers is None:
        db.close()
        await message.answer("Список админов пуст!")

     else:     
        try: 
            for i in offers:
                await bot.send_message(chat_id=i,text=f"{data['mail']}",disable_notification=True)
                await asyncio.sleep(2)
                print('sucsess!')
        except Exception as error:
            print('Failed to send message')        
            db.close()
     await message.answer("Рассылка завершена", reply_markup=types.ReplyKeyboardRemove())
     await state.reset_state()
     await bot_start(message, state)






def main():      
    executor.start_polling(dp, skip_updates=False)


if __name__ == '__main__':
        main()    