"""
The Hifumi bot object
"""
import sqlite3
import time
import traceback
from logging import CRITICAL, ERROR, WARNING
from pathlib import Path

from discord import ChannelType, Game, Message
from discord.ext.commands import BadArgument, Bot, CommandNotFound, \
    CommandOnCooldown, Context, MissingRequiredArgument
from websockets.exceptions import ConnectionClosed

from config.settings import DEFAULT_PREFIX, ENABLE_CONSOLE_LOGGING, OWNER
from data_controller import *
from data_controller.data_utils import get_prefix
from scripts.checks import AdminError, BadWordError, ManageMessageError, \
    ManageRoleError, NsfwError, OwnerError
from scripts.discord_functions import command_error_handler
from scripts.language_support import read_language
from scripts.logger import get_console_handler, info, setup_logging


class Hifumi(Bot):
    """
    The Hifumi bot class
    """
    __slots__ = ['default_prefix', 'shard_id', 'shard_count', 'start_time',
                 'language', 'default_language', 'logger', 'mention_normal',
                 'mention_nick', 'conn', 'cur', 'all_emojis']

    def __init__(self, shard_count, shard_id,
                 default_language='en'):
        """
        Initialize the bot object
        :param shard_count: the shard count, default is 1
        :param shard_id: shard id, default is 0
        :param default_language: the default language of the bot, default is en
        unless you know what you are doing
        """
        super().__init__(
            command_prefix=get_prefix,
            shard_count=shard_count,
            shard_id=shard_id
        )
        self.conn = sqlite3.connect(str(DB_PATH))
        self.cur = self.conn.cursor()
        self.tag_matcher = TagMatcher(self.conn, self.cur)
        self.data_manager = DataManager(self.conn, self.cur)
        self.default_prefix = DEFAULT_PREFIX
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.start_time = int(time.time())
        self.language = read_language(Path('./data/language'))
        self.default_language = default_language
        self.logger = setup_logging(
            self.start_time, Path('./data/logs')
        )
        self.mention_normal = ''
        self.mention_nick = ''
        with Path('./data/emojis.txt').open() as f:
            self.all_emojis = f.read().splitlines()
            f.close()

    def __del__(self):
        self.conn.close()

    async def on_ready(self):
        """
        Event for the bot is ready
        """
        g = '{}help'.format(self.default_prefix)
        info('Logged in as ' + self.user.name + '#' + self.user.discriminator)
        info('Bot ID: ' + self.user.id)
        self.mention_normal = '<@{}>'.format(self.user.id)
        self.mention_nick = '<@!{}>'.format(self.user.id)

        async def __change_presence():
            try:
                await self.wait_until_ready()
                await self.change_presence(game=Game(name=g))
            except ConnectionClosed as e:
                self.logger.warning(str(e))
                await self.logout()
                await self.login()
                await __change_presence()

        await __change_presence()
        if ENABLE_CONSOLE_LOGGING:
            self.logger.addHandler(get_console_handler())

    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        handled_exceptions = (
            CommandOnCooldown, NsfwError, BadWordError, ManageRoleError,
            AdminError, ManageMessageError, MissingRequiredArgument, OwnerError,
            BadArgument
        )
        if isinstance(exception, handled_exceptions):
            await self.send_message(
                context.message.channel,
                command_error_handler(
                    self.get_language_dict(context), exception
                )
            )
        elif isinstance(exception, CommandNotFound):
            # Ignore this case
            return
        else:
            try:
                raise exception
            except:
                tb = traceback.format_exc()
            triggered = context.message.content
            ex_type = type(exception).__name__
            four_space = ' ' * 4
            str_ex = str(exception)
            msg = '\n{0}Triggered message: {1}\n' \
                  '{0}Type: {2}\n' \
                  '{0}Exception: {3}\n\n{4}' \
                .format(four_space, triggered, ex_type, str_ex, tb)
            self.logger.log(WARNING, msg)
            await self.send_message(
                context.message.channel,
                self.get_language_dict(context)['ex_warn'].format(
                    triggered, ex_type, str_ex
                )
            )

    async def on_error(self, event_method, *args, **kwargs):
        """
        General error handling for discord
        Check :func:`discord.on_error` for more details.
        """
        ig = 'Ignoring exception in {}\n'.format(event_method)
        tb = traceback.format_exc()
        self.logger.log(ERROR, '\n' + ig + '\n' + tb)
        try:
            ctx = args[1]
            await self.send_message(
                ctx.message.channel,
                self.get_language_dict(ctx)['ex_error'].format(ig + tb)
            )
        except Exception as e:
            msg = str(e) + '\n' + str(tb)
            self.logger.log(CRITICAL, msg)
            for dev in [await self.get_user_info(i) for i in OWNER]:
                await self.send_message(
                    dev,
                    'An exception ocurred while the '
                    'bot was running. For help, check '
                    '"Troubleshooting" section in '
                    'documentation, come to our support '
                    'server or open an issue in Git repo.'
                    "\n```py" + msg + "```"
                )

    async def process_commands(self, message):
        """
        Overwrites the process_commands method
        to provide command black list support.
        Check :func:`Bot.process_commands` for more details.
        """
        if message.author.bot:
            return
        prefix = get_prefix(self, message)
        name = message.content.split(' ')[0][len(prefix):]
        # TODO Implement command black list
        await super().process_commands(message)

    def start_bot(self, cogs: list, token):
        """
        Start the bot
        :param cogs: a list of cogs
        :param token: the bot token
        """
        # TODO remove default help when custom help is finished
        # self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.run(token)

    def get_language_dict(self, ctx_msg):
        """
        Get the language of the given context
        :param ctx_msg: the discord context object, or a message object
        :return: the language dict
        :rtype: dict
        """
        return self.language[self.get_language_key(ctx_msg)]

    def get_language_key(self, ctx_msg):
        """
        Get the language key of the context
        :param ctx_msg: the discord context object, or a message object
        :return: the language key
        """
        if isinstance(ctx_msg, Context):
            message = ctx_msg.message
        elif isinstance(ctx_msg, Message):
            message = ctx_msg
        else:
            raise TypeError
        channel = message.channel
        if channel.type == ChannelType.text:
            lan = self.data_manager.get_language(int(message.server.id))
            return lan or self.default_language
        else:
            return self.default_language
