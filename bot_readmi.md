# Bot Documentation

## Overview
This bot is created using the Aiogram library for Telegram bot development. It includes various commands and features like user reviews, media file handling, and form submissions. The bot is designed to manage user reviews, handle media files (photos, videos, audio, documents), and interact with users through inline keyboards and state-based conversation forms.

## Features
- **User Reviews**: Collect user reviews with name, email, rating, and comment.
- **Media Handling**: Handle photo, video, audio, and document files.
- **Command Handling**: Multiple commands are available for user interaction.
- **Form Submission**: Users can submit reviews, and the bot tracks data in an SQLite database.
- **Inline Keyboard**: Inline buttons for different actions (e.g., submit review, view all reviews).

## Commands
Here are the commands available in the bot:

- **/start**: Starts the bot and displays a welcome message along with inline buttons for submitting and viewing reviews.
- **/help**: Displays a list of available commands.
- **/custom**: A custom reply message.
- **/info**: Information about the bot.
- **/echo**: Echoes a user's message.
- **/buttons**: Demonstrates inline buttons with external links and callback actions.
- **/begin**: Starts a conversation to collect name and email from the user.
- **/cancel**: Cancels the conversation or current form.
- **/send_photo**: Sends a sample photo.
- **/send_video**: Sends a sample video.
- **/send_audio**: Sends a sample audio file.
- **/send_doc**: Sends a sample document.

## Review Process
Users can submit reviews through a conversation flow where they provide their name, email, rating (1-5), and an optional comment. Reviews are saved in an SQLite database for later retrieval.

### Review Flow:
1. **/submit_review**: Starts the review submission process.
2. **Review Form**: Users are asked for their name, email, rating, and comment.
3. **Confirmation**: The bot confirms the submitted review, which is then stored in the database.

## File Handling
The bot can handle media files such as:
- **Photos**: Saved as `.jpg` files.
- **Videos**: Saved as `.mp4` files.
- **Audios**: Saved as `.mp3` files.
- **Documents**: Saved in their original file format.

### Example Media Handlers:
- **/send_photo**: Sends a sample photo.
- **/send_video**: Sends a sample video.
- **/send_audio**: Sends a sample audio file.
- **/send_doc**: Sends a sample document.

## Database (SQLite)
The bot stores reviews in an SQLite database (`reviews.db`). Each review entry includes the user's `user_id`, `name`, `email`, `rating`, and `comment`.

### Database Table: `reviews`
| Column   | Type      | Description                 |
|----------|-----------|-----------------------------|
| id       | INTEGER   | Primary key, auto-increment |
| user_id  | INTEGER   | User's unique ID            |
| name     | TEXT      | User's name                 |
| email    | TEXT      | User's email address        |
| rating   | INTEGER   | Review rating (1-5)         |
| comment  | TEXT      | Optional review comment     |

## Middleware
The bot includes middleware that cancels the current form if a new event occurs (e.g., if a new message is sent or a callback is triggered).

### `CancelFSMOnNewEventMiddleware`
This middleware clears the FSM (Finite State Machine) state whenever a new event (message or callback query) is triggered.

```python
class CancelFSMOnNewEventMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        state: FSMContext = data.get("state")
        if state and await state.get_state():
            if isinstance(event, Message) and event.text and event.text.startswith('/'):
                await state.clear()
            elif isinstance(event, CallbackQuery):
                await state.clear()
        return await handler(event, data)
