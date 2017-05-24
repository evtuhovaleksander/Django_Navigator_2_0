from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from Navigator.sub_models import Building, Graph, WayBuilderClass
from Navigator.models import Dialogs, Point, HistoryPath
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ParseMode

import time

key_val = 1
pre_key = 'tmp_pic'
pre_path = './pic_dir/tmp_pic_dir/'

id_counter = 0
id_list = []
bots = {}

import logging

logging.basicConfig(filename='ex.log', level=logging.DEBUG)
master_logger = logging.getLogger('BotMaster')



def dg(id,user):
    if user.dialog_style == 1:
        return Dialogs.objects.get(id=id).style1
    if user.dialog_style == 2:
        return Dialogs.objects.get(id=id).style2
    if user.dialog_style == 3:
        return Dialogs.objects.get(id=id).style3


class BotChild_oldold:
    bot_id = -1
    dialog_id = -1
    dialog_state = -1
    dialog_style = 0
    telebot = None

    building = None
    wb = None

    from_id = -1
    to_id = -1
    detalization_level = 2

    def __init__(self, telebot, dialog_id, id_ind, way_builder_instance):
        self.telebot = telebot
        self.dialog_id = dialog_id
        self.dialog_state = 0
        self.dialog_style = 1
        self.bot_id = id_ind
        # logging.debug('init bot '+str(id))
        # logging.debug('request building')
        # self.building = Building.get_building()
        # logging.debug('init WB class')
        self.wb = way_builder_instance
        # logging.debug('config wb')
        self.wb.init_pre_count()

    def get_answer(self, input_string):

        # logging.debug('request amswer from bot '+str(self.bot_id))
        # logging.debug('request by string '+input_string)
        # logging.debug('bot in  state ' + str(self.dialog_state))

        if self.dialog_state == 0:
            self.send_message(Dialogs.get_dialog_item(0, 1))
            # self.send_message(Dialogs.get_dialog_item(8, 1))
            self.dialog_state = 1
            return

        if self.dialog_state == 1:
            if int(input_string) in (1, 3):
                self.dialog_style = int(input_string)
                self.send_message(Dialogs.get_dialog_item(1, self.dialog_style))
                self.send_message(Dialogs.get_dialog_item(2, self.dialog_style))
                self.send_message(Dialogs.get_dialog_item(3, self.dialog_style))
                # self.send_photo('all.jpeg')
                self.send_message(Dialogs.get_dialog_item(4, self.dialog_style))
                self.dialog_state = 2
            else:
                self.send_message(Dialogs.get_dialog_item(5, self.dialog_style))
            return

        if self.dialog_state == 2:
            self.from_id = Point.get_id(input_string)
            self.send_message(Dialogs.get_dialog_item(6, self.dialog_style))
            # self.send_message(Dialogs.get_dialog_item(7, self.dialog_style))
            self.dialog_state = 3
            return

        if self.dialog_state == 3:
            self.to_id = Point.get_id(input_string)
            self.send_message(Dialogs.get_dialog_item(7, self.dialog_style))
            self.send_message(Dialogs.get_dialog_item(8, self.dialog_style))
            self.dialog_state = 4
            return

        if self.dialog_state == 4:
            out_style = int(input_string)
            path = self.wb.request_path(self.from_id, self.to_id)  #
            for i in range(len(path.points)):
                self.send_message(path.points[i].name)
                if 1 < out_style:
                    if i < len(path.connections):
                        self.send_message(str(path.connections[i].connection_comment))
            if out_style == 3:
                for i in path.floors_obj:
                    pic_path = path.floors_obj[i].picture_path
                    self.send_photo(pic_path)
            return

    def send_message(self, text):
        # logging.debug('bot ' + str(self.bot_id)+' sending text:'+text)
        self.telebot.send_message(self.dialog_id,
                                  text)

    def send_photo(self, path):
        # logging.debug('bot ' + str(self.bot_id) + ' sending photo:' + path)
        self.telebot.send_photo(self.dialog_id, open(path, 'rb'))


class BotChild_old:
    bot_id = -1
    dialog_id = -1
    dialog_state = -1
    dialog_style = 0
    telebot = None

    building = None
    wb = None

    from_id = -1
    to_id = -1
    detalization_level = 2

    def __init__(self, telebot, dialog_id, id_ind, way_builder_instance):
        self.telebot = telebot
        self.dialog_id = dialog_id
        self.dialog_state = 0
        self.dialog_style = 1
        self.bot_id = id_ind
        # logging.debug('init bot '+str(id))
        # logging.debug('request building')
        # self.building = Building.get_building()
        # logging.debug('init WB class')
        self.wb = way_builder_instance
        # logging.debug('config wb')
        self.wb.init_pre_count()

    def get_answer(self, input_string):

        # logging.debug('request amswer from bot '+str(self.bot_id))
        # logging.debug('request by string '+input_string)
        # logging.debug('bot in  state ' + str(self.dialog_state))

        if self.dialog_state == 0:
            self.send_message('get style')
            self.send_message('send keyboard')
            self.dialog_state = 1
            return

        if self.dialog_state == 1:
            if int(input_string) in (1, 3):
                self.dialog_style = int(input_string)
                self.send_message('greet')
                self.send_message('ask for route point 1')
                self.send_message('change keyboard to new way change style')
                self.dialog_state = 2
            else:
                self.send_message('eror choosing style message')
            return

        if self.dialog_state == 2:
            id = Point.get_id(input_string)
            if id == -1:
                self.send_message('eror no such a point')
            else:
                self.from_id = id
                self.send_message('point1 - ok')
                self.send_message('ask for 2nd point')
                self.dialog_state = 3
            return

        if self.dialog_state == 3:
            id = Point.get_id(input_string)
            if id == -1:
                self.send_message('eror no such a point')
            else:
                self.to_id = id
                self.send_message('point2 - ok')
                self.send_message('wait for route')
                self.dialog_state = 4

                path = self.wb.request_path(self.from_id, self.to_id)

                prev_inst_id = path.connections[0].instance.id
                cur_instance = 0
                for i in range(len(path.points)):
                    self.send_message(path.points[i].name)
                    if i < len(path.connections):
                        self.send_message(str(path.connections[i].connection_comment))

                        if path.connections[i].trans_instance_marker:
                            pic_path = path.floors_obj[prev_inst_id].picture_path
                            self.send_photo(pic_path)
                        else:
                            prev_inst_id = path.connections[i].instance.id
                            # for i in path.floors_obj:
                            #    pic_path = path.floors_obj[i].picture_path
                            #    self.send_photo(pic_path)
                pic_path = path.floors_obj[prev_inst_id].picture_path
                self.send_photo(pic_path)
                self.send_message('write something to new path')
                self.dialog_state = 4
            return

        if self.dialog_state == 4:
            self.send_message('get point 1')
            self.dialog_state = 1
            return
        if self.dialog_state == 5:
            # wait for new route or change style
            return

    def send_message(self, text):
        # logging.debug('bot ' + str(self.bot_id)+' sending text:'+text)
        self.telebot.send_message(self.dialog_id,
                                  text)

    def send_photo(self, path):
        # logging.debug('bot ' + str(self.bot_id) + ' sending photo:' + path)
        self.telebot.send_photo(self.dialog_id, open(path, 'rb'))


class BotChild:
    bot_id = -1
    dialog_id = -1
    dialog_state = -1
    dialog_style = 0
    telebot = None

    building = None
    wb = None

    from_id = -1
    to_id = -1
    detalization_level = 2
    logger = None

    @staticmethod
    def get_keyboard_for_change_style():
        keyboard = [
            ['Формальный'],
            ['Для друзей'],
            ['Для братишек', ]
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_keyboard():
        keyboard = [
            ['Построить маршрут', 'Сменить стиль диалога']
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    def __init__(self, telebot, dialog_id, id_ind, way_builder_instance):

        self.logger = logging.getLogger('BotChild' + str(id_ind))

        self.telebot = telebot
        self.dialog_id = dialog_id
        self.dialog_state = 0
        self.dialog_style = 1
        self.bot_id = id_ind
        self.logger.debug('init bot ' + str(id))
        self.logger.debug('request building')
        self.logger.debug('init WB class')
        self.wb = way_builder_instance
        self.logger.debug('config wb')
        self.wb.init_pre_count()

    def get_answer(self, input_string):

        self.logger.debug('request amswer from bot ' + str(self.bot_id))
        self.logger.debug('request by string ' + input_string)
        self.logger.debug('bot in  state ' + str(self.dialog_state))
        if input_string == 'Построить маршрут' or input_string == 'Сменить стиль диалога':
            if input_string == 'Сменить стиль диалога':
                self.send_message_with_keyboard('get style', self.get_keyboard_for_change_style())
                self.dialog_state = 1
                return
            if input_string == 'Построить маршрут':
                self.send_message('ask for route point 1')
                self.dialog_state = 2
                return

        if self.dialog_state == 0:
            self.send_message_with_keyboard('get style', self.get_keyboard_for_change_style())

            self.dialog_state = 1
            return

        if self.dialog_state == 1:
            if input_string == 'Формальный' or input_string == 'Для друзей' or input_string == 'Для братишек':

                if input_string == 'Формальный': self.dialog_style = 1;
                if input_string == 'Для друзей': self.dialog_style = 2;
                if input_string == 'Для братишек': self.dialog_style = 3;
                self.send_message_with_keyboard('change is registered', self.get_keyboard())
                self.send_message('greet')
                self.dialog_state = 5
            else:
                self.send_message('eror choosing style message')
            return

        if self.dialog_state == 2:
            id = Point.get_id(input_string)
            if id == -1:
                self.send_message('eror no such a point')
            else:
                self.from_id = id
                self.send_message('point1 - ok')
                self.send_message('ask for 2nd point')
                self.dialog_state = 3
            return

        if self.dialog_state == 3:
            id = Point.get_id(input_string)
            if id == -1:
                self.send_message('eror no such a point')
            else:
                self.to_id = id
                self.send_message('point2 - ok')
                self.send_message('wait for route')

                path = self.wb.request_path(self.from_id, self.to_id)

                prev_inst_id = path.connections[0].instance.id

                message = ''
                for i in range(len(path.points)):
                    # if not path.points[i].hidden:
                    #    message+='\n'+path.points[i].name

                    if i < len(path.connections):
                        message += '\n' + str(path.connections[i].connection_comment)
                        if not path.points[i].hidden:
                            message += ' ' + path.points[i].name
                        if path.connections[i].trans_instance_marker:
                            self.send_message(message)
                            pic_path = path.floors_obj[prev_inst_id].picture_path
                            self.send_photo(pic_path)
                            message = ''
                        else:
                            prev_inst_id = path.connections[i].instance.id
                message += '\n ' + path.points[len(path.points) - 1].name
                self.send_message(message)
                pic_path = path.floors_obj[prev_inst_id].picture_path
                self.send_photo(pic_path)

                self.send_message('going to wait state')
                self.dialog_state = 5
            return

        if self.dialog_state == 4:
            self.send_message('get point 1')
            self.dialog_state = 2
            return
        if self.dialog_state == 5:
            # wait for new route or change style
            if input_string == 'Построить маршрут' or input_string == 'Сменить стиль диалога':
                if input_string == 'Сменить стиль диалога':
                    self.send_message_with_keyboard('get style', self.get_keyboard_for_change_style())
                    self.dialog_state = 1
                    return
                if input_string == 'Построить маршрут':
                    self.send_message('ask for route point 1')
                    # self.send_message('change keyboard to new way change style')
                    self.dialog_state = 2
                    return

            else:
                self.send_message('dont understand')
            return

    def send_message(self, text):
        self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)
        self.telebot.send_message(self.dialog_id,
                                  text)

    def send_message_clear_keyboard(self, text):
        self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)

        keyboard = [
        ]
        keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

        self.telebot.sendMessage(chat_id=self.dialog_id, text=text, reply_markup=keyboard, disable_notification=False,
                                 disable_web_page_prewview=True)

    def send_message_with_keyboard(self, text, keyboard):
        self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)

        self.telebot.sendMessage(chat_id=self.dialog_id, text=text,
                                 reply_markup=keyboard, disable_notification=False, disable_web_page_prewview=True)
        # self.telebot.send_message(self.dialog_id,
        #                          text,keyboard)

    def send_photo(self, path):
        self.logger.debug('bot ' + str(self.bot_id) + ' sending photo:' + path)
        self.telebot.send_photo(self.dialog_id, open(path, 'rb'))


class BotChild_super_old_old:
    @staticmethod
    def get_keyboard_for_change_style():
        keyboard = [
            ['Формальный'],
            ['Для друзей'],
            ['Для братишек', ]
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_keyboard():
        keyboard = [
            ['Построить маршрут', 'Сменить стиль диалога']
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_answer(input_string, user, wb,bot):


        logger = logging.getLogger('tmp BotChild')
        logger.debug('request amswer from bot ')
        logger.debug('request by string ' + input_string)
        logger.debug('bot in  state ' + str(user.dialog_state))

        if input_string == 'Построить маршрут' or input_string == 'Сменить стиль диалога':
            if input_string == 'Сменить стиль диалога':
                BotChild_super.send_message_with_keyboard(bot,user,'get style', BotChild_super.get_keyboard_for_change_style())
                user.dialog_state = 1
                user.save()
                return

            if input_string == 'Построить маршрут':
                BotChild_super.send_message(bot,user,'ask for route point 1')
                user.dialog_state = 2
                user.save()
                return

        if user.dialog_state == 0:
            BotChild_super.send_message_with_keyboard(bot,user,'get style', BotChild_super.get_keyboard_for_change_style())

            user.dialog_state = 1
            user.save()

            return

        if user.dialog_state == 1:
            if input_string == 'Формальный' or input_string == 'Для друзей' or input_string == 'Для братишек':

                if input_string == 'Формальный': user.dialog_style = 1;
                if input_string == 'Для друзей': user.dialog_style = 2;
                if input_string == 'Для братишек': user.dialog_style = 3;
                BotChild_super.send_message_with_keyboard(bot,user,'change is registered', BotChild_super.get_keyboard())
                BotChild_super.send_message(bot,user,'greet')
                user.dialog_state = 5
                user.save()
            else:
                BotChild_super.send_message(bot,user,'eror choosing style message')
            return

        if user.dialog_state == 2:
            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,'eror no such a point')
            else:
                user.from_id = id
                BotChild_super.send_message(bot,user,'point1 - ok')
                BotChild_super.send_message(bot,user,'ask for 2nd point')
                user.dialog_state = 3
                user.save()
            return

        if user.dialog_state == 3:
            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,'eror no such a point')
            else:
                user.to_id = id
                BotChild_super.send_message(bot,user,'point2 - ok')
                BotChild_super.send_message(bot,user,'wait for route')
                user.save()

                path = wb.request_path(user.from_id, user.to_id)

                prev_inst_id = path.connections[0].instance.id

                message = ''
                for i in range(len(path.points)):
                    # if not path.points[i].hidden:
                    #    message+='\n'+path.points[i].name

                    if i < len(path.connections):
                        message += '\n' + str(path.connections[i].connection_comment)
                        if not path.points[i].hidden:
                            message += ' ' + path.points[i].name
                        if path.connections[i].trans_instance_marker:
                            BotChild_super.send_message(bot,user,message)
                            pic_path = path.floors_obj[prev_inst_id].picture_path
                            BotChild_super.send_photo(bot,user,pic_path)
                            message = ''
                        else:
                            prev_inst_id = path.connections[i].instance.id
                message += '\n ' + path.points[len(path.points) - 1].name
                BotChild_super.send_message(bot,user,message)
                pic_path = path.floors_obj[prev_inst_id].picture_path
                BotChild_super.send_photo(bot,user,pic_path)

                BotChild_super.send_message(bot,user,'going to wait state')
                user.dialog_state = 5
                user.save()
            return

        if user.dialog_state == 5:
            # wait for new route or change style
            if input_string == 'Построить маршрут' or input_string == 'Сменить стиль диалога':
                if input_string == 'Сменить стиль диалога':
                    BotChild_super.send_message_with_keyboard(bot,user,'get style', BotChild_super.get_keyboard_for_change_style())
                    user.dialog_state = 1
                    user.save()
                    return
                if input_string == 'Построить маршрут':
                    BotChild_super.send_message(bot,user,'ask for route point 1')
                    # self.send_message('change keyboard to new way change style')
                    user.dialog_state = 2
                    user.save()
                    return

            else:
                BotChild_super.send_message(bot,user,'dont understand')
            return

    @staticmethod
    def send_message(bot, user, text):
        # self.logger.debug('bot ' + str(self.bot_id)+' sending text:'+text)
        bot.sendMessage(chat_id=user.user_telegram_id, text=text, disable_notification=False,
                        disable_web_page_prewview=True)

    @staticmethod
    def send_message_clear_keyboard(bot, user, text):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)

        keyboard = [
        ]
        keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

        bot.sendMessage(chat_id=user.user_telegram_id, text=text, reply_markup=keyboard, disable_notification=False,
                        disable_web_page_prewview=True)

    @staticmethod
    def send_message_with_keyboard(bot, user, text, keyboard):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)

        bot.sendMessage(chat_id=user.user_telegram_id, text=text,
                        reply_markup=keyboard, disable_notification=False, disable_web_page_prewview=True)
        # self.telebot.send_message(self.dialog_id,
        #                          text,keyboard)

    def send_photo(bot, user, path):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending photo:' + path)
        bot.send_photo(user.user_telegram_id, open(path, 'rb'))

class BotChild_super_old:
    @staticmethod
    def get_keyboard_for_change_style():
        keyboard = [
            ['Формальный'],
            ['Для друзей'],
            ['Для братишек', ]
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_keyboard():
        keyboard = [
            ['Построить маршрут', 'Посмотреть избранные маршруты'],['Сменить стиль диалога']
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_keyboard_for_fav_mode():
        keyboard = [
            ['Создать новый избранный путь', 'Вернуться в режим ожидания']
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_keyboard_for_cancel():
        keyboard = [
            ['Отмена']
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)


    @staticmethod
    def make_message_from_path(path,user):
        text = dg(0,user) + path.point1.name + '\n' + dg(1,user) + path.point2.name
        return text

    @staticmethod
    def send_fav_paths(bot,user):
        keyboard = BotChild_super.get_keyboard_for_fav_mode()
        BotChild_super.send_message_with_keyboard(bot, user, dg(2,user), keyboard)

        # send fav paths
        #try:
        paths = HistoryPath.objects.filter(telegram_user_id=user.user_telegram_id)
        #except Exception as ex:
        #    print(ex)

        for path in paths:
            keyboard = [[InlineKeyboardButton("Построить", callback_data=str(str(path.id) + '#^*_1')),
                         InlineKeyboardButton("Удалить", callback_data=str(str(path.id) + '#^*_0'))]]
            keyboard = InlineKeyboardMarkup(keyboard)
            text = BotChild_super.make_message_from_path(path,user)
            BotChild_super.send_message_with_keyboard(bot, user, text, keyboard)

        user.dialog_state = 6
        user.save()

    @staticmethod
    def build_and_send_path(bot,user,wb):
        keyboard = BotChild_super.get_keyboard()
        BotChild_super.send_message_with_keyboard(bot, user, dg(3,user),keyboard)
        user.save()

        path = wb.request_path(user.from_id, user.to_id)

        prev_inst_id = path.connections[0].instance.id

        message = ''
        for i in range(len(path.points)):

            if i < len(path.connections):
                message += '\n' + str(path.connections[i].connection_comment)
                if not path.points[i].hidden:
                    message += ' ' + path.points[i].name
                if path.connections[i].trans_instance_marker:
                    BotChild_super.send_message(bot, user, message)
                    pic_path = path.floors_obj[prev_inst_id].picture_path
                    BotChild_super.send_photo(bot, user, pic_path)
                    message = ''
                else:
                    prev_inst_id = path.connections[i].instance.id
        message += '\n ' + path.points[len(path.points) - 1].name
        BotChild_super.send_message(bot, user, message)
        pic_path = path.floors_obj[prev_inst_id].picture_path
        BotChild_super.send_photo(bot, user, pic_path)

        BotChild_super.send_message(bot, user, dg(4,user))
        user.dialog_state = 5
        user.save()

    @staticmethod
    def get_answer(input_string, user, wb,bot):


        logger = logging.getLogger('tmp BotChild')
        logger.debug('request amswer from bot ')
        logger.debug('request by string ' + input_string)
        logger.debug('bot in  state ' + str(user.dialog_state))

        if input_string == 'Построить маршрут' or input_string == 'Сменить стиль диалога' or input_string == 'Посмотреть избранные маршруты':
            if input_string == 'Сменить стиль диалога':
                BotChild_super.send_message_with_keyboard(bot,user,dg(5,user), BotChild_super.get_keyboard_for_change_style())
                user.dialog_state = 1
                user.save()
                return

            if input_string == 'Построить маршрут':
                BotChild_super.send_message(bot,user,dg(6,user))
                user.dialog_state = 2
                user.save()
                return
            if input_string == 'Посмотреть избранные маршруты':
                BotChild_super.send_fav_paths(bot,user)
                #keyboard = BotChild_super.get_keyboard_for_fav_mode()
                #BotChild_super.send_message_with_keyboard(bot, user, 'enter favorite path mode',keyboard)
#
                ##send fav paths
                #paths = HistoryPath.objects.filter(telegram_user=user)
                #for path in paths:
                #    keyboard = [[InlineKeyboardButton("build", callback_data=str(str(path.id) + '#^*_1')),
                #        InlineKeyboardButton("delete", callback_data=str(str(path.id) + '#^*_0'))]]
                #    text='From '+path.point1.name+'\n'+'To '+path.point2.name
                #    BotChild_super.send_message_with_keyboard(bot,user,text,keyboard)
#
                #user.dialog_state = 6
                #user.save()
                return

        if user.dialog_state == 0:
            BotChild_super.send_message_with_keyboard(bot,user,dg(5,user), BotChild_super.get_keyboard_for_change_style())

            user.dialog_state = 1
            user.save()

            return

        if user.dialog_state == 1:
            if input_string == 'Формальный' or input_string == 'Для друзей' or input_string == 'Для братишек':

                if input_string == 'Формальный': user.dialog_style = 1;
                if input_string == 'Для друзей': user.dialog_style = 2;
                if input_string == 'Для братишек': user.dialog_style = 3;
                BotChild_super.send_message_with_keyboard(bot,user,dg(7,user), BotChild_super.get_keyboard())
                BotChild_super.send_message(bot,user,dg(8,user))
                user.dialog_state = 5
                user.save()
            else:
                BotChild_super.send_message(bot,user,dg(9,user))
            return

        if user.dialog_state == 2:
            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,dg(10,user))
            else:
                user.from_id = id
                BotChild_super.send_message(bot,user,dg(11,user))
                BotChild_super.send_message(bot,user,dg(12,user))
                user.dialog_state = 3
                user.save()
            return

        if user.dialog_state == 3:
            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,dg(10,user))
            else:
                user.to_id = id
                BotChild_super.send_message(bot,user,dg(13,user))
                user.save()
                BotChild_super.build_and_send_path(bot,user,wb)
                #BotChild_super.send_message(bot,user,'wait for route')
                #user.save()
#
                #path = wb.request_path(user.from_id, user.to_id)
#
                #prev_inst_id = path.connections[0].instance.id
#
                #message = ''
                #for i in range(len(path.points)):
#
                #    if i < len(path.connections):
                #        message += '\n' + str(path.connections[i].connection_comment)
                #        if not path.points[i].hidden:
                #            message += ' ' + path.points[i].name
                #        if path.connections[i].trans_instance_marker:
                #            BotChild_super.send_message(bot,user,message)
                #            pic_path = path.floors_obj[prev_inst_id].picture_path
                #            BotChild_super.send_photo(bot,user,pic_path)
                #            message = ''
                #        else:
                #            prev_inst_id = path.connections[i].instance.id
                #message += '\n ' + path.points[len(path.points) - 1].name
                #BotChild_super.send_message(bot,user,message)
                #pic_path = path.floors_obj[prev_inst_id].picture_path
                #BotChild_super.send_photo(bot,user,pic_path)
#
                #BotChild_super.send_message(bot,user,'going to wait state')
                #user.dialog_state = 5
                #user.save()
            return

        if user.dialog_state == 5:

#            # wait for new route or change style
#            if input_string == 'Построить маршрут' or input_string == 'Сменить стиль диалога':
#                if input_string == 'Сменить стиль диалога':
#                    BotChild_super.send_message_with_keyboard(bot,user,'get style', BotChild_super.get_keyboard_for_change_style())
#                    user.dialog_state = 1
#                    user.save()
#                    return
#                if input_string == 'Построить маршрут':
#                    BotChild_super.send_message(bot,user,'ask for route point 1')
#                    # self.send_message('change keyboard to new way change style')
#                    user.dialog_state = 2
#                    user.save()
#                    return

            #else:
            BotChild_super.send_message(bot,user,dg(14,user))
            return

        if user.dialog_state == 6:
            if input_string == 'Вернуться в режим ожидания' or input_string == 'Создать новый избранный путь':
                if input_string == 'Вернуться в режим ожидания':
                    keyboard=BotChild_super.get_keyboard()
                    BotChild_super.send_message_with_keyboard(bot, user, dg(4,user),keyboard)
                    return
                if input_string == 'Создать новый избранный путь':
                    keyboard = BotChild_super.get_keyboard_for_cancel()
                    BotChild_super.send_message_with_keyboard(bot, user,dg(6,user), keyboard)
                    user.dialog_state = 7
                    user.save()
                    return


        if user.dialog_state == 7:

            if input_string == 'Отмена':
                keyboard = BotChild_super.get_keyboard_for_fav_mode()
                BotChild_super.send_message_with_keyboard(bot, user, dg(17,user), keyboard)
                BotChild_super.send_fav_paths(bot, user)
                return



            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,dg(10,user))
            else:
                user.from_id = id
                BotChild_super.send_message(bot,user,dg(11,user))
                BotChild_super.send_message(bot,user,dg(12,user))
                user.dialog_state = 8
                user.save()
            return

        if user.dialog_state == 8:

            if input_string == 'Отмена':
                keyboard = BotChild_super.get_keyboard_for_fav_mode()
                BotChild_super.send_message_with_keyboard(bot, user, dg(17,user), keyboard)
                BotChild_super.send_fav_paths(bot, user)
                return


            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,dg(10,user))
            else:
                user.to_id = id
                BotChild_super.send_message(bot,user,dg(13,user))
                user.save()

                HistoryPath.objects.get_or_create(telegram_user_id=user.user_telegram_id,point1=Point.objects.get(id=user.from_id),point2=Point.objects.get(id=user.to_id))
                #path = HistoryPath()
                #path.telegram_user=user
                ##path.point1=Point.objects.get(id=user.from_id)
                #path.point2 = Point.objects.get(id=user.to_id)
                #path.save()
                keyboard = BotChild_super.get_keyboard_for_fav_mode()
                BotChild_super.send_message_with_keyboard(bot,user,dg(16,user),keyboard)
                BotChild_super.send_fav_paths(bot,user)

    @staticmethod
    def send_message(bot, user, text):
        # self.logger.debug('bot ' + str(self.bot_id)+' sending text:'+text)
        bot.sendMessage(chat_id=user.user_telegram_id, text=text, disable_notification=False,
                        disable_web_page_prewview=True)

    @staticmethod
    def send_message_clear_keyboard(bot, user, text):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)

        keyboard = [
        ]
        keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

        bot.sendMessage(chat_id=user.user_telegram_id, text=text, reply_markup=keyboard, disable_notification=False,
                        disable_web_page_prewview=True)

    @staticmethod
    def send_message_with_keyboard(bot, user, text, keyboard):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)

        bot.sendMessage(chat_id=user.user_telegram_id, text=text,
                        reply_markup=keyboard, disable_notification=False, disable_web_page_prewview=True)
        # self.telebot.send_message(self.dialog_id,
        #                          text,keyboard)

    def send_photo(bot, user, path):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending photo:' + path)
        bot.send_photo(user.user_telegram_id, open(path, 'rb'))

class BotChild_super:
    @staticmethod
    def get_keyboard_for_change_style():
        keyboard = [
            ['Формальный'],
            ['Для друзей'],
            ['Для братишек', ]
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_keyboard():
        keyboard = [
            ['Построить маршрут', 'Посмотреть избранные маршруты'],['Показать карту здания'],['Сменить стиль диалога']
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_keyboard_for_fav_mode():
        keyboard = [
            ['Создать новый избранный путь', 'Вернуться в режим ожидания']
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

    @staticmethod
    def get_keyboard_for_cancel():
        keyboard = [
            ['Отмена']
        ]
        return ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)


    @staticmethod
    def make_message_from_path(path,user):
        text = dg(0,user) + path.point1.name + '\n' + dg(1,user) + path.point2.name
        return text

    @staticmethod
    def send_fav_paths(bot,user):
        keyboard = BotChild_super.get_keyboard_for_fav_mode()
        BotChild_super.send_message_with_keyboard(bot, user, dg(2,user), keyboard)

        # send fav paths
        #try:
        paths = HistoryPath.objects.filter(telegram_user_id=user.user_telegram_id)
        #except Exception as ex:
        #    print(ex)

        for path in paths:
            keyboard = [[InlineKeyboardButton("Построить", callback_data=str(str(path.id) + '#^*_1')),
                         InlineKeyboardButton("Удалить", callback_data=str(str(path.id) + '#^*_0'))]]
            keyboard = InlineKeyboardMarkup(keyboard)
            text = BotChild_super.make_message_from_path(path,user)
            BotChild_super.send_message_with_keyboard(bot, user, text, keyboard)

        user.dialog_state = 6
        user.save()

    @staticmethod
    def build_and_send_path(bot,user,wb):
        keyboard = BotChild_super.get_keyboard()
        BotChild_super.send_message_with_keyboard(bot, user, dg(3,user),keyboard)
        user.save()

        path = wb.request_path(user.from_id, user.to_id)

        prev_inst_id = path.connections[0].instance.id

        message = ''
        for i in range(len(path.points)):

            if i < len(path.connections):
                message += '\n' + str(path.connections[i].connection_comment)
                if not path.points[i].hidden:
                    message += ' ' + path.points[i].name
                if path.connections[i].trans_instance_marker:
                    BotChild_super.send_message(bot, user, message)
                    pic_path = path.floors_obj[prev_inst_id].picture_path
                    BotChild_super.send_photo(bot, user, pic_path)
                    message = ''
                else:
                    prev_inst_id = path.connections[i].instance.id
        message += '\n ' + path.points[len(path.points) - 1].name
        BotChild_super.send_message(bot, user, message)
        pic_path = path.floors_obj[prev_inst_id].picture_path
        BotChild_super.send_photo(bot, user, pic_path)

        BotChild_super.send_message(bot, user, dg(4,user))
        user.dialog_state = 5
        user.save()

    @staticmethod
    def get_answer(input_string, user, wb,bot):


        logger = logging.getLogger('tmp BotChild')
        logger.debug('request amswer from bot ')
        logger.debug('request by string ' + input_string)
        logger.debug('bot in  state ' + str(user.dialog_state))

        if input_string == 'Построить маршрут' or input_string == 'Сменить стиль диалога' or input_string == 'Посмотреть избранные маршруты'or input_string == 'Показать карту здания':
            if input_string == 'Показать карту здания':
                BotChild_super.send_message(bot, user, dg(23, user))
                for instance in main_way_builder_instance.building.floors:
                    try:
                        BotChild_super.send_message(bot,user,instance.inst_name)
                    except Exception as ex:
                        print(ex)
                    BotChild_super.send_photo(bot,user,instance.path)




               #BotChild_super.send_message_with_keyboard(bot,user,dg(5,user), BotChild_super.get_keyboard_for_change_style())

                return

            if input_string == 'Сменить стиль диалога':
                BotChild_super.send_message_with_keyboard(bot,user,dg(5,user), BotChild_super.get_keyboard_for_change_style())
                user.dialog_state = 1
                user.save()
                return

            if input_string == 'Построить маршрут':
                BotChild_super.send_message_with_keyboard(bot,user,dg(6,user),BotChild_super.get_keyboard_for_cancel())
                user.dialog_state = 2
                user.save()
                return
            if input_string == 'Посмотреть избранные маршруты':
                BotChild_super.send_fav_paths(bot,user)
                #keyboard = BotChild_super.get_keyboard_for_fav_mode()
                #BotChild_super.send_message_with_keyboard(bot, user, 'enter favorite path mode',keyboard)
#
                ##send fav paths
                #paths = HistoryPath.objects.filter(telegram_user=user)
                #for path in paths:
                #    keyboard = [[InlineKeyboardButton("build", callback_data=str(str(path.id) + '#^*_1')),
                #        InlineKeyboardButton("delete", callback_data=str(str(path.id) + '#^*_0'))]]
                #    text='From '+path.point1.name+'\n'+'To '+path.point2.name
                #    BotChild_super.send_message_with_keyboard(bot,user,text,keyboard)
#
                #user.dialog_state = 6
                #user.save()
                return

        if user.dialog_state == 0:
            BotChild_super.send_message_with_keyboard(bot,user,dg(5,user), BotChild_super.get_keyboard_for_change_style())

            user.dialog_state = 1
            user.save()

            return

        if user.dialog_state == 1:
            if input_string == 'Формальный' or input_string == 'Для друзей' or input_string == 'Для братишек':

                if input_string == 'Формальный':
                    user.dialog_style = 1
                if input_string == 'Для друзей':
                    user.dialog_style = 2
                if input_string == 'Для братишек':
                    user.dialog_style = 3
                user.save()
                BotChild_super.send_message_with_keyboard(bot,user,dg(7,user), BotChild_super.get_keyboard())
                BotChild_super.send_message(bot,user,dg(8,user))
                user.dialog_state = 5
                user.save()
            else:
                BotChild_super.send_message(bot,user,dg(9,user))
            return

        if user.dialog_state == 2:
            if input_string == "Отмена":
                user.dialog_state = 5
                user.save()
                BotChild_super.send_message_with_keyboard(bot,user,dg(22,user),BotChild_super.get_keyboard())
                return
            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,dg(10,user))
            else:
                user.from_id = id
                BotChild_super.send_message(bot,user,dg(11,user))
                BotChild_super.send_message(bot,user,dg(12,user))
                user.dialog_state = 3
                user.save()
            return

        if user.dialog_state == 3:
            if input_string == "Отмена":
                user.dialog_state = 5
                user.save()
                BotChild_super.send_message_with_keyboard(bot,user,dg(22,user),BotChild_super.get_keyboard())
                return




            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,dg(10,user))
            else:
                user.to_id = id
                if user.to_id == user.from_id:
                    user.dialog_state = 5
                    user.save()
                    BotChild_super.send_message_with_keyboard(bot,user,dg(21,user),BotChild_super.get_keyboard())
                    return

                BotChild_super.send_message(bot,user,dg(13,user))
                user.save()
                BotChild_super.build_and_send_path(bot,user,wb)
                #BotChild_super.send_message(bot,user,'wait for route')
                #user.save()
#
                #path = wb.request_path(user.from_id, user.to_id)
#
                #prev_inst_id = path.connections[0].instance.id
#
                #message = ''
                #for i in range(len(path.points)):
#
                #    if i < len(path.connections):
                #        message += '\n' + str(path.connections[i].connection_comment)
                #        if not path.points[i].hidden:
                #            message += ' ' + path.points[i].name
                #        if path.connections[i].trans_instance_marker:
                #            BotChild_super.send_message(bot,user,message)
                #            pic_path = path.floors_obj[prev_inst_id].picture_path
                #            BotChild_super.send_photo(bot,user,pic_path)
                #            message = ''
                #        else:
                #            prev_inst_id = path.connections[i].instance.id
                #message += '\n ' + path.points[len(path.points) - 1].name
                #BotChild_super.send_message(bot,user,message)
                #pic_path = path.floors_obj[prev_inst_id].picture_path
                #BotChild_super.send_photo(bot,user,pic_path)
#
                #BotChild_super.send_message(bot,user,'going to wait state')
                #user.dialog_state = 5
                #user.save()
            return

        if user.dialog_state == 5:

#            # wait for new route or change style
#            if input_string == 'Построить маршрут' or input_string == 'Сменить стиль диалога':
#                if input_string == 'Сменить стиль диалога':
#                    BotChild_super.send_message_with_keyboard(bot,user,'get style', BotChild_super.get_keyboard_for_change_style())
#                    user.dialog_state = 1
#                    user.save()
#                    return
#                if input_string == 'Построить маршрут':
#                    BotChild_super.send_message(bot,user,'ask for route point 1')
#                    # self.send_message('change keyboard to new way change style')
#                    user.dialog_state = 2
#                    user.save()
#                    return

            #else:
            BotChild_super.send_message(bot,user,dg(14,user))
            return

        if user.dialog_state == 6:
            if input_string == 'Вернуться в режим ожидания' or input_string == 'Создать новый избранный путь':
                if input_string == 'Вернуться в режим ожидания':
                    keyboard=BotChild_super.get_keyboard()
                    BotChild_super.send_message_with_keyboard(bot, user, dg(4,user),keyboard)
                    return
                if input_string == 'Создать новый избранный путь':
                    keyboard = BotChild_super.get_keyboard_for_cancel()
                    BotChild_super.send_message_with_keyboard(bot, user,dg(6,user), keyboard)
                    user.dialog_state = 7
                    user.save()
                    return
            else:
                BotChild_super.send_message(bot,user,text=dg(19, user))



        if user.dialog_state == 7:

            if input_string == 'Отмена':
                keyboard = BotChild_super.get_keyboard_for_fav_mode()
                BotChild_super.send_message_with_keyboard(bot, user, dg(17,user), keyboard)
                BotChild_super.send_fav_paths(bot, user)
                return



            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,dg(10,user))
            else:
                user.from_id = id
                BotChild_super.send_message(bot,user,dg(11,user))
                BotChild_super.send_message(bot,user,dg(12,user))
                user.dialog_state = 8
                user.save()
            return

        if user.dialog_state == 8:

            if input_string == 'Отмена':
                keyboard = BotChild_super.get_keyboard_for_fav_mode()
                BotChild_super.send_message_with_keyboard(bot, user, dg(17,user), keyboard)
                BotChild_super.send_fav_paths(bot, user)
                return


            id = Point.get_id(input_string)
            if id == -1:
                BotChild_super.send_message(bot,user,dg(10,user))
            else:
                user.to_id = id
                BotChild_super.send_message(bot,user,dg(13,user))
                user.save()

                HistoryPath.objects.get_or_create(telegram_user_id=user.user_telegram_id,point1=Point.objects.get(id=user.from_id),point2=Point.objects.get(id=user.to_id))
                #path = HistoryPath()
                #path.telegram_user=user
                ##path.point1=Point.objects.get(id=user.from_id)
                #path.point2 = Point.objects.get(id=user.to_id)
                #path.save()
                keyboard = BotChild_super.get_keyboard_for_fav_mode()
                BotChild_super.send_message_with_keyboard(bot,user,dg(16,user),keyboard)
                BotChild_super.send_fav_paths(bot,user)

    @staticmethod
    def send_message(bot, user, text):
        # self.logger.debug('bot ' + str(self.bot_id)+' sending text:'+text)
        bot.sendMessage(chat_id=user.user_telegram_id, text=text, disable_notification=False,
                        disable_web_page_prewview=True)

    @staticmethod
    def send_message_clear_keyboard(bot, user, text):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)

        keyboard = [
        ]
        keyboard = ReplyKeyboardMarkup(keyboard, one_time_keyboard=False)

        bot.sendMessage(chat_id=user.user_telegram_id, text=text, reply_markup=keyboard, disable_notification=False,
                        disable_web_page_prewview=True)

    @staticmethod
    def send_message_with_keyboard(bot, user, text, keyboard):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending text:' + text)

        bot.sendMessage(chat_id=user.user_telegram_id, text=text,
                        reply_markup=keyboard, disable_notification=False, disable_web_page_prewview=True)
        # self.telebot.send_message(self.dialog_id,
        #                          text,keyboard)

    def send_photo(bot, user, path):
        # self.logger.debug('bot ' + str(self.bot_id) + ' sending photo:' + path)
        bot.send_photo(user.user_telegram_id, open(path, 'rb'))


print('start')
master_logger.debug('start')

building = Building.get_building()
master_logger.debug('init WB class')
main_way_builder_instance = WayBuilderClass(building)


def echo_old(bot, update):
    if update.message.chat.id not in id_list:
        id_list.append(update.message.chat.id)
        tmp_bot = BotChild(bot, update.message.chat.id, len(id_list), main_way_builder_instance)
        bots[update.message.chat.id] = tmp_bot

    bots[update.message.chat.id].get_answer(update.message.text)


def echo(bot, update):
    text=update.message.text

    BotChild_super.get_answer(text,TelegramUser.get_user(update.message.chat),main_way_builder_instance,bot)


from Navigator.models import TelegramUser


def command(bot, update):

    #styles = Dialogs.objects.filter()
    #for style in styles:
    #    style.style2=style.style1
    #    style.style3 = style.style1
    #    style.save()


    if update.message.text == '/start':
        user = TelegramUser.add_telegram_user(update.message.chat)
        bot.send_message(text=dg(18,user), chat_id=update.message.chat_id, disable_web_page_preview=True)
        BotChild_super.send_message_with_keyboard(bot, TelegramUser.get_user(update.message.chat), dg(5,user),
                                                  BotChild_super.get_keyboard_for_change_style())

    else:
        user =TelegramUser()
        user.dialog_style=1
        bot.send_message(text=dg(19,user) + update.message.text, chat_id=update.message.chat_id,
                         disable_web_page_preview=True)


def error(bot, updater):
    pass  # handle error

def get_data_tuple(query_data):
    ind = query_data.index('#^*_')
    data1 = query_data[:ind]
    data2 = int(query_data[ind + 4:])
    return data1, data2

def button(bot, update):
    try:
        query = update.callback_query
        query_data_tuple = get_data_tuple(query.data)

        user = TelegramUser.get_user(update.callback_query.message.chat)
        print(query_data_tuple[1])
        if query_data_tuple[1] == 0:
            f_path= HistoryPath.objects.filter(id=query_data_tuple[0])
            if len(f_path)!=0:
                text = "Маршрут \n"+BotChild_super.make_message_from_path(f_path[0],user)+'\n '+dg(20,user)

                for del_path in f_path:
                    del_path.delete()

                BotChild_super.send_message(bot,user,text)
                BotChild_super.send_fav_paths(bot,user)
            return
        if query_data_tuple[1] == 1:
            f_path = HistoryPath.objects.filter(id=query_data_tuple[0])
            if len(f_path) != 0:
                path=f_path[0]

                user.from_id=path.point1.id
                user.to_id=path.point2.id
                user.save()
                BotChild_super.build_and_send_path(bot, user, main_way_builder_instance)
            else:
                BotChild_super.send_message(bot, user, 'Fatal eror')

    except Exception as ex:
        print(ex)

def work_cycle():
    try:
        updater.start_polling()
        master_logger.debug('new pol')
        time.sleep(10)
        work_cycle()
    except Exception as exc:
        print('bot crashed:')
        master_logger.debug('bot crashed')
        print(exc)
        master_logger.debug(exc)
        work_cycle()


command_handler = MessageHandler(Filters.command, command)
echo_handler = MessageHandler(Filters.text, echo)

import getpass

user = getpass.getuser()

token1 = '333359292:AAGf_E6lYBiojMkuyfxW1wefq65D9f2QAss'
token2 = '362627334:AAHil__LDmOE0WQ0FY-Czyh7yd6KS9JlDbc'

token = ''
if user == 'aleksa':
    token = token2
else:
    token = token1

updater = Updater(token=token)

dispatcher = updater.dispatcher
dispatcher.add_handler(command_handler)
# dispatcher.add_error_handler(error)
dispatcher.add_handler(echo_handler)

updater.dispatcher.add_handler(CallbackQueryHandler(button)) #for message inline

import threading

th=threading.Thread(target=work_cycle)
th.start()

#work_cycle()
#
# while True:
#    print('new poling')
#    try:
#        updater.start_polling()
#        time.sleep(10)
#    except Exception as excp:
#        print('bot crashed:')
#        print(excp)
