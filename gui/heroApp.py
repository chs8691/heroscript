from kivy.app import App
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label


class OutputWidget(Label):

    def __init__(self,  **kwargs):
        super(OutputWidget, self).__init__(**kwargs)

        self.text = ("Holla Holla Holla Holla Holla Holla Holla Holla Holla Holla Holla Holla Holla Holla"
                                  " Holla Holla Holla Holla Holla Holla Holla Holla Holla Holla Holla "
                                  "\nHallo.")


class ButtonBarWidget(BoxLayout):
    def __init__(self, **kwargs):
        super(ButtonBarWidget, self).__init__(**kwargs)

        button = Button(text="Configuration")
        button.bind(on_press=self.btn_pressed(1, 1))

        self.add_widget(button)
        self.add_widget(Button(text="Download"))
        self.add_widget(Button(text="Staging"))
        self.add_widget(Button(text="Purge"))
        self.add_widget(Button(text="Transfer"))

    def btn_pressed(self, instance, key):
        print (f"pressed {instance}")


class HeroLauncher(GridLayout):

    def __init__(self, **kwargs):
        super(HeroLauncher, self).__init__(**kwargs)

        self.rows = 2
        self.cols = 1

        self.width = Config.get('graphics', 'width')
        self.height = Config.get('graphics', 'height')
        # print(f"Height:{self.height}")

        button_bar_widget = ButtonBarWidget()

        output_widget = OutputWidget()
        output_widget.height = self.height - button_bar_widget.height

        self.add_widget(button_bar_widget)
        self.add_widget(output_widget)


class HeroApp(App):

    def build(self):
        Config.set('graphics', 'width', '600')
        Config.set('graphics', 'height', '800')

        return HeroLauncher()


if __name__ == "__main__":
    HeroApp().run()
