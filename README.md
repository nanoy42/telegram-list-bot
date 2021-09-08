# Telegram list bot

 * [Introduction](#introduction)
 * [Installation](#installation)
 * [Configuration](#configuration)
 * [Screenshots](#screenshots)
 * [Under the hood](#under-the-hood)
 * [FAQ](#faq)

## Introduction

Telegram list bot is small telegram bot useful to store small to medium lists on a small number of chats.

Some functionnalities of the bot :

 * add one or more item to the list;
 * remove one or more item from the list;
 * print the list;
 * empty all list;
 * change the way the items are displayed (and some basic personalization)
 * shopping mode

Some application folows : 

 * todo-list
 * grocery list

### Shopping mode

The shopping mode was introduced in version 1.0 as an experimental feature.

It is a mode where you can interactively delete items from the list (when you are making your shopping), using a single message in the telegram chat.

## Installation


You can install all the dependencies with the following command :

```
pipenv install --ignore-pipfile
```

You can install all dependencies + dev dependencies with the following command :

```
pipenv install --dev --pre
```

Then you can clone the repository and copy the `config.ini.example` into `config.ini`. Make sure that the righs are good (the user executing the bot will need write permissions).

You will also need a telegram bot, basically it's just talking with @BotFather, but the documentation can be found here : https://core.telegram.org/bots.
## Configuration

### Basic configuration

You then need to configure your bot. The main part of the configuration is located in the config.ini file, where there are two paramters in the `[Global]` section :

| Parameter | Description                                                                | Default value                             |
| --------- | -------------------------------------------------------------------------- | ----------------------------------------- |
| token     | token of your telegram bot                                                 | 123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11 |
| chats     | list of chat ids, spearated by commas, where the bot is authorized to work | 0,1                                       |

Tip : If you don't know the chat id, which is likley, you can talk to the bot and use the /help command. It will say that the bot is not enabled and give the chat id.

This configuration will be sufficient in order to make the bot work. You can start the bot with 

```
python3 main.py exec
```

or

```
python3 main.py debug
```

### Advanced configuration

If you want more control, and small personalization, you can edit the file `variables.py`. 6 variables are stored there :

| Variable            | Descritpion                                              | Default value                                     |
| ------------------- | -------------------------------------------------------- | ------------------------------------------------- |
| DELIMITER           | Char used to split arguments of /add and /remove command | `";"`                                             |
| START_MESSAGE       | Message displayed on the /start command                  | `"I'm a bot storing lists. Type /help for help."` |
| LIST_MESSAGE_BEGIN  | Begin of messaage for /print command                     | `"List: "`                                        |
| LIST_MESSAGE_BEFORE | Placed before each item in /print command                | `"\n- "                                           |
| LIST_MESSAGE_AFTER  | Placed after each item in /primt command                 | `""`                                              |
| LIST_MESSAGE_EMPTY  | Displayed when list is empty on /print command           | `"Nothing in the list"`                           |

### Use the bot

There are 3 ways to use the bot:

 * in daemon mode
 * in exec mode
 * in debug mode

#### Daemon mode

For this, you will need the pip package `daemons` to be installed. You can then use the thre following commands :

```
python3 main.py start
python3 main.py stop
python3 main.py restart
```

to start, stop and restart the daemon. The logs are stored in the directory where the code is located.

#### Exec mode

You can start the exec mode with the command 

```
python3 main.py exex
```

The script will run in a blocking way in the current terminal until it receives an interruption (Ctrl-C for instance).

The logs are stored in the directory where the code is located.

#### Debug mode

You can start the debug mode with the command 

```
python3 main.py debug
```

The bot will start in a blocking way in the current terminal (as for the exec mode), but this times, logs are directly printed to the console and the log level is DEBUG.

## Screenshots
![Screenshot1](https://images.nanoy.fr/telegram-list-bot/screenshot1.png)

Here are the basics command of the bot.

![Screenshot2](https://images.nanoy.fr/telegram-list-bot/screenshot2.png)

You can change the default display by editing the `variables.py` file.

![Screenshot3](https://images.nanoy.fr/telegram-list-bot/screenshot3.png)

![Screenshot4](https://images.nanoy.fr/telegram-list-bot/screenshot4.png)

You can also change the delimiter in the `variables.py` file.
## Under the hood

The bot is using the python telegram bot wapper. The lists are stored as a python dictionnary chat => list. The list is written as a json file in order to have a reboot proof bot. 

## FAQ

### Can we change the variables in a local file ?

You can define the variables in a `local_variables.py` file.

### Command autocompletion

For the command autocompletion, you can talk to the BotFather, then select your bot and edit bot. Go on the commands button and give the foolowing description 

```
start - Small description of the bot
add - Add one or more item
remove - Remove one or more item
print - Display list
shopping - Start shopping mode
flush - Empty list
help - Display help message
```
