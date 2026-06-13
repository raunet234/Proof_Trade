from unittest.mock import patch, MagicMock
from src.agent_identity import register_agent

def test_register_agent_calls_sdk():
    mock_sdk = MagicMock()
    mock_sdk.generate_agent_uri.return_value = "uri://test"
    mock_sdk.register_agent.return_value = {"agentId": 42, "transactionHash": "0xabc"}

    with patch("src.agent_identity.ERC8004Agent", return_value=mock_sdk):
        with patch("src.agent_identity.EVMWalletProvider"):
            result = register_agent(
                wallet_password="test",
                private_key="0x123",
                network="bsc-testnet",
            )
            assert result["agentId"] == 42
            mock_sdk.register_agent.assert_called_once()
