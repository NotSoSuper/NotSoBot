import asyncio
import requests
import json
import random
import discord
from random import choice
from discord.ext import commands
from lxml.html import fromstring
from re import sub

class Chan():
    def __init__(self,bot):
        self.bot = bot

    API_PAGE = 'http://api.4chan.org/{}/1.json'
    POST_URL_TEMPLATE = 'http://boards.4chan.org/{}/res/{}#p{}'

    def format(element):
        '''Return the passed lxml.Element formatted in plain text.'''
        # i hate lxml

        formatted_element = list()

        text = [element.text, element.tail]

        if element.tag == 'br':
            text[0] = u'\n'

        text = filter(lambda x: x, text)

        text = u' '.join(text)

        formatted_element.append(text)

        for child in element:
            formatted_child = format(child)

            formatted_element.append(formatted_child)

        formatted_element = u' '.join(formatted_element)
        formatted_element = formatted_element.strip()
        formatted_element = sub(u' +', u' ', formatted_element)

        return formatted_element


    def get_posts(board):
        '''Return all posts of the board's front page.'''
        url = API_PAGE.format(board)
        # url = 'http://api.4chan.org/b/1.json'

        response = requests.get(url)

        threads = response.json()
        threads = threads['threads']
        threads = map(lambda x: x['posts'], threads)

        parsed_posts = list()

        for thread in threads:
            op = thread[0]

            for post in thread:
                url = POST_URL_TEMPLATE.format(board, op['no'], post['no'])

                try:
                    content = post['com']
                except KeyError:
                    content = ''
                else:
                    content = fromstring(content)
                    content = format(content)

                parsed_posts.append({
                    'content': content,
                    'url': url,
                })

        return parsed_posts


    def get_discord_posts(board):
        '''All posts that are in discords chat limits'''
        posts = get_posts(board)

        posts = filter(lambda x: x['content'], posts)
        posts = filter(lambda x: len(x['content']) <= 1999, posts)
        if len(['content']) >=9:
            return posts
        else:
            posts = get_posts(board)
            posts = filter(lambda x: x['content'], posts)
            posts = filter(lambda x: len(x['content']) <= 1999, posts)
            return posts


    def r_f_discord_post(board):
        '''Random formatted post that is within discord limits'''
        posts = get_discord_posts(board)
        posts = tuple(post['content'] for post in posts)

        post = choice(posts)
        return post

    @commands.command()
    async def chan(self):
        """Replies random 4chan post."""
        boards = ['b', 'pol', 'v', 's4s']
        post = r_f_discord_post(random.choice(boards))
        post = '{}'.format(post)
        await self.bot.say(post)

def setup(bot):
    bot.add_cog(Chan(bot))