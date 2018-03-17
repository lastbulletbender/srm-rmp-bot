from telegram.ext import Updater,CommandHandler, MessageHandler, Filters
import logging
import db
import random
import scraper
import hashlib
from lock import enc,dec
from telegram.ext.dispatcher import run_async

logging.basicConfig(format = '%(asctime)s - %(name)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

token='PUT-YOUR-TELEGRAM-TOKEN-HERE'

#Helper function to reply quickly
@run_async
def reply(bot, update, message):
	"""Shows the typing action and replies to original message sender."""
	bot.send_chat_action(chat_id=update.message.chat_id,action='typing')
	bot.sendMessage(chat_id=update.message.chat_id,text=message,parse_mode='markdown')
	return

#Handles the registration. Take care of the test cases.
@run_async
def register(bot, update, args):
	""" Responsible for registering a new user.
	    Test cases handled : 1. Check whether correct number of credentials are entered.
				 2. Check whether this chat id is already registered.
				 3. Check whether the credentials are correct by logging in college website.
	    Adds the data to database. Note password has to go through enc() which handles encrpytion.
	    Replies either with error_messages or success_message based on outcome. """ 

	chat_id = update.message.chat_id
	try:
		reg_num, pwd = args
	except ValueError:
		logger.info("Incorrect number of credentials by %s",chat_id)
		error_message = "Hmmm.. Is the format correct? It should be in the form : Try again typing\n */register RegisterNo Password*"
		reply(bot,update,error_message)
		return
	reg_status = db.is_registered(chat_id)
	if (reg_status):
		error_message = "Already registered with registration number : {}!\n Use */unregister* to unregister".format(reg_status)
		reply(bot,update,error_message)
		return
	try:
		name = scraper.scrape(reg_num,pwd,'check_registration')
	except:
		error_message = "Are you sure you entered the correct registration/password?"
		reply(bot,update,error_message)
		return
	db.register(chat_id,reg_num,enc(pwd))
	logger.info("Registered %s (%s)",name,reg_num)
	success_message = "Registered *" + name + "*!"
	success_message += "\n\n Delete the message you sent for registering to ensure no one else reads it"
	reply(bot,update,success_message)
	return

#Handles the unregistration using chat_id.
@run_async
def unregister(bot, update):
	chat_id = update.message.chat_id
	reg_status = db.is_registered(chat_id)
	if (not reg_status):
		error_message = "There is nothing to unregister! Use `/register` to register"
		reply(bot,update,error_message)
		return
	if (not db.unregister(chat_id)):
		error_message = "Something wrong happened while unregistering. It has been notified to my master"
		logger.error("Unexpected error in unregistering : Chat id : %s",chat_id)
		reply(bot,update,error_message)
		return
	logger.info("Registered %s",reg_status)
	success_message = "Successfully unregistered *" + reg_status +"*.\n\n Send feedback using /feedback and your feedback. Thank you"
	reply(bot,update,success_message)
	return


#Reply to messages which cannot be handled.
@run_async
def unknown(bot, update):
	messages = ["I'm not really a fully functional A.I, you know", "I'm not programmed to understand this yet.",\
		"Try harder!","Bleep Bloop Bleep. Don't really understand you", "Use */help* for the list of commands"]
	message = random.choice(messages);
	logger.info("Unknown by %s ",update.message.chat_id)
	reply(bot, update, message)
	return


#Replies to command /attendance
@run_async
def attendance(bot, update, args):
	chat_id = update.message.chat_id
	reg_status = db.is_registered(chat_id)
	if (not reg_status):
		error_message = "Are you registered?"
		logger.info("%s tried to fetch attendance without registering",chat_id)
		reply(bot,update,error_message)
		return
	registration_number,password = db.get_credentials(chat_id)
	attendance_message = scraper.scrape(registration_number,dec(str(password)),'attendance',args)
	logger.info("%s was sent attendance",registration_number)
	reply(bot,update,attendance_message);
	return

#Replies to command /start.
############
# NEEDS A COMPLETE MESSAGE
###########
@run_async
def start(bot, update):
	user_name = update.message.from_user.first_name
	message = "Hey " + user_name + "! Let's get started. To register type\n */register YOUR_REG_NUMBER PASSWORD*"
	logger.info("New user : %s (%s)",update.message.chat_id, user_name)
	reply(bot,update,message)


@run_async
def timetable(bot, update, args):
	chat_id = update.message.chat_id
	reg_status = db.is_registered(chat_id)
	if (not reg_status):
		error_message = "Are you registered?"
		reply(bot,update,error_message)
		return
	timetable_message = db.get_timetable(chat_id)
	if (timetable_message):
		reply(bot,update,timetable_message)
		return
	registration_number,password = db.get_credentials(chat_id)
	timetable_message = scraper.scrape(registration_number,dec(str(password)),'timetable',args)
	db.set_timetable(chat_id,timetable_message,hashlib.sha1(timetable_message).hexdigest())
	reply(bot,update,timetable_message)
	return

@run_async
def marks(bot, update, args):
	chat_id = update.message.chat_id
	reg_status = db.is_registered(chat_id)
	if (not reg_status):
		error_message ="Are you registered?"
		reply(bot,update,error_message)
		return
	registration_number,password = db.get_credentials(chat_id)
	marks_message = scraper.scrape(registration_number,dec(str(password)),'marks',args)
	reply(bot,update,marks_message)
	return

if (__name__ == "__main__"):
	updater = Updater(token)
	dispatcher = updater.dispatcher

	start_handler= CommandHandler('start', start)
	register_handler = CommandHandler('register', register, pass_args=True)
	unregister_handler = CommandHandler('unregister', unregister)
	attendance_handler = CommandHandler('attendance', attendance, pass_args=(True,False))
	timetable_handler = CommandHandler('timetable', timetable, pass_args=(True,False))
	marks_handler = CommandHandler('marks', marks, pass_args=(True,False))
	unknown_handler = MessageHandler(Filters.text, unknown)

	dispatcher.add_handler(start_handler)
	dispatcher.add_handler(register_handler)
	dispatcher.add_handler(unregister_handler)
	dispatcher.add_handler(attendance_handler)
	dispatcher.add_handler(marks_handler)
	dispatcher.add_handler(timetable_handler)
	dispatcher.add_handler(unknown_handler)

	updater.start_webhook(listen='0.0.0.0',
			port=443,
			url_path=token,
			key='private.key',
			cert='cert.pem',
			webhook_url='https://YOUR-SERVER-IP-OR-DOMAIN/TOKEN',
			clean=True )
	updater.idle()

