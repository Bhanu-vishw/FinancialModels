"""
Random number generation and simulation
"""

from abc import ABC, abstractmethod
from typing import Any

import numpy as np


class StandardNormalRNG:
    """Wrapper around NumPy's RNG functionality to make the API (maybe) a bit
    clearer"""

    def __init__(self, seed) -> None:
        self.rng = np.random.default_rng(seed=seed)

    def single(self) -> float:
        """A single random number"""
        return self.rng.standard_normal()

    def vector(self, size: int) -> np.ndarray[np.float64]:
        """A random vector"""
        return self.rng.standard_normal(size=size)

    def matrix(self, rows: int, cols: int) -> np.ndarray[np.float64]:
        """A random matrix"""
        return self.rng.standard_normal(size=(rows, cols))


class Paths:
    """Encapsulates underlying price paths where the row index corresponds to
    the path number and column index corresponds to the time step"""

    def __init__(self, time_step: float, data: np.ndarray):
        """

        Args:
            time_step (float): _description_
            data (np.ndarray): _description_
        """
        self.num_paths = data.shape[0]
        self.num_steps = data.shape[1] - 1
        self.time_step = time_step
        self._storage = data

    def __getitem__(self, key) -> np.ndarray[Any, float]:
        """Index into storage with slice"""
        return self._storage.__getitem__(key)

    @property
    def shape(self) -> tuple:
        return self._storage.shape

    def __repr__(self) -> str:
        return f"Paths(time_step={self.time_step}, data={repr(self._storage)})"


class PathGenerator(ABC):
    """Abstract base class for generating and storing paths"""

    def __init__(self, num_paths: int, num_steps: int):
        """Parent initializer

        Args:
            num_paths (int): number of paths
            num_steps (int): number of time steps
        """
        self.num_paths = num_paths
        self.num_steps = num_steps

    @abstractmethod
    def generate(self) -> Paths:
        """Generate a Path object"""


class GBMPathGenerator(PathGenerator):
    """Geometric Brownian Motion path generator"""

    def __init__(
        self,
        num_paths: int,
        num_steps: int,
        *,
        s0: float,
        drift: float,
        diffusion: float,
        to_time: float,
        rng: StandardNormalRNG,
    ) -> None:
        """Initializer

        Args:
            num_paths (int): number of paths
            num_steps (int): number of time steps
            s0 (float): initial underlying value
            drift (float): drift parameter
            diffusion (float): volatility (diffusion) parameter
            to_time (float): the time (year fraction) to simulate to
        """
        super().__init__(num_paths, num_steps)
        # Your implementation

        # Initializing parameters 
        self.s0 = s0
        self.drift = drift
        self.diffusion = diffusion
        self.to_time = to_time
        self.rng = rng
        self.num_paths = num_paths
        self.time_step_value = to_time / num_steps

    def generate(self) -> Paths:
        pass
        # Your implementation

        # taking dt = to_time / num_steps
        dt = self.time_step()
        paths = np.zeros((self.num_paths, self.num_steps + 1))
        paths[:, 0] = self.s0

        # Implying variance reduction by antithetic variate
        half_paths = self.num_paths // 2
        
        for step in range(1, self.num_steps + 1):
            # Generate random numbers for half the paths
            z = self.rng.vector(half_paths)
            
            # Calculate the drift and diffusion terms
            drift_term = (self.drift - 0.5 * self.diffusion ** 2) * dt
            diffusion_term = self.diffusion * np.sqrt(dt)
            
            # Apply GBM to first half of paths using original variates
            paths[:half_paths, step] = paths[:half_paths, step - 1] * np.exp( drift_term + diffusion_term * z)
            
            # Apply GBM to second half of paths using antithetic variates
            paths[half_paths:, step] = paths[half_paths:, step - 1] * np.exp(drift_term + diffusion_term * (-z))

        return Paths(time_step=dt, data=paths)

    def time_step(self) -> float:
        pass
        # Your implementation
        return self.time_step_value
