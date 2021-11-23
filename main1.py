# -*- coding: utf-8 -*-
import telebot
from telebot import types

bot = telebot.TeleBot('')

lastPool = [6]

manager_list = []
moderator_list = []

pools = [[], [], [], [], []]
freePools = [[], [], [], [], []]


chatList = ['kek.com', 'eee.ru', 'wow.org']
poolsChat = [[], [], [], [], []]


for i in range(5):
    with open(r"../managerBot/pool" + str(i+1) + ".txt", "r") as file:
        for line in file:
            pools[i].append(line)
    pools[i] = [line.rstrip() for line in pools[i]]
    file.close()

for i in range(5):
    with open(r"../managerBot/pool" + str(i+1) + "free.txt", "r") as file:
        for line in file:
            freePools[i].append(line)
    freePools[i] = [line.rstrip() for line in freePools[i]]
    file.close()


with open(r"../managerBot/moderatorList.txt", "r") as file:
    for line in file:
        moderator_list.append(line)
moderator_list = [line.rstrip() for line in moderator_list]
file.close()

with open(r"../managerBot/managerList.txt", "r") as file:
    for line in file:
        manager_list.append(line)
manager_list = [line.rstrip() for line in manager_list]
file.close()



def check_all_database(id):
    return bool(manager_list.count(str(id))) or bool(moderator_list.count(str(id)))


@bot.message_handler(commands=['start'])
def start(message):
    markup_inline = types.InlineKeyboardMarkup()
    item_manager = types.InlineKeyboardButton(text='Manager', callback_data='manager')
    item_moderator = types.InlineKeyboardButton(text='Moderator', callback_data='moderator')
    markup_inline.add(item_manager)
    markup_inline.add(item_moderator)
    bot.send_message(message.chat.id, 'I am:', reply_markup=markup_inline)

def remove_values_from_list(the_list, val):
   return [value for value in the_list if value != val]

@bot.message_handler(commands=['delete'])
def delete(message):
    global moderator_list
    global manager_list
    global pools
    global freePools
    if check_all_database(message.chat.id) == False:
        bot.send_message(message.chat.id, 'You dont have created account. Create new: /start',
                         reply_markup=types.ReplyKeyboardRemove())
    else:
        if moderator_list.count(str(message.chat.id)) != 0:
             moderator_list = remove_values_from_list(moderator_list, str(message.chat.id))
        if manager_list.count(str(message.chat.id)) != 0:
            manager_list = remove_values_from_list(manager_list, str(message.chat.id))
        with open(r"../managerBot/managerList.txt", "w") as file:
            for line in manager_list:
                file.write(line + '\n')
        file.close()
        with open(r"../managerBot/moderatorList.txt", "w") as file:
            for line in moderator_list:
                file.write(line + '\n')
        file.close()
        poolNum = findInFreePool(str(message.chat.id))
        if poolNum:
            freePools[poolNum-1] = remove_values_from_list(freePools[poolNum-1], str(message.chat.id))
            with open(r"../managerBot/pool" + str(poolNum) + "free.txt", "w") as file:
                for line in freePools[poolNum - 1]:
                    file.write(line + '\n')
            file.close()
        poolNum = findInPool(str(message.chat.id))
        if poolNum:
            pools[poolNum - 1] = remove_values_from_list(pools[poolNum - 1], str(message.chat.id))
            with open(r"../managerBot/pool" + str(poolNum) + ".txt", "w") as file:
                for line in pools[poolNum - 1]:
                    file.write(line + '\n')
            file.close()
        bot.send_message(message.chat.id, 'Your account has been successfully deleted. To create an account - /start',
                         reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    global freePools
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Send a new task')
    if message.text == "/help":
        bot.send_message(message.chat.id, "To create an account - /start, delete - /delete")
    elif message.text == 'Send a new task':
        bot.send_message(message.chat.id, "Describe your task:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, createOrder_2)
    elif message.text == 'Do not accept tasks':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Get to work')
        bot.send_message(message.chat.id, "When you decide to return to work, click on the button", reply_markup=keyboard)
        poolNum = findInFreePool(str(message.chat.id))
        if poolNum:
            freePools[poolNum - 1] = remove_values_from_list(freePools[poolNum - 1], str(message.chat.id))
            with open(r"../managerBot/pool" + str(poolNum) + "free.txt", "w") as file:
                for line in freePools[poolNum - 1]:
                    file.write(line + '\n')
            file.close()
        else:
            bot.send_message(message.chat.id, "You can't leave work until you finish the assignment.",
                             reply_markup=keyboard)
    elif message.text == 'Get to work':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Do not accept tasks')
        poolNum = findInPool(str(message.chat.id))
        if freePools[poolNum-1].count(str(message.chat.id)) > 0:
            bot.send_message(message.chat.id, "You are already on the list of current managers")
        else:
            freePools[poolNum-1].append(str(message.chat.id))
            with open(r"../managerBot/pool" + str(poolNum) + "free.txt", "w") as file:
                for line in freePools[poolNum - 1]:
                    file.write(line + '\n')
            file.close()
            bot.send_message(message.chat.id, "Wait for the order", reply_markup=keyboard)
    else:
        bot.send_message(message.chat.id,
                         "I don't understand you. To create an account - /start, delete - /delete")


def registerManager(message):
    if checkKey('manager', message.text):
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Do not accept tasks')
        regInPool(message.chat.id)
        bot.send_message(message.chat.id, "Wait for the order", reply_markup=keyboard)
    else:
        sent = bot.send_message(message.chat.id, "Invalid code. Try again")
        bot.register_next_step_handler(sent, registerManager)


def checkKey(role, key):
    keys = []
    with open(r"../managerBot/key.txt", "r") as file:
        for line in file:
            keys.append(line)
    keys = [line.rstrip() for line in keys]
    file.close()
    if role == 'moderator':
        return key == keys[0]
    elif role == 'manager':
        return key == keys[1]
    else:
        return False


def regInPool(id):
    if lastPool[0] == 6:
        lastPool[0] = 1
    if findInPool(str(id)):
        bot.send_message(id, "You are already registered in the system.")
    else:
        pools[lastPool[0]-1].append(str(id))
        with open(r"../managerBot/pool" + str(lastPool[0]) + ".txt", "w") as file:
            for line in pools[lastPool[0]-1]:
                file.write(line + '\n')
        file.close()
    if findInFreePool(str(id)):
        bot.send_message(id, "You are already registered in the system.")
    else:
        freePools[lastPool[0]-1].append(str(id))
        with open(r"../managerBot/pool" + str(lastPool[0]) + "free.txt", "w") as file:
            for line in freePools[lastPool[0]-1]:
                file.write(line + '\n')
        file.close()
    if not check_all_database(id):
        manager_list.append(str(id))
        with open(r"../managerBot/managerList.txt", "w") as file:
            for line in manager_list:
                file.write(line + '\n')
        file.close()
    lastPool[0] += 1


def registerModerator(message):
    if checkKey('moderator', message.text):
        moderator_list.append(str(message.chat.id))
        with open(r"../managerBot/moderatorList.txt", "w") as file:
            for line in moderator_list:
                file.write(line + '\n')
        file.close()
        bot.send_message(message.chat.id, "Registration successful")
        moderatorMenu(message.chat.id)
    else:
        sent = bot.send_message(message.chat.id, "Invalid code. Try again")
        bot.register_next_step_handler(sent, registerModerator)


def moderatorMenu(id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Send a new task')
    sent = bot.send_message(id, "Create a new task by clicking on the button", reply_markup=keyboard)
    bot.register_next_step_handler(sent, createOrder_1)


def createOrder_1(message):
    mes = message.text
    if mes == 'Send a new task':
        bot.send_message(message.chat.id, "Describe your task:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, createOrder_2)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add('Send a new task')
        bot.send_message(message.chat.id, "To create a task, click on the button", reply_markup=keyboard)


def createOrder_2(message):
    task = message.text
    bot.send_message(message.chat.id, "Your task:\n" + task)
    keyboard, count = checkFreePool()
    if count > 0:
        sent = bot.send_message(message.chat.id, "Choose one of the free pools:", reply_markup=keyboard)
        bot.register_next_step_handler(sent, createOrder_3, task)
    else:
        bot.send_message(message.chat.id, "There are no free pools. Try again later")
        moderatorMenu(message.chat.id)


def checkFreePool():
    count = 0
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for i in range(5):
        if len(freePools[i]) >= 1:
            if i+1 == 1:
                keyboard.add('First pool')
                count += 1
            elif i+1 == 2:
                keyboard.add('Second pool')
                count += 1
            elif i+1 == 3:
                keyboard.add('Third pool')
                count += 1
            elif i+1 == 4:
                keyboard.add('Fourth pool')
                count += 1
            elif i+1 == 5:
                keyboard.add('Fifth pool')
                count += 1
    return keyboard, count


def createOrder_3(message, task):
    poolNum = message.text
    markup_inline = types.InlineKeyboardMarkup()
    item_take = types.InlineKeyboardButton(text='Take', callback_data='take_order')
    item_complete = types.InlineKeyboardButton(text='Completed', callback_data='completed_order')
    markup_inline.add(item_take)
    markup_inline.add(item_complete)
    if poolNum == 'First pool':
        tt = sendOrder(0, task)
    elif poolNum == 'Second pool':
        tt = sendOrder(1, task)
    elif poolNum == 'Third pool':
        tt = sendOrder(2, task)
    elif poolNum == 'Fourth pool':
        tt = sendOrder(3, task)
    elif poolNum == 'Fifth pool':
        tt = sendOrder(4, task)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add('Send a new task')
    bot.send_message(message.chat.id, tt, reply_markup=keyboard)
    moderatorMenu(message.chat.id)


def getChat(poolNum):
    sendChat = ''
    for chat in chatList:
        if poolsChat[poolNum - 1].count(chat) == 0:
            sendChat = chat
            break
    if sendChat == '':
        poolsChat[poolNum - 1].clear()
        return chatList[0]
    else:
        return sendChat


def sendOrder(poolNum, task):
    sendChat = getChat(poolNum)
    poolsChat[poolNum - 1].append(sendChat)
    markup_inline = types.InlineKeyboardMarkup()
    item_take = types.InlineKeyboardButton(text='Take', callback_data='take_order')
    item_complete = types.InlineKeyboardButton(text='Completed', callback_data='completed_order')
    markup_inline.add(item_take)
    markup_inline.add(item_complete)
    if len(freePools[poolNum]) >= 1:
        tt = 'Tasks sent to:\n'
        for id in freePools[poolNum]:
            bot.send_message(int(id), 'New task: \n' + task + '\nChat: ' + sendChat, reply_markup=markup_inline)
            tt += (id + '\n')
        tt += 'A chat is assigned: ' + sendChat
    else:
        tt = 'Unfortunately, there are no available managers. Try again later'
    return tt



@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global freePools
    if call.data == "manager":
        if check_all_database(call.message.chat.id) == False:
            sent = bot.send_message(call.message.chat.id, 'Please enter the access code:')
            bot.register_next_step_handler(sent, registerManager)
        else:
            bot.send_message(call.message.chat.id, "Delete your previous account using the /delete command")
        bot.answer_callback_query(call.id)

    elif call.data == "moderator":
        if check_all_database(call.message.chat.id) == False:
            sent = bot.send_message(call.message.chat.id, 'Please enter the access code:')
            bot.register_next_step_handler(sent, registerModerator)
        else:
            bot.send_message(call.message.chat.id, "Delete your previous account using the /delete command")
        bot.answer_callback_query(call.id)

    elif call.data == "take_order":
        poolNum = findInFreePool(str(call.message.chat.id))
        if poolNum:
            freePools[poolNum-1] = remove_values_from_list(freePools[poolNum - 1], str(call.message.chat.id))
            with open(r"../managerBot/pool" + str(poolNum) + "free.txt", "w") as file:
                for line in freePools[poolNum-1]:
                    file.write(line + '\n')
            file.close()
            bot.send_message(call.message.chat.id, "Great! After completing the task, do not forget to press the button.")
            bot.answer_callback_query(call.id)
        else:
            bot.send_message(call.message.chat.id,
                             "You can't take the assignment. Complete the previous task or click on the button that you are ready to accept tasks")

    elif call.data == "completed_order":
        poolNum = findInPool(str(call.message.chat.id))
        if freePools[poolNum-1].count(str(call.message.chat.id)) > 0:
            bot.send_message(call.message.chat.id, "You didn't take on the task")
        else:
            freePools[poolNum-1].append(str(call.message.chat.id))
            with open(r"../managerBot/pool" + str(poolNum) + "free.txt", "w") as file:
                for line in freePools[poolNum-1]:
                    file.write(line + '\n')
            file.close()
            bot.send_message(call.message.chat.id, "Super! Expect new tasks")
            bot.answer_callback_query(call.id)


def findInFreePool(id):
    for i in range(5):
        if freePools[i].count(id) >= 1:
            return i + 1


def findInPool(id):
    for i in range(5):
        if pools[i].count(id) >= 1:
            return i + 1


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)