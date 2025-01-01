import pytest
import numpy as np

import final as fn


def test_gbm():
    s0 = 200
    t = 2
    mu = 0.12
    vol = 0.30
    days = 252

    generator = fn.GBMPathGenerator(
        num_paths=100000,
        num_steps=t * days,
        s0=s0,
        drift=mu,
        diffusion=vol,
        to_time=t,
        rng=fn.StandardNormalRNG(seed=42),
    )
    paths = generator.generate()
    mu_sim = np.log(paths[:, -1].mean() / s0) / t
    vol_sim = np.log(paths[:, 1:] / paths[:, :-1]).std() / np.sqrt(paths.time_step)

    assert mu_sim == pytest.approx(mu, rel=1e-2)
    assert vol_sim == pytest.approx(vol, rel=1e-3)
