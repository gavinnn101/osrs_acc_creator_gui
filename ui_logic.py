import sys
import acc_creator

from datetime import datetime
from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QTimer

from acc_creator_gui import Ui_MainWindow
from modules.helper_modules.utility import (get_user_settings, get_site_settings, get_tribot_settings, get_osbot_settings)


# Pull settings from settings.ini
site_key, site_url = get_site_settings()
use_proxies = get_user_settings()[0]
proxy_auth_type = get_user_settings()[1]
num_of_accs = get_user_settings()[4]
username_prefix = get_user_settings()[5]
acc_password = get_user_settings()[6]
retry_seconds = get_user_settings()[8]

use_tribot = get_tribot_settings()[0]
tribot_username = get_tribot_settings()[1]
tribot_password = get_tribot_settings()[2]
tribot_script = get_tribot_settings()[3]

use_osbot = get_osbot_settings()[0]
osbot_username = get_osbot_settings()[1]
osbot_password = get_osbot_settings()[2]
osbot_script = get_osbot_settings()[3]


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        QTimer.singleShot(1, self.load_settings) # Initialize settings after ui setup


    def load_settings(self):
        """Loads our settings from the settings.ini file"""
        self.console_browser.setText(f"Today's Date is: {str(datetime.now())}")
        self.username_prefix_field.setText(username_prefix)
        self.account_password_field.setText(acc_password)
        self.accs_field.setText(str(num_of_accs))
        self.retry_timer_field.setText(str(retry_seconds))

        # Proxy Settings
        if use_proxies == 1:
            self.use_proxies_box.setCurrentIndex(1)
        else:
            self.use_proxies_box.setCurrentIndex(0)
        if proxy_auth_type == 1:
            self.proxy_auth_box.setCurrentIndex(1)
        else:
            self.proxy_auth_box.setCurrentIndex(0)

        # Client Settings
        if use_osbot == 1:
            self.use_client_box.setCurrentIndex(1)
            self.client_username_field.setText(osbot_username)
            self.client_password_field.setText(osbot_password)
            self.script_name_field.setText(osbot_script)
        elif use_tribot == 1:
            self.use_client_box.setCurrentIndex(2)
            self.client_username_field.setText(tribot_username)
            self.client_password_field.setText(tribot_password)
            self.script_name_field.setText(tribot_script)
        else:
            self.use_client_box.setCurrentIndex(0)

    def save_settings(self):
        pass

    def save_console(self):
        """Saves the entire contents of the console to the log.txt file"""
        log = self.console_browser.toPlainText()
        with open('log.txt', 'a+') as log_file:
            log_file.write(log)

    def clear_console(self):
        """Clears the entire contents of the console"""
        self.console_browser.clear()

    def create_accounts(self):
        acc_creator.create_account(self.console_browser)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
