import sys
import subprocess
import json
import os
from jsoneditor import JsonEditor
from PyQt5.QtCore import QThread, pyqtSignal, QCoreApplication
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QPlainTextEdit, QScrollArea, QLabel, QFrame, QDialog


class ScriptThread(QThread):
    output_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, settings_path, main_window):
        super().__init__()
        self.settings_path = settings_path
        self.main_window = main_window
        self.process = None

        with open(self.settings_path) as file:
            settings = json.load(file)

        server_name = settings.get('server_name', '')

        if not server_name:
            self.output_received.emit('Please name your server, opening up the config...')
            self.main_window.open_json_editor("settings.json")

    def run(self):
        with open(self.settings_path) as file:
            settings = json.load(file)

        executable_path = os.path.join(settings.get('server_path', ''), 'VRisingServer.exe')
        persistent_data_path = settings.get('persistent_data_path', '')
        server_name = settings.get('server_name', '')
        save_name = settings.get('save_name', '')
        
        steamcmd_filename = "steamcmd.exe"
        script_dir = os.path.dirname(os.path.abspath(__file__))
        steamcmd_path = os.path.join(script_dir, "steamcmd", steamcmd_filename)

        if not os.path.isfile(steamcmd_path):
            #print("Steam not found, downloading and begining update...")
            self.output_received.emit('Steam not found, assuming fresh startup')
            update_server(self.settings_path, self.output_received)

        command = [
            executable_path,
            '-persistentDataPath', persistent_data_path,
            '-serverName', server_name,
            '-saveName', save_name
        ]

        self.process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        while self.process.poll() is None:
            output = self.process.stdout.readline().strip()
            if output:
                self.output_received.emit(output)

        self.finished.emit()

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_path = "settings.json"

        self.setWindowTitle("VRising Simple Server Manager")
        self.setGeometry(100, 100, 800, 600)
        self.start_button = None
        self.stop_button = None
        self.update_button = None
        self.console_output = None
        self.script_thread = ScriptThread('settings.json', self)

        with open(self.settings_path) as file:
            settings = json.load(file)

        game_settings = settings.get('game_settings', '')
        host_settings = settings.get('host_settings', '')

        title_label = QLabel("VRising Simple Server Manager", self)
        title_label.setGeometry(50, 50, 500, 30)
        title_label.setStyleSheet("QLabel { font-size: 24px; font-weight: bold; color: #3498db; }")

        settings_button = QPushButton("Manager Settings", self)
        settings_button.setGeometry(430, 50, 100, 30)
        settings_button.setStyleSheet(
            "QPushButton { background-color: #808080; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:hover { background-color: #696969; }"
            "QPushButton:pressed { background-color: #585858; }"
        )

        settings_button.clicked.connect(lambda: self.open_json_editor('settings.json'))

        game_settings_button = QPushButton("Game Settings", self)
        game_settings_button.setGeometry(660, 50, 120, 30)
        game_settings_button.setStyleSheet(
            "QPushButton { background-color: #6c757d; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:hover { background-color: #5a6268; }"
            "QPushButton:pressed { background-color: #484f54; }"
        )
        abs_file_path = os.path.abspath(game_settings)
        game_settings_button.clicked.connect(lambda: self.open_json_editor(abs_file_path))

        server_settings_button = QPushButton("Server Settings", self)
        server_settings_button.setGeometry(535, 50, 120, 30)
        server_settings_button.setStyleSheet(
            "QPushButton { background-color: #6c757d; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:hover { background-color: #5a6268; }"
            "QPushButton:pressed { background-color: #484f54; }"
        )
        
        server_settings_button.clicked.connect(lambda: self.open_json_editor(host_settings))


        abs_file_path = os.path.abspath(game_settings)  # Get the absolute file path

        

        line = QFrame(self)
        line.setGeometry(50, 90, 700, 2)
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        self.start_button = QPushButton("Start", self)
        self.start_button.setGeometry(50, 110, 100, 30)
        self.start_button.setStyleSheet(
            "QPushButton { background-color: #2ecc71; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:disabled { background-color: #bdc3c7; }"
        )
        self.start_button.setEnabled(True)
        self.start_button.clicked.connect(self.start_script)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setGeometry(170, 110, 100, 30)
        self.stop_button.setStyleSheet(
            "QPushButton { background-color: #e74c3c; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:disabled { background-color: #bdc3c7; }"
        )
        self.stop_button.setEnabled(False)
        self.stop_button.clicked.connect(self.stop_script)

        self.update_button = QPushButton("Update", self)
        self.update_button.setGeometry(290, 110, 100, 30)
        self.update_button.setStyleSheet(
            "QPushButton { background-color: #f39c12; color: white; font-weight: bold; border-radius: 5px; }"
            "QPushButton:disabled { background-color: #bdc3c7; }"
        )
        self.update_button.setEnabled(True)
        self.update_button.clicked.connect(self.update_server)

        self.console_output = QPlainTextEdit(self)
        self.console_output.setStyleSheet(
            "QPlainTextEdit { background-color: #212121; color: #ffffff; font-family: Consolas; font-size: 12px; }"
        )
        self.console_output.setReadOnly(True)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setGeometry(50, 150, 700, 400)
        scroll_area.setWidget(self.console_output)

    def start_script(self):
        if self.script_thread is None or not self.script_thread.isRunning():
            with open('settings.json') as file:
                settings = json.load(file)

            executable_path = os.path.join(settings.get('server_path', ''), 'VRisingServer.exe')
            self.script_thread = ScriptThread('settings.json', self)
            self.script_thread.output_received.connect(self.append_output)
            self.script_thread.finished.connect(self.script_finished)

            self.script_thread.start()

            self.console_output.clear()
            self.console_output.appendPlainText('Server started.')

            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.update_button.setEnabled(False)

    def stop_script(self):
        if self.script_thread and self.script_thread.isRunning():
            self.script_thread.stop()
            self.script_finished()

            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.update_button.setEnabled(True)

    def update_server(self):
        self.console_output.appendPlainText('Updating server...')
        self.update_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(False)
        self.script_thread = UpdateThread('settings.json')
        self.script_thread.output_received.connect(self.append_output)
        self.script_thread.finished.connect(self.update_finished)
        self.script_thread.start()

    def append_output(self, output):
        self.console_output.appendPlainText(output)

    def script_finished(self):
        self.console_output.appendPlainText('Server stopped.')

    def update_finished(self):
        self.console_output.appendPlainText('Server update complete.')
        self.start_button.setEnabled(True)
        self.update_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def open_json_editor(self, filename):
        print("Filename: ", filename)
        editor = JsonEditor(filename)
        editor.show()

    def dialog_finished(self):
        # Dialog finished and closed
        print("Dialog closed, continue with the script")
        # Proceed with the rest of the script here

class UpdateThread(QThread):
    output_received = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, settings_path):
        super().__init__()
        self.settings_path = settings_path
        self.process = None

    def run(self):
        update_server(self.settings_path, self.output_received)

        self.finished.emit()


def update_server(settings_path, output_received):
    steamcmd_filename = "steamcmd.exe"
    script_dir = os.path.dirname(os.path.abspath(__file__))
    steamcmd_path = os.path.join(script_dir, "steamcmd", steamcmd_filename)

    # Load the settings from settings.json
    with open(settings_path, "r") as f:
        settings = json.load(f)

    installDir = os.path.join(script_dir, settings["server_path"])
    forceInstall = "+force_install_dir " + installDir

    if not os.path.isfile(steamcmd_path):
        # Download SteamCMD if it's not found
        download_url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
        download_path = os.path.join(script_dir, "steamcmd.zip")
        download_cmd = f'curl -o "{download_path}" -L "{download_url}"'
        subprocess.call(download_cmd, shell=True)

        output_received.emit("SteamCMD downloaded")

        # Extract SteamCMD
        extract_cmd = f'powershell -Command "Expand-Archive -Path \'{download_path}\' -DestinationPath \'{os.path.dirname(steamcmd_path)}\'"'
        subprocess.call(extract_cmd, shell=True)

        # Remove the downloaded zip file
        os.remove(download_path)

    output_received.emit("Downloading the files for server...")
    command = f'{steamcmd_path} +login anonymous +force_install_dir "{installDir}" +app_update 1829350 validate +quit'

    # Run the command and capture the output
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    #output, error = process.communicate()

    while process.poll() is None:
            output = process.stdout.readline().strip()
            if output:
                output_received.emit(output)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
