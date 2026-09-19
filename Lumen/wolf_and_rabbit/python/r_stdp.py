"""
R-STDP cu Eligibility Traces pentru iepure.

STDP standard: conectează doar evenimente la ~20ms distanță.
R-STDP + Eligibility Traces: conectează death spike-ul cu decizii
luate cu ~200 pași înapoi.

Iepurele nu știe că stamina=0 → moarte.
Știe doar că "după ce am alergat mult, am murit".
Corelația apare din trace-uri, nu din programare.
"""

import numpy as np


class EligibilityTrace:
    """
    Trace sinaptic pentru o conexiune.
    
    Fiecare sinapsă păstrează o 'amintire' a activității recente.
    La death spike, toate trace-urile active sunt penalizate.
    La reward (vizuină), toate trace-urile active sunt întărite.
    """

    def __init__(self, decay: float = 0.99):
        """
        Args:
            decay: rata de decay per frame (0.99 = trace supraviețuiește ~100 pași)
        """
        self.decay = decay
        self.value = 0.0

    def update(self, spike: float):
        """Actualizează trace după un spike presynaptic."""
        self.value = self.decay * self.value + spike

    def reset(self):
        self.value = 0.0


class RSTDPLearner:
    """
    Reward-modulated STDP cu eligibility traces.
    
    Cum funcționează:
    1. La fiecare pas, trace-urile se actualizează cu activitatea neuronilor
    2. La death spike (reward negativ): Δw = -η × trace × |reward|
    3. La reward pozitiv (vizuină):     Δw = +η × trace × reward
    4. Weights se clampează în [w_min, w_max]
    
    Efectul: sinapsa care a fost activă cu 200 de pași înainte de moarte
    primește penalizare proporțională cu trace-ul ei rezidual.
    """

    def __init__(
        self,
        n_synapses: int,
        learning_rate: float = 0.01,
        trace_decay: float = 0.99,
        w_min: float = 0.0,
        w_max: float = 1.0,
    ):
        self.n = n_synapses
        self.lr = learning_rate
        self.w_min = w_min
        self.w_max = w_max

        # Weights inițiale random mic
        self.weights = np.random.uniform(0.1, 0.3, n_synapses)

        # Eligibility traces per sinapsă
        self.traces = [EligibilityTrace(decay=trace_decay) for _ in range(n_synapses)]

    def step(self, pre_spikes: np.ndarray):
        """
        Actualizează trace-urile după activitatea presynaptică.
        Apelat la fiecare frame de simulare.
        
        Args:
            pre_spikes: array de spike-uri presynaptice (0 sau 1)
        """
        for i, spike in enumerate(pre_spikes):
            self.traces[i].update(float(spike))

    def apply_reward(self, reward: float):
        """
        Aplică reward (pozitiv sau negativ) pe toate trace-urile active.
        
        Args:
            reward: pozitiv = supraviețuire/vizuină, negativ = death spike
        """
        trace_values = np.array([t.value for t in self.traces])
        delta_w = self.lr * reward * trace_values
        self.weights = np.clip(self.weights + delta_w, self.w_min, self.w_max)

    def death_spike(self, magnitude: float = -1.0):
        """Shortcut pentru death spike — reward negativ extrem."""
        self.apply_reward(magnitude)

    def home_reward(self, magnitude: float = 1.0):
        """Shortcut pentru ajuns la vizuină — reward pozitiv major."""
        self.apply_reward(magnitude)

    def reset_traces(self):
        """Reset trace-uri la începutul fiecărui episod."""
        for t in self.traces:
            t.reset()

    def get_weights(self) -> np.ndarray:
        return self.weights.copy()
