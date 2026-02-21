from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.label import Label
import random

Window.size = (400,600)

score = 10

# -------- HOME SCREEN --------

class HomeScreen(Screen):
    def on_enter(self):
        layout = FloatLayout()

        bg = Image(source="assets/background.png",
                   allow_stretch=True,
                   keep_ratio=False)
        layout.add_widget(bg)

        start = Button(text="START GAME",
                       size_hint=(0.5,0.1),
                       pos_hint={"center_x":0.5,"center_y":0.6})
        start.bind(on_press=self.start_game)

        quit_btn = Button(text="QUIT",
                          size_hint=(0.5,0.1),
                          pos_hint={"center_x":0.5,"center_y":0.4})
        quit_btn.bind(on_press=self.quit_game)

        layout.add_widget(start)
        layout.add_widget(quit_btn)

        self.add_widget(layout)

    def start_game(self,instance):
        self.manager.current="game"

    def quit_game(self,instance):
        App.get_running_app().stop()
        Window.close()

# -------- GAME SCREEN --------

class GameScreen(Screen):

    def on_enter(self):
        global score
        score = 10

        self.layout = FloatLayout()

        self.bg = Image(source="assets/background.png",
                        allow_stretch=True,
                        keep_ratio=False)
        self.layout.add_widget(self.bg)

        self.player = Image(source="assets/player.png",
                            size_hint=(None,None),
                            size=(80,80),
                            pos=(160,10))
        self.layout.add_widget(self.player)

        self.coin = Image(source="assets/coin.png",
                          size_hint=(None,None),
                          size=(50,50),
                          pos=(random.randint(0,350),600))
        self.layout.add_widget(self.coin)

        self.bone = Image(source="assets/bone.png",
                          size_hint=(None,None),
                          size=(60,60),
                          pos=(random.randint(0,340),600))
        self.layout.add_widget(self.bone)

        self.score_label = Label(text="Score: 10",
                                 pos_hint={"right":1,"top":1},
                                 size_hint=(0.3,0.1))
        self.layout.add_widget(self.score_label)

        self.music = SoundLoader.load("assets/background.wav")
        self.shoot = SoundLoader.load("assets/shoot.wav")

        if self.music:
            self.music.loop=True
            self.music.play()

        self.bullets=[]
        self.game_over = False

        self.add_widget(self.layout)
        Clock.schedule_interval(self.update,1/60)

    def on_touch_move(self, touch):
        if not self.game_over:
            self.player.center_x = touch.x
            if self.player.x < 0:
                self.player.x = 0
            if self.player.x > Window.width - self.player.width:
                self.player.x = Window.width - self.player.width

    def on_touch_down(self, touch):
        if not self.game_over:
            bullet = Image(source="assets/slash.png",
                           size_hint=(None,None),
                           size=(20,40),
                           pos=(self.player.center_x-10,self.player.top))
            self.layout.add_widget(bullet)
            self.bullets.append(bullet)

            if self.shoot:
                self.shoot.play()

    def gameover(self):
        self.game_over = True

        over = Label(text="GAME OVER",
                     font_size=40,
                     pos_hint={"center_x":0.5,"center_y":0.5})
        self.layout.add_widget(over)

        Clock.schedule_once(self.back_home,5)

    def back_home(self,dt):
        self.manager.current="home"

    def update(self,dt):
        global score

        if self.game_over:
            return

        for bullet in self.bullets[:]:
            bullet.y += 15
            if bullet.y > self.height:
                self.layout.remove_widget(bullet)
                self.bullets.remove(bullet)

        for bullet in self.bullets[:]:
            if bullet.collide_widget(self.bone):

                self.layout.remove_widget(bullet)
                if bullet in self.bullets:
                    self.bullets.remove(bullet)

                self.bone.y = self.height
                self.bone.x = random.randint(0,int(self.width-60))

        self.coin.y -= 5
        if self.coin.y < 0:
            self.coin.y = self.height
            self.coin.x = random.randint(0,int(self.width-50))

        self.bone.y -= 7
        if self.bone.y < 0:
            self.bone.y = self.height
            self.bone.x = random.randint(0,int(self.width-60))

        if self.player.collide_widget(self.coin):
            score += 10
            self.score_label.text = "Score: "+str(score)
            self.coin.y = self.height

        if self.player.collide_widget(self.bone):
            score -= 5
            self.score_label.text = "Score: "+str(score)
            self.bone.y = self.height

        if score <= 0:
            self.gameover()

# -------- SCREEN MANAGER --------

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name="home"))
        sm.add_widget(GameScreen(name="game"))
        return sm

MyApp().run()
