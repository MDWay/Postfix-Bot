import asyncio
import re

import discord
import requests

import main

client = None
config = None

YOUTUBE_VIDEOS_LIST = "https://www.googleapis.com/youtube/v3/videos?part=snippet%2CcontentDetails%2Cstatistics&id={" \
                      "}&key="

YOUTUBE_CHANNEL = "https://www.googleapis.com/youtube/v3/channels?part=snippet&id={}&fields=items%2Fsnippet" \
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
    regex = re.compile(r"^https?://(www\.)?(youtube\.com/watch/?\?v=|youtu\.be/)(?P<id>[a-z\-_0-9]+)$", re.IGNORECASE)
    id = regex.search(args[0]).group("id")
    json_data = requests.get(YOUTUBE_VIDEOS_LIST.format(id)).json()
    print(json_data)
    entry = json_data['items'][0]
    content_details = entry['contentDetails']
    statistics = entry['statistics']
    snippet = entry['snippet']
    title = snippet['title']
    published_at = snippet['publishedAt']
    uploaded_by = snippet['channelTitle']
    uploader_id = snippet['channelId']
    uploader_json = requests.get(YOUTUBE_CHANNEL.format(uploader_id)).json()
    uploader_icon = uploader_json['items'][0]['snippet']['thumbnails']['default']
    keywords = ', '.join(snippet['tags'])
    description = snippet['description']
    thumbnail = snippet['thumbnails']['default']['url']
    likes = statistics['likeCount']
    dislikes = statistics['dislikeCount']
    views = statistics['viewCount']
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
    embed.add_field(name="Ratings", value="+%s;-%s;ratio %.2f" % (likes, dislikes, int(likes) / int(dislikes)))
    embed.add_field(name="Views", value=str(views))
    yield from client.send_message(channel, embed=embed)


def setup(default_cmds, cclient, cconfig):
    global client
    global config
    global YOUTUBE_CHANNEL
    global YOUTUBE_VIDEOS_LIST
    config = cconfig
    default_cmds += [get_youtube_info]
    client = cclient
    YOUTUBE_VIDEOS_LIST += config.google['developer-token']
    YOUTUBE_CHANNEL += config.google['developer-token']
