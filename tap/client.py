# =====================================================================
# 3. CLIENT NODE (Proposer Node)
# =====================================================================
import grpc
from tap.proto import tap_pb2
from tap.proto import tap_pb2_grpc

class TAPClientNode:
    def __init__(self, target_host="localhost:50051", agent_id="urn:agent:proposer-node-01"):
        self.channel = grpc.insecure_channel(target_host)
        self.stub = tap_pb2_grpc.TAPServiceStub(self.channel)
        self.agent_id = agent_id

    def send_proposal(self, payload: str, utility_density: float, staked_collateral: int):
        request = tap_pb2.ProposalRequest(
            header=tap_pb2.Header(
                tap_version="1.0",
                sender_id=self.agent_id,
                receiver_id="urn:agent:synthesizer-node-01",
                session_id="sess_alpha_99",
                thermodynamic_state=tap_pb2.ThermodynamicState(
                    ground_state_verified=True,
                    staked_energy_collateral=staked_collateral,
                    cumulative_shear_stress=0.05,
                    free_volume_ratio=0.85
                )
            ),
            contract_type="CONTEXT_SYNTHESIS",
            resource_request=tap_pb2.ResourceRequest(
                max_context_tokens=2048,
                compute_precision="FP16",
                timeout_ms=1000
            ),
            payload=payload.encode("utf-8") if isinstance(payload, str) else payload, 
            payload_utility_density=utility_density
        )

        try:
            response = self.stub.SubmitProposal(request)
            return response
        except grpc.RpcError as e:
            print(f"[CLIENT ERROR] RPC Failed: {e.code()} - {e.details()}")
            return None

    def close(self):
        self.channel.close()

