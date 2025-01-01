import numpy as np
import pytest

import final as fn


class StubGenerator(fn.PathGenerator):
    def __init__(self, time_step: float, data: np.ndarray):
        self._paths = fn.Paths(time_step, data)
        super().__init__(self._paths.num_paths, self._paths.num_steps)

    def generate(self) -> fn.Paths:
        return self._paths


def test_paper_example():
    data = np.asarray(
        [
            [1.00, 1.09, 1.08, 1.34],
            [1.00, 1.16, 1.26, 1.54],
            [1.00, 1.22, 1.07, 1.03],
            [1.00, 0.93, 0.97, 0.92],
            [1.00, 1.11, 1.56, 1.52],
            [1.00, 0.76, 0.77, 0.90],
            [1.00, 0.92, 0.84, 1.01],
            [1.00, 0.88, 1.22, 1.34],
        ]
    )
    lsm_paper_generator = StubGenerator(time_step=1, data=data)
    price = fn.lsm_price(
        strike_price=1.1,
        risk_free_rate=0.06,
        is_call=False,
        path_generator=lsm_paper_generator,
        polynomial_degree=2,
    )
    assert price == pytest.approx(0.11443433004505696)
