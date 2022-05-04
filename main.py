import asyncio
import random as r
import typing

import pandas as pd
from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardRemove)
from aiogram.utils import executor
from fuzzywuzzy import fuzz as f

# 1321420361,Глеб,-1,False

time_left = 0
TOKEN = '2135887109:AAFLxx5voHiy1M1LomP9cqhE2db_0rzgHTY'
tmp_id = 0
d_st = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=d_st)
is_game = False
all_players = []
f_place = "./DB/allusers.csv"
df = pd.read_csv(f_place)
play_count = 0


class dialog(StatesGroup):
    spam = State()
    start = State()
    delete = State()
    time_set = State()


greet_kb = ReplyKeyboardMarkup(resize_keyboard=True
                               ).add(KeyboardButton('Начать игру')).add(KeyboardButton('Зайти в игру'))
setup_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True,
                               input_field_placeholder='Количество охотников'
                               ).row(KeyboardButton('1'), KeyboardButton('2'), KeyboardButton('3'))
time_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(
    KeyboardButton('10'), KeyboardButton('15')).row(
    KeyboardButton('20'), KeyboardButton('25')).row(
    KeyboardButton('30'), KeyboardButton('35')).row(
    KeyboardButton('40'), KeyboardButton('45')).row(
    KeyboardButton('50'), KeyboardButton('55'))
game_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True
                              ).row(KeyboardButton('Словили'), KeyboardButton('Выйти')).add(
    KeyboardButton('Просмотр')).add(KeyboardButton('Время'))
admin_kb = ReplyKeyboardMarkup(resize_keyboard=True, input_field_placeholder='Время в минутах'
                               ).row(KeyboardButton('Словили'), KeyboardButton('Остановить')).add(
    KeyboardButton('Просмотр')).add(KeyboardButton('Время')).row(KeyboardButton('Рассылка'), KeyboardButton('Изменить'))
edit_kb = InlineKeyboardMarkup().row(InlineKeyboardButton('udalit', callback_data='3'), InlineKeyboardButton(
    'jivoi', callback_data='0')).row(InlineKeyboardButton('ohotnik', callback_data='1'), InlineKeyboardButton(
        'pomer', callback_data='2'))


@dp.callback_query_handler(lambda callback_query: True)
async def process_callback_st(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    count = 0
    while df.at[count, 'id'] != tmp_id:
        count += 1
    message = df.at[count, 'nick']
    mode = int(callback_query.data[-1])
    if mode == 3:
        message += " bil udalon"
        mode = -1
    elif mode == 0:
        message += " ojil"
    elif mode == 1:
        message += " ohotitsa"
    elif mode == 2:
        message += " ubili"
    df.at[count, 'hunt_st'] = mode
    df.to_csv(f_place, encoding='utf-8', index=False, header=True)
    await send_s(message)


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.answer("TODO tutorial")


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    if not isReg(message.chat.id):
        df.loc[df.shape[0]] = [message.from_user.id, message.from_user.full_name, -1, False]
        df.to_csv(f_place, encoding='utf-8', index=False, header=True)
        print('ababa')
        await message.answer("esli tupoi uzni komandu help.")
    await message.answer(message.from_user.username + ", привіт.", reply_markup=greet_kb)


@dp.message_handler(state=dialog.time_set)
async def start_game_time(message: types.Message, state: FSMContext):
    await send_s("pognali pad fonkы, kazakі", game_kb)
    await message.answer("pognali pad fonkы, kazakі", reply_markup=admin_kb)
    for i in range(len(df)):
        if df.at[i, 'hunt_st'] == 0:
            tmp += f"{df.at[i, 'nick']}  prosto chel\n"
        if df.at[i, 'hunt_st'] == 1:
            tmp += f"<b>{df.at[i, 'nick']}</b>  ohotnik\n"
        if df.at[i, 'hunt_st'] == 2:
            tmp += f"<s>{df.at[i, 'nick']}</s>  pomer\n"
    await send_s(tmp)
    await state.finish()
    print("tuda,suda")
    global time_left
    time_left = int(message.text) * 60
    while time_left:
        time_left -= 1
        await asyncio.sleep(1)

    global play_count
    play_count = 0
    tmp = ''
    for i in range(len(df)):
        if df.at[i, 'hunt_st'] == 0:
            tmp += f"{df.at[i, 'nick']}  prosto chel\n"
        if df.at[i, 'hunt_st'] == 1:
            tmp += f"<b>{df.at[i, 'nick']}</b>  ohotnik\n"
        if df.at[i, 'hunt_st'] == 2:
            tmp += f"<s>{df.at[i, 'nick']}</s>  pomer\n"
    await send_s(f" konets igri\n{tmp}", greet_kb)
    for i in range(len(df)):
        df.at[i, 'hunt_st'] = -1
        df.at[i, 'is_admin'] = False
    df.to_csv(f_place, encoding='utf-8', index=False, header=True)
    await state.finish()


@dp.message_handler(state=dialog.start)
async def start_game(message: types.Message, state: FSMContext):
    amount = int(message.text)
    print(play_count)
    if amount > play_count - 1 or amount <= 0:
        await message.answer("ti durnoi? ", reply_markup=greet_kb)
        count = 0
        while df.at[count, 'id'] != message.from_user.id:
            count += 1
        df.at[count, 'hunt_st'] = -1
        df.at[count, 'is_admin'] = False
        await state.finish()
    coutn, num = 0, 0
    while coutn != amount:
        num = r.randint(0, len(df) - 1)
        if df.at[num, 'hunt_st'] == 0:
            df.at[num, 'hunt_st'] = 1
            coutn += 1
    df.to_csv(f_place, encoding='utf-8', index=False, header=True)
    await message.answer("ukajite vrema v minutah:", reply_markup=time_kb)
    await state.set_state(dialog.time_set)


@dp.message_handler(state=dialog.delete)
async def process_delete(message: types.Message, state: FSMContext):
    await state.finish()
    count = 0
    global tmp_id
    while f.WRatio(df.at[count, 'nick'], message.text) < 85:
        if count > play_count:
            await message.answer("ti durnoi? ", reply_markup=admin_kb)
            await state.finish()
            return
        count += 1
    tmp_id = int(df.at[count, 'id'])
    await message.answer('chto izmenit u ' + df.at[count, 'nick'], reply_markup=edit_kb)


@dp.message_handler(state=dialog.spam, content_types=types.ContentType.ANY)
async def start_spam(message: types.Message, state: FSMContext):
    if message.text == 'назад':
        await message.answer('Otmena', reply_markup=admin_kb)
        await state.finish()
    else:
        for i in range(len(df)):
            if not df.at[i, 'is_admin']:
                await bot.forward_message(df.at[i, 'id'], message.from_user.id, message.message_id)
        await message.answer('Рассылка завершена')
        await state.finish()


@dp.message_handler(content_types=['text'], text='Время')
async def process_time_get_command(message: types.Message):
    a = str((time_left % 3600) // 60)
    b = str((time_left % 3600) % 60)
    c = f"{a} mins {b} seconds"
    await message.answer(c)


@dp.message_handler(content_types=['text'], text='Просмотр')
async def process_show_command(message: types.Message):
    tmp = ''
    for i in range(len(df)):
        if df.at[i, 'hunt_st'] == 0:
            tmp += f"{df.at[i, 'nick']}  prosto chel\n"
        if df.at[i, 'hunt_st'] == 1:
            tmp += f"<b>{df.at[i, 'nick']}</b>  ohotnik\n"
        if df.at[i, 'hunt_st'] == 2:
            tmp += f"<s>{df.at[i, 'nick']}</s>  pomer\n"
    await message.answer(tmp, parse_mode='HTML')


@dp.message_handler(content_types=['text'], text='Выйти')
async def process_log_out_command(message: types.Message):
    count = 0
    while df.at[count, 'id'] != message.from_user.id:
        count += 1
    df.at[count, 'hunt_st'] = -1
    df.to_csv(f_place, encoding='utf-8', index=False, header=True)
    await message.answer('Ti vishel',reply_markup=greet_kb)
    await send_s(str(df.at[count, 'nick']) + ' vishel')


@dp.message_handler(content_types=['text'], text='Начать игру')
async def process_game_command(message: types.Message):
    count = 0
    while df.at[count, 'id'] != message.from_user.id:
        count += 1
    df.at[count, 'hunt_st'] = 0
    df.at[count, 'is_admin'] = True

    df.to_csv(f_place, encoding='utf-8', index=False, header=True)
    if is_game:
        await message.answer("jdem nachala igri... ", )
    else:
        await dialog.start.set()
        await message.answer("vvedi kol-vo ohtnikov: ", reply_markup=setup_kb)


@dp.message_handler(content_types=['text'], text='Остановить')
async def process_stop_command(message: types.Message):
    global play_count
    play_count = 0
    tmp = ''
    for i in range(len(df)):
        if df.at[i, 'hunt_st'] == 0:
            tmp += f"{df.at[i, 'nick']}  prosto chel\n"
        if df.at[i, 'hunt_st'] == 1:
            tmp += f"<b>{df.at[i, 'nick']}</b>  ohotnik\n"
        if df.at[i, 'hunt_st'] == 2:
            tmp += f"<s>{df.at[i, 'nick']}</s>  pomer\n"
    await send_s(f" konets igri\n{tmp}", greet_kb)
    for i in range(len(df)):
        df.at[i, 'hunt_st'] = -1
        df.at[i, 'is_admin'] = False
    df.to_csv(f_place, encoding='utf-8', index=False, header=True)


@dp.message_handler(content_types=['text'], text='Изменить')
async def process_delete_command(message: types.Message):
    await dialog.delete.set()
    await message.answer("kogo izmenit: ")


@dp.message_handler(content_types=['text'], text='Словили')
async def process_catch_command(message: types.Message):
    count = 0
    while df.at[count, 'id'] != message.from_user.id:
        count += 1
    df.at[count, 'hunt_st'] = 2
    df.to_csv(f_place, encoding='utf-8', index=False, header=True)
    await send_s(df.at[count, 'nick'] + " ubili")


@dp.message_handler(commands=['get_csv'])
async def process_get_command(message: types.Message):
    await message.answer(df.to_string())


@dp.message_handler(commands=['get_adm'])
async def process_get_command(message: types.Message):
    await message.answer("admin", reply_markup=admin_kb)


@dp.message_handler(commands=['fetch_csv'])
async def process_fetch_command(message: types.Message):
    global df
    df = pd.read_csv(f_place)
    await message.answer("data fetched")


@dp.message_handler(commands=['start_gm'])
async def process_gamestrt_command(message: types.Message):
    await dialog.start.set()
    await message.answer("started")


@dp.message_handler(commands=['set_0'])
async def process_set_command(message: types.Message):
    for i in range(len(df)):
        df.at[i, 'hunt_st'] = -1
        df.at[i, 'is_admin'] = False
    df.to_csv(f_place, encoding='utf-8', index=False, header=True)
    await message.answer('dannie po nulam', reply_markup=greet_kb)


@dp.message_handler(content_types=['text'], text='Зайти в игру')
async def process_login_command(message: types.Message):
    count = 0
    global play_count
    play_count += 1
    while df.at[count, 'id'] != message.from_user.id:
        count += 1
    df.at[count, 'hunt_st'] = 0
    df.to_csv(f_place, encoding='utf-8', index=False, header=True)

    await message.answer("jdem nachala igri... ")


@dp.message_handler(content_types=['text'], text='Рассылка')
async def spam(message: types.Message):
    await dialog.spam.set()
    await message.answer('Напиши текст рассылки(назад, если не хочешь)')


async def send_s(text: str, reply_markup: typing.Union[types.InlineKeyboardMarkup,
                                                       types.ReplyKeyboardMarkup,
                                                       types.ReplyKeyboardRemove,
                                                       types.ForceReply, None] = None
                 ):
    for i in range(len(df)):
        await bot.send_message(df.at[i, 'id'], text, reply_markup=reply_markup, parse_mode='HTML')


def isReg(idd: int) -> bool:
    isreg = False
    for i in range(len(df)):
        if int(df.at[i, 'id']) == idd:
            isreg = 1
    return isreg


if __name__ == '__main__':
    print(df)
    executor.start_polling(dp, skip_updates=True)
