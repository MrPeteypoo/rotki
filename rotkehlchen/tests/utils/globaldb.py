from rotkehlchen.assets.asset import EvmToken, UnderlyingToken
from rotkehlchen.constants.resolver import ChainID, EvmTokenKind
from rotkehlchen.fval import FVal
from rotkehlchen.tests.utils.constants import A_MKR
from rotkehlchen.tests.utils.factories import make_ethereum_address
from rotkehlchen.typing import Timestamp

underlying_address1 = make_ethereum_address()
underlying_address2 = make_ethereum_address()
underlying_address3 = make_ethereum_address()

custom_address1 = make_ethereum_address()
custom_address2 = make_ethereum_address()
INITIAL_TOKENS = [
    EvmToken.initialize(
        address=custom_address1,
        decimals=4,
        name='Custom 1',
        symbol='CST1',
        started=Timestamp(0),
        swapped_for=A_MKR,
        coingecko='internet-computer',
        cryptocompare='ICP',
        protocol='uniswap',
        underlying_tokens=[
            UnderlyingToken(identifier=f'eip155:1/ERC20:{underlying_address1}', weight=FVal('0.5055')),  # noqa: E501
            UnderlyingToken(identifier=f'eip155:1/ERC20:{underlying_address2}', weight=FVal('0.1545')),  # noqa: E501
            UnderlyingToken(identifier=f'eip155:1/ERC20:{underlying_address3}', weight=FVal('0.34')),  # noqa: E501
        ],
        chain=ChainID.ETHEREUM,
        token_type=EvmTokenKind.ERC20,
    ),
    EvmToken.initialize(
        address=custom_address2,
        decimals=18,
        name='Custom 2',
        symbol='CST2',
        chain=ChainID.ETHEREUM,
        token_type=EvmTokenKind.ERC20,
    ),
]

INITIAL_EXPECTED_TOKENS = [INITIAL_TOKENS[0]] + [
    EvmToken.initialize(underlying_address1),
    EvmToken.initialize(underlying_address2),
    EvmToken.initialize(underlying_address3),
] + [INITIAL_TOKENS[1]]


underlying_address4 = make_ethereum_address()
custom_address3 = make_ethereum_address()
CUSTOM_TOKEN3 = EvmToken.initialize(
    address=custom_address3,
    decimals=15,
    name='Custom 3',
    symbol='CST3',
    cryptocompare='ICP',
    protocol='aave',
    underlying_tokens=[
        UnderlyingToken(identifier=f'eip155:1/ERC20:{custom_address1}', weight=FVal('0.55')),
        UnderlyingToken(identifier=f'eip155:1/ERC20:{underlying_address4}', weight=FVal('0.45')),
    ],
    chain=ChainID.ETHEREUM,
    token_type=EvmTokenKind.ERC20,
)
