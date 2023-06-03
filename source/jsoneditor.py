import sys
import json
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea
from PyQt5.QtCore import QTimer


class JsonEditor(QWidget):
    def __init__(self, json_file):
        super().__init__()
        self.json_file = json_file
        self.data = {}
        self.load_json()
        self.init_ui()

    def load_json(self):
        try:
            with open(self.json_file) as file:
                self.data = json.load(file)
        except Exception as e:
            #this is stupid and i hate it
            print("ABSOLUTE PAIN")
            try:
                with open(self.json_file, encoding='utf-8-sig') as file:
                    self.data = json.load(file)
            except Exception as e:
                print(f"Error opening JSON file: {e}")


    def save_json(self):
        with open(self.json_file, 'w') as file:
            json.dump(self.data, file, indent=4)
        self.close()
    
    def show_save_feedback(self):
    # Temporarily change the button color to a darker shade of green
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #388E3C; /* Darker green */
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        # Use a QTimer to reset the button style after a short delay
        QTimer.singleShot(1000, self.reset_save_button_style)

    def reset_save_button_style(self):
        # Reset the button style back to its original state
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: black;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def init_ui(self):
        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setLayout(layout)
        scroll_area.setWidget(scroll_widget)

        self.save_button = QPushButton('Save')
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: black;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.save_button.clicked.connect(self.save_json)
        self.save_button.clicked.connect(self.show_save_feedback)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.save_button)
        main_layout.addWidget(scroll_area)

        self.setLayout(main_layout)
        self.setWindowTitle('JSON Editor')

        self.populate_layout(layout, self.data)

    def populate_layout(self, layout, data, parent_key=''):
        for key, value in data.items():
            full_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                group_box = self.create_group_box(full_key)
                inner_layout = QVBoxLayout()
                inner_layout.setContentsMargins(10, 5, 10, 5)  # Adjust the margins as needed
                group_box.layout().addLayout(inner_layout)
                self.populate_layout(inner_layout, value, full_key)
                layout.addWidget(group_box)
            else:
                label = QLabel(f"<b>{key}:</b>")
                value_widget = self.create_widget(full_key, value)
                hbox = QHBoxLayout()
                hbox.addWidget(label)
                hbox.addWidget(value_widget)
                layout.addLayout(hbox)

    def create_group_box(self, title):
        group_box = QWidget()
        group_box.setStyleSheet("""
            QWidget {
                border: 1px solid #000;
                border-radius: 10px;
                background-color: #FFEEEE; /* Very light red */
            }
            QLabel {
                padding: 5px;
                color: black;
            }
        """)
        group_box_layout = QVBoxLayout()
        title_label = QLabel(f"<b>{title}</b>")
        title_label.setStyleSheet("QLabel { color: black; }")
        group_box_layout.addWidget(title_label)
        group_box.setLayout(group_box_layout)
        return group_box

    def create_widget(self, key, value):
        line_edit = QLineEdit(str(value))
        line_edit.setFixedWidth(100)  # Adjust the width
        line_edit.textChanged.connect(lambda text, k=key: self.update_data(k, text))
        return line_edit

    def update_data(self, key, value):
        keys = key.split('.')
        current_dict = self.data
        for k in keys[:-1]:
            current_dict = current_dict[k]
        current_dict[keys[-1]] = value

    def open_json_file(self, json_file):
        self.json_file = json_file
        self.load_json()
        layout = QVBoxLayout()
        self.populate_layout(layout, self.data)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = JsonEditor('data.json')
    editor.show()
    sys.exit(app.exec_())
