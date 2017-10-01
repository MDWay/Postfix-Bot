import asyncio
import json
import re

import discord
import requests

import main

client = None
config = None

YOUTUBE_VIDEOS_LIST = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id=%s" \
                      "&key="

YOUTUBE_CHANNEL = "https://www.googleapis.com/youtube/v3/channels?part=snippet&id=%s&fields=items%2Fsnippet" \
                  "%2Fthumbnails&key="


def timeformat(seconds):
    mins = seconds / 60
    seconds %= 60
    hours = mins / 60
    mins %= 60
    return "%02d:%02d:%02d" % (hours, mins, seconds)


@main.description("Gives you information about a youtube video")
@main.name("youtube")
@asyncio.coroutine
def get_youtube_info(args, author, channel, message):
    print("IN HERE")
    regex = re.compile(r"https?://(www\.)?(youtube\.com/watch/?\?v=|youtu\.be/)(?P<id>[a-z\-_]+)")
    id = regex.search(args[0]).group("id")
    json_data = json.loads(requests.get(YOUTUBE_VIDEOS_LIST % id))
    entry = json_data['items'][0]
    content_details = json_data['contentDetails']
    snippet = entry['snippet']
    title = snippet['title']
    published_at = snippet['publishedAt']
    uploaded_by = snippet['channelTitle']
    uploader_id = snippet['channelId']
    uploader_json = json.loads(requests.get(YOUTUBE_CHANNEL % uploader_id))
    uploader_icon = uploader_json['items'][0]['snippet']['thumbnails']['default']
    keywords = ', '.join(snippet['tags'])
    description = snippet['description']
    thumbnail = snippet['thumbnail']['default']['url']
    likes = content_details['likeCount']
    dislikes = content_details['dislikeCount']
    views = content_details['viewCount']
    duration = content_details['duration'].replace("PT", "").replace("S", "").replace("M", ":")
    url = args[0]
    embed = discord.Embed(title=title,
                          description=description,
                          url=url)
    embed.set_image(url=thumbnail)
    embed.set_author(name=uploaded_by, icon_url=uploader_icon)
    embed.set_footer(text='Youtube API?', icon_url="http://youtube.com/yts/img/favicon-vfl8qSV2F.ico")
    embed.add_field(name="Published at", value=published_at)
    embed.add_field(name="Keywords", value=keywords)
    embed.add_field(name="Duration", value=duration)
    embed.add_field(name="Ratings", value="+%d;-%d;ratio %.2f" % (likes, dislikes, likes / dislikes))
    embed.add_field(name="Views", value=str(views))
    yield from client.send_message(channel, embed=embed)


def setup(default_cmds, cclient, cconfig):
    global client
    global config
    global YOUTUBE_VIDEOS_LIST
    config = cconfig
    default_cmds += [get_youtube_info]
    client = cclient
    YOUTUBE_VIDEOS_LIST += config.google['developer-token']
