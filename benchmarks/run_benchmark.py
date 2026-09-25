import concurrent.futures
import time
import grpc
from tap.proto import tap_pb2
from tap.proto import tap_pb2_grpc


def run_mutualistic_agent(agent_id: str, cycles: int = 10):
    """Simulates an agent submitting high-utility, low-shear payloads."""
    channel = grpc.insecure_channel("localhost:50051")
    stub = tap_pb2_grpc.TAPServiceStub(channel)

    print(f"[{agent_id}] Starting Mutualistic Agent Simulation...")
    for i in range(cycles):
        request = tap_pb2.ProposalRequest(
            agent_id=agent_id,
            staked_energy_collateral=100.0,
            payload_utility_density=0.85,  # High utility -> Shear = 0.15 (Accepted)
            payload_data=f"Valid execution frame {i}".encode("utf-8"),
        )
        try:
            response = stub.SubmitProposal(request)
            print(
                f"[{agent_id}] Cycle {i+1}: Accepted={response.accepted} | "
                f"Shear={response.instantaneous_shear_stress:.2f} | "
                f"Balance={response.updated_energy_balance:.2f}"
            )
        except grpc.RpcError as e:
            print(f"[{agent_id}] RPC Error: {e.details()}")
        time.sleep(0.1)


def run_parasitic_agent(agent_id: str, cycles: int = 10):
    """Simulates an agent submitting low-utility, high-shear payloads (bloat/free-riding)."""
    channel = grpc.insecure_channel("localhost:50051")
    stub = tap_pb2_grpc.TAPServiceStub(channel)

    print(f"[{agent_id}] Starting Parasitic Agent Simulation...")
    for i in range(cycles):
        request = tap_pb2.ProposalRequest(
            agent_id=agent_id,
            staked_energy_collateral=100.0,
            payload_utility_density=0.40,  # Low utility -> Shear = 0.60 (Triggers Slashing)
            payload_data=f"Bloated context frame {i}".encode("utf-8"),
        )
        try:
            response = stub.SubmitProposal(request)
            print(
                f"[{agent_id}] Cycle {i+1}: Accepted={response.accepted} | "
                f"Shear={response.instantaneous_shear_stress:.2f} | "
                f"Balance={response.updated_energy_balance:.2f} | "
                f"Status='{response.status_message}'"
            )
        except grpc.RpcError as e:
            print(f"[{agent_id}] RPC Error: {e.details()}")
        time.sleep(0.1)


def execute_benchmark():
    print("=" * 60)
    print("      TAP/1.0 MULTI-AGENT THERMODYNAMIC BENCHMARK      ")
    print("=" * 60)

    # Run agent workers concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(run_mutualistic_agent, "Mutualist_Node_01", 5),
            executor.submit(run_mutualistic_agent, "Mutualist_Node_02", 5),
            executor.submit(run_parasitic_agent, "Parasite_Node_01", 5),
        ]
        concurrent.futures.wait(futures)

    print("=" * 60)
    print("Benchmark completed. Check collateral slashing logs above.")
    print("=" * 60)


if __name__ == "__main__":
    execute_benchmark()