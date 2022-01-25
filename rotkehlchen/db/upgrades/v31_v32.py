from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler


def upgrade_v31_to_v32(db: 'DBHandler') -> None:
    """Upgrades the DB from v31 to v32
    We will use random identifiers for the history_events table. The id will be generated by sqlite
    and will be the column rowid

    Also adds the subtype REWARD to staking rewards (before they had type staking
    and no subtype)
    """
    cursor = db.conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS history_events_copy (
        event_identifier TEXT NOT NULL,
        sequence_index INTEGER NOT NULL,
        timestamp INTEGER NOT NULL,
        location TEXT NOT NULL,
        location_label TEXT,
        asset TEXT NOT NULL,
        amount TEXT NOT NULL,
        usd_value TEXT NOT NULL,
        notes TEXT,
        type TEXT NOT NULL,
        subtype TEXT
    );""")
    cursor.execute("""
    INSERT INTO history_events_copy (event_identifier, sequence_index, timestamp, location,
    location_label, asset, amount, usd_value, notes, type, subtype)
    SELECT event_identifier, sequence_index, timestamp, location, location_label, asset,
    amount, usd_value, notes, type, subtype
    FROM history_events;
    """)
    cursor.execute('DROP TABLE history_events;')
    cursor.execute('ALTER TABLE history_events_copy RENAME TO history_events;')
    cursor.execute(
        'UPDATE history_events SET subtype="reward" WHERE type="staking" AND subtype IS NULL;',
    )
    db.conn.commit()
