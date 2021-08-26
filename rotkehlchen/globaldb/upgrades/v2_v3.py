import logging
import sqlite3
from collections import defaultdict

from rotkehlchen.constants.resolver import CHAIN_ID, EVM_TOKEN_KIND, evm_address_to_identifier
from rotkehlchen.globaldb.schema import (
    DB_V3_CREATE_COMMON_ASSETS_DETAILS,
    DB_V3_CREATE_ASSETS,
    DB_V3_CREATE_EVM_TOKENS,
    DB_V3_CREATE_ASSETS_EVM_TOKENS,
    DB_V3_CREATE_MULTIASSETS,
)

log = logging.getLogger(__name__)

def upgrade_ethereum_assets(query: List[Any]) -> Tuple[Any]
    old_ethereum_data = []
    old_ethereum_id_to_new = {}
    emv_tuples = []
    assets_tuple = []
    common_asset_details = []

    for entry in result:
        new_id = evm_address_to_identifier(
            address=entry[0],
            chain=CHAIN_ID.ETHEREUM_CHAIN_IDENTIFIER,
            token_type=EVM_TOKEN_KIND.ERC20,
            collectible_id=None,
        )
        old_ethereum_id_to_new[entry[3]] = new_id
        old_ethereum_data.append((new_id, *entry))

    for entry in old_ethereum_data:
        emv_tuples.append((
            entry[0],  # identifier
            EVM_TOKEN_KIND.ERC20.value,  # token type
            '1',  # chain
            entry[1],  # address
            entry[2],  # decimals
            entry[3],  # protocol
        ))
        new_swapped_for = old_ethereum_id_to_new.get(entry[8], entry[8])
        assets_tuple.append((
            entry[0],  # identifier
            'C',  # type
            entry[7],  # started
            new_swapped_for,  # swapped for
            entry[0],  # common_details_id
        ))
        common_asset_details.append((
            entry[0],  # identifier
            entry[5],  # name
            entry[6],  # symbol
            entry[9],  # coingecko
            entry[10],  # cryptocompare
            None,  # forked
        ))

    return (
        emv_tuples,
        assets_tuple,
        common_asset_details
    )

def upgrade_other_assets(query: List[Any]) -> Tuple[Any]:


def upgrade_ethereum_asset_ids_v3(connection: sqlite3.Connection) -> None:
    # Get all ethereum ids
    cursor = connection.cursor()
    result = cursor.execute('SELECT * from underlying_tokens_list;')
    underlying_tokens_list_tuples = result.fetchall()
    result = cursor.execute(
        'SELECT A.address, A.decimals, A.protocol, B.identifier, B.name, B.symbol, B.started, '
        'B.swapped_for, B.coingecko, B.cryptocompare FROM assets '
        'AS B JOIN ethereum_tokens '
        'AS A ON A.address = B.details_reference WHERE B.type="C";',
    )

    emv_tuples, assets_tuple, common_asset_details = upgrade_ethereum_assets(result)

    # Purge or delete tables with outdated information
    cursor.executescript("""
    PRAGMA foreign_keys=off;
    DELETE FROM user_owned_assets;
    DROP TABLE IF EXISTS assets;
    DROP TABLE IF EXISTS ethereum_tokens;
    DROP TABLE IF EXISTS common_asset_details;
    DROP TABLE IF EXISTS underlying_tokens_list;
    PRAGMA foreign_keys=on;
    """)

    # Create new tacles
    cursor.execute(DB_V3_CREATE_COMMON_ASSETS_DETAILS)
    cursor.execute(DB_V3_CREATE_ASSETS)
    cursor.execute(DB_V3_CREATE_EVM_TOKENS)
    cursor.execute(DB_V3_CREATE_ASSETS_EVM_TOKENS)
    cursor.execute(DB_V3_CREATE_MULTIASSETS)

    cursor.executemany(
        """INSERT OR IGNORE INTO common_asset_details(
            identifier, name, symbol, coingecko, cryptocompare, forked
        ) VALUES(?, ?, ?, ?, ?, ?)""",
        common_asset_details,
    )

    cursor.executemany(
        """INSERT OR IGNORE INTO assets(
            identifier, type, started, swapped_for, common_details_id
        )VALUES(?, ?, ?, ?, ?);""",
        assets_tuple,
    )
    # Underlying token list

    # all other asset details
    cursor.executemany(
        """INSERT OR IGNORE INTO evm_tokens(
            identifier, token_type, chain, address, decimals, protocol
        ) VALUES(?, ?, ?, ?, ?, ?)""",
        emv_tuples,
    )
    # and finally the user owned assets table
    #cursor.executemany(
    #    'INSERT OR IGNORE INTO user_owned_assets(asset_id) VALUES(?)',
    #    owned_assets_tuples,
    #)
    connection.commit()
