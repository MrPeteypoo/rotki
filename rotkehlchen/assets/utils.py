import logging
from typing import TYPE_CHECKING, List, Optional

from rotkehlchen.constants.assets import A_ETH
from rotkehlchen.constants.resolver import ChainID, EvmTokenKind, evm_address_to_identifier
from rotkehlchen.errors import DeserializationError, UnknownAsset
from rotkehlchen.globaldb.handler import GlobalDBHandler
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.typing import ChecksumEvmAddress

from .asset import Asset, EvmToken, UnderlyingToken
from .typing import AssetType

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)


def add_ethereum_token_to_db(token_data: EvmToken) -> EvmToken:
    """Adds an ethereum token to the DB and returns it

    May raise:
    - InputError if token already exists in the DB
    """
    globaldb = GlobalDBHandler()
    globaldb.add_asset(
        asset_id=token_data.identifier,
        asset_type=AssetType.ETHEREUM_TOKEN,
        data=token_data,
    )
    # This can, but should not raise UnknownAsset, DeserializationError
    return EvmToken(token_data.identifier, form_with_incomplete_data=True)


def get_or_create_evm_token(
        userdb: 'DBHandler',
        symbol: str,
        ethereum_address: ChecksumEvmAddress,
        chain: ChainID,
        token_type: EvmTokenKind,
        name: Optional[str] = None,
        decimals: Optional[int] = None,
        protocol: Optional[str] = None,
        underlying_tokens: Optional[List[UnderlyingToken]] = None,
        form_with_incomplete_data: bool = False,
) -> EvmToken:
    """Given a token symbol and address return the <EvmToken>

    If the token exists in the GlobalDB it's returned. If not it's created and added.
    Note: if the token already exists but the other arguments don't match the
    existing token will still be silently returned
    """
    try:
        identifier = evm_address_to_identifier(
            address=ethereum_address,
            chain=chain,
            token_type=token_type,
        )
        ethereum_token = EvmToken(identifier, form_with_incomplete_data)
    except (UnknownAsset, DeserializationError):
        log.info(
            f'Encountered unknown asset {symbol} with address '
            f'{ethereum_address}. Adding it to the global DB',
        )
        token_data = EvmToken.initialize(
            address=ethereum_address,
            name=name,
            decimals=decimals,
            symbol=symbol,
            protocol=protocol,
            underlying_tokens=underlying_tokens,
            chain=chain,
            token_type=token_type,
        )
        # This can but should not raise InputError since it should not already exist
        ethereum_token = add_ethereum_token_to_db(token_data)
        userdb.add_asset_identifiers([ethereum_token.identifier])

    return ethereum_token


def get_asset_by_symbol(symbol: str, asset_type: Optional[AssetType] = None) -> Optional[Asset]:
    """Gets an asset by symbol from the DB.

    If no asset with that symbol or multiple assets with the same
    symbol are found returns None
    """
    if symbol == 'ETH':
        return A_ETH  # ETH can be ETH and ETH2 in the DB

    assets_data = GlobalDBHandler().get_assets_with_symbol(symbol, asset_type)
    if len(assets_data) != 1:
        return None

    return Asset(assets_data[0].identifier)


def symbol_to_asset_or_token(symbol: str) -> Asset:
    """Tries to turn the given symbol to an asset or an ethereum Token

    May raise:
    - UnknownAsset if an asset can't be found by the symbol or if
    more than one tokens match this symbol
    """
    try:
        asset = Asset(symbol)
    except UnknownAsset:
        # Let's search by symbol if a single asset matches
        maybe_asset = get_asset_by_symbol(symbol)
        if maybe_asset is None:
            raise
        asset = maybe_asset

    return asset


def symbol_to_ethereum_token(symbol: str) -> EvmToken:
    """Tries to turn the given symbol to an ethereum token

    May raise:
    - UnknownAsset if an ethereum token can't be found by the symbol or if
    more than one tokens match this symbol
    """
    maybe_asset = get_asset_by_symbol(symbol, asset_type=AssetType.ETHEREUM_TOKEN)
    if maybe_asset is None:
        raise UnknownAsset(symbol)

    # ignore type here since the identifier has to match an ethereum token at this point
    return EvmToken.from_asset(maybe_asset)  # type: ignore
