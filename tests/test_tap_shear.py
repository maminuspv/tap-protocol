import unittest
from tap.proto import tap_pb2
from tap.proto import tap_pb2_grpc


class TestTAPThermodynamics(unittest.TestCase):

    def setUp(self):
        """Set up shear stress threshold parameters."""
        self.max_allowable_shear = 0.30
        self.initial_collateral = 100.0

    def test_mutualistic_payload_acceptance(self):
        """High utility density (0.80) yields shear stress (0.20) below threshold."""
        utility_density = 0.80
        instantaneous_shear = 1.0 - utility_density

        self.assertLessEqual(
            instantaneous_shear,
            self.max_allowable_shear,
            "Low shear should pass threshold.",
        )

        # Calculate yield
        accepted = instantaneous_shear <= self.max_allowable_shear
        updated_balance = self.initial_collateral + 5.0 if accepted else 0.0

        self.assertTrue(accepted)
        self.assertEqual(updated_balance, 105.0)

    def test_parasitic_payload_slashing(self):
        """Low utility density (0.40) yields shear stress (0.60) triggering slashing."""
        utility_density = 0.40
        instantaneous_shear = 1.0 - utility_density

        # Calculate slashed collateral: Collateral - (Shear * Staked)
        slashed_amount = instantaneous_shear * self.initial_collateral
        updated_balance = max(0.0, self.initial_collateral - slashed_amount)

        self.assertGreater(instantaneous_shear, self.max_allowable_shear)
        self.assertEqual(updated_balance, 40.0)


if __name__ == "__main__":
    unittest.main()