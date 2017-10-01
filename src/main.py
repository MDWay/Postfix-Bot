import asyncio
import importlib
import re
import traceback
from string import whitespace

import discord
import sys
import json
import argparse
import os

client = discord.Client()

commands = []


def description(desc):
    def wrapper(func):
        func.description = desc
        return func

    return wrapper


def name(name):
    def wrapper(func):
        func.name = name
        return func

    return wrapper


@description('Helps you...')
@name('help')
@asyncio.coroutine
def help_cmd(cmd_args, author, channel, message):
    embed = discord.Embed()
    embed.colour = discord.Colour.gold()
    embed.description = 'Helping you...'
    for command in commands:
        embed.add_field(name=command.name, value=command.description, inline=False)
    embed.title = 'Command list'
    yield from client.send_message(channel, embed=embed)
    return True


commands += [help_cmd]


class Config(object):
    def __init__(self, **kwargs):
        self.token = kwargs['token']
        self.postfix = kwargs.get('postfix', '...')


def parse_split(content):
    def temp():
        buffer = None
        inquote = False
        escape = False
        for c in content:
            if escape:
                if buffer is None:
                    buffer = c
                else:
                    buffer += c
            if c in "'\"":
                inquote = not inquote
                if buffer is not None:
                    yield buffer
                    buffer = None
            elif c in whitespace and not inquote:
                if buffer is not None:
                    yield buffer
                    buffer = None
            elif c == '\\':
                escape = True
            else:
                if buffer is None:
                    buffer = c
                else:
                    buffer += c
        if buffer is not None:
            yield buffer

    return list(temp())


@client.event
@asyncio.coroutine
def process_message(message):
    content = message.content[:-len(config.postfix)]
    cmd_args = list(parse_split(content))
    print(cmd_args)
    cmd = cmd_args[-1]
    cmd_args = cmd_args[:-1]
    author = message.author
    for c in commands:
        if c.name.lower() == cmd.lower():
            print('Executing command: %s(%s)' % (c.name, str(c)))
            yield from c(cmd_args, author, message.channel, message)
            return
    help_cmd(cmd_args, author, message.channel, message)


@client.event
@asyncio.coroutine
def on_message(message: discord.Message):
    if message.author.id == client.user.id:
        return
    if message.content.endswith(config.postfix):
        yield from process_message(message)


@client.event
@asyncio.coroutine
def on_ready():
    print('Ready')


def load_modules(dir='modules', module='modules') -> tuple:
    print(flush=True, end='')
    loaded_count = 0
    total = 0
    fails = 0
    for file in os.listdir(dir):
        newdir = os.path.join(dir, file)
        if os.path.isdir(newdir):
            add_loaded, add_fails, add_total = load_modules(newdir, module + '.' + file)
            loaded_count += add_loaded
            fails += add_fails
            total += add_total
        if file.endswith('.py'):
            file = file[:-3]
            total += 1
            print('Loading module: %s' % (module + '.' + file), flush=True)
            try:
                importlib.import_module('%s.%s' % (module, file)).setup(commands, client)
            except KeyboardInterrupt:
                raise
            except Exception as e:
                traceback.print_tb(e)
                print('Module load failed: %s' % (module + '.' + file), flush=True)
                fails += 1
                continue
            print('Loaded module: %s' % (module + '.' + file), flush=True)
            loaded_count += 1
    return loaded_count, fails, total


if __name__ == '__main__':
    args = argparse.ArgumentParser()
    args.add_argument('config_file', type=open, help='Config file in json format.')
    ns = args.parse_args(sys.argv[1:])
    config = json.load(ns.config_file)
    print('Config: %s' % str(config))
    print()
    print('Loading modules')
    loaded, fails, total = load_modules()
    print('[' + '#' * loaded + '-' * fails + ']')
    if fails == 0:
        print('Loaded all modules successfully')
    else:
        print('Some modules failed to load.')
        line = ""
        while line.lower() not in ["y", "n"]:
            line = input("Start anyway? (Y/N)")
        if line.lower() == 'n':
            sys.exit(1)
    config = Config(**config)
    client.run(config.token, bot=True)
