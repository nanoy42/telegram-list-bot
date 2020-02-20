# Telegram list Bot - Small bot storing lists
# Copyright (C) 2020 Yoann Pietri

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Telegram List Bot.

Usage:
  main.py (start|stop|restart)
  main.py exec
  main.py debug
  main.py (-h | --help)
  main.py --version

Options:
  start         Start the daemon
  stop          Stop the daemon
  restart       Restart the daemon
  exec          Laucnh bot in blocking mode
  debug         Launch bot in blocking mode with debug info
  -h --help     Show this screen.
  --version     Show version.

"""

import configparser
import json
import logging
import os
import re
import sys

import telegram
from docopt import docopt
from telegram.ext import CommandHandler, Updater

from variables import *

try:
    from local_variables import *
except:
    pass


class Bot:
    """"
    Define a wrapper for telegram-list-bot. Defines handlers for commands.
    """

    def __init__(self, directory=None):
        """Initilise the bot
        
        Args:
            directory (string, optional): Where to find list.json and config.ini files. Defaults to None.
        """
        if directory:
            self.directory = directory
        else:
            self.directory = os.path.dirname(os.path.realpath(__file__))

        self.load_config()

        try:
            self.updater = Updater(token=self.token, use_context=True)
            logging.info("Bot {} grabbed.".format(self.updater.bot.username))
        except:
            logging.error("Unable to grab bot.")
            sys.exit()

        self.dispatcher = self.updater.dispatcher
        self.my_list = {}  # dict containing the chat id as key and list as value
        self.read_list_from_file()

        self.start_handler = CommandHandler("start", self.start)
        self.add_handler = CommandHandler("add", self.add)
        self.remove_handler = CommandHandler("remove", self.remove)
        self.print_handler = CommandHandler("print", self.print_list)
        self.flush_handler = CommandHandler("flush", self.flush)
        self.help_handler = CommandHandler("help", self.help)

        self.dispatcher.add_handler(self.start_handler)
        self.dispatcher.add_handler(self.add_handler)
        self.dispatcher.add_handler(self.remove_handler)
        self.dispatcher.add_handler(self.print_handler)
        self.dispatcher.add_handler(self.flush_handler)
        self.dispatcher.add_handler(self.help_handler)

    def load_config(self):
        """Load configuration file. The configuration file is the config.ini file in code directory.
        """
        config = configparser.ConfigParser()
        try:
            config.read("{}/config.ini".format(self.directory))
        except Exception as e:
            logging.error("Unable to read config : {}".format(str(e)))
            sys.exit()
        try:
            self.token = config.get("Global", "token")
        except:
            logging.error("Unable to find 'token' parameter in section 'Global'.")
            sys.exit()
        try:
            self.chats = [
                int(chat) for chat in config.get("Global", "chats").split(",")
            ]
        except:
            logging.error("Unable to find 'chats' paraneter in section 'Global'.")
            sys.exit()
        logging.info("Configuration loaded")

    def write_list_to_file(self):
        """Write list to file, which is list.json in code directory.
        """
        filename = "{}/list.json".format(self.directory)
        try:
            with open(filename, "w") as outfile:
                json.dump(self.my_list, outfile)
        except:
            logging.error("Could not write to file {}".format(filename))

    def read_list_from_file(self):
        """Read list from file, which is list.json in code directory.
        """
        filename = "{}/list.json".format(self.directory)
        try:
            with open(filename) as json_file:
                tmp = json.load(json_file)
                for key in tmp:
                    self.my_list[int(key)] = tmp[key]
        except:
            logging.warning("Could not read from file {}".format(filename))

    def start(self, update, context):
        """start command handler.

        This command do one of the two followings thing :
            - send a small summary if the chat id is in the chat list
            - send a message explaning that it won't work on this chan otherwise
        
        Args:
            update (dict): message that triggered the handler
            context (CallbackContext): context
        """
        print(update)
        chat_id = update.effective_chat.id
        if chat_id in self.chats:
            if START_MESSAGE:
                context.bot.send_message(chat_id=chat_id, text=START_MESSAGE)
        else:
            logging.info(
                "Chat with id {} tried to communicate but the id is not in the list".format(
                    chat_id
                )
            )
            context.bot.send_message(
                chat_id=chat_id, text="I won't work on this chan. Type /help for help."
            )

    def add(self, update, context):
        """add command handler.

        This command do one of the two followings thing :
            - identify argument, split in items regarding the DELIMITER and adding them to the correct list if the chat is authorised
            - do nothing otherwise
        
        Args:
            update (dict): message that triggered the handler
            context (CallbackContext): context
        """
        chat_id = update.effective_chat.id
        if chat_id in self.chats:
            if chat_id not in self.my_list:
                self.my_list[chat_id] = []
            regexp = re.compile("/add.* (.*)")
            argument = regexp.search(update.message.text).group(1)
            for item in argument.split(DELIMITER):
                self.my_list[chat_id].append(item)
            self.write_list_to_file()

    def remove(self, update, context):
        """remove command handler.

        This command do one of the two followings thing :
            - identify argument, split in items regarding the DELIMITER and removing them from the correct list if the chat is authorised
            - do nothing otherwise
        
        Args:
            update (dict): message that triggered the handler
            context (CallbackContext): context
        """
        chat_id = update.effective_chat.id
        if chat_id in self.chats:
            regexp = re.compile("/remove.* (.*)")
            argument = regexp.search(update.message.text).group(1)
            for item in argument.split(DELIMITER):
                try:
                    self.my_list[chat_id].remove(item)
                except:
                    pass
            self.write_list_to_file()

    def print_list(self, update, context):
        """print command handler.

        This command do one of the two followings thing :
            - print the list if the chat is authorised
            - do nothing otherwise
        
        Args:
            update (dict): message that triggered the handler
            context (CallbackContext): context
        """
        chat_id = update.effective_chat.id
        if chat_id in self.chats:
            if chat_id in self.my_list and self.my_list[chat_id]:
                text = LIST_MESSAGE_BEGIN
                for item in self.my_list[chat_id]:
                    text += "{}{}{}".format(
                        LIST_MESSAGE_BEFORE, item, LIST_MESSAGE_AFTER
                    )
            else:
                text = LIST_MESSAGE_EMPTY
            context.bot.send_message(chat_id=update.effective_chat.id, text=text)

    def flush(self, update, context):
        """flush command handler.

        This command do one of the two followings thing :
            - empty the list if the chat is authorised
            - do nothing otherwise
        
        Args:
            update (dict): message that triggered the handler
            context (CallbackContext): context
        """
        chat_id = update.effective_chat.id
        if chat_id in self.chats:
            if chat_id in self.my_list:
                self.my_list[chat_id] = []
                self.write_list_to_file()

    def help(self, update, context):
        """help command handler.

        This command do one of the two followings thing :
            - print possible commands if the chat is authorised
            - say the bot can't work on this chan and print the id otherwise
        
        Args:
            update (dict): message that triggered the handler
            context (CallbackContext): context
        """
        chat_id = update.effective_chat.id
        if chat_id in self.chats:
            context.bot.send_message(
                chat_id=chat_id,
                text="Telegram list bot\nA simple bot storing list \n\n/start : Summary of the bot.\n/add argument : Add argument to list. Several items may be added at the sane time by separating them with {}.\n/remove argument : Remove argument from list. Several items may be removed at the same time by separating them with {}.\n/print : Print list.\n/flush : Empty list.".format(
                    DELIMITER, DELIMITER
                ),
            )
        else:
            context.bot.send_message(
                chat_id=chat_id,
                text="Bot will not work on this chan. You need to add the following chat id : {} to the chats list in config.ini file.".format(
                    chat_id
                ),
            )

    def start_bot(self):
        """Start the bot.
        """
        self.updater.start_polling()


if __name__ == "__main__":
    arguments = docopt(__doc__, version="Telegram List Bot 0.9")
    daemon = arguments["start"] or arguments["stop"] or arguments["restart"]
    debug = arguments["debug"]

    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logfile = os.path.join(os.getcwd(), "telegram-list-bot.log")
        logging.basicConfig(filename=logfile, level=logging.WARNING)

    d = None

    if daemon:
        from daemons.prefab import run

        class ListBotDaemon(run.RunDaemon):
            def __init__(self, directory, *args, **kwargs):
                """Initialise the daemon
                
                Args:
                    directory (string): directory to pass to the bot
                """
                self.directory = directory
                super().__init__(*args, **kwargs)

            def run(self):
                """Run method (called when daemon starts).
                """
                bot = Bot(self.directory)
                bot.start_bot()

        pidfile = "/tmp/telegram-list-bot.pid"
        d = ListBotDaemon(os.path.dirname(os.path.realpath(__file__)), pidfile=pidfile)

    if arguments["start"]:
        d.start()
    elif arguments["stop"]:
        d.stop()
    elif arguments["restart"]:
        d.restart()
    else:
        bot = Bot()
        bot.start_bot()
