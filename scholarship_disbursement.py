"""Scholarship disbursement ledger.

Grants awards under different schemes, disburses the funds, archives
records and counts awards per scheme. Data is kept in an in-memory
SQLite database.
"""

import sqlite3


class ScholarshipLedger:
    """Ledger of scholarship awards backed by an SQLite connection."""

    def __init__(self, db_path=":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS awards ("
            "id INTEGER PRIMARY KEY, student TEXT, scheme TEXT, "
            "amount INTEGER, disbursed INTEGER)"
        )

    def grant(self, student, scheme, amount, audit=None):
        """Record a new award and append the student to the audit list.

        Returns the audit list. A fresh list is created for every call
        unless the caller passes one in.
        """
        if audit is None:
            audit = []
        if not isinstance(amount, int) or amount <= 0:
            raise ValueError(f"amount must be a positive integer: {amount!r}")
        self.conn.execute(
            "INSERT INTO awards (student, scheme, amount, disbursed) "
            "VALUES (?, ?, ?, 0)",
            (student, scheme, amount),
        )
        audit.append(student)
        return audit

    def disburse(self, award_id):
        """Mark an award as disbursed and return its amount.

        Returns None if the award does not exist or was already paid out,
        so the same award can never be disbursed twice.
        """
        row = self.conn.execute(
            "SELECT amount, disbursed FROM awards WHERE id = ?", (award_id,)
        ).fetchone()
        if row is None or row[1]:
            return None
        self.conn.execute(
            "UPDATE awards SET disbursed = 1 WHERE id = ?", (award_id,)
        )
        return row[0]

    def disbursed_total(self):
        """Return the total amount disbursed so far."""
        return self.conn.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM awards WHERE disbursed = 1"
        ).fetchone()[0]

    def archive(self):
        """Archive the awards (currently just reports that it ran)."""
        print("archiving awards")

    def by_scheme_count(self, scheme):
        """Return the number of awards granted under the given scheme."""
        if scheme is None:
            return 0
        return self.conn.execute(
            "SELECT COUNT(*) FROM awards WHERE scheme = ?", (scheme,)
        ).fetchone()[0]


def main():
    """Run a short demonstration of the ledger."""
    ledger = ScholarshipLedger()
    ledger.grant("Ishaan", "Merit", 50000)
    ledger.grant("Divya", "Need-based", 75000)
    print(ledger.disburse(1), ledger.disburse(9))
    print(ledger.by_scheme_count("Merit"), ledger.disbursed_total())
    ledger.archive()


if __name__ == "__main__":
    main()
