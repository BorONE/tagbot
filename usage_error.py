from telegram import Update
from telegram.ext import ContextTypes

class UsageError(Exception):
    def __init__(self, redirect, *lines) -> None:
        self.redirect = redirect
        self.message = '\n'.join(lines)


def RedirectUsageError():
    def decorator(func):
        async def internal(*args, **kwargs):
            try:
                await func(*args, **kwargs)
            except UsageError as e:
                await e.redirect(e.message)
        return internal
    return decorator


def IgnoreEdit():
    def decorator(func):
        async def internal(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message is None:
                if update.edited_message is not None:
                    raise UsageError(update.edited_message.reply_text, 'Edit ignored')
                raise NotImplementedError()
            await func(update, context)
        return internal
    return decorator
