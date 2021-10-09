
import requests
import json
import time
import xmltodict
from gtts import gTTS
import datetime

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang.builder import Builder
from kivy.core.text import Label as CoreLabel
from kivy.lang.builder import Builder
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.clock import Clock
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.label import CoreLabel
from kivy.uix.label import Label
from jnius import autoclass

activity = autoclass('org.kivy.android.PythonActivity').mActivity
activity.removeLoadingScreen()


def getdata():
    try:
        timestamp = round(time.time() * 1000)
        response = requests.get(
            f"http://jiofi.local.html/st_dev.w.xml?_={timestamp}")
        dictdata = xmltodict.parse(response.text)
        jsondata = json.loads(json.dumps(dictdata))
        batt_per = jsondata['dev']['batt_per']
        batt_st = jsondata['dev']['batt_st']
        if int(batt_st) < 1000:
            battery_status = "Not charging"
        else:
            battery_status = "Charging"
        return False, batt_per, battery_status
    except Exception as e:
        return True, None, None


def monitor(arg):
    try:
        timestamp = round(time.time() * 1000)
        response = requests.get(
            f"http://jiofi.local.html/st_dev.w.xml?_={timestamp}")
        dictdata = xmltodict.parse(response.text)
        jsondata = json.loads(json.dumps(dictdata))
        batt_per = jsondata['dev']['batt_per']
        batt_st = jsondata['dev']['batt_st']
        if int(batt_st) < 1000:
            battery_status = "Not charging"
        else:
            battery_status = "Charging"
        log = 'Timestamp:  {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now(
        )) + f' data: {{Battery percent: {batt_per}, Battery status: {battery_status}}}'
        print(log)
        if int(batt_per) < 10 and int(batt_st) < 1000:
            mytext = "Battery dying"
            language = 'en'
            myobj = gTTS(text=mytext, lang=language)
            myobj.save("battery_dying.wav")
            MediaPlayer = autoclass('android.media.MediaPlayer')
            mPlayer_norm = MediaPlayer()
            mPlayer_norm.setDataSource('battery_dying.wav')
            mPlayer_norm.prepare()
            mPlayer_norm.start()
            time.sleep(5)
            mPlayer_norm.release()
        elif int(batt_per) > 98 and int(batt_st) > 1000:
            mytext = "Battery full"
            language = 'en'
            myobj = gTTS(text=mytext, lang=language)
            myobj.save("battery_full.wav")
            MediaPlayer = autoclass('android.media.MediaPlayer')
            mPlayer_norm = MediaPlayer()
            mPlayer_norm.setDataSource('battery_full.wav')
            mPlayer_norm.prepare()
            mPlayer_norm.start()
            time.sleep(5)
            mPlayer_norm.release()
    except Exception as e:
        print(
            'Timestamp: {:%Y-%m-%d %H:%M:%S} '.format(datetime.datetime.now()) + str(e))
        time.sleep(2)


KV = '''
<HomePage>:
    Button:
        text:"Monitor"
        size_hint:(.3, .05)
        border: (20, 20, 20, 20)
        pos_hint:{'center_x': 0.2, 'center_y': 0.2}
        background_color: "cyan"
        on_press:root.monitorbutton()
    CircularProgressBar:
        id: cp
        size_hint:(None,None)
        pos_hint:{'center_x': 0.5, 'center_y': 0.6}
        height:400
        width:400
        max:80
    Button:
        text:"Stop"
        size_hint:(.3, .05)
        border: (20, 20, 20, 20)
        pos_hint:{'center_x': 0.8, 'center_y': 0.2}
        background_color:"cyan"
        on_press:root.stopbutton()
    '''


def show_popup():
    show = Screen()

    def exitfunc(arg):
        exit(0)
    popupWindow = Popup(title="JioFi Monitoring", content=show,
                        size_hint=(.8, .4))
    label = Label(
        text="Are you sure you want to stop monitoring and exit?",
        size_hint=(.4, .2),
        pos_hint={"x": 0.3, 'top': 1}
    )
    yes = Button(
        text='Yes',
        size_hint=(.3, .15),
        pos_hint={"x": 0, "bottom": 1},
        background_color="cyan",
        on_press=exitfunc
    )
    no = Button(
        text='No',
        size_hint=(.3, .15),
        pos_hint={"x": 0.7, "bottom": 1},
        background_color="cyan",
        on_press=popupWindow.dismiss
    )
    show.add_widget(label)
    show.add_widget(yes)
    show.add_widget(no)
    popupWindow.open()


def monitor_popup():
    show1 = Screen()

    popupWindow1 = Popup(title="JioFi Monitoring", content=show1,
                         size_hint=(.6, .3))
    label = Label(
        text="Monitoring has been started",
        size_hint=(0.4, .2),
        pos_hint={"x": 0.2, 'top': 1}
    )
    ok = Button(
        text='OK',
        size_hint=(.3, .2),
        pos_hint={"x": 0.4, "bottom": 1},
        background_color="cyan",
        on_press=popupWindow1.dismiss
    )
    show1.add_widget(label)
    show1.add_widget(ok)
    popupWindow1.open()


class HomePage(Screen):
    def monitorbutton(self):
        Clock.schedule_interval(monitor, .1)
        monitor_popup()

    def stopbutton(self):
        show_popup()


class CircularProgressBar(ProgressBar):
    def __init__(self, **kwargs):
        super(CircularProgressBar, self).__init__(**kwargs)
        # Set constant for the bar thickness
        self.thickness = 40
        # Create a direct text representation
        self.label = CoreLabel(text="0%", font_size=30)
        # Initialise the texture_size variable
        self.texture_size = None
        # Refresh the text
        self.refresh_text()
        # Redraw on innit
        self.draw([0, 1, 0], 100)

    def draw(self, colorValue, val):
        with self.canvas:
            # Empty canvas instructions
            self.canvas.clear()
            # Draw no-progress circle
            Color(0.26, 0.26, 0.26)
            Ellipse(pos=self.pos, size=self.size)
            # Draw progress circle, small hack if there is no progress (angle_end = 0 results in full progress)
            Color(colorValue[0], colorValue[1], colorValue[2])
            Ellipse(pos=self.pos, size=self.size,
                    angle_end=(val/100.0)*360)
            # Draw the inner circle (colour should be equal to the background)
            Color(0, 0, 0)
            Ellipse(pos=(self.pos[0] + self.thickness / 2, self.pos[1] + self.thickness / 2),
                    size=(self.size[0] - self.thickness, self.size[1] - self.thickness))
            # Center and draw the progress text
            Color(1, 1, 1, 1)
            # added pos[0]and pos[1] for centralizing label text whenever pos_hint is set
            Rectangle(texture=self.label.texture, size=self.texture_size,
                      pos=(self.size[0] / 2 - self.texture_size[0] / 2 + self.pos[0], self.size[1] / 2 - self.texture_size[1] / 2 + self.pos[1]))

    def refresh_text(self):
        # Render the label
        self.label.refresh()
        # Set the texture size each refresh
        self.texture_size = list(self.label.texture.size)

    def set_value(self, value, status):
        if status == 'Not charging':
            text = '       ' + \
                str(value) + f"%\n{status}"
        else:
            text = '     ' + \
                str(value) + f"%\n{status}"
        # Update the progress bar value
        self.value = value
        # Update textual value and refresh the texture
        self.label.text = text
        self.refresh_text()
        # Draw all the elements
        if value < 20:
            # red
            colorValue = [1, 0, 0]
        elif value >= 20 and value <= 60:
            # yellow
            colorValue = [1, 1, 0]
        else:
            # green
            colorValue = [0, 1, 0]
        self.draw(colorValue, value)


class Demo(App):
    def __init__(self, **kwargs):
        super(Demo, self).__init__(**kwargs)
        Window.bind(on_keyboard=self.on_key)

    def on_key(self, window, key, *args):
        if key == 27:  # the esc key
            show_popup()
            return True
            # return False  # exit the app from this page

    def animate(self, dt):
        circProgressBar = self.root.get_screen("HomePage").ids.cp
        err, per, status = getdata()
        if not err:
            circProgressBar.set_value(int(per), status)

    def build(self):
        from android import AndroidService
        service = AndroidService('my pong service', 'running')
        service.start('service started')
        self.service = service

        Builder.load_string(KV)
        screen = ScreenManager()
        screen.add_widget(HomePage(name="HomePage"))
        Clock.schedule_interval(self.animate, 0.1)
        return screen


if __name__ == "__main__":
    demo = Demo()
    demo.run()
