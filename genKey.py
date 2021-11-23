# -*- coding: utf-8 -*-
import telebot
import schedule
import time
import random
bot = telebot.TeleBot('2103396031:AAFGYJlt8VW_EbPKr8ECzKwUzlbONk1x8qo')
moderator_id = ['266415145']
keys = []

#1 - модератор
#2 - менеджер

with open(r"../managerBot/key.txt", "r") as file:
    for line in file:
        keys.append(line)
keys = [line.rstrip() for line in keys]

def getKey():
    keys[0] = str(random.randint(100000, 999999))
    keys[1] = str(random.randint(100000, 999999))
    with open(r"../managerBot/key.txt", "w") as file:
        for line in keys:
            file.write(line + '\n')
    file.close()

def sendKeyMessage():
    getKey()
    for id in moderator_id:
        bot.send_message(int(id), 'New keys:\n' + 'Moderator - ' + keys[0] + '\nManager - ' + keys[1])


schedule.every().day.at("10:00").do(sendKeyMessage)

while True:
    schedule.run_pending()
    time.sleep(60)

