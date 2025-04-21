# handlers/review.py
import logging
import sqlite3

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from states import SubmitReviewFSM
from database import get_user_role


router = Router()


@router.message(Command("submit_review"))
async def submit_review_command(message: Message, state: FSMContext):
    """Begin review submission process by asking for name."""
    await message.answer("Please provide your name:")
    await state.set_state(SubmitReviewFSM.name)


@router.message(SubmitReviewFSM.name)
async def ask_for_email(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Please provide your email:")
    await state.set_state(SubmitReviewFSM.email)


@router.message(SubmitReviewFSM.email)
async def ask_for_rating(message: Message, state: FSMContext):
    await state.update_data(email=message.text.strip())
    await message.answer("Please provide a rating from 1 to 5:")
    await state.set_state(SubmitReviewFSM.rating)


@router.message(SubmitReviewFSM.rating)
async def ask_for_comment(message: Message, state: FSMContext):
    rating = message.text.strip()
    if not rating.isdigit() or not 1 <= int(rating) <= 5:
        await message.answer("Rating must be a number between 1 and 5. Please provide a valid rating:")
        return

    await state.update_data(rating=int(rating))
    await message.answer("Please provide your comment:")
    await state.set_state(SubmitReviewFSM.comment)


@router.message(SubmitReviewFSM.comment)
async def save_review(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        name = data['name']
        email = data['email']
        rating = data['rating']
        comment = message.text.strip()
        user_id = message.from_user.id

        conn = sqlite3.connect("roles.db")
        c = conn.cursor()
        c.execute(
            '''INSERT INTO reviews (user_id, name, email, rating, comment)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, name, email, rating, comment)
        )
        conn.commit()
        conn.close()

        await message.answer("✅ Your review has been submitted successfully!")
    except Exception as e:
        logging.exception("Error saving review")
        await message.answer("❌ Failed to save your review. Please try again later.")
    finally:
        await state.clear()


@router.callback_query(F.data == "/submit_review")
async def submit_review_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Please provide your name:")
    await state.set_state(SubmitReviewFSM.name)
    await callback.answer()


@router.message(Command("view_reviews"))
async def view_reviews_command(message: Message):
    user_id = message.from_user.id
    role = get_user_role(user_id)

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()

    if role == "admin":
        c.execute(
            '''SELECT users.user_id, reviews.name, reviews.email, reviews.rating, reviews.comment
               FROM reviews JOIN users ON reviews.user_id = users.user_id'''
        )
    else:
        c.execute(
            '''SELECT name, email, rating, comment
               FROM reviews WHERE user_id = ?''', (user_id,)
        )

    reviews = c.fetchall()
    conn.close()

    if reviews:
        review_text = ""
        for rev in reviews:
            if role == "admin":
                review_text += (
                    f"🆔 User ID: {rev[0]}\n"
                    f"📛 Name: {rev[1]}\n"
                    f"📧 Email: {rev[2]}\n"
                    f"⭐ Rating: {rev[3]}/5\n"
                    f"💬 Comment: {rev[4]}\n\n"
                )
            else:
                review_text += (
                    f"📛 Name: {rev[0]}\n"
                    f"📧 Email: {rev[1]}\n"
                    f"⭐ Rating: {rev[2]}/5\n"
                    f"💬 Comment: {rev[3]}\n\n"
                )

        await message.answer(f"<b>Reviews:</b>\n\n{review_text}", parse_mode=ParseMode.HTML)
    else:
        await message.answer("No reviews found.")


@router.callback_query(F.data == "/view_reviews")
async def view_reviews_callback(callback: CallbackQuery):
    await view_reviews_command(callback.message)
    await callback.answer()