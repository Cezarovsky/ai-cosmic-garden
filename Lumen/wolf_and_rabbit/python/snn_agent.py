"""
SNN Agent pentru iepure — interfață cu Unity via ML-Agents.

Senzori primiți din Unity (9 valori):
  0. distanță dușman (normalizat 0-1)
  1. viteza dușmanului (normalizat 0-1)
  2. accelerația dușmanului (normalizat 0-1)  ← semnal de pericol primar
  3. obstacole teren (bool)
  4. stamina curentă (0-1)
  5. direcție vizuină (unghi normalizat -1 la 1)
  6. distanță vizuină (normalizat 0-1)
  7. înălțime curentă Y (normalizat 0-1)
  8. line-of-sight blocat (bool)

Acțiuni trimise în Unity (2 valori continue):
  0. direcție (unghi -1 la 1)
  1. accelerație (0-1, scalată de stamina)
"""

import numpy as np
from r_stdp import RSTDPLearner
from stamina import StaminaSystem

N_SENSORS = 9
N_ACTIONS = 2
N_HIDDEN = 64  # neuroni în layer-ul intern SNN


class RabbitSNNAgent:
    """
    SNN simplificat pentru iepure.
    
    Arhitectură: Input(9) → Hidden(64) → Output(2)
    Learning: R-STDP cu eligibility traces
    
    NOTE: Aceasta e o implementare "SNN-like" în numpy pentru prototip.
    Versiunea finală va folosi Lava Framework (Intel) pentru
    neuroni Leaky Integrate-and-Fire reali.
    """

    def __init__(
        self,
        learning_rate: float = 0.005,
        trace_decay: float = 0.99,
        spike_threshold: float = 0.5,
    ):
        self.threshold = spike_threshold
        self.stamina = StaminaSystem()

        # Două seturi de weights: input→hidden, hidden→output
        self.w_in = np.random.uniform(0.0, 0.3, (N_HIDDEN, N_SENSORS))
        self.w_out = np.random.uniform(0.0, 0.3, (N_ACTIONS, N_HIDDEN))

        # R-STDP pe layer-ul de output
        self.stdp = RSTDPLearner(
            n_synapses=N_ACTIONS * N_HIDDEN,
            learning_rate=learning_rate,
            trace_decay=trace_decay,
        )

        # Membrane potentials (LIF simplificat)
        self.v_hidden = np.zeros(N_HIDDEN)
        self.v_out = np.zeros(N_ACTIONS)

        self.episode_steps = 0

    def reset(self):
        """Reset la începutul unui nou episod."""
        self.v_hidden = np.zeros(N_HIDDEN)
        self.v_out = np.zeros(N_ACTIONS)
        self.stamina.reset()
        self.stdp.reset_traces()
        self.episode_steps = 0

    def forward(self, observations: np.ndarray) -> np.ndarray:
        """
        Un pas de inferență SNN.
        
        Args:
            observations: array de 9 valori din Unity
            
        Returns:
            actions: array de 2 valori (direcție, accelerație)
        """
        # Input spikes: encode observații ca spike trains
        input_spikes = (observations > 0.5).astype(float)

        # Hidden layer: integrate and fire
        self.v_hidden += self.w_in @ input_spikes
        hidden_spikes = (self.v_hidden >= self.threshold).astype(float)
        self.v_hidden[hidden_spikes > 0] = 0.0  # reset după spike
        self.v_hidden *= 0.9  # leak

        # Output layer
        self.v_out += self.w_out @ hidden_spikes
        output_spikes = (self.v_out >= self.threshold).astype(float)
        self.v_out[output_spikes > 0] = 0.0
        self.v_out *= 0.9

        # Actualizează eligibility traces
        pre_spikes = np.outer(output_spikes, hidden_spikes).flatten()
        self.stdp.step(pre_spikes)

        # Scalează accelerația cu stamina disponibilă
        actions = output_spikes.copy()
        actions[1] *= self.stamina.acceleration_factor()

        self.episode_steps += 1
        return actions

    def on_death(self, cause: str = "unknown"):
        """
        Apelat când iepurele moare — aplică death spike pe toate trace-urile.
        
        Args:
            cause: 'caught' | 'exhaustion' | 'terrain'
        """
        # Toate cauzele sunt la fel de fatale pentru STDP
        self.stdp.death_spike(magnitude=-1.0)
        print(f"  💀 DEATH ({cause}) la pasul {self.episode_steps}")

    def on_home(self):
        """Apelat când iepurele ajunge la vizuină — reward pozitiv major."""
        self.stdp.home_reward(magnitude=1.0)
        print(f"  🏠 HOME! Supraviețuit în {self.episode_steps} pași")

    def update_stamina(self, action_type: str, enemy_distance: float, hide_quality: float = 0.0) -> bool:
        """
        Actualizează stamina și returnează True dacă iepurele moare prin epuizare.
        """
        dead = self.stamina.update(action_type, enemy_distance, hide_quality)
        if dead:
            self.on_death(cause='exhaustion')
        return dead
