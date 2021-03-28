import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt


class ScoreBoard:
    def __init__(self):
        self.player_score = 0
        self.high_score = 0
        self.game_num = 1

    def score(self):
        self.player_score += 1
        if self.player_score > self.high_score:
            self.high_score = self.player_score

    @staticmethod
    def plot_seaborn(array_counter, array_score, train):
        sns.set(color_codes=True, font_scale=1.5)
        sns.set_style("white")
        plt.figure(figsize=(13, 8))
        fit_reg = False if not train else True
        ax = sns.regplot(
            x=np.array([array_counter])[0],
            y=np.array([array_score])[0],
            # color="#36688D",
            x_jitter=.1,
            scatter_kws={"color": "#36688D"},
            label='Data',
            fit_reg=fit_reg,
            line_kws={"color": "#F49F05"}
        )
        # Plot the average line
        y_mean = [np.mean(array_score)] * len(array_counter)
        ax.plot(array_counter, y_mean, label='Mean', linestyle='--')
        ax.legend(loc='upper right')
        ax.set(xlabel='# games', ylabel='score')
        plt.show()
