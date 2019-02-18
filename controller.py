import logging
import os
import threading

from utils import notify

logger = logging.getLogger(__name__)


class Controller:
    """
    # MVC
    # Model is data from telegram
    # Controller handles keyboad events
    # View is terminal vindow
    """

    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.lock = threading.Lock()

    def run(self):
        try:
            self.handle_chats()
        except Exception as e:
            logger.exception('Error happened in main loop')

    def handle_msgs(self):
        # set width to 0.25, move window to left
        # refresh everything
        self.view.chats.resize(0.25)
        self.view.msgs.resize(0.25)
        self.refresh_chats()

        while True:

            key = self.view.get_key(self.view.chats.h, self.view.chats.w)
            logger.info('Pressed key: %s', key)
            if key == 'q':
                return 'QUIT'
            elif key == ']':
                if self.model.next_chat():
                    self.refresh_chats()
            elif key == '[':
                if self.model.prev_chat():
                    self.refresh_chats()
            elif key == 'j':
                if self.model.next_msg():
                    self.refresh_msgs()
            elif key == 'k':
                if self.model.prev_msg():
                    self.refresh_msgs()
            elif key == 'G':
                # move to the bottom
                pass
            elif key == 'gg':
                # move to the top
                pass
            elif key == 'e':
                # edit msg
                pass
            elif key == 'r':
                # reply to this msg
                # print to status line
                pass
            elif key == 'I':
                # open vim or emacs to write long messages
                pass
            elif key == 'i':
                # write new message
                msg = self.view.get_input()
                if msg:
                    chat_id = self.model.get_current_chat_id()
                    self.model.msgs.tg.send_message(
                        chat_id=chat_id,
                        text=msg,
                    )

            elif key == 'h':
                return 'BACK'

    def handle_chats(self):
        # set width to 0.5, move window to center?
        # refresh everything
        self.view.chats.resize(0.5)
        self.view.msgs.resize(0.5)
        self.refresh_chats()
        while True:

            key = self.view.get_key(self.view.chats.h, self.view.chats.w)
            logger.info('Pressed key: %s', key)
            if key == 'q':
                return
            elif key == 'l':
                rc = self.handle_msgs()
                if rc == 'QUIT':
                    return
                self.view.chats.resize(0.5)
                self.view.msgs.resize(0.5)
                self.refresh_chats()

            elif key == 'j':
                is_changed = self.model.next_chat()
                if is_changed:
                    self.refresh_chats()

            elif key == 'k':
                is_changed = self.model.prev_chat()
                if is_changed:
                    self.refresh_chats()

    def refresh_chats(self):
        self.view.draw_chats(
            self.model.current_chat,
            self.model.get_chats()
        )
        self.refresh_msgs()

    def refresh_msgs(self):
        msgs = self.model.get_current_msgs()
        self.view.draw_msgs(self.model.get_current_msg(), msgs)

    def update_handler(self, update):
        logger.debug('===============Received: %s', update)
        _type = update['@type']
        if _type == 'updateNewMessage':
            logger.debug('Updating... new message')
            # with self.lock:
            chat_id = update['message']['chat_id']
            self.model.msgs.msgs[chat_id].append(update['message'])
            msgs = self.model.get_current_msgs()
            self.refresh_msgs()
            try:
                notify(update['message']['content']['text']['text'])
            except Exception:
                logger.exception(
                    'Error happened on notify: %s', update['message'])
            # message_content = update['message']['content'].get('text', {})
        # we need this because of different message types: photos, files, etc.
        # message_text = message_content.get('text', '').lower()

        # if message_text == 'ping':
        #     chat_id = update['message']['chat_id']
        #     # print(f'Ping has been received from {chat_id}')
        #     self.tg.send_message(
        #         chat_id=chat_id,
        #         text='pong',
        #     )
