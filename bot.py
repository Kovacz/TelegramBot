import telebot
import config
import eventlet
import requests
import logging
import random
from telebot import types

url = 'https://api.vk.com/method/wall.get?domain=tproger&count=10&access_token=' + config.VK_TOKEN
urlTop = "https://api.vk.com/method/wall.get?domain=tproger&count=100&offset={}&access_token=" + config.VK_TOKEN
urlLast100 = "https://api.vk.com/method/wall.get?domain=tproger&count=100&access_token=" + config.VK_TOKEN
urlRandom = "https://api.vk.com/method/wall.get?domain=tproger&posts={}&access_token=" + config.VK_TOKEN

bot = telebot.TeleBot(config.token)


@bot.message_handler(content_types=['text'])
def repeat_all_messages(message):
    buttons = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    buttons.add('New posts')
    buttons.add('TOP 10 posts')
    buttons.add('Random post')
    bot.send_message(chat_id=message.chat.id, text='Here is it: ', reply_markup=buttons)
    bot.register_next_step_handler(message, process_step)


def process_step(message):
    chat_id = message.chat.id
    if message.text == 'New posts':
        get_last_10(chat_id)
    if message.text == 'TOP 10 posts':
        get_top(chat_id)
    if message.text == 'Random post':
        get_random(chat_id)


def get_top(chat_id):
    posts = get_all_posts()
    posts.sort(key=sortByLikes)
    posts.reverse()
    send_messages(posts[0:10], chat_id)

def sortByLikes(post):
    return post['likes']['count']


def get_last_10(chat_id):
    posts = get_data(url)
    send_messages(posts, chat_id)


def get_random(chat_id):
    posts = get_data(urlLast100)[random.randint(0, 99)]
    send_messages(posts, chat_id)


#########################################
def send_messages(posts, chat_id):
    if (isinstance(posts, list)):
        text_array = []
        for i, post in enumerate(posts):
            text = '\n\n------№{}---------\n'.format(i + 1).__add__(post["text"].replace("<br>", "\n")).__add__(
                '\n\nRating of likes: {}'.format(post['likes']["count"]))
            text_array.append(text)
            if (i % 3 == 0):
                join = ''.join(text_array)
                bot.send_message(chat_id, join)
                text_array.clear()
    else:
        text = posts["text"].replace("<br>", "\n").__add__(
            '\n\nRating of likes: {}'.format(posts['likes']["count"]))
        bot.send_message(chat_id, text)


def get_data(url):
    timeout = eventlet.Timeout(10)
    try:
        feed = requests.get(url)
        list = []
        for i, post in enumerate(feed.json()['response']):
            if (i >= 1): list.append(post)
        return list
    except eventlet.timeout.Timeout:
        logging.warning('Got Timeout while retrieving VK JSON data. Cancelling...')
        return None
    finally:
        timeout.cancel()


def get_all_posts():
    offset = 0
    posts = []
    while offset < 1000:
        posts.extend(get_data(urlTop.format(offset)))
        offset += 100
    return posts


if __name__ == '__main__':
    bot.polling(none_stop=True)