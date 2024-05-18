import asyncio
import logging
import random
import sys
from aiogram import Bot, Router, types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.input_file import FSInputFile
from aiogram.filters.command import Command, CommandStart
from aiogram.filters.state import State

from sightreader.sight_reader import SightReader

sights = SightReader.read_from_directory("res")
if len(sights) == 0:
    print("Не смог считать ни одной достопримечатлеьности! Завершаю работу...")
    exit(1)
router = Router()


class ClientState(StatesGroup):
    """Хранит на каком этапе диалога находится клиент"""

    GENERATE = State()
    GUESSING = State()


token = "7091921555:AAG7tiMimRz0BjVa-RRXH1DFFQhqQUBp-9c"


@router.message(CommandStart())
async def start_proccess(message: types.Message, state: FSMContext) -> None:
    msg = (
        "Привет! Я бот который поможет тебе выучить достопримечательности Италии. "
        "Когда ты нажмешь кнопку 'Загадать' я пришлю тебе картинку, название и место. "
        "Твоя задача правильно определить существует ли такая достопримечательность в таком месте с таким названием. "
        "Ну что, поехали?"
    )

    markup = ReplyKeyboardMarkup(
        resize_keyboard=True, keyboard=[[KeyboardButton(text="Загадать")]]
    )

    await message.answer(msg, reply_markup=markup)
    await state.set_state(ClientState.GENERATE)


@router.message(ClientState.GENERATE)
async def generate_triple_sh(message: types.Message, state: FSMContext):
    user_msg = message.text
    if user_msg.lower() != "загадать":
        await message.answer("Введите 'Загадать'")
        return
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        keyboard=[
            [
                KeyboardButton(text="Да, всё верно"),
                KeyboardButton(text="Нет, комбинация неверная"),
            ]
        ],
    )
    is_valid = random.choice((True, False))
    if is_valid:
        index = random.randint(0, len(sights) - 1)
        logging.info("Generating valid combination with index %s", index)
        sight = sights[index]
        caption = f"Название: {sight.name}\n" f"Место: {sight.place}\n\n" "Всё верно?"
        await message.answer_photo(FSInputFile(sight.image), caption=caption, reply_markup=markup)
        await state.update_data({"is_valid": True, "sight_index": index})
        await state.set_state(ClientState.GUESSING)
    else:
        image_sight_index = random.randint(0, len(sights) - 1)
        name_sight_index = random.randint(0, len(sights) - 1)
        place_sight_index = random.randint(0, len(sights) - 1)
        logging.info("Generated indexes %s %s %s", image_sight_index, name_sight_index, place_sight_index)
        while image_sight_index == name_sight_index == place_sight_index:
            image_sight_index = random.randint(0, len(sights) - 1)
            name_sight_index = random.randint(0, len(sights) - 1)
            place_sight_index = random.randint(0, len(sights) - 1)
        sight = sights[image_sight_index]
        caption = (
            f"Название: {sights[name_sight_index].name}\n"
            f"Место: {sights[place_sight_index].place}\n\n"
            "Всё верно?"
        )
        await message.answer_photo(
            FSInputFile(sights[image_sight_index].image), caption=caption, reply_markup=markup
        )
        await state.update_data({"is_valid": False, "sight_index": None})
        await state.set_state(ClientState.GUESSING)


@router.message(ClientState.GUESSING)
async def guessing_sh(message: types.Message, state: FSMContext):
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True, keyboard=[[KeyboardButton(text="Загадать")]]
    )
    user_msg = message.text.lower()
    data = await state.get_data()
    if user_msg.startswith("да") and data["is_valid"]:
        congratulations_text = ("\n\nПоздравляем, вы успешно справились! "
                                "Сверху вы можете почитать описание данной достопримечательности. "
                                "Нажмите кнопку загадать если желаете сыграть еще")
        await message.answer(sights[data["sight_index"]].description + congratulations_text, reply_markup=markup)
        await state.set_state(ClientState.GENERATE)
    elif user_msg.startswith("нет") and not data["is_valid"]:
        congratulations_text = ("\n\nПоздравляем, вы успешно справились! "
                                "Эти данные относятся к разным достопримечательностям. "
                                "Нажмите кнопку загадать если желаете сыграть еще")
        await message.answer(congratulations_text, reply_markup=markup)
        await state.set_state(ClientState.GENERATE)
    elif user_msg.startswith("да") and not data["is_valid"]:
        reply_text = ("К сожалению, вы не угадали... "
                    "Эти данные относятся к разным достопримечательностям. "
                    "Нажмите кнопку загадать если желаете сыграть еще")
        await message.answer(reply_text, reply_markup=markup)
        await state.set_state(ClientState.GENERATE)
    elif user_msg.startswith("нет") and data["is_valid"]:
        reply_text = ("\n\nК сожалению, вы не угадали... "
                    "Такая достопримечательность действительно существует. "
                    "Сверху вы можете почитать описание данной достопримечательности. "
                    "Нажмите кнопку загадать если желаете сыграть еще")
        await message.answer(sights[data["sight_index"]].description + reply_text, reply_markup=markup)
        await state.set_state(ClientState.GENERATE)
    return

@router.message()
async def any_sh(message: types.Message) -> None:
    msg = (
        "Чтобы начать напишите /start"
    )

    markup = ReplyKeyboardMarkup(
        resize_keyboard=True, keyboard=[[KeyboardButton(text="/start")]]
    )

    await message.answer(msg, reply_markup=markup)

async def main():
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.info("Считал %s достопримечательностей", len(sights))
    asyncio.run(main())
