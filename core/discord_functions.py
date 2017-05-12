"""
A collection of functions that's related to discord
"""
import re

from discord import HTTPException, Forbidden
from discord.embeds import Embed
from discord.ext.commands import CommandOnCooldown
from discord.ext.commands.errors import MissingRequiredArgument

from core import data_controller as db
from core.checks import ManageMessageError, AdminError, ManageRoleError, \
    BadWordError, NsfwError
from core.helpers import strip_letters


def command_error_handler(localize, exception):
    """
    A function that handles command errors
    :param localize: the localization strings
    :param exception: the exception raised
    :return: the message to be sent based on the exception type
    """
    if isinstance(exception, CommandOnCooldown):
        return localize['time_out'].format(strip_letters(str(exception))[0])
    elif isinstance(exception, NsfwError):
        return localize['nsfw_str']
    elif isinstance(exception, BadWordError):
        return localize['bad_word'].format(str(exception))
    elif isinstance(exception, ManageRoleError):
        return localize['not_manage_role']
    elif isinstance(exception, AdminError):
        return localize['not_admin']
    elif isinstance(exception, ManageMessageError):
        return localize['no_manage_messages']
    elif 'Member' in str(exception) and 'not found' in str(exception):
        regex = re.compile('\".*\"')
        name = regex.findall(str(exception))[0].strip('"')
        return localize['member_not_found'].format(name)
    elif isinstance(exception, MissingRequiredArgument):
        if str(exception).startswith('member'):
            return localize['empty_member']
    else:
        # This case should never happen, since it's should be checked in
        # bot.on_command_error
        raise exception


def get_prefix(cur, server, default_prefix):
    """
    the the prefix of commands for a channel
    defaults to the default database
    :param cur: the database cursor
    :param server: the discord server
    :param default_prefix: the bot default prefix
    :return: the prefix for the server
    """
    if server is None:
        return default_prefix
    res = db.get_prefix(cur, server.id)
    return res if res is not None else default_prefix


def build_embed(content: list, colour, **kwargs):
    """
    Build a discord embed object 
    :param content: list of tuples with as such:
        (name, value, *optional: Inline)
        If inline is not provided it defaults to true
    :param colour: the colour of the embed
    :param kwargs: extra options
        author: a dictionary to supply author info as such:
            {
                'name': author name,
                'icon_url': icon url, optional
            }
        footer: the info_footer for the embed, optional
    :return: a discord embed object
    """
    res = Embed(colour=colour)
    if 'author' in kwargs:
        author = kwargs['author']
        name = author['name'] if 'name' in author else None
        url = author['icon_url'] if 'icon_url' in author else None
        if url is not None:
            res.set_author(name=name, icon_url=url)
        else:
            res.set_author(name=name)
    for c in content:
        name = c[0]
        value = c[1]
        inline = len(c) != 3 or c[2]
        res.add_field(name=name, value=value, inline=inline)
    if 'footer' in kwargs:
        if isinstance(kwargs['footer'], str):
            res.set_footer(text=kwargs['footer'])
        elif 'icon_url' in kwargs['footer']:
            res.set_footer(
                text=kwargs['footer']['text'],
                icon_url=kwargs['footer']['icon_url']
            )
        else:
            res.set_footer(text=kwargs['footer']['text'])

    return res


def check_message(bot, message, expected):
    """
    A helper method to check if a message's content matches with expected 
    result and the author isn't the bot.
    :param bot: the bot
    :param message: the message to be checked
    :param expected: the expected result
    :return: true if the message's content equals the expected result and 
    the author isn't the bot
    """
    return \
        message.content == expected and \
        message.author.id != bot.user.id and \
        not message.author.bot


def check_message_startwith(bot, message, expected):
    """
    A helper method to check if a message's content start with expected 
    result and the author isn't the bot.
    :param bot: the bot
    :param message: the message to be checked
    :param expected: the expected result
    :return: true if the message's content equals the expected result and 
    the author isn't the bot
    """
    return \
        message.content.startswith(expected) and \
        message.author.id != bot.user.id and \
        not message.author.bot


def clense_prefix(message, prefix: str):
    """
    Clean the message's prefix
    :param message: the message
    :param prefix: the prefix to be cleaned
    :return: A new message without the prefix
    """
    if not message.content.startswith(prefix):
        return message.content
    else:
        return message.content[len(prefix):].strip()


async def handle_forbidden_http(ex, bot, channel, localize, action):
    """
    Exception handling for Forbidden and HTTPException
    :param ex: the exception raised
    :param bot: the bot
    :param channel: the channel to send a message to
    :param localize: the localize strings
    :param action: the action that caused the exception
    """
    if isinstance(ex, Forbidden):
        await bot.send_message(channel, localize['no_perms'])
    elif isinstance(ex, HTTPException):
        await bot.send_message(channel, localize['https_fail'].format(action))
    else:
        raise ex


def get_avatar_url(member):
    """
    Get the avatar url of a member
    :param member: the discord member
    :return: the avatar url of the member
    """
    return '{0.avatar_url}'.format(member) if member.avatar_url != '' \
        else member.default_avatar_url


def get_name_with_discriminator(member):
    """
    Get the name of a member with discriminator
    :param member: the member
    :return: the name of a member with discriminator
    """
    return member.display_name + '#' + member.discriminator
