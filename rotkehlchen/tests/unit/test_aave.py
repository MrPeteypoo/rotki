from rotkehlchen.assets.asset import EvmToken
from rotkehlchen.chain.ethereum.modules.aave.common import (
    aave_reserve_address_to_reserve_asset,
    asset_to_aave_reserve_address,
    atoken_to_asset,
)
from rotkehlchen.constants.assets import A_ETH
from rotkehlchen.constants.ethereum import AAVE_ETH_RESERVE_ADDRESS
from rotkehlchen.globaldb.handler import GlobalDBHandler
from rotkehlchen.tests.utils.aave import ATOKENV1_TO_ASSET, ATOKENV2_ADDRESS_TO_RESERVE_ASSET


def test_aave_reserve_mapping():
    atokensv1 = GlobalDBHandler().get_evm_tokens(protocol='aave')
    for token in atokensv1:
        underlying_asset = ATOKENV1_TO_ASSET[token]
        if underlying_asset == A_ETH:
            assert asset_to_aave_reserve_address(underlying_asset) == AAVE_ETH_RESERVE_ADDRESS
            continue

        assert aave_reserve_address_to_reserve_asset(underlying_asset.evm_address) == underlying_asset  # noqa: E501
        assert asset_to_aave_reserve_address(underlying_asset) == underlying_asset.evm_address


def test_atoken_to_asset():
    cursor = GlobalDBHandler()._conn.cursor()
    result = cursor.execute(
        'SELECT A.address from evm_tokens as A LEFT OUTER JOIN common_asset_details as B '
        'WHERE A.identifier=B.identifier AND A.protocol IN (?, ?)',
        ('aave', 'aave-v2'),
    )
    for entry in result:
        atoken = EvmToken(entry[0])
        reserve_asset = atoken_to_asset(atoken)
        if atoken in ATOKENV1_TO_ASSET:
            assert reserve_asset == ATOKENV1_TO_ASSET[atoken]
        else:
            assert reserve_asset == ATOKENV2_ADDRESS_TO_RESERVE_ASSET[atoken.evm_address]

    for atokenv1, reserve_asset in ATOKENV1_TO_ASSET.items():
        assert atoken_to_asset(atokenv1) == reserve_asset
