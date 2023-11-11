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
