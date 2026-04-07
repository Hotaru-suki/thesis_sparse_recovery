from __future__ import annotations

import unittest

import numpy as np

from algorithms import gomp, improved_gomp, omp, rmp
from algorithms.improved_gomp import _select_candidates, _try_rescue_step
from utils.linalg import IncrementalCholeskySolver, IncrementalGramSolver, solve_least_squares


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
        self.assertEqual(info["implementation"], "optimized")
        self.assertIn("timing_breakdown_sec", info)

    def test_omp_baseline_recovers_identity_support(self) -> None:
        x_hat, support_hat, info = omp(self.Phi, self.y, k=len(self.support), implementation="baseline")
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertLess(np.linalg.norm(x_hat - self.x_true), 1e-8)
        self.assertEqual(info["implementation"], "baseline")

    def test_omp_light_profile_reports_memory_info(self) -> None:
        x_hat, support_hat, info = omp(self.Phi, self.y, k=len(self.support), implementation="optimized", profile_level="light")
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertEqual(info["profile_level"], "light")
        self.assertEqual(info["iterations"], len(self.support))
        self.assertIn("peak_working_set_bytes", info)
        self.assertGreaterEqual(info["peak_working_set_bytes"], 0)

    def test_gomp_recovers_identity_support(self) -> None:
        x_hat, support_hat, info = gomp(self.Phi, self.y, k=len(self.support), group_size=2)
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertLess(np.linalg.norm(x_hat - self.x_true), 1e-8)
        self.assertIn("max_support_condition", info)
        self.assertEqual(info["implementation"], "optimized")

    def test_gomp_baseline_recovers_identity_support(self) -> None:
        x_hat, support_hat, info = gomp(self.Phi, self.y, k=len(self.support), group_size=2, implementation="baseline")
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertLess(np.linalg.norm(x_hat - self.x_true), 1e-8)
        self.assertEqual(info["implementation"], "baseline")

    def test_gomp_light_profile_reports_memory_info(self) -> None:
        x_hat, support_hat, info = gomp(
            self.Phi, self.y, k=len(self.support), group_size=2, implementation="optimized", profile_level="light"
        )
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertEqual(info["profile_level"], "light")
        self.assertGreaterEqual(info["peak_working_set_bytes"], 0)

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
        self.assertEqual(info["implementation"], "optimized")

    def test_improved_gomp_light_profile_reports_memory_info(self) -> None:
        x_hat, support_hat, info = improved_gomp(
            self.Phi,
            self.y,
            k=len(self.support),
            group_size=2,
            implementation="optimized",
            profile_level="light",
            use_incremental_solver=True,
        )
        self.assertSetEqual(set(support_hat.tolist()), set(self.support.tolist()))
        self.assertEqual(info["profile_level"], "light")
        self.assertEqual(info["iterations"], len(info["support_size_history"]))
        self.assertGreaterEqual(info["peak_working_set_bytes"], 0)

    def test_incremental_solver_matches_reference_least_squares(self) -> None:
        rng = np.random.default_rng(0)
        Phi = rng.standard_normal((6, 10))
        y = rng.standard_normal(6)
        support = [1, 3, 7]
        solver = IncrementalGramSolver(Phi=Phi, y=y)
        solver.extend(support)
        coef_inc, solver_name = solver.solve()
        coef_ref, ref_name = solve_least_squares(Phi[:, support], y)
        self.assertEqual(solver_name, "gram_solve")
        self.assertEqual(ref_name, "lstsq")
        self.assertTrue(np.allclose(coef_inc, coef_ref, atol=1e-8))

    def test_incremental_cholesky_solver_matches_reference_least_squares(self) -> None:
        rng = np.random.default_rng(1)
        Phi = rng.standard_normal((6, 10))
        y = rng.standard_normal(6)
        support = [0, 4, 8]
        solver = IncrementalCholeskySolver(Phi=Phi, y=y)
        solver.extend(support)
        coef_inc, solver_name = solver.solve()
        coef_ref, ref_name = solve_least_squares(Phi[:, support], y)
        self.assertEqual(solver_name, "cholesky_solve")
        self.assertEqual(ref_name, "lstsq")
        self.assertTrue(np.allclose(coef_inc, coef_ref, atol=1e-8))

    def test_improved_gomp_rescue_step_adds_missing_atom(self) -> None:
        Phi = np.eye(6, dtype=float)
        x_true = np.zeros(6, dtype=float)
        x_true[[1, 3, 5]] = np.array([1.0, 0.8, 0.15])
        y = Phi @ x_true
        support = [1, 3]
        residual = y - Phi[:, support] @ x_true[support]
        solver = IncrementalGramSolver(Phi=Phi, y=y)
        solver.extend(support)
        solver_time_history: list[float] = []

        rescued_support, rescued_x_hat, rescued_residual, rescued_residual_norm, solver_name = _try_rescue_step(
            Phi=Phi,
            y=y,
            residual=residual,
            support=support,
            residual_norm=float(np.linalg.norm(residual)),
            group_size=2,
            screening_ratio=2.0,
            min_group_size=1,
            k=3,
            solver=solver,
            solver_time_history=solver_time_history,
        )

        self.assertEqual(solver_name, "gram_solve")
        self.assertSetEqual(set(rescued_support), {1, 3, 5})
        self.assertLess(rescued_residual_norm, 1e-8)
        self.assertAlmostEqual(rescued_x_hat[5], 0.15, places=8)
        self.assertEqual(solver.support, support)
        self.assertEqual(len(solver_time_history), 1)

    def test_tail_refinement_prefers_candidate_with_better_residual_gain(self) -> None:
        Phi = np.array(
            [
                [1.0, 0.0, 0.8, 0.0],
                [0.0, 1.0, 0.6, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ],
            dtype=float,
        )
        y = np.array([1.0, 1.0, 1.0], dtype=float)
        support = [0]
        residual = y - Phi[:, support] @ np.array([1.0])
        candidates = np.array([2, 3], dtype=int)

        chosen = _select_candidates(
            Phi=Phi,
            y=y,
            residual=residual,
            support=support,
            candidates=candidates,
            active_group_size=1,
            use_tail_refinement=True,
            remaining_target=1,
            use_gain_reranking=True,
        )

        self.assertEqual(chosen, [3])

    def test_improved_gomp_tail_refinement_runs_end_to_end(self) -> None:
        Phi = np.eye(6, dtype=float)
        x_true = np.zeros(6, dtype=float)
        x_true[[0, 2, 5]] = np.array([1.0, -1.2, 0.5])
        y = Phi @ x_true
        x_hat, support_hat, info = improved_gomp(
            Phi,
            y,
            k=3,
            group_size=2,
            screening_ratio=2.0,
            use_tail_refinement=True,
            use_gain_reranking=True,
            use_forward_backward=True,
            use_two_phase_tail=True,
            use_cholesky_solver=True,
        )
        self.assertSetEqual(set(support_hat.tolist()), {0, 2, 5})
        self.assertLess(np.linalg.norm(x_hat - x_true), 1e-8)
        self.assertTrue(info["used_tail_refinement"])
        self.assertTrue(info["used_cholesky_solver"])

    def test_rmp_runs_and_reports_rescale_stats(self) -> None:
        x_hat, support_hat, info = rmp(self.Phi, self.y, k=len(self.support))
        self.assertGreaterEqual(len(support_hat), 1)
        self.assertEqual(len(info["rescale_history"]), info["iterations"])
        self.assertIn("avg_rescale_alpha", info)
        self.assertEqual(x_hat.shape, self.x_true.shape)
        self.assertEqual(info["implementation"], "optimized")

    def test_rmp_baseline_runs_and_reports_rescale_stats(self) -> None:
        x_hat, support_hat, info = rmp(self.Phi, self.y, k=len(self.support), implementation="baseline")
        self.assertGreaterEqual(len(support_hat), 1)
        self.assertEqual(len(info["rescale_history"]), info["iterations"])
        self.assertEqual(x_hat.shape, self.x_true.shape)
        self.assertEqual(info["implementation"], "baseline")

    def test_rmp_light_profile_reports_memory_info(self) -> None:
        x_hat, support_hat, info = rmp(self.Phi, self.y, k=len(self.support), implementation="optimized", profile_level="light")
        self.assertGreaterEqual(len(support_hat), 1)
        self.assertEqual(info["profile_level"], "light")
        self.assertGreaterEqual(info["peak_working_set_bytes"], 0)
        self.assertEqual(x_hat.shape, self.x_true.shape)


if __name__ == "__main__":
    unittest.main()
