import asyncio
import logging
import os
import sys
import dotenv
from aiogram import Bot, Router, types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.input_file import FSInputFile
from aiogram.filters.command import CommandStart
from quiz.question import *

dotenv.load_dotenv()
quiz = load_quiz_from_json("quiz.json")
if len(quiz.questions) == 0:
    print("Couldn't load any questions! Exiting...")
    exit(1)

router = Router()


class QuizState(StatesGroup):
    """Tracks user's quiz state"""

    WAITING_ANSWER = State()


TOKEN = os.getenv("TOKEN")


@router.message(CommandStart())
async def start_quiz(message: types.Message, state: FSMContext) -> None:
    welcome_msg = (
        "🎓 Добро пожаловать на увлекательный квиз связанный с нефтегазовой отраслью!\n"
        "Я буду отправлять вам случайные вопросы, вам необходимо будет выбирать правильный ответ.\n"
    )

    await message.answer(welcome_msg)
    await send_random_question(message.chat.id, state)


async def send_random_question(chat_id: int, state: FSMContext):
    if not hasattr(send_random_question, "question_index"):
        send_random_question.question_index = 0
    question_data = quiz.questions[send_random_question.question_index]
    send_random_question.question_index = (
        send_random_question.question_index + 1
    ) % len(quiz.questions)
    options = question_data.options

    # Create answer buttons
    markup = ReplyKeyboardMarkup(
        resize_keyboard=True,
        is_persistent=False,
        keyboard=[
            [KeyboardButton(text=str(i + 1)), KeyboardButton(text=str(i + 2))]
            for i in range(0, len(options), 2)
        ],
    )

    # Create question text with options
    question_text_with_options = f"❓ {question_data.question_text}\n\n" + "\n".join(
        f"{i+1}. {opt.text}" for i, opt in enumerate(options)
    )

    # Send question with image if available
    if question_data.image_path:
        try:
            await bot.send_photo(
                chat_id=chat_id,
                photo=FSInputFile(question_data.image_path),
                caption=question_text_with_options,
                reply_markup=markup,
            )
        except:
            await bot.send_message(
                chat_id=chat_id, text=question_text_with_options, reply_markup=markup
            )
    else:
        await bot.send_message(
            chat_id=chat_id, text=question_text_with_options, reply_markup=markup
        )

    # Store correct answer in state
    await state.update_data({"question_data": question_data})
    await state.set_state(QuizState.WAITING_ANSWER)


@router.message(QuizState.WAITING_ANSWER)
async def check_answer(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    question: Question = user_data["question_data"]
    correct_answer = next(
        i + 1 for i, opt in enumerate(question.options) if opt.is_correct
    )

    try:
        user_answer = int(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите число!")
        return

    if user_answer == correct_answer:
        reply = "✅ Поздравляем! Вы ответили правильно!\n" + (question.explanation or "")
    else:
        reply = f"❌ Неправильно! Правильный ответ под номером {correct_answer}"

    await message.answer(reply)
    await send_random_question(message.chat.id, state)


@router.message()
async def handle_other_messages(message: types.Message):
    await message.answer("Введите /start чтобы начать!")


async def main():
    global bot
    bot = Bot(token=TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    logging.info("Loaded %s questions", len(quiz.questions))
    asyncio.run(main())
