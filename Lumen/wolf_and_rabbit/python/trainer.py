"""
Training loop — conectează Python SNN cu Unity via ML-Agents.

Flux:
  Unity (C#) ←→ ML-Agents socket ←→ trainer.py ←→ RabbitSNNAgent

Rulare:
  1. Pornește Unity cu scena RabbitSNN
  2. python trainer.py

Sau fără Unity (mock pentru test):
  python trainer.py --mock
"""

import argparse
import numpy as np

from snn_agent import RabbitSNNAgent

N_SENSORS = 9


def run_mock(n_episodes: int = 100):
    """
    Rulează fără Unity — simulare minimală pentru a testa SNN-ul și R-STDP.
    Iepurele primește observații random, moare aleatoriu.
    """
    agent = RabbitSNNAgent()
    survival_steps = []

    print("🐇 Wolf & Rabbit — Mock Training")
    print(f"   {n_episodes} episoade, fără Unity\n")

    for ep in range(n_episodes):
        agent.reset()
        done = False
        step = 0

        while not done and step < 2000:
            # Observații mock: random între 0 și 1
            obs = np.random.uniform(0, 1, N_SENSORS)

            # Acțiune SNN
            actions = agent.forward(obs)

            # Simulare stamina mock
            action_type = 'accelerate' if actions[1] > 0.5 else 'move'
            enemy_dist = obs[0] * 50.0  # distanță în metri (0-50m)
            dead = agent.update_stamina(action_type, enemy_dist)

            if dead:
                done = True
            elif obs[0] < 0.05:  # dușman foarte aproape → prins
                agent.on_death(cause='caught')
                done = True
            elif obs[6] < 0.05:  # aproape de vizuină → acasă!
                agent.on_home()
                done = True

            step += 1

        survival_steps.append(step)

        if (ep + 1) % 10 == 0:
            avg = np.mean(survival_steps[-10:])
            print(f"  Ep {ep+1:3d} | Avg supraviețuire: {avg:.0f} pași")

    print(f"\n✅ Training complet. Supraviețuire medie finală: {np.mean(survival_steps[-20:]):.0f} pași")


def run_unity():
    """
    Conectare la Unity via ML-Agents.
    Necesită Unity să ruleze cu scena RabbitSNN.
    """
    try:
        from mlagents_envs.environment import UnityEnvironment
        from mlagents_envs.base_env import ActionTuple
    except ImportError:
        print("❌ mlagents-envs nu e instalat. Rulează: pip install mlagents-envs")
        return

    agent = RabbitSNNAgent()

    print("🎮 Aștept Unity să pornească scena...")
    env = UnityEnvironment(file_name=None, seed=42)  # None = editorul deschis
    env.reset()

    behavior_name = list(env.behavior_specs.keys())[0]
    print(f"✅ Conectat la Unity. Behavior: {behavior_name}")

    episode = 0
    try:
        while True:
            decision_steps, terminal_steps = env.get_steps(behavior_name)

            # Episod nou
            if len(terminal_steps) > 0:
                for agent_id, ts in terminal_steps.items():
                    if ts.reward > 0:
                        agent.on_home()
                    else:
                        agent.on_death(cause='caught')
                agent.reset()
                episode += 1
                if episode % 10 == 0:
                    print(f"  Episod {episode} complet")

            # Pas curent
            if len(decision_steps) > 0:
                for agent_id, ds in decision_steps.items():
                    obs = ds.obs[0]  # primul observation vector
                    actions = agent.forward(obs)

                    action_tuple = ActionTuple(
                        continuous=np.array([[actions[0], actions[1]]])
                    )
                    env.set_actions(behavior_name, action_tuple)

            env.step()

    except KeyboardInterrupt:
        print("\n⏹ Training oprit.")
    finally:
        env.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mock", action="store_true", help="Rulează fără Unity")
    parser.add_argument("--episodes", type=int, default=100)
    args = parser.parse_args()

    if args.mock:
        run_mock(n_episodes=args.episodes)
    else:
        run_unity()
