
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton,
    FSInputFile
)


router = Router()


@router.message(Command("media"))
async def show_media_options(message: Message):
    """Display media selection buttons."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📸 Photo", callback_data="send_photo"),
            InlineKeyboardButton(text="🎬 Video", callback_data="send_video")
        ],
        [
            InlineKeyboardButton(text="🎵 Audio", callback_data="send_audio"),
            InlineKeyboardButton(text="📄 Document", callback_data="send_doc")
        ]
    ])
    await message.answer("Select a media type to send:", reply_markup=keyboard)


@router.callback_query(F.data == "/media")
async def media_button_clicked(callback: CallbackQuery):
    """Callback handler to show media buttons from inline menu."""
    await show_media_options(callback.message)
    await callback.answer()


@router.callback_query(F.data == "send_photo")
async def handle_send_photo(callback: CallbackQuery):
    file = FSInputFile("media/download.png")
    await callback.message.answer_photo(file, caption="📸 Sample photo!")
    await callback.answer()


@router.callback_query(F.data == "send_video")
async def handle_send_video(callback: CallbackQuery):
    file = FSInputFile("media/sample_video.mp4")
    await callback.message.answer_video(file, caption="🎬 Sample video!")
    await callback.answer()


@router.callback_query(F.data == "send_audio")
async def handle_send_audio(callback: CallbackQuery):
    file = FSInputFile("media/sample_audio.mp3")
    await callback.message.answer_audio(file, caption="🎵 Sample audio!")
    await callback.answer()


@router.callback_query(F.data == "send_doc")
async def handle_send_doc(callback: CallbackQuery):
    file = FSInputFile("media/sample_doc.doc")
    await callback.message.answer_document(file, caption="📄 Sample document!")
    await callback.answer()
