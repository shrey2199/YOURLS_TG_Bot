# -*- coding: utf-8 -*-

import telegram
import telebot
import requests
import json
import logging
import urllib.parse
from functools import wraps
from random import *

min_char = 4
max_char = 6

# CONFIG

API_TOKEN = ''
YL_DOMAIN = '' # ==> Without https:// or http://
YL_SIG = ''
try:
    ADMIN_LIST = ['','']  # ==> Enter Admin Chat IDs here !!
    restricted_mode = True
except:
    ADMIN_LIST = []  # ==> Do Not Touch This !!
    restricted_mode = False

# BOT CODE

bot = telebot.TeleBot(API_TOKEN)
logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

def restricted(func):
    @wraps(func)
    def wrapped(update, *args, **kwargs):
        user_id = update.from_user.id
        if (restricted_mode) and (str(user_id) not in ADMIN_LIST):
            print("Unauthorized access denied for {} - {}.".format(user_id, update.from_user.username))
            bot.send_message(update.chat.id, "*Error :\t\t*You are not Authorized to access the bot.\n\nPls Contact [Bot Admin](https://t.me/s_rawal) !!", parse_mode='Markdown', disable_web_page_preview=True)
            return
        return func(update, *args, **kwargs)
    return wrapped

@bot.message_handler(commands=['start'])
@restricted
def start(m):
    bot.send_message(m.chat.id, text="""Hey !! Welcome to Shrey23 URL Shorten Bot !
    \n<b>To Shorten your URLs :-</b>
    Send /short <code>&lt;link&gt;</code> to the bot.
    \nSend /help for More Info !""", parse_mode=telegram.ParseMode.HTML)

@bot.message_handler(commands=['help'])
@restricted
def help(m):
	bot.send_message(chat_id=m.chat.id, text="""This Bot can Shorten Your URLs with support for Custom Keywords.
    \n<b>For using Random Keyword :-</b>
    Send /short <code>&lt;link&gt;</code>
    \n<b>For using Custom Keyword :-</b>
    Send /short <code>&lt;link&gt;</code> <code>&lt;keyword&gt;</code>
    \n<b>To get Link Info :-</b>
    Send /info <code>&lt;keyword/link&gt;</code>
    \n<b>To Delete A Link :-</b>
    Send /delete <code>&lt;keyword/link&gt;</code>""", parse_mode=telegram.ParseMode.HTML)

@bot.message_handler(commands=['short'])
@restricted
def short(m):
    chat = m.text[9:]
    if chat == "":
        bot.send_message(chat_id=m.chat.id, text="""Pls Send the Command with Valid Queries !!
        \n<b>For using Random Keyword :-</b>
        Send /short <code>&lt;link&gt;</code>
        \n<b>For using Custom Keyword :-</b>
        Send /short <code>&lt;link&gt;</code> <code>&lt;keyword&gt;</code>""", parse_mode=telegram.ParseMode.HTML)
    else:

        link = m.text.split()[1]
        elink = urllib.parse.quote(link)
        allchar = "abcdefghijklmnopqrstuvwxyz0123456789"
        if len(m.text.split()) == 3:
        	word = m.text.split()[2]
        if len(m.text.split()) == 2:
        	word = "".join(choice(allchar) for x in range(randint(min_char, max_char)))
        url = 'https://'+YL_DOMAIN+'/yourls-api.php?signature='+YL_SIG+'&action=shorturl&url=' + elink + '&keyword=' + word + '&format=json'

        try:
            r = requests.get(url)
            res = r.json()
            if res["statusCode"] == 200:
            	if res["status"] == str("success"):
            		bot.send_message(m.chat.id, "*Shortened URL :*\t\t" + str(res["shorturl"]), parse_mode='Markdown', disable_web_page_preview=True)
            	if res["status"] == str("fail"):
            		if res["code"] == str("error:url"):
            			error_message = "*Error :\t\t*" + str(res["message"])
            			url_message = "*It's Shortened URL :\t\t*" + str(res["shorturl"])
            			bot.send_message(m.chat.id, error_message + 
                        "\n\n" + url_message, parse_mode='Markdown', disable_web_page_preview=True)
            		if res["code"] == str("error:keyword"):
            			error_message = "<b>Error :\t\t</b>" + str(res["message"] + "\n\nFor More Info about <b>" + word + "</b> keyword :-\n\nSend /info <code>" + word +"</code> to the Bot.")
            			bot.send_message(m.chat.id, error_message, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
            else:
                bot.send_message(m.chat.id, "*Error :\t\t*" + str(res["message"]), parse_mode='Markdown', disable_web_page_preview=True)
        except:
            bot.send_message(m.chat.id, text = "An error occurred sending http request.", parse_mode=telegram.ParseMode.HTML)

@bot.message_handler(commands=['info'])
@restricted
def info(m):
    chat = m.text[5:]
    if chat == "":
        bot.send_message(m.chat.id, text = """Pls Send the Command with Valid Queries !!
        \n<b>To get Link Info :-</b>
        Send /info <code>&lt;keyword/link&gt;</code>""", parse_mode=telegram.ParseMode.HTML)
    else:
        link = m.text.split()[1]
        elink = urllib.parse.quote(link, safe='')
        url = 'https://'+YL_DOMAIN+'/yourls-api.php?signature='+YL_SIG+'&action=url-stats&shorturl=' + elink + '&format=json'
        try:
            r = requests.get(url)
            res = r.json()
            if res["message"] == "success":
                bot.send_message(m.chat.id, "*Shortened URL :\t\t*" + str(res["link"]["shorturl"]) + 
                "\n*URL :\t\t*" + str(res["link"]["url"]) + 
                "\n*Created :\t\t*" + str(res["link"]["timestamp"]) +
                "\n*Clicks :\t\t*" + str(res["link"]["clicks"]), parse_mode='Markdown')
                print("RESPONSE: " + str(res))
            if res["statusCode"] == 404:
                bot.send_message(m.chat.id, "*Error :\t\t*Short URL not found.", parse_mode='Markdown')
            else:
                bot.send_message(m.chat.id, str(res["message"]), parse_mode='Markdown')
        except json.JSONDecodeError:
            bot.send_message(m.chat.id, "*Error :\t\t*YOURLS SERVER NOT REACHABLE; TRY AGAIN LATER", parse_mode='Markdown')

@bot.message_handler(commands=['delete'])
@restricted
def info(m):
    chat = m.text[7:]
    if chat == "":
        bot.send_message(m.chat.id, text = """Pls Send the Command with Valid Queries !!
        \n<b>To Delete A Link :-</b>
        Send /delete <code>&lt;keyword/link&gt;</code>""", parse_mode=telegram.ParseMode.HTML)
    else:
        link = m.text.split()[1]
        elink = urllib.parse.quote(link, safe='')
        url = 'https://'+YL_DOMAIN+'/yourls-api.php?signature='+YL_SIG+'&action=delete&shorturl=' + elink + '&format=json'
        try:
            r = requests.get(url)
            res = r.json()
            if res["statusCode"] == 200:
                bot.send_message(m.chat.id, "The <b>link/keyword</b>: <code>"+link+"</code> has been successfully deleted.", parse_mode=telegram.ParseMode.HTML)
            if res["statusCode"] == 404:
                bot.send_message(m.chat.id, "*Error :\t\t*Short URL not found.", parse_mode='Markdown')
            else:
                bot.send_message(m.chat.id, str(res["message"]), parse_mode='Markdown')
        except json.JSONDecodeError:
            bot.send_message(m.chat.id, "*Error :\t\t*YOURLS SERVER NOT REACHABLE; TRY AGAIN LATER", parse_mode='Markdown')


bot.polling(none_stop=True, timeout=3600)
