"""
Stamina dynamics pentru iepure.

Stamina NU controlează viteza direct.
Controlează accelerația disponibilă — viteza e output emergent al deciziilor SNN.

Două tipuri de moarte prin stamina:
  - Sprint excesiv → epuizare înainte de vizuină
  - Prea lent      → prins de dușman
"""


class StaminaSystem:
    """
    Gestionează stamina iepurelui.
    
    Stamina (0-100%) dictează cât de mult poate accelera iepurele.
    Nu setează viteza — viteza e output al SNN-ului constrâns de stamina.
    """

    # Consum stamina
    ACCELERATION_COST = 0.8      # % per frame la accelerare maximă
    MOVEMENT_COST = 0.1          # % per frame la mers lent

    # Recuperare stamina
    RECOVERY_PARTIAL = 0.3       # % per frame în ascunziș parțial (tufă)
    RECOVERY_FULL = 1.0          # % per frame în ascunziș complet (bârlog)
    RECOVERY_OPEN = 0.05         # % per frame la stat pe loc în câmp deschis

    # Prag stres: dacă dușmanul e mai aproape de această distanță, recuperarea se oprește
    STRESS_DISTANCE = 5.0        # metri

    def __init__(self):
        self.value = 100.0       # stamina curentă (0-100)
        self.is_exhausted = False

    def reset(self):
        self.value = 100.0
        self.is_exhausted = False

    def update(self, action: str, enemy_distance: float, hide_quality: float = 0.0):
        """
        Actualizează stamina după o acțiune.
        
        Args:
            action: 'accelerate' | 'move' | 'hide' | 'stop'
            enemy_distance: distanța față de dușman în metri
            hide_quality: 0.0 = câmp deschis, 0.5 = tufă, 1.0 = bârlog
        
        Returns:
            bool: True dacă stamina a ajuns la 0 (DEATH)
        """
        # Consum
        if action == 'accelerate':
            self.value -= self.ACCELERATION_COST
        elif action == 'move':
            self.value -= self.MOVEMENT_COST

        # Recuperare (blocată dacă dușmanul e aproape — stres)
        elif action in ('hide', 'stop'):
            if enemy_distance > self.STRESS_DISTANCE:
                recovery = self.RECOVERY_PARTIAL + hide_quality * (self.RECOVERY_FULL - self.RECOVERY_PARTIAL)
                self.value += recovery

        self.value = max(0.0, min(100.0, self.value))

        if self.value <= 0.0:
            self.is_exhausted = True
            return True  # DEATH SPIKE

        return False

    def acceleration_factor(self) -> float:
        """
        Factorul de accelerație disponibil, liniar cu stamina.
        La stamina 100% → 1.0 (accelerație maximă)
        La stamina 10%  → 0.1 (abia se mișcă)
        """
        return self.value / 100.0

    def danger_level(self) -> float:
        """
        Nivel de pericol din perspectiva staminei (0.0 = ok, 1.0 = critic).
        SNN-ul primește asta ca senzor — nu știe de ce, dar corelează cu moartea.
        """
        return 1.0 - (self.value / 100.0)
