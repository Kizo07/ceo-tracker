"""Relationship integrity tests.

Guards the back_populates wiring between Company.mentions_received and
CompanyMention.mentioned_company (previously one-sided — see PR #3 review).
"""
from app.models import Company, CompanyMention


def test_company_mention_relationship_is_bidirectional(db_session):
    company = Company(name="Marvell Technology", ticker="MRVL", is_tracked=False)
    db_session.add(company)
    db_session.flush()

    # A press-release mention (speech_id NULL) — exercises Company <-> CompanyMention.
    mention = CompanyMention(
        mentioned_company_id=company.id,
        context_text="positive mention",
        sentiment="positive",
    )
    db_session.add(mention)
    db_session.commit()

    db_session.expire_all()
    fresh_company = db_session.get(Company, company.id)
    fresh_mention = db_session.get(CompanyMention, mention.id)

    # Bidirectional navigation works only when back_populates is mutual.
    assert fresh_mention.mentioned_company is fresh_company
    assert fresh_mention in fresh_company.mentions_received
