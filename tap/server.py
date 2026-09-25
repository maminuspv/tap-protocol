#=====================================================================
# 2. SERVER NODE (Thermodynamic Middleware & Vault)
# =====================================================================

import concurrent.futures
import grpc
from tap.proto import tap_pb2
from tap.proto import tap_pb2_grpc

class TAPServerServicer(tap_pb2_grpc.TAPServiceServicer):
    def __init__(self, max_allowed_shear: float = 0.30):
        self.max_allowed_shear = max_allowed_shear
        self.agent_vaults = {}

    def SubmitProposal(self, request, context):
        sender = request.header.sender_id
        staked = request.header.thermodynamic_state.staked_energy_collateral
        utility_density = request.payload_utility_density

        if sender not in self.agent_vaults:
            self.agent_vaults[sender] = 5000  # Initial energy allocation

        instantaneous_shear = 1.0 - utility_density

        # Shear stress enforcement
        if instantaneous_shear > self.max_allowed_shear:
            slashed = staked
            self.agent_vaults[sender] -= slashed
            return tap_pb2.ProposalResponse(
                status="REJECT_SHEAR",
                reason=f"Shear stress ({instantaneous_shear:.2f}) breached maximum threshold ({self.max_allowed_shear})",
                collateral_returned=0,
                earned_yield=0,
                current_shear_score=instantaneous_shear
            )

        # Work executed at zero-shear baseline
        earned_yield = int(staked * 0.25)
        self.agent_vaults[sender] += earned_yield

        return tap_pb2.ProposalResponse(
            status="ANNEALED",
            reason="Work executed at zero-shear baseline.",
            collateral_returned=staked,
            earned_yield=earned_yield,
            current_shear_score=instantaneous_shear
        )


def run_server(port=50051):
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=4))
    tap_pb2_grpc.add_TAPServiceServicer_to_server(TAPServerServicer(max_allowed_shear=0.30), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[SYSTEM] TAP Server initialized on port {port}. Listening for proposal streams...")
    return server
