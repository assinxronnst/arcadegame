import arcade
import random
import os

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Subway Surfers"

PLAYER_SCALING = 0.7
BARRICADE_SCALING = 0.5
COIN_SCALING = 0.5

WORLD_SPEED = 8
PLAYER_JUMP_SPEED = 15
GRAVITY = 0.8
OBSTACLE_SPAWN_CHANCE = 0.03
COIN_SPAWN_CHANCE = 0.02

LANES = [200, 400, 600]
CURRENT_LANE = 1

PLAYER_HEIGHT_GROUND = 150

class Player(arcade.Sprite):
    def __init__(self):
        super().__init__("player.jpg", PLAYER_SCALING)
        self.center_x = LANES[CURRENT_LANE]
        self.center_y = PLAYER_HEIGHT_GROUND
        self.change_y = 0
        self.lane_index = CURRENT_LANE
        
    def update(self, delta_time=1/60):
        target_x = LANES[self.lane_index]
        if abs(self.center_x - target_x) > 2:
            self.center_x += (target_x - self.center_x) * 0.2
            
    def move_left(self):
        if self.lane_index > 0:
            self.lane_index -= 1
            
    def move_right(self):
        if self.lane_index < len(LANES) - 1:
            self.lane_index += 1

class Barricade(arcade.Sprite):
    def __init__(self):
        # Загружаем баррикаду из изображения
        super().__init__("barricade.png", BARRICADE_SCALING)
        self.center_x = random.choice(LANES)
        self.center_y = SCREEN_HEIGHT + random.randint(50, 200)
        self.speed = WORLD_SPEED
        
    def update(self, delta_time=1/60):
        self.center_y -= self.speed
        if self.center_y < -50:
            self.remove_from_sprite_lists()

class Coin(arcade.Sprite):
    def __init__(self):
        super().__init__(":resources:images/items/coinGold.png", COIN_SCALING)
        self.center_x = random.choice(LANES)
        self.center_y = SCREEN_HEIGHT + random.randint(50, 400)
        self.speed = WORLD_SPEED
        
    def update(self, delta_time=1/60):
        self.center_y -= self.speed
        self.angle += 5
        if self.center_y < -50:
            self.remove_from_sprite_lists()

class MyGame(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        
        self.player_list = None
        self.barricade_list = None
        self.coin_list = None
        
        self.player = None
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.game_speed = 1.0
        self.world_speed = WORLD_SPEED
        
        # Оптимизированный фон
        self.background_shapes = None
        self.road_offset = 0
        
        # Текстовые объекты
        self.score_text = None
        self.distance_text = None
        self.state_text = None
        
        # Звуки
        self.jump_sound = arcade.load_sound(":resources:sounds/jump3.wav")
        self.coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.crash_sound = arcade.load_sound(":resources:sounds/explosion1.wav")
        
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)
        
    def create_static_background(self):
        self.background_shapes = arcade.shape_list.ShapeElementList()
        road = arcade.shape_list.create_rectangle_filled(
            center_x=SCREEN_WIDTH // 2,
            center_y=SCREEN_HEIGHT,
            width=SCREEN_WIDTH - 300,
            height=SCREEN_HEIGHT * 2,
            color=arcade.color.GRAY
        )
        self.background_shapes.append(road)
        for lane in LANES:
            line = arcade.shape_list.create_line(
                start_x=lane,
                start_y=0,
                end_x=lane,
                end_y=SCREEN_HEIGHT * 2,
                color=arcade.color.WHITE,
                line_width=3
            )
            self.background_shapes.append(line)
            for i in range(-10, 11):
                stripe_y = i * 80
                stripe = arcade.shape_list.create_line(
                    start_x=lane - 40,
                    start_y=stripe_y,
                    end_x=lane + 40,
                    end_y=stripe_y,
                    color=arcade.color.YELLOW,
                    line_width=2
                )
                self.background_shapes.append(stripe)
        
    def setup(self):
        self.player_list = arcade.SpriteList()
        self.barricade_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        
        self.player = Player()
        self.player_list.append(self.player)
        
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.game_speed = 1.0
        self.world_speed = WORLD_SPEED
        self.road_offset = 0
        
        self.create_static_background()
        
        self.score_text = arcade.Text(f"ОЧКИ: {int(self.score)}", 20, SCREEN_HEIGHT - 40, arcade.color.YELLOW, 24, bold=True)
        self.distance_text = arcade.Text(f"ДИСТАНЦИЯ: {int(self.distance)}m", SCREEN_WIDTH - 250, SCREEN_HEIGHT - 40, arcade.color.WHITE, 20)
        
        self.barricade_list.clear()
        self.coin_list.clear()
        
    def on_draw(self):
        self.clear(arcade.color.SKY_BLUE)
        self.background_shapes.center_y = self.road_offset
        self.background_shapes.draw()
        self.barricade_list.draw()
        self.coin_list.draw()
        self.player_list.draw()
        arcade.draw_rect_filled(arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30, SCREEN_WIDTH, 60), arcade.color.BLACK)
        self.score_text.draw()
        self.distance_text.draw()
        if self.game_over:
            arcade.draw_rect_filled(arcade.rect.XYWH(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 600, 300), (0, 0, 0, 200))
            arcade.draw_text("ИГРА ОКОНЧЕНА!", SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT // 2 + 50, arcade.color.RED, 36, bold=True)
            arcade.draw_text(f"Счет: {int(self.score)}", SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 2, arcade.color.YELLOW, 28)
            arcade.draw_text("ПРОБЕЛ - рестарт", SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 60, arcade.color.WHITE, 22)
    
    def on_update(self, delta_time):
        if self.game_over:
            return
        self.player.update(delta_time)
        self.distance += self.world_speed * delta_time * 2
        self.score += delta_time * 10 * self.game_speed
        self.score_text.value = f"ОЧКИ: {int(self.score)}"
        self.distance_text.value = f"ДИСТАНЦИЯ: {int(self.distance)}m"
        self.game_speed += delta_time * 0.001
        self.world_speed = WORLD_SPEED * self.game_speed
        self.road_offset -= self.world_speed * 0.7
        if self.road_offset < -SCREEN_HEIGHT:
            self.road_offset += SCREEN_HEIGHT
        for barricade in self.barricade_list:
            barricade.speed = self.world_speed
        self.barricade_list.update(delta_time)
        for coin in self.coin_list:
            coin.speed = self.world_speed
        self.coin_list.update(delta_time)
        
        # ИСПРАВЛЕННАЯ ГЕНЕРАЦИЯ БАРРИКАД: максимум 2 баррикады одновременно
        if random.random() < OBSTACLE_SPAWN_CHANCE:
            # Выбираем случайное количество баррикад (1 или 2)
            num_to_spawn = random.choice([1, 2])
            # Выбираем случайные дорожки для спавна
            available_lanes = LANES.copy()
            random.shuffle(available_lanes)
            lanes_to_spawn = available_lanes[:num_to_spawn]
            
            for lane in lanes_to_spawn:
                new_barricade = Barricade()
                new_barricade.center_x = lane
                self.barricade_list.append(new_barricade)
        
        if random.random() < COIN_SPAWN_CHANCE:
            self.coin_list.append(Coin())
        
        # Проверка столкновений с баррикадами
        if arcade.check_for_collision_with_list(self.player, self.barricade_list):
            arcade.play_sound(self.crash_sound)
            self.game_over = True
        
        # Сбор монеток
        coin_hit = arcade.check_for_collision_with_list(self.player, self.coin_list)
        for coin in coin_hit:
            coin.remove_from_sprite_lists()
            self.score += 100 * self.game_speed
            arcade.play_sound(self.coin_sound)
    
    def on_key_press(self, key, modifiers):
        if self.game_over and key == arcade.key.SPACE:
            self.setup()
            return
        if self.game_over:
            return
        elif key == arcade.key.LEFT:
            self.player.move_left()
        elif key == arcade.key.RIGHT:
            self.player.move_right()

def main():
    window = MyGame()
    window.setup()
    arcade.run()

if __name__ == "__main__":
    main()