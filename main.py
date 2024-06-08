import json
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime

from kivymd.uix.list import TwoLineAvatarIconListItem, ILeftBody
from kivymd.uix.selectioncontrol import MDCheckbox


class DialogContent(MDBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ids.date_text.text = datetime.now().strftime("%A %d %B %Y")

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_save)
        date_dialog.open()

    def on_save(self, instance, value, date_range):
        date = value.strftime("%A %d %B %Y")
        self.ids.date_text.text = str(date)


class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    def __init__(self, app=None, **kwargs):
        self.app = app
        super().__init__(**kwargs)

    def mark(self, check):
        if check.active:
            self.text = '[s][b]' + self.text + '[/b][/s]'
        else:
            self.text = self.text.replace('[s][b]', '').replace('[/b][/s]', '')


class ListItemWithCheckbox(TwoLineAvatarIconListItem):
    def __init__(self, app=None, checked=False, **kwargs):
        self.app = app
        self.checked = checked
        super().__init__(**kwargs)

    def mark(self, check):
        self.checked = check.active
        if self.checked:
            self.text = '[s][b]' + self.text + '[/b][/s]'
        else:
            self.text = self.text.replace('[s][b]', '').replace('[/b][/s]', '')

    def delete_item(self):
        container = self.parent
        if container:
            task_text = self.text.strip('[s][b][/b][/s]')
            container.remove_widget(self)
            if self.app:
                self.app.remove_task_from_file(task_text)


class LeftCheckbox(ILeftBody, MDCheckbox):
    pass


class MainApp(MDApp):
    task_list_dialog = None
    tasks_file = "tasks.json"

    def remove_task(self, list_item):
        task_text = list_item.text
        self.root.ids['container'].remove_widget(list_item)
        self.remove_task_from_file(task_text)

    def build(self):
        self.theme_cls.primary_palette = "Teal"
        self.load_tasks()

    def load_tasks(self):
        try:
            with open(self.tasks_file, "r") as file:
                tasks_data = json.load(file)

            self.root.ids['container'].clear_widgets()  # Clear existing widgets

            for task_data in tasks_data:
                task_text = task_data["task"]
                task_date = task_data["due_date"]
                checked = task_data.get("checked", False)
                list_item = ListItemWithCheckbox(
                    text='[b]' + task_text + '[/b]',
                    secondary_text=task_date,
                    app=self,
                    checked=checked
                )
                self.root.ids['container'].add_widget(list_item)
        except FileNotFoundError:
            pass

    def save_tasks(self):
        tasks_data = []
        for widget in self.root.ids['container'].children:
            task_data = {
                "task": widget.text.strip('[b][/b]'),
                "due_date": widget.secondary_text,
                "checked": widget.checked
            }
            tasks_data.append(task_data)

        with open(self.tasks_file, "w") as file:
            json.dump(tasks_data, file)

    def show_task_function(self):
        self.task_list_dialog = MDDialog(
            title="Create a Task",
            type="custom",
            content_cls=DialogContent()
        )
        self.task_list_dialog.open()

    def add_task(self, task, task_date):
        list_item = ListItemWithCheckbox(
            text='[b]' + task.text + '[/b]',
            secondary_text=task_date,
        )
        self.root.ids['container'].add_widget(list_item)
        task.text = ''
        self.save_tasks()

    def remove_task_from_file(self, task_text):
        tasks_data = []
        for widget in self.root.ids['container'].children:
            task_data = {
                "task": widget.text.strip('[b][/b]'),
                "due_date": widget.secondary_text
            }
            tasks_data.append(task_data)

        with open(self.tasks_file, "w") as file:
            json.dump(tasks_data, file)

    def close_dialog(self, *args):
        self.task_list_dialog.dismiss()
        self.remove_task_from_file("")
        self.save_tasks()


if __name__ == "__main__":
    app = MainApp()
    app.run()
