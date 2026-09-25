from unittest.mock import MagicMock
import pytest

# Adjust imports based on your protobuf build paths
from tap.proto import tap_pb2 
from tap.server import TAPServerServicer


@pytest.fixture
def servicer():
    """Provides a fresh TAPServerServicer instance for each test."""
    return TAPServerServicer(max_allowed_shear=0.30)


def test_submit_proposal_annealed(servicer):
    """Submitting a proposal below the shear threshold should result in ANNEALED status and yield."""
    mock_context = MagicMock()

    request = tap_pb2.ProposalRequest(
        header=tap_pb2.Header(
            sender_id="urn:agent:test-node-01",
            thermodynamic_state=tap_pb2.ThermodynamicState(
                staked_energy_collateral=500
            ),
        ),
        payload=b"SELECT * FROM knowledge_base;",
        payload_utility_density=0.90,  # 10% shear
    )

    response = servicer.SubmitProposal(request, mock_context)

    assert response.status == "ANNEALED"
    assert response.earned_yield == 125  # 25% of 500
    assert response.collateral_returned == 500
    assert (
        servicer.agent_vaults["urn:agent:test-node-01"] == 5125
    )  # 5000 base + 125 yield


def test_submit_proposal_rejected_shear(servicer):
    """Submitting a proposal above the shear threshold should result in REJECT_SHEAR status and slashing."""
    mock_context = MagicMock()

    request = tap_pb2.ProposalRequest(
        header=tap_pb2.Header(
            sender_id="urn:agent:test-node-02",
            thermodynamic_state=tap_pb2.ThermodynamicState(
                staked_energy_collateral=1000
            ),
        ),
        payload=b"Fluffy uncalibrated input data...",
        payload_utility_density=0.40,  # 60% shear
    )

    response = servicer.SubmitProposal(request, mock_context)

    assert response.status == "REJECT_SHEAR"
    assert response.earned_yield == 0
    assert response.collateral_returned == 0
    assert (
        servicer.agent_vaults["urn:agent:test-node-02"] == 4000
    )  # 5000 base - 1000 slashed