from agent import Agent
from game import AIGame
import random
import copy

class Evolution:
    def __init__(self) -> None:
        self.agents = []
        self.alive_agents = []
        self.num_agents = 10
        self.seed = 670
        self.game = None
        self.best_agents = set()
        self.mutation_rate = 0.3
    
    def train(self):
        for i in range(self.num_agents):
            self.agents.append(Agent(i))
        game = AIGame(w=1540, h=800, seed = self.seed, num_players=self.num_agents)
        
        while True:
            print("Agenci: ", len(self.agents))
            self.alive_agents = self.agents.copy()
            print("Żywi agenci", len(self.alive_agents))
            game.reset()

            while len(self.alive_agents) > 0:
                for agent in self.alive_agents:
                    done = False
                    
                    # get old state
                    state_old = agent.get_state(game)

                    # get move
                    final_move = agent.get_action(state_old)

                    # perform move and get new state
                    reward, done, reason, score = game.play_step(final_move, agent.index)
                    state_new = agent.get_state(game)

                    # train short memory
                    agent.train_short_memory(state_old, final_move, reward, state_new, done)

                    # remember
                    agent.remember(state_old, final_move, reward, state_new, done)

                    if done:
                        # train long memory, plot result
                        print(reason)
                        game.add_log("Agent " + str(agent.index) + " "+ reason)
                        
                        agent.n_games += 1
                        agent.train_long_memory()

                        if score > agent.record:
                            agent.record = score
                            game.set_stats(agent.record)
                            self.best_agents.add(agent)
                            agent.model.save()


                        print('Game', agent.n_games, 'Score', score, 'Record:', agent.record, "Reason:", reason)
                        agent.total_score += score
                        print("removing agent", agent.index)
                        self.alive_agents.remove(agent)
            self.evolve()
            print("Nobody is alive~!")
                        
    def evolve(self):
        if len(self.best_agents)  == 0:
            return
        if len(self.best_agents) == 1:
            self.agents = []
            for i in range(self.num_agents):
                agent = Agent(i)
                x = random.randint(0, 10)
                if x > 3:
                    agent.model.load_weights_from_array(self.best_agents[0].model.get_weights_as_array())
                self.agents.append(agent)
        else:
            selected_agents = self.tournament_selection(self.agents, 2)
            offspring = []
            for i in range(0, len(selected_agents)-2):
                child = Agent(i)
                child_weights = self.crossover(selected_agents[i], selected_agents[i + 1])
                child.model.load_weights_from_array(child_weights)
                offspring.append(child)

            # Mutation
            mutated_offspring = [self.mutate(child) for child in offspring]
            if len(mutated_offspring) < self.num_agents:
                for i in range(len(mutated_offspring), self.num_agents-1):
                    mutated_offspring.append(Agent(i))
            self.agents = mutated_offspring


    def tournament_selection(self, agents, tournament_size):
        selected_agents = []
        for _ in range(self.num_agents):
            participants = random.sample(agents, tournament_size)
            winner = max(participants, key=lambda i: i.record)
            selected_agents.append(winner)
        return selected_agents

    def negative_tournament_selection(self, agents, tournament_size):
        selected_agents = []
        for _ in range(self.num_agents):
            participants = random.sample(agents, tournament_size)
            loser = min(participants, key=lambda i: i.record)
            selected_agents.append(loser)
        return selected_agents

    def crossover(self, parent1, parent2):
        weights1 = parent1.model.get_weights_as_array()
        weighst2 = parent2.model.get_weights_as_array()
        crossover_point = random.randint(0, len(weights1) - 1)
        child_weights = weights1[:crossover_point] + weighst2[crossover_point:]
        return child_weights

    def mutate(self, agent):
        weights = agent.model.get_weights_as_array()
        for i in range(len(weights)):
            if random.random() < self.mutation_rate:
                weights[i] += random.uniform(-0.5, 0.5)
        agent.model.load_weights_from_array(weights)
        return agent



if __name__ == '__main__':
    ev = Evolution()
    ev.train()
