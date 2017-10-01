import asyncio

import main

client = None

config = None


@main.description("aka cat")
@main.name("echo")
@asyncio.coroutine
def echo(args, author, channel, message):
    yield from client.send_message(channel, content=author.mention + ': ' + args[0])


def setup(default_cmds, cclient, cconfig):
    global client
    global config
    config = cconfig
    default_cmds += [echo]
    client = cclient
