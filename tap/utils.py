# =====================================================================
# 4. RUNNABLE VERIFICATION WORKFLOW
# =====================================================================
import time
from tap.client import TAPClientNode
from tap.server import run_server

if __name__ == "__main__":
    # Start the TAP Server
    server = run_server()
    time.sleep(1)

    client = TAPClientNode()

    try:
        print("\n=======================================================")
        print("TEST 1: Submitting High-Utility / Low-Shear Proposal")
        print("=======================================================")
        res1 = client.send_proposal(
            payload="SELECT * FROM verified_knowledge_base WHERE confidence > 0.95;",
            utility_density=0.90,  # 90% Signal -> 10% Shear (PASSES)
            staked_collateral=500
        )
        print(f"[CLIENT RESULT] Status: {res1.status} | Reason: {res1.reason}")

        print("\n=======================================================")
        print("TEST 2: Submitting Low-Utility / High-Shear Proposal (Bloat/Noise)")
        print("=======================================================")
        res2 = client.send_proposal(
            payload="A long, uncalibrated, conversational prompt with heavy fluff...",
            utility_density=0.40,  # 40% Signal -> 60% Shear (FAILS & SLASHES)
            staked_collateral=1000
        )
        print(f"[CLIENT RESULT] Status: {res2.status} | Reason: {res2.reason}")

    finally:
        client.close()
        server.stop(grace=0)
        print("\n[SYSTEM] Simulation complete. TAP Server shut down.")
