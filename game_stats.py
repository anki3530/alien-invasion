import High_score

class GameStats:
    def __init__(self, ai_game):
        """initiate statistics"""
        self.settings = ai_game.settings
        self.reset_stats()
        self.game_active = False
        self.high_score = High_score.highscore

    def reset_stats(self):
        """initialise statistics that can change during game."""
        self.ship_left = self.settings.ship_limit
        self.score = 0
        self.level = 1
