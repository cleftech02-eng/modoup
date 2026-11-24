from database import SessionLocal
from model import Realm, Lesson
REALMS = [
    {"name": "Frontend", "slug": "frontend",
     "description": "Build what users see: HTML, CSS, JavaScript and React."},
    {"name": "Backend", "slug": "backend",
     "description": "Power the apps behind the scenes: APIs, databases and servers."},
    {"name": "Cybersecurity", "slug": "cybersecurity",
     "description": "Learn to protect systems, data and people online."},
    {"name": "Data Analytics", "slug": "data-analytics",
     "description": "Turn raw data into insights with Excel, SQL and dashboards."},
    {"name": "Product Design", "slug": "product-design",
     "description": "Design friendly, usable products with UI/UX principles."},
]

def seed():
    db = SessionLocal()
    try:
        for r in REALMS:
            exists = db.query(Realm).filter(Realm.slug == r["slug"]).first()
            if exists:
                continue
            realm = Realm(**r)
            db.add(realm)
            db.flush()  # gives realm.id without committing yet

            # Placeholder lessons: replace the content with real material later
            for i in range(1, 4):
                db.add(Lesson(
                    title=f"{r['name']} Lesson {i}",
                    content=f"Content for {r['name']} lesson {i} goes here.",
                    order_index=i,
                    realm_id=realm.id,
                ))
        db.commit()
        print("Seeding done.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()