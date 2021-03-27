class ScoreBoard:
    def __init__(self):
        self.player_score = 0
        self.high_score = 0

    def score(self):
        self.player_score += 1
        if self.player_score > self.high_score:
            self.high_score = self.player_score
