import random
import torch
from agent import Agent
from main import AppAi
from helper import plot

class Population:
    def __init__(self, size):
        self.size = size
        self.agents = [Agent() for _ in range(size)]

    def evaluate(self):
        plot_scores = []  # Lista wyników do wykresu
        plot_avg_scores = []  # Lista średnich wyników do wykresu
        total_score = 0  # Całkowita suma wyników
        record = 0  # Najlepszy wynik

        scores = []

        for agent in self.agents:
            game = AppAi()
            score = 0

            while not game.tetris.gameover:
                state = agent.get_state(game)
                action = agent.get_action(state)
                reward, game_over, score = game.play_step(action)
                agent.remember(state, action, reward, agent.get_state(game), game_over)
                agent.train_short_mem(state, action, reward, agent.get_state(game), game_over)

            # Sprawdzamy, czy to nowy rekord
            if score > record:
                record = score

            print('Game: ', agent.number_of_games, ', Score: ', score, ' Record: ', record, flush=True)

            scores.append((score, agent))

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / (agent.number_of_games + 1)  # Uniknięcie dzielenia przez zero
            plot_avg_scores.append(mean_score)

            plot(plot_scores, plot_avg_scores)

        return scores

    def select_and_mutate(self):
        scores = self.evaluate()
        scores.sort(reverse=True, key=lambda x: x[0])
        best_agents = [agent for _, agent in scores[:self.size // 2]]

        new_agents = []
        for agent in best_agents:
            new_agent = Agent()
            new_agent.model.load_state_dict(agent.model.state_dict())
            self.mutate(new_agent)
            new_agents.append(new_agent)

        self.agents = best_agents + new_agents

    def mutate(self, agent):
        for param in agent.model.parameters():
            if random.random() < 0.2:
                param.data += torch.randn_like(param) * 0.1

def train_population():
    pop = Population(size=10)
    generations = 50

    for gen in range(generations):
        pop.select_and_mutate()
        print(f'Generation {gen+1} complete')

    best_agent = max(pop.agents, key=lambda agent: agent.number_of_games)
    best_agent.model.save()

if __name__ == '__main__':
    train_population()