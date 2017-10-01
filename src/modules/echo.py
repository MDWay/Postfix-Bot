import asyncio

import main

client = None


@main.description("aka cat")
@main.name("echo")
@asyncio.coroutine
def echo(args, author, channel, message):
    yield from client.send_message(channel, content=author.mention + ': ' + args[0])


def setup(default_cmds, cclient):
    global client
    default_cmds += [echo]
    client = cclient
