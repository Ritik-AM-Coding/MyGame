from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label
from kivy.config import Config
import random

# Mobile settings (IMPORTANT)
Config.set('graphics', 'resizable', False)
Config.set('graphics', 'fullscreen', 'auto')

score = 10


# -------- HOME SCREEN --------

class HomeScreen(Screen):

    def on_enter(self):
        self.clear_widgets()
        layout = FloatLayout()

        bg = Image(source="assets/background.png",
                   allow_stretch=True,
                   keep_ratio=False,
                   size_hint=(1, 1))
        layout.add_widget(bg)

        start = Button(text="START GAME",
                       size_hint=(0.5, 0.1),
                       pos_hint={"center_x": 0.5, "center_y": 0.6})
        start.bind(on_press=self.start_game)

        quit_btn = Button(text="QUIT",
                          size_hint=(0.5, 0.1),
                          pos_hint={"center_x": 0.5, "center_y": 0.4})
        quit_btn.bind(on_press=self.quit_game)

        layout.add_widget(start)
        layout.add_widget(quit_btn)

        self.add_widget(layout)

    def start_game(self, instance):
        self.manager.current = "game"

    def quit_game(self, instance):
        App.get_running_app().stop()


# -------- GAME SCREEN --------

class GameScreen(Screen):

    def on_enter(self):
        global score
        score = 10
        self.clear_widgets()

        self.layout = FloatLayout()

        self.bg = Image(source="assets/background.png",
                        allow_stretch=True,
                        keep_ratio=False,
                        size_hint=(1, 1))
        self.layout.add_widget(self.bg)

        self.player = Image(source="assets/player.png",
                            size_hint=(None, None),
                            size=(80, 80),
                            pos=(self.width / 2 - 40, 50))
        self.layout.add_widget(self.player)

        self.coin = Image(source="assets/coin.png",
                          size_hint=(None, None),
                          size=(50, 50),
                          pos=(random.randint(0, int(self.width - 50)), self.height))
        self.layout.add_widget(self.coin)

        self.bone = Image(source="assets/bone.png",
                          size_hint=(None, None),
                          size=(60, 60),
                          pos=(random.randint(0, int(self.width - 60)), self.height))
        self.layout.add_widget(self.bone)

        self.score_label = Label(text="Score: 10",
                                 size_hint=(0.3, 0.1),
                                 pos_hint={"right": 1, "top": 1})
        self.layout.add_widget(self.score_label)

        self.music = SoundLoader.load("assets/background.wav")
        self.shoot = SoundLoader.load("assets/shoot.wav")

        if self.music:
            self.music.loop = True
            self.music.play()

        self.bullets = []
        self.game_over = False

        self.add_widget(self.layout)
        self.event = Clock.schedule_interval(self.update, 1 / 60)

    # PLAYER MOVE IN ALL DIRECTIONS
    def on_touch_move(self, touch):
        if not self.game_over:
            self.player.center = touch.pos

            # Boundary restriction
            if self.player.x < 0:
                self.player.x = 0
            if self.player.right > self.width:
                self.player.right = self.width
            if self.player.y < 0:
                self.player.y = 0
            if self.player.top > self.height:
                self.player.top = self.height

    def on_touch_down(self, touch):
        if not self.game_over:
            bullet = Image(source="assets/slash.png",
                           size_hint=(None, None),
                           size=(20, 40),
                           pos=(self.player.center_x - 10, self.player.top))
            self.layout.add_widget(bullet)
            self.bullets.append(bullet)

            if self.shoot:
                self.shoot.play()

    def gameover(self):
        self.game_over = True

        over = Label(text="GAME OVER",
                     font_size=40,
                     size_hint=(1, 1),
                     halign="center",
                     valign="middle")
        over.bind(size=over.setter('text_size'))

        self.layout.add_widget(over)

        Clock.schedule_once(self.back_home, 4)

    def back_home(self, dt):
        Clock.unschedule(self.event)
        self.manager.current = "home"

    def update(self, dt):
        global score

        if self.game_over:
            return

        # Move bullets
        for bullet in self.bullets[:]:
            bullet.y += 15
            if bullet.y > self.height:
                self.layout.remove_widget(bullet)
                self.bullets.remove(bullet)

        # Bullet hits bone
        for bullet in self.bullets[:]:
            if bullet.collide_widget(self.bone):
                self.layout.remove_widget(bullet)
                self.bullets.remove(bullet)
                self.bone.y = self.height
                self.bone.x = random.randint(0, int(self.width - 60))

        # Move coin
        self.coin.y -= 5
        if self.coin.y < 0:
            self.coin.y = self.height
            self.coin.x = random.randint(0, int(self.width - 50))

        # Move bone
        self.bone.y -= 7
        if self.bone.y < 0:
            self.bone.y = self.height
            self.bone.x = random.randint(0, int(self.width - 60))

        # Player collects coin
        if self.player.collide_widget(self.coin):
            score += 10
            self.score_label.text = "Score: " + str(score)
            self.coin.y = self.height

        # Player hits bone
        if self.player.collide_widget(self.bone):
            score -= 5
            self.score_label.text = "Score: " + str(score)
            self.bone.y = self.height

        if score <= 0:
            self.gameover()


# -------- APP --------

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(GameScreen(name="game"))
        return sm


MyApp().run()
