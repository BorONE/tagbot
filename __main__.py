# TODO gitignore

# pip install python-telegram-bot
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from pkl import LoadSaver
from usage_error import RedirectUsageError, UsageError


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command, *args = update.message.text.split()
    me = command[len('/help'):]
    await update.message.reply_markdown('\n'.join([
        f'/help{me} – show this message',
        f'/new{me} – to create tagname with users',
        f'/delete{me} – to delete tagname',
        f'/list{me} – list all tagnames',
        '',
        'Tag groups of users with created tagnames ',
    ]))


@RedirectUsageError()
async def new_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message is None:
        if update.edited_message is not None:
            raise UsageError(update.edited_message.reply_text, 'Edit ignored')
        raise NotImplementedError()

    command, *args = update.message.text.split()

    usage_example = f'{command} @tagname @user1 @user2 @user3'
    reply_text = update.message.reply_text

    if len(args) == 0:
        raise UsageError(reply_text, 'Got empty /new. Use:', usage_example)
    if len(args) == 1:
        raise UsageError(reply_text, 'Got /new with no users. Use:', usage_example)
    
    tagname, *users = args

    if not tagname.startswith('@'):
        raise UsageError(reply_text, 'Tagname is missing @. Use:', usage_example)
    if not all(user.startswith('@') for user in users):
        raise UsageError(reply_text, 'Some users are missing @. Use:', usage_example)

    with LoadSaver(update.message.chat.id) as group:
        group[tagname] = ' '.join(users)
        await update.message.reply_markdown(f'`{tagname}` created')


@RedirectUsageError()
async def delete_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    command, *args = update.message.text.split()

    usage_example = f'{command} @tagname'
    async def reply_text(msg): await update.message.reply_text(msg)

    if len(args) == 0:
        raise UsageError(reply_text, 'Got empty /delete. Use:', usage_example)

    tagnames = args

    if not all(tagname.startswith('@') for tagname in tagnames):
        raise UsageError(reply_text, 'Some tagnames are missing @. Use:', usage_example)

    log = []
    with LoadSaver(update.message.chat.id) as group:
        for tagname in tagnames:
            if tagname in group:
                group.pop(tagname)
                log.append(f'{tagname} deleted')
            else:
                log.append(f'{tagname} not found')
    await update.message.reply_markdown('\n'.join(log))


async def list_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with LoadSaver(update.message.chat.id) as group:
        tagnames = list(group.keys())

    if len(tagnames) > 0:
        await update.message.reply_text('\n'.join(tagnames))
    else:
        await update.message.reply_text('no tagnames')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tokens = update.message.text.split()
    tagnames = list(token for token in tokens if token.startswith('@'))
    if len(tagnames) == 0:
        return
    
    with LoadSaver(update.message.chat.id) as group:
        users = group.get('@all', '').split()
        result = [f'{tagname}: {group.get(tagname, "")}' for tagname in tagnames if tagname not in users]
    await update.message.reply_text('\n'.join(result))


async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print({
        'text':         update.message.text,
        'entities':     update.message.entities,
        'error':        context.error,
        'error_type':   type(context.error),
    })


def read_token(filename='token.txt') -> str:
    token = None
    with open(filename, 'r') as file:
        token = file.readline().strip()
    assert token is not None
    return token


if __name__ == '__main__':
    token = read_token()
    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler('help',   help_command))
    app.add_handler(CommandHandler('new',    new_command))
    app.add_handler(CommandHandler('delete', delete_command))
    app.add_handler(CommandHandler('list',   list_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    print('Polling...')

    app.run_polling(poll_interval=5)
