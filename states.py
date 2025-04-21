# states.py
from aiogram.fsm.state import StatesGroup, State


class RoleFSM(StatesGroup):
    """FSM for setting a user's role."""
    username = State()
    role = State()


class DeleteUserFSM(StatesGroup):
    """FSM for deleting a user."""
    username = State()


class ResetPasswordFSM(StatesGroup):
    """FSM for resetting a user's password."""
    username = State()
    new_password = State()


class LoginFSM(StatesGroup):
    """FSM for user login."""
    username = State()
    password = State()


class AddUserFSM(StatesGroup):
    """FSM for adding a new user."""
    username = State()
    password = State()
    role = State()


class SubmitReviewFSM(StatesGroup):
    """FSM for submitting a review."""
    name = State()
    email = State()
    rating = State()
    comment = State()
