from agent import Agent
from game import AIGame

class Evolution:
    def __init__(self) -> None:
        self.agents = []
        self.alive_agents = []
        self.num_agents = 10
        self.seed = 890
        self.game = None
    
    def train(self):
        for i in range(self.num_agents):
            self.agents.append(Agent(i))
        game = AIGame(w=1540, h=800, seed = self.seed, num_players=self.num_agents)
        
        while True:
            print(len(self.agents))
            self.alive_agents = self.agents.copy()
            print(len(self.alive_agents))
            game.reset()

            while len(self.alive_agents) > 0:
                for agent in self.alive_agents:
                    done = False
                    print("Agent" + str(agent.index) + "play loop!")
                    
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
                            agent.model.save()


                        print('Game', agent.n_games, 'Score', score, 'Record:', agent.record, "Reason:", reason)
                        agent.total_score += score
                        print("removing agent", agent.index)
                        self.alive_agents.remove(agent)
            print("Nobody is alive~!")
                        
                       


if __name__ == '__main__':
    ev = Evolution()
    ev.train()
