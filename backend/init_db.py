"""
Database initialization script for CEO Tracker.

Seeds the database with the top 20 companies and their CEOs.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import engine, SessionLocal, Base
from app.models import Company, CEO


def seed_database():
    """Seed the database with top 20 companies and CEOs."""
    db = SessionLocal()

    try:
        # Check if already seeded
        existing_companies = db.query(Company).count()
        if existing_companies > 0:
            print(f"Database already contains {existing_companies} companies. Skipping seed.")
            return

        print("Seeding database...")

        # Top 20 Companies and CEOs by market cap
        companies_data = [
            {
                "name": "Apple",
                "ticker": "AAPL",
                "ceo": "Tim Cook",
                "sector": "Technology",
                "industry": "Consumer Electronics"
            },
            {
                "name": "Microsoft",
                "ticker": "MSFT",
                "ceo": "Satya Nadella",
                "sector": "Technology",
                "industry": "Software"
            },
            {
                "name": "NVIDIA",
                "ticker": "NVDA",
                "ceo": "Jensen Huang",
                "sector": "Technology",
                "industry": "Semiconductors"
            },
            {
                "name": "Alphabet",
                "ticker": "GOOGL",
                "ceo": "Sundar Pichai",
                "sector": "Technology",
                "industry": "Internet Services"
            },
            {
                "name": "Amazon",
                "ticker": "AMZN",
                "ceo": "Andy Jassy",
                "sector": "Consumer Cyclical",
                "industry": "Internet Retail"
            },
            {
                "name": "Meta",
                "ticker": "META",
                "ceo": "Mark Zuckerberg",
                "sector": "Technology",
                "industry": "Social Media"
            },
            {
                "name": "Tesla",
                "ticker": "TSLA",
                "ceo": "Elon Musk",
                "sector": "Consumer Cyclical",
                "industry": "Auto Manufacturers"
            },
            {
                "name": "Berkshire Hathaway",
                "ticker": "BRK.B",
                "ceo": "Warren Buffett",
                "sector": "Financial",
                "industry": "Conglomerates"
            },
            {
                "name": "Broadcom",
                "ticker": "AVGO",
                "ceo": "Hock Tan",
                "sector": "Technology",
                "industry": "Semiconductors"
            },
            {
                "name": "Eli Lilly",
                "ticker": "LLY",
                "ceo": "David Ricks",
                "sector": "Healthcare",
                "industry": "Drug Manufacturers"
            },
            {
                "name": "Taiwan Semiconductor",
                "ticker": "TSM",
                "ceo": "C.C. Wei",
                "sector": "Technology",
                "industry": "Semiconductors"
            },
            {
                "name": "Novo Nordisk",
                "ticker": "NVO",
                "ceo": "Lars Fruergaard Jorgensen",
                "sector": "Healthcare",
                "industry": "Drug Manufacturers"
            },
            {
                "name": "Walmart",
                "ticker": "WMT",
                "ceo": "Doug McMillon",
                "sector": "Consumer Defensive",
                "industry": "Discount Stores"
            },
            {
                "name": "JPMorgan Chase",
                "ticker": "JPM",
                "ceo": "Jamie Dimon",
                "sector": "Financial",
                "industry": "Banks"
            },
            {
                "name": "Visa",
                "ticker": "V",
                "ceo": "Ryan McInerney",
                "sector": "Financial",
                "industry": "Credit Services"
            },
            {
                "name": "Mastercard",
                "ticker": "MA",
                "ceo": "Michael Miebach",
                "sector": "Financial",
                "industry": "Credit Services"
            },
            {
                "name": "Adobe",
                "ticker": "ADBE",
                "ceo": "Shantanu Narayen",
                "sector": "Technology",
                "industry": "Software"
            },
            {
                "name": "Netflix",
                "ticker": "NFLX",
                "ceo": "Ted Sarandos",
                "sector": "Communication",
                "industry": "Entertainment"
            },
            {
                "name": "Costco",
                "ticker": "COST",
                "ceo": "Ron Vachris",
                "sector": "Consumer Defensive",
                "industry": "Discount Stores"
            },
            {
                "name": "PayPal",
                "ticker": "PYPL",
                "ceo": "Alex Chriss",
                "sector": "Technology",
                "industry": "Transaction Services"
            },
        ]

        # Additional companies that might be mentioned (not in top 20)
        additional_companies = [
            {"name": "Marvell Technology", "ticker": "MRVL", "sector": "Technology", "industry": "Semiconductors"},
            {"name": "AMD", "ticker": "AMD", "sector": "Technology", "industry": "Semiconductors"},
            {"name": "Intel", "ticker": "INTC", "sector": "Technology", "industry": "Semiconductors"},
            {"name": "Qualcomm", "ticker": "QCOM", "sector": "Technology", "industry": "Semiconductors"},
            {"name": "Johnson & Johnson", "ticker": "JNJ", "sector": "Healthcare", "industry": "Drug Manufacturers"},
        ]

        # Create tracked companies (top 5)
        for company_data in companies_data:
            ceo_name = company_data.pop("ceo")

            company = Company(
                is_tracked=True,
                **company_data
            )
            db.add(company)
            db.flush()

            # Create CEO
            ceo = CEO(
                name=ceo_name,
                company_id=company.id,
                title="CEO"
            )
            db.add(ceo)

            print(f"Created company: {company.name} ({company.ticker}) - CEO: {ceo_name}")

        # Create additional companies (not tracked, but can be mentioned)
        for company_data in additional_companies:
            company = Company(
                is_tracked=False,
                **company_data
            )
            db.add(company)
            print(f"Created additional company: {company.name} ({company.ticker})")

        db.commit()
        print("\nDatabase seeded successfully!")
        print(f"Created {len(companies_data)} tracked companies with CEOs")
        print(f"Created {len(additional_companies)} additional companies")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created.")

    # Seed the database
    seed_database()
