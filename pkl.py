import pickle

class LoadSaver:
    def __init__(self, chat_id = None):
        self._chat_id = chat_id
        self._chats = None

    def __enter__(self):
        self._chats = load_data()
        return self._chats.setdefault(self._chat_id, {})
    
    def __exit__(self, exc_type, exc_value, exc_tb):
        if exc_type is None:
            save_data(self._chats)
        return False


def load_data(fallback={}):
    try:
        with open('data.pkl', 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return fallback


def save_data(value):
    with open('data.pkl', 'wb') as f:
        pickle.dump(value, f)

print('data:\n', load_data())
