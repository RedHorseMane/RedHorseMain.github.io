import pygame
import sys
import random
import math
from enum import Enum

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)


# Game states
class GameState(Enum):
    MENU = 0
    STORY = 1
    MAP = 2
    FLYING_TUTORIAL = 3
    PECKING_GAME = 4
    DECISION = 5
    FLOWER_CHALLENGE = 6
    SNAKE_ENCOUNTER = 7
    NEST_BUILDING = 8
    GAME_OVER = 9
    WIN = 10


class Player:
    def __init__(self):
        # Player stats
        self.feathers = 0
        self.health = 100
        self.unlocked_zones = ["Tree Tops", "Home Forest"]
        self.unlocked_decorations = []
        self.unlocked_hats = []
        self.current_hat = None

        # Player position and movement
        self.x = 100
        self.y = 300
        self.velocity_y = 0
        self.velocity_x = 0
        self.jumping = False
        self.flying = False
        self.facing_right = True

        # Animation state
        self.animation_frame = 0
        self.animation_speed = 0.2

        # Create simple rectangle for collision detection
        self.rect = pygame.Rect(self.x, self.y, 40, 40)

        # Load images
        self.images_right = [pygame.Surface((40, 40)), pygame.Surface((40, 40))]
        self.images_left = [pygame.Surface((40, 40)), pygame.Surface((40, 40))]

        # Color the player surfaces red for now (will be replaced with actual sprites)
        for img in self.images_right + self.images_left:
            img.fill(RED)

        self.current_image = self.images_right[0]

    def update(self, obstacles):
        # Gravity
        self.velocity_y += 0.5
        if self.velocity_y > 10:
            self.velocity_y = 10

        # Apply velocities
        new_y = self.y + self.velocity_y
        new_x = self.x + self.velocity_x

        # Check for collisions with obstacles
        self.rect.x = new_x
        self.rect.y = new_y

        collision = False
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                collision = True
                # Handle collision (simplified for now)
                if self.velocity_y > 0:  # Falling
                    self.rect.bottom = obstacle.top
                    self.jumping = False
                    self.flying = False
                    self.velocity_y = 0
                elif self.velocity_y < 0:  # Jumping/flying up
                    self.rect.top = obstacle.bottom
                    self.velocity_y = 0

                if self.velocity_x > 0:  # Moving right
                    self.rect.right = obstacle.left
                    self.velocity_x = 0
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = obstacle.right
                    self.velocity_x = 0

        # Update position from rect
        self.x = self.rect.x
        self.y = self.rect.y

        # Animation
        self.animation_frame += self.animation_speed
        if self.animation_frame >= len(self.images_right):
            self.animation_frame = 0

        if self.facing_right:
            self.current_image = self.images_right[int(self.animation_frame)]
        else:
            self.current_image = self.images_left[int(self.animation_frame)]

        # Reset horizontal velocity for next frame
        self.velocity_x *= 0.9
        if abs(self.velocity_x) < 0.1:
            self.velocity_x = 0

    def jump(self):
        if not self.jumping:
            self.velocity_y = -12
            self.jumping = True

    def fly(self):
        # Simplified flying mechanic - apply upward force
        if self.flying or self.jumping:
            self.velocity_y = -6
            self.flying = True

    def move_left(self):
        self.velocity_x = -5
        self.facing_right = False

    def move_right(self):
        self.velocity_x = 5
        self.facing_right = True

    def peck(self, target_objects):
        # Define a small area in front of the woodpecker
        peck_rect = pygame.Rect(
            self.rect.right if self.facing_right else self.rect.left - 20,
            self.rect.centery - 10,
            20,
            20,
        )

        # Check for collision with peckable objects
        for obj in target_objects:
            if peck_rect.colliderect(obj.rect):
                return obj
        return None

    def draw(self, screen):
        screen.blit(self.current_image, (self.x, self.y))

        # Draw peck area for debugging
        if self.facing_right:
            pygame.draw.rect(
                screen, YELLOW, (self.rect.right, self.rect.centery - 10, 20, 20), 1
            )
        else:
            pygame.draw.rect(
                screen, YELLOW, (self.rect.left - 20, self.rect.centery - 10, 20, 20), 1
            )


class PeckableObject:
    def __init__(self, x, y, width, height, type="tree"):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = type
        self.health = 3
        self.has_larva = random.choice([True, False])
        self.pecked = False

        # Simple color coding for now
        if self.type == "tree":
            self.color = BROWN
        elif self.type == "flower":
            self.color = (255, 192, 203)  # Pink
        else:
            self.color = YELLOW

    def peck(self):
        self.health -= 1
        self.pecked = True
        return self.has_larva and self.health <= 0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.pecked:
            # Show "damage" from pecking
            pygame.draw.line(
                screen,
                BLACK,
                (self.rect.left, self.rect.top),
                (self.rect.right, self.rect.bottom),
                2,
            )


class Snake:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 30
        self.speed = 2
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.active = True

    def update(self, player_x):
        # Snake follows player's x position
        if self.x < player_x:
            self.x += self.speed
        else:
            self.x -= self.speed

        self.rect.x = self.x

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, (0, 100, 0), self.rect)  # Dark green snake
            # Draw snake eyes
            pygame.draw.circle(
                screen, BLACK, (self.rect.left + 10, self.rect.top + 10), 3
            )


class NestPiece:
    def __init__(self, x, y, piece_type):
        self.x = x
        self.y = y
        self.piece_type = piece_type
        self.width = 40
        self.height = 20
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.placed = False

        # Color based on type
        if piece_type == "twig":
            self.color = (101, 67, 33)  # Dark brown
        elif piece_type == "leaf":
            self.color = (0, 128, 0)  # Green
        elif piece_type == "moss":
            self.color = (107, 142, 35)  # Olive green
        else:
            self.color = BROWN

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.rect.x = self.x
        self.rect.y = self.y


class Button:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        text,
        color=(200, 200, 200),
        hover_color=(150, 150, 150),
    ):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.SysFont("Arial", 20)
        self.is_hovered = False

    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)  # Border

        text_surface = self.font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.is_hovered
        return False


class WorldMap:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.zones = [
            {
                "name": "Tree Tops",
                "position": (200, 150),
                "color": GREEN,
                "unlocked": True,
            },
            {
                "name": "Home Forest",
                "position": (300, 250),
                "color": BROWN,
                "unlocked": True,
            },
            {
                "name": "Flower Meadow",
                "position": (500, 200),
                "color": (255, 192, 203),
                "unlocked": False,
            },
            {
                "name": "Lake",
                "position": (400, 350),
                "color": (0, 0, 255),
                "unlocked": False,
            },
        ]
        self.selected_zone = None
        self.font = pygame.font.SysFont("Arial", 16)
        self.title_font = pygame.font.SysFont("Arial", 24)

    def draw(self, screen, unlocked_zones):
        # Draw map background
        screen.fill((230, 230, 200))  # Light tan

        # Draw title
        title = self.title_font.render("Choose Your Adventure", True, BLACK)
        screen.blit(title, (self.width // 2 - title.get_width() // 2, 50))

        # Update unlocked status
        for zone in self.zones:
            zone["unlocked"] = zone["name"] in unlocked_zones

        # Draw zones and paths
        for i, zone in enumerate(self.zones):
            # Draw paths between zones
            if i > 0:
                prev_zone = self.zones[i - 1]
                pygame.draw.line(
                    screen, BLACK, prev_zone["position"], zone["position"], 2
                )

            # Draw zone circle
            color = zone["color"] if zone["unlocked"] else (150, 150, 150)
            pygame.draw.circle(screen, color, zone["position"], 30)
            pygame.draw.circle(screen, BLACK, zone["position"], 30, 2)

            # Draw zone name
            text = self.font.render(zone["name"], True, BLACK)
            screen.blit(
                text,
                (zone["position"][0] - text.get_width() // 2, zone["position"][1] + 40),
            )

            # Highlight selected zone
            if self.selected_zone == zone["name"]:
                pygame.draw.circle(screen, WHITE, zone["position"], 35, 3)

    def handle_click(self, mouse_pos, unlocked_zones):
        for zone in self.zones:
            distance = math.sqrt(
                (mouse_pos[0] - zone["position"][0]) ** 2
                + (mouse_pos[1] - zone["position"][1]) ** 2
            )
            if distance <= 30 and zone["name"] in unlocked_zones:
                self.selected_zone = zone["name"]
                return zone["name"]
        return None


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("William's Wild Adventure")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = GameState.MENU
        self.player = Player()
        self.obstacles = []
        self.peckable_objects = []
        self.enemies = []
        self.nest_pieces = []
        self.nest_slots = []
        self.buttons = []
        self.score = 0
        self.level_timer = 0
        self.story_phase = 0
        self.font = pygame.font.SysFont("Arial", 24)
        self.small_font = pygame.font.SysFont("Arial", 18)
        self.world_map = WorldMap(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Game progress
        self.completed_levels = set()
        self.current_zone = "Tree Tops"

        # Initialize menu buttons
        self.init_menu()

        # Load educational content
        self.educational_tips = {
            "Tree Tops": "Woodpeckers have strong beaks for drilling into trees!",
            "Home Forest": "Woodpeckers create homes by pecking holes in trees.",
            "Flower Meadow": "Some birds like hummingbirds can hover to drink nectar!",
            "Snake Encounter": "Birds need to be alert to avoid predators like snakes.",
        }

        # Initialize game elements based on level
        self.init_level()

    def init_menu(self):
        # Clear existing buttons
        self.buttons.clear()

        # Add menu buttons
        start_button = Button(SCREEN_WIDTH // 2 - 100, 250, 200, 50, "Start Adventure")
        instructions_button = Button(
            SCREEN_WIDTH // 2 - 100, 320, 200, 50, "Instructions"
        )
        quit_button = Button(SCREEN_WIDTH // 2 - 100, 390, 200, 50, "Quit")

        self.buttons.extend([start_button, instructions_button, quit_button])

    def init_level(self):
        # Reset level-specific elements
        self.obstacles.clear()
        self.peckable_objects.clear()
        self.enemies.clear()
        self.nest_pieces.clear()
        self.nest_slots.clear()
        self.level_timer = 0

        # Add ground as an obstacle
        ground = pygame.Rect(0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50)
        self.obstacles.append(ground)

        if self.state == GameState.FLYING_TUTORIAL:
            # Add some platforms for the flying tutorial
            self.obstacles.extend(
                [
                    pygame.Rect(200, 450, 100, 20),
                    pygame.Rect(400, 350, 100, 20),
                    pygame.Rect(600, 250, 100, 20),
                ]
            )

            # Reset player position
            self.player.x = 100
            self.player.y = SCREEN_HEIGHT - 150
            self.player.rect.x = self.player.x
            self.player.rect.y = self.player.y

        elif self.state == GameState.PECKING_GAME:
            # Add trees to peck
            for i in range(5):
                tree = PeckableObject(
                    100 + i * 150, SCREEN_HEIGHT - 300, 40, 250, "tree"
                )
                self.peckable_objects.append(tree)

            # Reset player position
            self.player.x = 100
            self.player.y = SCREEN_HEIGHT - 150
            self.player.rect.x = self.player.x
            self.player.rect.y = self.player.y

        elif self.state == GameState.SNAKE_ENCOUNTER:
            # Add a snake enemy
            snake = Snake(SCREEN_WIDTH - 100, SCREEN_HEIGHT - 80)
            self.enemies.append(snake)

            # Reset player position
            self.player.x = 100
            self.player.y = SCREEN_HEIGHT - 150
            self.player.rect.x = self.player.x
            self.player.rect.y = self.player.y

        elif self.state == GameState.DECISION:
            # Create decision buttons
            self.buttons.clear()

            follow_button = Button(
                SCREEN_WIDTH // 2 - 200, 300, 180, 50, "Follow the Sunbird"
            )
            stay_button = Button(SCREEN_WIDTH // 2 + 20, 300, 180, 50, "Stay at Home")

            self.buttons.extend([follow_button, stay_button])

        elif self.state == GameState.FLOWER_CHALLENGE:
            # Add flowers for hovering challenge
            for i in range(4):
                flower = PeckableObject(
                    150 + i * 180, SCREEN_HEIGHT - 130, 50, 80, "flower"
                )
                self.peckable_objects.append(flower)

            # Reset player position
            self.player.x = 100
            self.player.y = SCREEN_HEIGHT - 200
            self.player.rect.x = self.player.x
            self.player.rect.y = self.player.y

        elif self.state == GameState.NEST_BUILDING:
            # Create nest building puzzle pieces
            piece_types = ["twig", "leaf", "moss", "twig", "leaf"]

            # Create pieces to place
            for i, piece_type in enumerate(piece_types):
                piece = NestPiece(50 + i * 60, SCREEN_HEIGHT - 100, piece_type)
                self.nest_pieces.append(piece)

            # Create slots where pieces go
            for i in range(5):
                slot = pygame.Rect(300 + i * 50, 300, 40, 20)
                self.nest_slots.append(slot)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Button clicks
            for button in self.buttons:
                if button.is_clicked(event):
                    self.handle_button_click(button)

            # Map clicks
            if self.state == GameState.MAP:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    zone = self.world_map.handle_click(
                        event.pos, self.player.unlocked_zones
                    )
                    if zone:
                        self.current_zone = zone
                        if zone == "Tree Tops":
                            self.state = GameState.FLYING_TUTORIAL
                        elif zone == "Home Forest":
                            self.state = GameState.PECKING_GAME
                        elif zone == "Flower Meadow":
                            self.state = GameState.FLOWER_CHALLENGE
                        self.init_level()

            # Nest building drag and drop
            if self.state == GameState.NEST_BUILDING:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Check if clicked on a piece
                    for piece in self.nest_pieces:
                        if piece.rect.collidepoint(event.pos) and not piece.placed:
                            self.dragging_piece = piece
                            self.drag_offset_x = piece.rect.x - event.pos[0]
                            self.drag_offset_y = piece.rect.y - event.pos[1]
                            break

                elif event.type == pygame.MOUSEBUTTONUP:
                    if hasattr(self, "dragging_piece"):
                        # Check if piece is over a slot
                        for slot in self.nest_slots:
                            if self.dragging_piece.rect.colliderect(slot):
                                self.dragging_piece.rect.x = slot.x
                                self.dragging_piece.rect.y = slot.y
                                self.dragging_piece.placed = True
                                # Check if all pieces are placed
                                if all(piece.placed for piece in self.nest_pieces):
                                    self.completed_levels.add("Nest Building")
                                    self.score += 50
                                    self.player.feathers += 3
                                    # Wait a bit then go to win state
                                    self.level_timer = 0
                        delattr(self, "dragging_piece")

                elif event.type == pygame.MOUSEMOTION:
                    if hasattr(self, "dragging_piece"):
                        self.dragging_piece.rect.x = event.pos[0] + self.drag_offset_x
                        self.dragging_piece.rect.y = event.pos[1] + self.drag_offset_y
                        self.dragging_piece.x = self.dragging_piece.rect.x
                        self.dragging_piece.y = self.dragging_piece.rect.y

            # Keyboard events
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.state in [
                        GameState.FLYING_TUTORIAL,
                        GameState.PECKING_GAME,
                        GameState.FLOWER_CHALLENGE,
                        GameState.SNAKE_ENCOUNTER,
                    ]:
                        self.player.jump()

                if event.key == pygame.K_p:
                    if self.state == GameState.PECKING_GAME:
                        pecked_object = self.player.peck(self.peckable_objects)
                        if pecked_object:
                            found_larva = pecked_object.peck()
                            if found_larva:
                                self.score += 10
                                self.player.feathers += 1

                    elif self.state == GameState.FLOWER_CHALLENGE:
                        pecked_object = self.player.peck(self.peckable_objects)
                        if pecked_object and not pecked_object.pecked:
                            pecked_object.pecked = True
                            self.score += 5

                if event.key == pygame.K_RETURN:
                    if self.state == GameState.STORY:
                        self.story_phase += 1
                        if self.story_phase >= 3:  # After showing 3 story screens
                            self.state = GameState.FLYING_TUTORIAL
                            self.init_level()

                    elif self.state in [GameState.GAME_OVER, GameState.WIN]:
                        self.state = GameState.MENU
                        self.init_menu()

                    elif self.state == GameState.MAP:
                        if self.world_map.selected_zone:
                            self.current_zone = self.world_map.selected_zone
                            if self.current_zone == "Tree Tops":
                                self.state = GameState.FLYING_TUTORIAL
                            elif self.current_zone == "Home Forest":
                                self.state = GameState.PECKING_GAME
                            elif self.current_zone == "Flower Meadow":
                                self.state = GameState.FLOWER_CHALLENGE
                            self.init_level()

                if event.key == pygame.K_ESCAPE:
                    if self.state not in [
                        GameState.MENU,
                        GameState.STORY,
                        GameState.GAME_OVER,
                        GameState.WIN,
                    ]:
                        self.state = GameState.MAP

    def handle_button_click(self, button):
        if self.state == GameState.MENU:
            if button.text == "Start Adventure":
                self.state = GameState.STORY
                self.story_phase = 0

            elif button.text == "Instructions":
                # Create instruction buttons
                self.buttons.clear()
                back_button = Button(
                    SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 80, 200, 40, "Back to Menu"
                )
                self.buttons.append(back_button)
                self.state = GameState.INSTRUCTIONS

            elif button.text == "Quit":
                self.running = False

        elif self.state == GameState.INSTRUCTIONS:
            if button.text == "Back to Menu":
                self.state = GameState.MENU
                self.init_menu()

        elif self.state == GameState.DECISION:
            if button.text == "Follow the Sunbird":
                self.state = GameState.FLOWER_CHALLENGE
                self.current_zone = "Flower Meadow"
                self.player.unlocked_zones.append("Flower Meadow")
                self.init_level()

            elif button.text == "Stay at Home":
                self.state = GameState.SNAKE_ENCOUNTER
                self.init_level()

    def handle_input(self):
        keys = pygame.key.get_pressed()

        if self.state in [
            GameState.FLYING_TUTORIAL,
            GameState.PECKING_GAME,
            GameState.FLOWER_CHALLENGE,
            GameState.SNAKE_ENCOUNTER,
        ]:
            if keys[pygame.K_LEFT]:
                self.player.move_left()

            if keys[pygame.K_RIGHT]:
                self.player.move_right()

            if keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.fly()

    def update(self):
        # Update button hover states
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons:
            button.update(mouse_pos)

        # Update game logic based on current state
        if self.state in [
            GameState.FLYING_TUTORIAL,
            GameState.PECKING_GAME,
            GameState.FLOWER_CHALLENGE,
            GameState.SNAKE_ENCOUNTER,
        ]:

            self.player.update(self.obstacles)

            # Update enemies
            for enemy in self.enemies:
                enemy.update(self.player.x)

                # Check for collision with player
                if enemy.rect.colliderect(self.player.rect):
                    self.player.health -= 10
                    # Push player away from snake
                    if self.player.x < enemy.x:
                        self.player.x -= 30
                    else:
                        self.player.x += 30
                    self.player.rect.x = self.player.x

                    if self.player.health <= 0:
                        self.state = GameState.GAME_OVER

            # Update timer
            self.level_timer += 1 / 60  # Assuming 60 FPS

            # Level-specific updates
            if self.state == GameState.FLYING_TUTORIAL:
                # Check if player reached the highest platform
                highest_platform = self.obstacles[
                    3
                ]  # The third platform added (index 3 because ground is at 0)
                if (
                    self.player.rect.colliderect(highest_platform)
                    and "Flying Tutorial" not in self.completed_levels
                ):
                    self.completed_levels.add("Flying Tutorial")
                    self.score += 50
                    self.player.feathers += 3
                    # Show a transition after a delay
                    if self.level_timer > 3:  # 3 seconds after completion
                        self.state = GameState.PECKING_GAME
                        self.init_level()

            elif self.state == GameState.PECKING_GAME:
                # Check if player found enough larvae
                larvae_found = sum(
                    1
                    for obj in self.peckable_objects
                    if obj.pecked and obj.has_larva and obj.health <= 0
                )
                if larvae_found >= 2 and "Pecking Game" not in self.completed_levels:
                    self.completed_levels.add("Pecking Game")
                    self.score += 50
                    # Transition to decision point
                    if self.level_timer > 3:
                        self.state = GameState.DECISION
                        self.init_level()

            elif self.state == GameState.FLOWER_CHALLENGE:
                # Check if player visited all flowers
                flowers_visited = sum(1 for obj in self.peckable_objects if obj.pecked)
                if (
                    flowers_visited >= 3
                    and "Flower Challenge" not in self.completed_levels
                ):
                    self.completed_levels.add("Flower Challenge")
                    self.score += 50
                    self.player.feathers += 2
                    # Transition to next level
                    if self.level_timer > 3:
                        self.state = GameState.SNAKE_ENCOUNTER
                        self.init_level()

            elif self.state == GameState.SNAKE_ENCOUNTER:
                # Check if player escaped the snake for long enough
                if (
                    self.level_timer > 15
                    and "Snake Encounter" not in self.completed_levels
                ):  # 15 seconds survival
                    self.completed_levels.add("Snake Encounter")
                    self.score += 75
                    self.player.feathers += 4
                    # Transition to next level
                    self.state = GameState.NEST_BUILDING
                    self.init_level()

            elif self.state == GameState.NEST_BUILDING:
                # Check if all pieces are placed
                if "Nest Building" in self.completed_levels and self.level_timer > 3:
                    self.state = GameState.WIN

            # Check for falling off screen
            if self.player.y > SCREEN_HEIGHT:
                self.player.health -= 25
                self.player.x = 100
                self.player.y = SCREEN_HEIGHT - 150
                self.player.rect.x = self.player.x
                self.player.rect.y = self.player.y

                if self.player.health <= 0:
                    self.state = GameState.GAME_OVER

    def render_menu(self):
        # Draw menu background
        self.screen.fill(SKY_BLUE)

        # Draw title
        title_font = pygame.font.SysFont("Arial", 48)
        title = title_font.render("William's Wild Adventure", True, BLACK)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))

        # draw menu buttons
        for button in self.buttons:
            button.draw(self.screen)

        # small footer hint
        footer_font = pygame.font.SysFont("Arial", 18)
        hint = footer_font.render("Press ESC to quit", True, BLACK)
        self.screen.blit(
            hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 40)
        )

    # ──────────────────────────────────────────────────────────────
    #  END OF Game.render_menu
    # ──────────────────────────────────────────────────────────────
        pygame.display.flip()          # <-- add this line


def main() -> None:
    game = Game()

    while game.running:
        # 1. poll events so the window stays responsive
        game.handle_events()

        # 2. keyboard-state input that isn’t event-based
        game.handle_input()

        # 3. advance the simulation
        game.update()

        # 4. draw the current scene
        if game.state == GameState.MENU:
            game.render_menu()
        else:
            # placeholder until the other render_* functions are written
            game.screen.fill(SKY_BLUE)

        # 5. present the frame
        pygame.display.flip()

        # 6. keep a steady frame-rate
        game.clock.tick(FPS)

if __name__ == "__main__":
    main()
