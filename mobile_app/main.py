from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.uix.popup import Popup
from plyer import camera
import requests
import os

class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(orientation='vertical', spacing=15, padding=20, **kwargs)

        # Title
        self.title_label = Label(
            text="Campus Navigation Assistant",
            font_size='26sp',
            size_hint=(1, 0.1),
            halign="center",
            valign="middle"
        )
        self.add_widget(self.title_label)

        # Image Preview
        self.image_widget = KivyImage(
            source='',
            size_hint=(1, 0.5),
            allow_stretch=True,
            keep_ratio=True
        )
        self.add_widget(self.image_widget)

        # Prediction Label
        self.result_label = Label(
            text="Upload an image to start prediction",
            font_size='18sp',
            size_hint=(1, 0.15),
            halign="center",
            valign="top",
            markup=True
        )
        self.add_widget(self.result_label)

        # Buttons container
        self.button_box = BoxLayout(orientation='horizontal', spacing=15, size_hint=(1, 0.15))

        # Capture Button
        self.capture_btn = Button(
            text="Capture Image",
            font_size='18sp',
            background_color=(0.1, 0.5, 0.8, 1),
            background_normal=''
        )
        self.capture_btn.bind(on_release=self.capture_image)
        self.button_box.add_widget(self.capture_btn)

        # Select Button
        self.choose_btn = Button(
            text="Select Image",
            font_size='18sp',
            background_color=(0.2, 0.7, 0.4, 1),
            background_normal=''
        )
        self.choose_btn.bind(on_release=self.select_image)
        self.button_box.add_widget(self.choose_btn)

        self.add_widget(self.button_box)

    def capture_image(self, instance):
        temp_path = "captured_image.jpg"
        try:
            camera.take_picture(filename=temp_path, on_complete=self.image_captured)
        except Exception as e:
            self.show_result(f"[b]Camera Error:[/b]\n{str(e)}")

    def image_captured(self, file_path):
        if file_path and os.path.exists(file_path):
            self.image_widget.source = file_path
            self.image_widget.reload()
            self.upload_image(file_path)
        else:
            self.show_result("[b]No image captured or file not found.[/b]")

    def select_image(self, instance):
        content = FileChooserIconView()
        popup = Popup(title="Select an Image", content=content, size_hint=(0.9, 0.9))

        def on_selection(_, selection, touch):
            if selection:
                popup.dismiss()
                self.image_widget.source = selection[0]
                self.image_widget.reload()
                self.upload_image(selection[0])

        content.bind(on_submit=on_selection)
        popup.open()

    def upload_image(self, file_path):
        self.result_label.text = "[b]⏳ Uploading image for prediction...[/b]"
        url = 'http://127.0.0.1:5000/predict'  # Change for Android

        try:
            files = {'image': open(file_path, 'rb')}
            response = requests.post(url, files=files)
        except Exception as e:
            self.show_result(f"[b]Upload Error:[/b] {str(e)}")
            return

        if response.status_code == 200:
            result = response.json()
            landmark = result.get('landmark', 'Unknown')
            distance = result.get('estimated_distance', 'Unknown')
            self.show_result(f"[b]Landmark:[/b] {landmark}\n[b]Distance:[/b] {distance} meters")
        else:
            self.show_result(f"[b]Server Error:[/b] {response.status_code}")

    def show_result(self, message):
        self.result_label.text = message

class CampusNavigationApp(App):
    def build(self):
        return MainScreen()

if __name__ == '__main__':
    CampusNavigationApp().run()
