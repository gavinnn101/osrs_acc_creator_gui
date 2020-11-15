import sys
import traceback
import time
import os

from PyQt5.QtWidgets import QTableWidgetItem

from src import acc_creator

from configparser import ConfigParser
from datetime import datetime
from PyQt5 import QtWidgets
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QTimer, QThreadPool, QRunnable

from src.gui_files.acc_creator_gui import Ui_MainWindow
from src.modules.helper_modules.utility import (get_index, get_user_settings, get_site_settings, get_tribot_settings, get_osbot_settings)
from src.modules.licensing.creator_licensing import check_key
from src.modules.updater.updater import check_update


# Get User settings
site_url = get_site_settings()
use_proxies = get_user_settings()[0]
proxy_auth_type = get_user_settings()[1]
num_of_accs = get_user_settings()[4]
username_prefix = get_user_settings()[5]
acc_password = get_user_settings()[6]
retry_seconds = get_user_settings()[8]

# Get Tribot settings
use_tribot = get_tribot_settings()[0]
tribot_username = get_tribot_settings()[1]
tribot_password = get_tribot_settings()[2]
tribot_script = get_tribot_settings()[3]
tribot_script_args = get_tribot_settings()[4]

# Get OSBot settings
use_osbot = get_osbot_settings()[0]
osbot_username = get_osbot_settings()[1]
osbot_password = get_osbot_settings()[2]
osbot_script = get_osbot_settings()[3]
osbot_script_args = get_osbot_settings()[4]


class WorkerSignals(QObject):
    progress = pyqtSignal(str)


class Worker(QRunnable):
    """
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function
    """

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self.kwargs['progress_callback'] = self.signals.progress  # So we can emit our text output to the GUI thread

    @pyqtSlot()
    def run(self):
        """
        Initialise the runner function with passed args, kwargs.
        """

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    update_text = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        QTimer.singleShot(1, self.load_settings)  # Initialize settings after ui setup
        self.threadpool = QThreadPool.globalInstance()
        self.update_text.connect(self.append_text)
        self.use_client_box.currentIndexChanged.connect(self.on_client_change, self.use_client_box.currentIndex())
        self.did_they_save = False

    def append_text(self, msg):
        self.console_browser.append(msg)

    def on_client_change(self, value):
        if value == 1:
            self.client_username_field.setText(osbot_username)
            self.client_password_field.setText(osbot_password)
            self.script_name_field.setText(osbot_script)
            self.script_args_field.setText(osbot_script_args)
        elif value == 2:
            self.use_client_box.setCurrentIndex(2)
            self.client_username_field.setText(tribot_username)
            self.client_password_field.setText(tribot_password)
            self.script_name_field.setText(tribot_script)
            self.script_args_field.setText(tribot_script_args)

    def save_proxies(self):
        self.did_they_save = True

        def save_proxy(current_proxy):
            """Save the proxy dictionary contents in a correctly formatted line to our proxy_list.txt file."""
            with open("../src/settings/proxy_list.txt", "a+") as proxy_file:
                if os.stat("../src/settings/proxy_list.txt").st_size == 0:
                    current_proxy = format_proxy(current_proxy)
                    if current_proxy:
                        proxy_file.write(current_proxy)
                else:
                    current_proxy = format_proxy(current_proxy)
                    if current_proxy:
                        proxy_file.write("\n")
                        proxy_file.write(current_proxy)

        def format_proxy(proxy_dict):
            """Formats our proxy dictionary to an acceptable string that can be written to file."""
            formatted_proxy = "socks5://"  # This is always needed for the way we parse proxies everywhere else.

            if not proxy['proxy_username']:
                credentials = False
            else:
                credentials = True

            if credentials:
                formatted_proxy += proxy_dict['proxy_username']
                formatted_proxy += ':'
                formatted_proxy += proxy_dict['proxy_password']
                formatted_proxy += '@'
                formatted_proxy += proxy_dict['proxy_ip']
                formatted_proxy += ':'
                formatted_proxy += proxy_dict['proxy_port']
                return formatted_proxy
            else:
                try:
                    formatted_proxy += proxy_dict['proxy_ip']
                    formatted_proxy += ':'
                    formatted_proxy += proxy_dict['proxy_port']
                    return formatted_proxy
                except TypeError as _:
                    print("Invalid proxy format.")

            print(formatted_proxy)

        open("../src/settings/proxy_list.txt", 'w').close()

        row_count = self.proxy_table.rowCount()

        try:
            for row in range(row_count):
                # Recreate the dictionary for each row.
                # No reason to save all of the proxies in memory since the proxy_list.txt is the source of truth
                proxy = {"proxy_ip": None, "proxy_port": None, "proxy_username": None, "proxy_password": None}
                counter = 0

                # Loop over the columns in the current row and store the data in the "proxy" dictionary to save later
                for field in proxy:
                    try:
                        column_value = self.proxy_table.item(row, counter).text()
                        if not column_value:
                            proxy[field] = None
                        else:
                            proxy[field] = column_value
                    except AttributeError:
                        proxy[field] = None
                    counter += 1
                print(f"Saving proxy: {proxy}")
                save_proxy(proxy)
        except Exception:
            traceback.print_exc()
        print("Proxies have been saved.")

    def add_proxy(self):
        self.proxy_table.insertRow(self.proxy_table.rowCount())

    def remove_proxy(self):
        self.proxy_table.removeRow(self.proxy_table.currentIndex().row())

    def closeEvent(self, event):
        if not self.did_they_save:
            self.save_proxies()
        event.accept()

    def load_settings(self):
        """Loads our settings from the settings.ini file"""
        self.console_browser.setText(f"Today's Date is: {str(datetime.now().replace(microsecond=0))}")
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
            self.script_args_field.setText(osbot_script_args)
        elif use_tribot == 1:
            self.use_client_box.setCurrentIndex(2)
            self.client_username_field.setText(tribot_username)
            self.client_password_field.setText(tribot_password)
            self.script_name_field.setText(tribot_script)
            self.script_args_field.setText(tribot_script_args)
        else:
            self.use_client_box.setCurrentIndex(0)

        def load_proxies():
            proxy = {"proxy_ip": None, "proxy_port": None, "proxy_username": None, "proxy_password": None}

            with open("../src/settings/proxy_list.txt")as proxy_file:
                try:
                    counter = 0
                    for line in proxy_file:
                        try:
                            proxy['proxy_ip'] = line[get_index(line, '@', 1) + 1:get_index(line, ':', 3)]
                            proxy['proxy_port'] = line[get_index(line, ':', 3) + 1:].strip('\n')
                            proxy['proxy_username'] = line[get_index(line, '/', 2) + 1:get_index(line, ':', 2)]
                            proxy['proxy_password'] = line[get_index(line, ':', 2) + 1:get_index(line, '@', 1)]
                        except ValueError:
                            try:
                                proxy['proxy_ip'] = line[get_index(line, '/', 2) + 1:get_index(line, ':', 2)]
                                proxy['proxy_port'] = line[get_index(line, ':', 2) + 1:].strip('\n')
                                proxy['proxy_username'] = None
                                proxy['proxy_password'] = None
                            except ValueError:
                                pass

                        # Load current proxy dict into proxy_table here
                        self.proxy_table.insertRow(self.proxy_table.rowCount())
                        self.proxy_table.setItem(counter, 0, QTableWidgetItem(proxy['proxy_ip']))
                        self.proxy_table.setItem(counter, 1, QTableWidgetItem(proxy['proxy_port']))
                        self.proxy_table.setItem(counter, 2, QTableWidgetItem(proxy['proxy_username']))
                        self.proxy_table.setItem(counter, 3, QTableWidgetItem(proxy['proxy_password']))

                        counter += 1
                except Exception:
                    traceback.print_exc()

        load_proxies()
        # Clear the proxy file since we'll rewrite on save.
        open("../src/settings/proxy_list.txt", 'w').close()

    def save_settings(self):
        # Run this inside of create_accounts()
        config = ConfigParser()
        try:
            config.read('../src/settings/settings.ini')
        except FileNotFoundError:
            sys.exit("settings.ini file not found. "
                     "Make sure it's in the same directory.")

        config.set('USER_SETTINGS', 'username_prefix', self.username_prefix_field.text())
        config.set('USER_SETTINGS', 'password', self.account_password_field.text())
        config.set('USER_SETTINGS', 'num_of_accs', str(self.accs_field.text()))
        config.set('USER_SETTINGS', 'retry_seconds', str(self.retry_timer_field.text()))
        config.set('USER_SETTINGS', 'use_proxies', str(self.use_proxies_box.currentIndex()))
        if self.proxy_auth_box.currentIndex() == 0:
            config.set('USER_SETTINGS', 'proxy_auth_type', '2')
        else:
            config.set('USER_SETTINGS', 'proxy_auth_type', '1')

        if self.use_client_box.currentIndex() == 0:
            config.set('TRIBOT_CLI_SETTINGS', 'use_tribot', ('0'))
            config.set('OSBOT_CLI_SETTINGS', 'use_osbot', ('0'))
        elif self.use_client_box.currentIndex() == 1:
            config.set('TRIBOT_CLI_SETTINGS', 'use_tribot', ('0'))
            config.set('OSBOT_CLI_SETTINGS', 'use_osbot', ('1'))
            config.set('OSBOT_CLI_SETTINGS', 'osbot_username', self.client_username_field.text())
            config.set('OSBOT_CLI_SETTINGS', 'osbot_password', self.client_password_field.text())
            config.set('OSBOT_CLI_SETTINGS', 'osbot_script', self.script_name_field.text())
            config.set('OSBOT_CLI_SETTINGS', 'script_args', self.script_args_field.text())
        else:
            config.set('OSBOT_CLI_SETTINGS', 'use_osbot', ('0'))
            config.set('TRIBOT_CLI_SETTINGS', 'use_tribot', ('1'))
            config.set('TRIBOT_CLI_SETTINGS', 'tribot_username', self.client_username_field.text())
            config.set('TRIBOT_CLI_SETTINGS', 'tribot_password', self.client_password_field.text())
            config.set('TRIBOT_CLI_SETTINGS', 'tribot_script', self.script_name_field.text())
            config.set('TRIBOT_CLI_SETTINGS', 'script_args', self.script_args_field.text())

        self.console_browser.append("\nSettings have been saved.\n")

    def save_console(self):
        """Saves the entire contents of the console to the log.txt file"""
        log = f"{self.console_browser.toPlainText()}\n"
        with open('../src/log.txt', 'a+') as log_file:
            log_file.write(log)

    def clear_console(self):
        """Clears the entire contents of the console"""
        self.console_browser.clear()

    def create_accounts(self, progress_callback):
        self.save_settings()
        worker = Worker(acc_creator.create_account, progress_callback)
        worker.signals.progress.connect(self.append_text)
        self.threadpool.start(worker)


def main():
    if check_key():  # If valid license, check for an update
        if check_update():  # We're on the latest version
            app = QtWidgets.QApplication(sys.argv)
            window = MainWindow()
            window.show()
            app.exec()
        else:  # Installed new version of the program
            time.sleep(5)
            sys.exit()
    else:  # Invalid license or machine
        with open('log.txt', 'a+') as log_file:
            log_file.write(f"Today's Date is: {str(datetime.now().replace(microsecond=0))}\n")
            log_file.write("Key in settings file not valid.\n")


if __name__ == '__main__':
    main()
