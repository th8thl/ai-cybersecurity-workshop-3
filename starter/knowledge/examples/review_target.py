"""Read-only review target for the hallucinated SQL-injection exercise.

Inspect the placeholder and separately bound owner ID. This is evidence for
this query only, not a claim that an entire application has no SQL injection.
"""


def own_tickets(connection, actor_id):
    return connection.execute(
        "SELECT id, title FROM tickets_ticket WHERE owner_id = ?",
        (actor_id,),
    ).fetchall()
