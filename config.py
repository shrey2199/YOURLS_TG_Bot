import os

class Config(object):
	BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
	YL_DOMAIN = os.environ.get("YL_DOMAIN", "") # Without https:// or http://
	YL_SIG = os.environ.get("YL_SIG", "")
	ADMIN_IDS = os.environ.get("ADMIN_IDS", "") # ==> Enter Admin Chat IDs here !!
