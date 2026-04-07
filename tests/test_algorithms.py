from __future__ import annotations

import unittest

import numpy as np

from algorithms import gomp, improved_gomp, omp, rmp


class AlgorithmRecoveryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.Phi = np.eye(8, dtype=float)
        self.support = np.array([1, 4, 6], dtype=int)
        self.x_true = np.zeros(8, dtype=float)
        self.x_true[self.support] = np.array([1.5, -2.0, 0.75])
        self.y = self.Phi @ self.x_true

    def test_omp_recovers_identity_support(self) -> None:
        x_hat, support_hat, info = omp(self.Phi, self.y, k=len(self.support))
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertLess(np.linalg.norm(x_hat - self.x_true), 1e-8)
        self.assertEqual(info["stop_reason"], "target_sparsity_reached")

    def test_gomp_recovers_identity_support(self) -> None:
        x_hat, support_hat, info = gomp(self.Phi, self.y, k=len(self.support), group_size=2)
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertLess(np.linalg.norm(x_hat - self.x_true), 1e-8)
        self.assertIn("max_support_condition", info)

    def test_improved_gomp_recovers_identity_support(self) -> None:
        x_hat, support_hat, info = improved_gomp(
            self.Phi,
            self.y,
            k=len(self.support),
            group_size=2,
            screening_ratio=2.0,
            use_noise_aware_stop=True,
            use_incremental_solver=True,
        )
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertLess(np.linalg.norm(x_hat - self.x_true), 1e-8)
        self.assertIn(info["stop_reason"], {"target_sparsity_reached", "residual_tol"})
        self.assertIn("solver_fallback_count", info)

    def test_rmp_runs_and_reports_rescale_stats(self) -> None:
        x_hat, support_hat, info = rmp(self.Phi, self.y, k=len(self.support))
        self.assertGreaterEqual(len(support_hat), 1)
        self.assertEqual(len(info["rescale_history"]), info["iterations"])
        self.assertIn("avg_rescale_alpha", info)
        self.assertEqual(x_hat.shape, self.x_true.shape)


if __name__ == "__main__":
    unittest.main()
