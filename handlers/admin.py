import sqlite3

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from states import RoleFSM, DeleteUserFSM, ResetPasswordFSM, AddUserFSM
from database import get_user_role
from config import ADMIN_ROLE


router = Router()


@router.message(Command("set_role"))
async def cmd_set_role(message: Message, state: FSMContext):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to use this command.")
        return
    await message.answer("👤 Enter the target username:")
    await state.set_state(RoleFSM.username)


@router.message(RoleFSM.username)
async def role_target_username(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer("🎭 Enter role to assign (admin/user):")
    await state.set_state(RoleFSM.role)


@router.message(RoleFSM.role)
async def role_assign(message: Message, state: FSMContext):
    role = message.text.lower().strip()
    if role not in ["admin", "user"]:
        await message.answer("⚠️ Role must be 'admin' or 'user'.")
        return

    data = await state.get_data()
    username = data['username']

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT rowid FROM credentials WHERE username = ?", (username,))
    if not c.fetchone():
        await message.answer("❌ Username not found.")
    else:
        c.execute("UPDATE credentials SET role = ? WHERE username = ?", (role, username))
        await message.answer(f"✅ Role '{role}' assigned to user <b>{username}</b>.")
    conn.commit()
    conn.close()
    await state.clear()


@router.message(Command("delete_user"))
async def delete_user_command(message: Message, state: FSMContext):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to delete users.")
        return
    await message.answer("❌ Enter username to delete:")
    await state.set_state(DeleteUserFSM.username)


@router.message(DeleteUserFSM.username)
async def delete_user_action(message: Message, state: FSMContext):
    username = message.text.strip()
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("DELETE FROM credentials WHERE username = ?", (username,))
    conn.commit()
    conn.close()
    await message.answer(f"🗑️ User <b>{username}</b> has been deleted.")
    await state.clear()


@router.message(Command("reset_password"))
async def reset_password_command(message: Message, state: FSMContext):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to reset passwords.")
        return
    await message.answer("🔐 Enter username to reset password:")
    await state.set_state(ResetPasswordFSM.username)


@router.message(ResetPasswordFSM.username)
async def reset_password_get_new(message: Message, state: FSMContext):
    await state.update_data(username=message.text.strip())
    await message.answer("🆕 Enter new password:")
    await state.set_state(ResetPasswordFSM.new_password)


@router.message(ResetPasswordFSM.new_password)
async def reset_password_apply(message: Message, state: FSMContext):
    data = await state.get_data()
    username = data['username']
    new_password = message.text.strip()

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("UPDATE credentials SET password = ? WHERE username = ?", (new_password, username))
    conn.commit()
    conn.close()

    await message.answer(f"🔑 Password for <b>{username}</b> has been reset.")
    await state.clear()


@router.message(Command("add_user"))
async def cmd_add_user(message: Message, state: FSMContext):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to add users.")
        return
    await message.answer("🧑 Enter a new username:")
    await state.set_state(AddUserFSM.username)


@router.message(AddUserFSM.username)
async def add_user_username(message: Message, state: FSMContext):
    username = message.text.strip()
    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT username FROM credentials WHERE username = ?", (username,))
    if c.fetchone():
        await message.answer("⚠️ Username already exists. Please use a different one.")
        conn.close()
        return
    conn.close()
    await state.update_data(username=username)
    await message.answer("🔑 Enter a password for the user:")
    await state.set_state(AddUserFSM.password)


@router.message(AddUserFSM.password)
async def add_user_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text.strip())
    await message.answer("🎭 Enter role (admin/user):")
    await state.set_state(AddUserFSM.role)


@router.message(AddUserFSM.role)
async def add_user_role(message: Message, state: FSMContext):
    role = message.text.lower().strip()
    if role not in ["admin", "user"]:
        await message.answer("⚠️ Role must be 'admin' or 'user'.")
        return

    data = await state.get_data()
    username = data['username']
    password = data['password']

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("INSERT INTO credentials (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()

    await message.answer(f"✅ User <b>{username}</b> added with role <b>{role}</b>.")
    await state.clear()


@router.message(Command("view_users"))
async def view_users(message: Message):
    if get_user_role(message.from_user.id) != ADMIN_ROLE:
        await message.answer("🚫 You do not have permission to view users.")
        return

    conn = sqlite3.connect("roles.db")
    c = conn.cursor()
    c.execute("SELECT username, role FROM credentials")
    users = c.fetchall()
    conn.close()

    if not users:
        await message.answer("No users found.")
    else:
        text = "\n".join(f"👤 <b>{u}</b>: {r}" for u, r in users)
        await message.answer(f"<b>Users:</b>\n\n{text}")


@router.callback_query(F.data == "/add_user")
async def cb_add_user(callback: CallbackQuery, state: FSMContext):
    await cmd_add_user(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "/set_role")
async def cb_set_role(callback: CallbackQuery, state: FSMContext):
    await cmd_set_role(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "/view_users")
async def cb_view_users(callback: CallbackQuery):
    await view_users(callback.message)
    await callback.answer()


@router.callback_query(F.data == "/delete_user")
async def cb_delete_user(callback: CallbackQuery, state: FSMContext):
    await delete_user_command(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "/reset_password")
async def cb_reset_password(callback: CallbackQuery, state: FSMContext):
    await reset_password_command(callback.message, state)
    await callback.answer()