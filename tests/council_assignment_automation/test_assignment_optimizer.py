"""Independent exhaustive oracle for the shipped generated assignment program.

This validates the recurrence and ordering, not CK3 scope/trigger behavior. The
native harness provides that separate acceptance gate.
"""
from itertools import product
from pathlib import Path
import random
import re
import unittest

ROOT = Path(__file__).absolute().parents[2]
GENERATED = ROOT / "mod/council_assignment_automation/common/scripted_effects/caa_effects.txt"


def vector(assignment, candidates, roles):
    assigned = [(r, c) for r, c in enumerate(assignment) if c is not None]
    return (
        sum(candidates[c]["keep"] for _, c in assigned),
        len(assigned),
        sum(candidates[c]["power"] for _, c in assigned),
        sum(candidates[c]["skill"][r] * 10 + (candidates[c]["old"] == r)
            for r, c in assigned),
    )


def exhaustive(candidates, roles):
    """Enumerate every legal assignment directly; no DP or greedy recurrence."""
    choices = [[None] + [i for i, c in enumerate(candidates) if c["valid"][r]]
               for r in range(roles)]
    best, best_assignment = None, None
    for assignment in product(*choices):
        used = [x for x in assignment if x is not None]
        if len(used) != len(set(used)):
            continue
        score = vector(assignment, candidates, roles)
        if best is None or score > best:
            best, best_assignment = score, assignment
    return best, best_assignment


def emitted_program(candidates, roles):
    """Read transition order from the shipped source, then execute its math."""
    source = GENERATED.read_text(encoding="utf-8-sig")
    transitions = [(int(role), int(src, 2), int(dst, 2)) for role, src, dst in
                   re.findall(r"# Candidate to seat (\d): mask ([01]{5}) -> ([01]{5})", source)]
    if len(transitions) != 80 or len(set(transitions)) != 80:
        raise AssertionError("Expected exactly 80 unique generated transitions")
    table = {0: (0, 0, 0, (None,) * roles)}
    for index, candidate in enumerate(candidates):
        for role, src, dst in transitions:
            if role >= roles or src >= 1 << roles or not candidate["valid"][role] or src not in table:
                continue
            keep, power, score, assignment = table[src]
            proposal = (keep + candidate["keep"], power + candidate["power"],
                        score + candidate["skill"][role] * 10 + (candidate["old"] == role))
            if dst not in table or proposal > table[dst][:3]:
                filled = list(assignment)
                filled[role] = index
                table[dst] = (*proposal, tuple(filled))
    best_mask, best = max(table.items(), key=lambda kv: (kv[1][0], kv[0].bit_count(), kv[1][1], kv[1][2]))
    return (best[0], best_mask.bit_count(), best[1], best[2]), best[3]


def candidate(skills, power=0, keep=0, old=None, valid=None):
    return {"skill": skills, "power": power, "keep": keep, "old": old,
            "valid": valid if valid is not None else [True] * len(skills)}


class AssignmentOracleTests(unittest.TestCase):
    def check_oracle(self, pool, roles):
        expected, _ = exhaustive(pool, roles)
        actual, assignment = emitted_program(pool, roles)
        self.assertEqual(expected, actual)
        used = [x for x in assignment if x is not None]
        self.assertEqual(len(used), len(set(used)))
        return assignment

    def test_non_greedy_shared_best_candidate(self):
        pool = [candidate([50, 49]), candidate([49, 1])]
        self.assertEqual(self.check_oracle(pool, 2), (1, 0))

    def test_three_cycle_beats_every_pair_swap(self):
        # Baseline 30. Every pair swap is 21, yet the 3-cycle is 33.
        pool = [candidate([10, 11, 0], old=0), candidate([0, 10, 11], old=1),
                candidate([11, 0, 10], old=2)]
        self.assertEqual(self.check_oracle(pool, 3), (2, 0, 1))

    def test_incumbents_break_exact_skill_ties(self):
        pool = [candidate([20, 20], old=1), candidate([20, 20], old=0)]
        self.assertEqual(self.check_oracle(pool, 2), (1, 0))

    def test_one_skill_point_beats_all_five_stability_bonuses(self):
        pool = [candidate([10] * 5, old=i) for i in range(5)]
        pool[0]["skill"][1] = 11
        assignment = self.check_oracle(pool, 5)
        self.assertEqual(assignment[1], 0)

    def test_filled_seats_before_powerful_count_and_skill(self):
        pool = [candidate([1000, 1], power=1), candidate([0, 0], valid=[True, False])]
        self.assertEqual(self.check_oracle(pool, 2), (1, 0))

    def test_powerful_priority_is_lexicographic_unbounded_skills(self):
        pool = [candidate([0], power=1), candidate([100000])]
        self.assertEqual(self.check_oracle(pool, 1), (0,))

    def test_observer_off_retains_required_incumbents(self):
        pool = [candidate([1, 1], power=1, keep=1, old=0),
                candidate([20, 20], power=1), candidate([30, 30], power=1)]
        assignment = self.check_oracle(pool, 2)
        self.assertIn(0, assignment)
        self.assertNotIn(1, assignment)

    def test_incumbent_can_move_into_vacancy_without_dismissal(self):
        pool = [candidate([10, 30], power=1, keep=1, old=0), candidate([20, 1], power=1)]
        self.assertEqual(self.check_oracle(pool, 2), (1, 0))

    def test_no_valid_candidates(self):
        self.assertEqual(self.check_oracle([candidate([100] * 5, valid=[False] * 5)], 5), (None,) * 5)

    def test_seeded_random_pools_against_exhaustive_oracle(self):
        rng = random.Random(20261008)
        for case in range(600):
            roles = rng.randint(1, 5)
            size = rng.randint(0, 6)
            pool = [candidate([rng.randint(0, 10000) for _ in range(roles)],
                              power=rng.randint(0, 1), keep=rng.randint(0, 1),
                              old=rng.choice([None] + list(range(roles))),
                              valid=[rng.random() < 0.7 for _ in range(roles)])
                    for _ in range(size)]
            with self.subTest(case=case, roles=roles, size=size):
                self.check_oracle(pool, roles)


if __name__ == "__main__":
    unittest.main()
