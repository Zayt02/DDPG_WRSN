import numpy as np
# import gym
import tensorflow as tf
import copy

from DDPG import Agent
from environment import Environment

# gpu = tf.config.experimental.list_logical_devices('GPU')
# tf.config.experimental.set_memory_growth(gpu[0], True)

# tf.debugging.set_log_device_placement(True)


EPISODES = 1000
MAX_STEPS = 300
BATCH_SIZE = 32
SEED = 22
continued = True
path = "path"
NOISE_C = 1.1
first_ep = 0

with tf.device('/GPU:0'):
    env = Environment("data/u20.txt", SEED)
    # env = gym.wrappers.Monitor(e.env, 'video/', video_callable=lambda episode_id: True,force = True)
    # video = VideoRecorder(env, "video.mp4"
    state_shape = env.state_shape
    action_len = env.action_shape[0]
    action_scale = None
    NOISE = 0.6
    # np.random.seed(SEED)

    agent = Agent(state_shape, action_len, action_scale)
    if continued:
        agent.load(path)
    agent.summary()

    for episode in range(first_ep, EPISODES):
        state = env.reset()
        state = np.reshape(state, state_shape)
        score = 0
        # print(state)
        # done = False
        noise = np.random.normal(NOISE, NOISE / 2, 2) / (1+pow(NOISE_C, episode+10))
        for st in range(MAX_STEPS):
        # while not done :
        #     env.render()
            # video.capture_frame()
            action = agent.act(state)
            if not continued:
                action = np.clip(action + np.random.choice([-1, 1])*noise, 0, 0.99)
            # print(state, action)
            # print(action)
            # print(state, action)
            next_state, reward, times, done, info = env.step(action)
            # print(next_state, action, reward, done, info)

            # print(next_state, reward, done, info)
            score += times
            # print(times)
            if next_state is not None: next_state = np.reshape(next_state, state_shape)
            # if next_state[0] > 0.95:
            #     if 0 < next_state[1] < 0.312:
            #         reward = min(-action[0] * 4 - 4, 0)
            #     elif -0.312 < next_state[1] <= 0:
            #         reward = min(action[0] * 4 - 4, 0)
            if episode == first_ep:
                env.start.append(copy.copy(state))
            env.memorize([copy.copy(x) for x in [state, action, reward, next_state, done]])
            # print(score)
            if done:
                print("episode: {}, score: {}\n".format(episode, score))
                break
            state = next_state
            if len(env.memory) >= BATCH_SIZE:  # and st % (MAX_STEPS/20) == 0:
                samples = env.get_samples(BATCH_SIZE)
                agent.train(samples)
                agent.update_target_net()
        if (episode+1) % 10 == 0:
            agent.network_copy()
            agent.save(path)
        # if episode == first_ep+2:
        #     break
