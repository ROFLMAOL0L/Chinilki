import pygame
import math
import trigonometry_functions as t_f
import game_settings as g_s

keyboard_controls = [{pygame.K_w: False, pygame.K_a: False, pygame.K_s: False, pygame.K_d: False,
                      pygame.K_j: False, pygame.K_k: False},
                     {pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_DOWN: False, pygame.K_RIGHT: False,
                      pygame.K_f: False, pygame.K_g: False},
                     {pygame.JOYAXISMOTION: [0, 0], pygame.JOYBUTTONDOWN: False},
                     {pygame.JOYAXISMOTION: [0, 0], pygame.JOYBUTTONDOWN: False}
                     ]

# Animations are stored as follows: models[model[walk up, walk left, walk down, walk right, stand in 4 dir] ]
player_models = [
    [[pygame.image.load("sprites/models/zelda/zelda_walk_up_0.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_up_1.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_up_2.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_up_3.png"),
      ],
     [pygame.image.load("sprites/models/zelda/zelda_walk_left_0.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_left_1.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_left_2.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_left_3.png"),
      ],
     [pygame.image.load("sprites/models/zelda/zelda_walk_down_0.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_down_1.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_down_2.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_down_3.png"),
      ],
     [pygame.image.load("sprites/models/zelda/zelda_walk_right_0.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_right_1.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_right_2.png"),
     pygame.image.load("sprites/models/zelda/zelda_walk_right_3.png"),
      ],
     [pygame.image.load("sprites/models/zelda/zelda_stand_up.png"),
     pygame.image.load("sprites/models/zelda/zelda_stand_left.png"),
     pygame.image.load("sprites/models/zelda/zelda_stand_down.png"),
     pygame.image.load("sprites/models/zelda/zelda_stand_right.png"),
      ]
     ]]


class Game:
    def __init__(self):
        self.screen_size = (g_s.screen_width, g_s.screen_height)
        self._run = True
        try:
            pygame.init()
            self.clock = pygame.time.Clock()
            self.screen = pygame.display.set_mode(self.screen_size, pygame.FULLSCREEN)
        except ImportError:
            self._run = False
            print('An error occurred while loading modules. In case if you are sure you have Pygame module installed'
                  ', we suggest you reinstall the game.')
        except:
            self._run = False
            print('An unknown error occurred while loading.')

        # Loading main background (I call the class BackgroundFloor to avoid repetition)
        self._background = BackgroundFloor()

        # Get the joysticks
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

    def execution(self):
        a = [Conveyor(100, "sprites/objects/conveyor/conveyor_0.PNG"),
             Conveyor(100, "sprites/objects/conveyor/conveyor_1.PNG")]

        players = [PlayerZelda(0), PlayerZelda(1)]

        if len(self.joysticks) > 0:
            for i in range(len(self.joysticks)):
                players.append(PlayerJoystick(2 + i))

        car_creation_button_instance = CarCreationButton()

        joy_horizontal_axis, joy_vertical_axis = 0, 0

        frame_number = 0
        while self._run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return 1
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return 1
                    if event.key in keyboard_controls[0]:
                        keyboard_controls[0][event.key] = True
                    elif event.key in keyboard_controls[1]:
                        keyboard_controls[1][event.key] = True
                if event.type == pygame.KEYUP:
                    if event.key in keyboard_controls[0]:
                        keyboard_controls[0][event.key] = False
                    elif event.key in keyboard_controls[1]:
                        keyboard_controls[1][event.key] = False
                if event.type == pygame.JOYAXISMOTION:
                    if event.axis == 0:
                        joy_horizontal_axis = event.value
                    if event.axis == 1:
                        joy_vertical_axis = event.value
                    keyboard_controls[2 + event.instance_id][pygame.JOYAXISMOTION] = [joy_horizontal_axis,
                                                                                      joy_vertical_axis]
            for player in players:
                player.update_walk()
                player.update_animation()

                if car_creation_button_instance.image != car_creation_button_instance.button_pressed:
                    car_creation_button_instance.update_car((player.pos_x, player.pos_y))


            self.screen.blit(self._background.image, self._background.rect)
            # self.screen.blit(a[frame_number // 30].image, a[frame_number // 30].rect)
            # self.screen.blit(car_creation_button_instance.image, car_creation_button_instance.rect)

            for player in players:
                self.screen.blit(player.image, (player.pos_x, player.pos_y))

            '''for i in range(len(players_joystick)):
                keyboard_controls[2 + i][pygame.JOYAXISMOTION] = [0, 0]'''

            pygame.display.update()

            self.clock.tick(g_s.FPS)

            frame_number += 1
            if frame_number >= g_s.FPS:
                frame_number = 0


class PlayerZelda(pygame.sprite.Sprite):
    def __init__(self, index_number):
        pygame.sprite.Sprite.__init__(self)
        # Getting the standard skin
        self.up_anim = player_models[0][0]
        self.left_anim = player_models[0][1]
        self.down_anim = player_models[0][2]
        self.right_anim = player_models[0][3]
        self.stand_anim = player_models[0][4]
        self.image = self.stand_anim[0]

        # Getting "frame counter" for animations
        self.animation_frame = 0

        # Used to separate WASD and Arrows players
        self._number = index_number

        self.rect = self.image.get_rect(center=(self.image.get_width() / 2,
                                                self.image.get_height()))

        self.speed = 0
        self.direction_angle = 0
        self.max_speed = g_s.players_max_speed
        self.acceleration = -self.max_speed / 10

        self.pos_x, self.pos_y = 1000 + index_number * g_s.cell_size, 700

        # [Up, Left, Down, Right]
        self.walking = [False, False, False, False]

        # Decide if it`s a joystick player
        if index_number > 1:
            self._is_joystick = True
        else:
            self._is_joystick = False

    def update_walk(self):
        if not self._is_joystick:
            # Getting the "directions" that the player has pressed
            for i, key in enumerate(keyboard_controls[self._number].keys()):
                if i < 4:
                    self.walking[i] = keyboard_controls[self._number][key]

            # Delete opposite movement
            if self.walking[0] == self.walking[2]:
                self.walking[0], self.walking[2] = False, False
            if self.walking[1] == self.walking[3]:
                self.walking[1], self.walking[3] = False, False

            if self.walking.count(True) != 0:   # player is pressing WASD
                self.acceleration = self.max_speed / 10
            else:  # player is not pressing WASD
                if self.speed > 0:   # player stopped pressing WASD a few moments ago, we have momentum, but decelerate
                    self.acceleration = -self.max_speed / 10
                else:   # player stopped decelerating, zero momentum, zero speed, change the animation and acceleration
                    if self.acceleration != 0:
                        self.acceleration = 0
                        self.update_animation(stop_direction=self.direction_angle // 90 - 1)

            # Handle speed logic
            self.speed += self.acceleration
            if self.speed < 0:
                self.speed = 0
            elif self.speed > self.max_speed:
                self.speed = self.max_speed
            # Handle direction logic since we need to make the angle = 0 if we don`t movea

            # Handle making a direction out of WASD
            if self.walking[0]:
                self.direction_angle = 90
                if self.walking[1]:
                    self.direction_angle += 45
                elif self.walking[3]:
                    self.direction_angle -= 45
            elif self.walking[2]:
                self.direction_angle = 270
                if self.walking[1]:
                    self.direction_angle -= 45
                elif self.walking[3]:
                    self.direction_angle += 45
            elif self.walking[1]:
                self.direction_angle = 180
            elif self.walking[3]:
                self.direction_angle = 0

            # Actual changes in position
            self.pos_x += self.speed * math.cos(self.direction_angle / 180 * 3.1415926)
            self.pos_y -= self.speed * math.sin(self.direction_angle / 180 * 3.1415926)
        else:   # ITS A JOYSTICK!!!
            print('ASD')
            # Getting the "directions" that the player has pressed  !!!(BUT FOR JOYSTICKS)!!!!
            dx = keyboard_controls[self._number][pygame.JOYAXISMOTION][0]
            if 0.0000001 < dx < 0.0000001:
                dx = 0
            elif dx > 1:
                dx = 1
            elif dx < -1:
                dx = -1
            dy = keyboard_controls[self._number][pygame.JOYAXISMOTION][1]
            if 0.0000001 < dy < 0.0000001:
                dy = 0
            elif dy > 1:
                dy = 1
            elif dy < -1:
                dy = -1
            dx *= (math.sqrt(2) / 2)
            dy *= (math.sqrt(2) / 2)
            dc = math.sqrt(dx ** 2 + dy ** 2)
            if dc != 0:
                self.direction_angle = t_f.sin_to_a(dx / dc, dy / dc)
            else:
                self.direction_angle = 0
            # Deciding where the player is moving
            if dx != dy != 0:
                self.walking[int(self.direction_angle // 90)] = True
            else:
                self.walking = [False, False, False, False]

            if self.walking.count(True) != 0:  # player is pressing WASD
                self.acceleration = self.max_speed / 10
            else:  # player is not pressing WASD
                if self.speed > 0:  # player stopped pressing WASD a few moments ago, we have momentum, but decelerate
                    self.acceleration = -self.max_speed / 10
                else:  # player stopped decelerating, zero momentum, zero speed, change the animation and acceleration
                    if self.acceleration != 0:
                        print(self.direction_angle, dx, dy)
                        self.acceleration = 0
                        self.update_animation(stop_direction=int(self.direction_angle // 90 - 1))

            # Handle speed logic
            self.speed += self.acceleration
            if self.speed < 0:
                self.speed = 0
            elif self.speed > self.max_speed:
                self.speed = self.max_speed

            # Actual changes in position
            self.pos_x += self.speed * math.cos(self.direction_angle / 180 * 3.1415926)
            self.pos_y -= self.speed * math.sin(self.direction_angle / 180 * 3.1415926)

    def update_animation(self, stop_direction=-2):
        if self.walking[0]:
            self.image = self.up_anim[self.animation_frame // 6 % 4]
        elif self.walking[1]:
            self.image = self.left_anim[self.animation_frame // 6 % 4]
        elif self.walking[2]:
            self.image = self.down_anim[self.animation_frame // 6 % 4]
        elif self.walking[3]:
            self.image = self.right_anim[self.animation_frame // 6 % 4]
        elif stop_direction != -2:
            self.image = self.stand_anim[stop_direction]

        self.animation_frame += 1
        if self.animation_frame > 60:
            self.animation_frame = 0


class PlayerJoystick(PlayerZelda):
    def __init__(self, index_number):
        PlayerZelda.__init__(self, index_number)

    def update_walk_joy(self):
        # Getting the "directions" that the player has pressed  !!!(BUT FOR JOYSTICKS)!!!!
        dx = keyboard_controls[self._number][pygame.JOYAXISMOTION][0]
        if 0.01 < dx < 0.01:
            dx = 0
        elif dx > 1:
            dx = 1
        elif dx < -1:
            dx = -1
        dy = keyboard_controls[self._number][pygame.JOYAXISMOTION][1]
        if 0.01 < dy < 0.01:
            dy = 0
        elif dy > 1:
            dy = 1
        elif dy < -1:
            dy = -1
        self.direction_angle = t_f.sin_to_a(dx, dy)
        print(dx, dy, self.direction_angle)
        # Deciding where the player is moving
        if dx != dy != 0:
            self.walking[int(self.direction_angle // 90)] = True
        else:
            self.walking = [False, False, False, False]

        if self.walking.count(True) != 0:  # player is pressing WASD
            self.acceleration = self.max_speed / 10
        else:  # player is not pressing WASD
            if self.speed > 0:  # player stopped pressing WASD a few moments ago, we have momentum, but decelerate
                self.acceleration = -self.max_speed / 10
            else:  # player stopped decelerating, zero momentum, zero speed, change the animation and acceleration
                if self.acceleration != 0:
                    self.acceleration = 0
                    self.update_animation(stop_direction=int(self.direction_angle // 90 - 1))

        # Handle speed logic
        self.speed += self.acceleration
        if self.speed < 0:
            self.speed = 0
        elif self.speed > self.max_speed:
            self.speed = self.max_speed

        # Actual changes in position
        self.pos_x += self.speed * math.cos(self.direction_angle / 180 * 3.1415926)
        self.pos_y -= self.speed * math.sin(self.direction_angle / 180 * 3.1415926)


class CarCreationButton(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.button_normal = pygame.image.load("sprites/objects/car_creation_button/button_normal.png").convert_alpha()
        self.button_in_range = pygame.image.load("sprites/objects/car_creation_button/button_in_range.png").convert_alpha()
        self.button_pressed = pygame.image.load("sprites/objects/car_creation_button/button_pressed.png").convert_alpha()
        self.image = self.button_normal
        self.pos_x, self.pos_y = g_s.screen_width - 100, 200
        self.rect = self.image.get_rect(center=(self.pos_x, self.pos_y))

    def update_car(self, player_pos, pressed=False):
        if pressed:
            if (player_pos[0] - self.pos_x) ** 2 + (player_pos[1] - self.pos_y) ** 2 < 300 ** 2:
                self.image = self.button_pressed
        else:
            if (player_pos[0] - self.pos_x) ** 2 + (player_pos[1] - self.pos_y) ** 2 < 300 ** 2:
                self.image = self.button_in_range
            else:
                self.image = self.button_normal


class Conveyor(pygame.sprite.Sprite):
    def __init__(self, x, sprite_name):
        pygame.sprite.Sprite.__init__(self)
        self.sprites = pygame.sprite.Group()
        self.image = pygame.image.load(sprite_name).convert_alpha()
        self.rect = self.image.get_rect(center=(self.image.get_width() / 2, g_s.screen_height -
                                                self.image.get_height() / 2))


class BackgroundFloor(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('sprites/textures/background/background_sprite_0.png').convert_alpha()
        self.rect = self.image.get_rect(center=(self.image.get_width() / 2,
                                                g_s.screen_height - self.image.get_height() / 2))


if __name__ == '__main__':
    print('Starting...')
    game_instance = Game()
    game_instance.execution()
    print('Program over.')
