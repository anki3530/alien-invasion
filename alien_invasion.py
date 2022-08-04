import sys
import json
import pygame

from time import sleep
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from ship import Ship
from bullet import Bullet
from settings import Settings
from alien import Alien


class AlienInvasion:
    """class to manage the game and its behaviours"""

    def __init__(self):
        """initialize game and create game resources."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        # making color by mixing red green blue
        pygame.display.set_caption("Alien Invasion")
        # Create an instance to store game statistics.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        # Make the Play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """starts the main loop for the game"""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

    def _check_events(self):
        """respond to keypress and mouse movement"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """start the game when clicked on play button"""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self.settings.initialize_dynamic_settings()
            self._start_game()

    def _start_game(self):
        # reset the game stats
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # get rid of anything remaining
        self.aliens.empty()
        self.bullets.empty()

        # create a new fleet and center the ship
        self._create_fleet()
        self.ship.center_ship()

        # hide the cursor after hitting play button
        pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """responds to the pressing of key"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            filename = 'highscore.json'
            highscore = self.stats.high_score
            with open(filename, 'w') as f:
                json.dump(highscore, f)
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            self._start_game()

    def _check_keyup_events(self, event):
        """responds to the releasing of key"""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """creates a new bullet and adds in bullet group"""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        self.bullets.update()
        # gets rid of bullets reached top
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        #  print(len(self.bullets))
        self._check_bullet_alien_collision()

    def _check_bullet_alien_collision(self):
        # check if there is any bullet collided
        # if so get rid of the bullet and the respective alien
        collisions = pygame.sprite.groupcollide(self.bullets,
                                                self.aliens, True, True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            # increase level
            self.stats.level += 1
            self.sb.prep_level()

    def _update_aliens(self):
        """check if there is any alien at the edge and
        update the position of fleet"""
        self._check_fleet_edges()
        self.aliens.update()

        # look for alien-ship collision
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # looks if any alien reaching bottom
        self._check_alien_bottom()

    def _ship_hit(self):
        """respond to the ship being hit by an alien"""
        if self.stats.ship_left > 0:
            # decrement ship left & update scoreboard
            self.stats.ship_left -= 1
            self.sb.prep_ships()
            # Get rid of any remaining bullets and aliens
            self.aliens.empty()
            self.bullets.empty()
            # Create a new fleet and center the ship
            self._create_fleet()
            self.ship.center_ship()
            #pause
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

    def _check_alien_bottom(self):
        """check if any alien reaches the bottom of the screen"""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

    def _create_fleet(self):
        """create the fleet of aliens"""
        # make an alien
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2*alien_width)
        number_alien_x = available_space_x // (2*alien_width)

        # determine the number of rows that fit on screen
        ship_height = self.ship.rect.height
        available_space_y = (self.settings.screen_height - ship_height -(3*alien_height))
        number_rows = available_space_y // (2*alien_height)

        # creating the full fleet of aliens

        for row_number in range(number_rows):
            for alien_number in range(number_alien_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien_height + 2 * alien_height * row_number
        self.aliens.add(alien)

    def _check_fleet_edges(self):
        """response appropriately when any alien reaches to the edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """drops the entire fleet and change the fleet's direction"""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _update_screen(self):
        """update the screen and flip the new screen"""
        self.screen.fill(self.settings.bg_color)  # fills the background with the color we made
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # draw the score information
        self.sb.show_score()

        # draw the play button if the game is inactive
        if not self.stats.game_active:
            self.play_button.draw_button()
        pygame.display.flip()


if __name__ == '__main__':
    ai = AlienInvasion()
    ai.run_game()