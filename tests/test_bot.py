import os
import tempfile
from unittest import TestCase

from flask import Flask

from supplychainpy._helpers._config_file_paths import ABS_FILE_PATH_APPLICATION_CONFIG
from supplychainpy._helpers._pickle_config import serialise_config
from supplychainpy.bot.dash import ChatBot
from supplychainpy.launch_reports import load_db
from supplychainpy.reporting.config.settings import ProdConfig, DevConfig
from supplychainpy.reporting.extensions import db
from supplychainpy.sample_data.config import ABS_FILE_PATH


class TestBot(TestCase):

    def setUp(self):
        self.__dude = ChatBot()
        self.__SALUTATION_RESPONSES = ["hi", "hello", "how's tricks?"]
        app = Flask(__name__, instance_relative_config=True)
        app.config.from_object(DevConfig)
        PWD = os.path.abspath(os.curdir)
        app.config['DATABASE'] = PWD
        app.config['TESTING'] = True
        self.app = app.test_client()

        app_settings = {
            'file': ABS_FILE_PATH['COMPLETE_CSV_SM'],
            'currency': 'USD',
            'database_path': PWD,
        }
        serialise_config(app_settings, ABS_FILE_PATH_APPLICATION_CONFIG)

        with app.app_context():
            db.init_app(app)
            db.create_all()
            load_db(file=ABS_FILE_PATH['COMPLETE_CSV_SM'])


    def test_chatbot(self):
        greeting1 = self.__dude.chat_machine("hello")[0]
        greeting2 = self.__dude.chat_machine("hello")[0]
        greeting3 = self.__dude.chat_machine("hello")[0]
        self.assertIn(*greeting3, self.__SALUTATION_RESPONSES)
        self.assertIn('KR202-244', *self.__dude.chat_machine("Which SKU has the highest reorder level?")[0])
        self.assertEqual('<a href="/sku_detail/36">Here you go!</a>', *self.__dude.chat_machine("show KR202-244")[0])
        self.assertIn('SKU KR202-244', *self.__dude.chat_machine("what is the biggest shortage?")[0])
        self.assertIn('KR202-223',*self.__dude.chat_machine("what is the biggest excess?")[0])
