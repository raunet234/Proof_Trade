from __future__ import annotations
from bnbagent import ERC8004Agent, AgentEndpoint, EVMWalletProvider


def register_agent(
    wallet_password: str,
    private_key: str,
    network: str = "bsc-testnet",
    name: str = "ProofTrade",
    description: str = "Prop-firm-style autonomous crypto trading agent on BSC",
) -> dict:
    wallet = EVMWalletProvider(
        password=wallet_password,
        private_key=private_key,
    )

    sdk = ERC8004Agent(network=network, wallet_provider=wallet)

    agent_uri = sdk.generate_agent_uri(
        name=name,
        description=description,
        endpoints=[
            AgentEndpoint(
                name="ProofTrade-Agent",
                endpoint="https://prooftrade.example.com/status",
                version="0.1.0",
            ),
        ],
    )

    result = sdk.register_agent(agent_uri=agent_uri)
    return result
