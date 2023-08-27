from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

menu = InlineKeyboardMarkup(row_width=3,
                            inline_keyboard=[
                                [
                                    InlineKeyboardButton(text='Техника', callback_data='podbor'),
                                    InlineKeyboardButton(text='Сервис', callback_data='service')
                                ]
                               
                            ])


