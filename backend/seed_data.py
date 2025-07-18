#!/usr/bin/env python3
"""
Seed data script to create 15 dummy mentors for testing
"""
import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime
from passlib.context import CryptContext

# Load environment variables
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Dummy mentor data
DUMMY_MENTORS = [
    {
        "name": "Dr. Sarah Chen",
        "email": "sarah.chen@email.com",
        "skills": ["Machine Learning", "Python", "TensorFlow", "Data Science"],
        "bio": "PhD in Computer Science with 10+ years in AI/ML. Former Google researcher, now helping startups implement AI solutions.",
        "experience_years": 10,
        "hourly_rate": 120.0,
        "avatar_url": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150"
    },
    {
        "name": "Marcus Rodriguez",
        "email": "marcus.rodriguez@email.com",
        "skills": ["React", "Node.js", "JavaScript", "Full Stack"],
        "bio": "Senior Full Stack Developer at Meta. Specialized in React ecosystem and modern web development practices.",
        "experience_years": 8,
        "hourly_rate": 95.0,
        "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
    },
    {
        "name": "Emily Johnson",
        "email": "emily.johnson@email.com",
        "skills": ["Product Management", "Strategy", "Agile", "Leadership"],
        "bio": "VP of Product at successful fintech startup. Expert in product strategy, user research, and team leadership.",
        "experience_years": 12,
        "hourly_rate": 150.0,
        "avatar_url": "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150"
    },
    {
        "name": "David Kim",
        "email": "david.kim@email.com",
        "skills": ["DevOps", "AWS", "Docker", "Kubernetes"],
        "bio": "Cloud Infrastructure Engineer with expertise in AWS, containerization, and CI/CD pipelines. Helped scale multiple startups.",
        "experience_years": 9,
        "hourly_rate": 110.0,
        "avatar_url": "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150"
    },
    {
        "name": "Rachel Green",
        "email": "rachel.green@email.com",
        "skills": ["UI/UX Design", "Figma", "User Research", "Prototyping"],
        "bio": "Senior UX Designer at Apple. Passionate about creating intuitive user experiences and mentoring junior designers.",
        "experience_years": 7,
        "hourly_rate": 85.0,
        "avatar_url": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150"
    },
    {
        "name": "James Wilson",
        "email": "james.wilson@email.com",
        "skills": ["Java", "Spring Boot", "Microservices", "Architecture"],
        "bio": "Enterprise Software Architect with 15+ years experience. Specialized in large-scale distributed systems and team mentoring.",
        "experience_years": 15,
        "hourly_rate": 130.0,
        "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150"
    },
    {
        "name": "Lisa Wang",
        "email": "lisa.wang@email.com",
        "skills": ["Data Analysis", "SQL", "Python", "Business Intelligence"],
        "bio": "Senior Data Analyst at Netflix. Expert in data visualization, statistical analysis, and business intelligence.",
        "experience_years": 6,
        "hourly_rate": 75.0,
        "avatar_url": "https://images.unsplash.com/photo-1487412720507-e7ab37603c6f?w=150"
    },
    {
        "name": "Michael Brown",
        "email": "michael.brown@email.com",
        "skills": ["Cybersecurity", "Penetration Testing", "Network Security", "Compliance"],
        "bio": "Cybersecurity expert with government and enterprise experience. Specialized in threat assessment and security architecture.",
        "experience_years": 11,
        "hourly_rate": 140.0,
        "avatar_url": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150"
    },
    {
        "name": "Jennifer Davis",
        "email": "jennifer.davis@email.com",
        "skills": ["Mobile Development", "Swift", "iOS", "Android"],
        "bio": "Mobile app developer with 50+ apps published. Former iOS engineer at Uber, now freelancing and mentoring.",
        "experience_years": 9,
        "hourly_rate": 100.0,
        "avatar_url": "https://images.unsplash.com/photo-1489424731084-a5d8b219a5bb?w=150"
    },
    {
        "name": "Robert Taylor",
        "email": "robert.taylor@email.com",
        "skills": ["Blockchain", "Solidity", "Web3", "Smart Contracts"],
        "bio": "Blockchain developer and consultant. Built DeFi protocols and NFT platforms. Early adopter with deep Web3 expertise.",
        "experience_years": 5,
        "hourly_rate": 160.0,
        "avatar_url": "https://images.unsplash.com/photo-1463453091185-61582044d556?w=150"
    },
    {
        "name": "Amanda Martinez",
        "email": "amanda.martinez@email.com",
        "skills": ["Digital Marketing", "SEO", "Content Strategy", "Analytics"],
        "bio": "Digital marketing expert with proven track record of growing startups. Specialized in SEO, content marketing, and growth hacking.",
        "experience_years": 8,
        "hourly_rate": 80.0,
        "avatar_url": "https://images.unsplash.com/photo-1508214751196-bcfd4ca60f91?w=150"
    },
    {
        "name": "Chris Anderson",
        "email": "chris.anderson@email.com",
        "skills": ["Sales", "Business Development", "Negotiation", "CRM"],
        "bio": "VP of Sales with consistent record of exceeding targets. Expert in B2B sales, team building, and sales process optimization.",
        "experience_years": 13,
        "hourly_rate": 125.0,
        "avatar_url": "https://images.unsplash.com/photo-1519244703995-f4e0f30006d5?w=150"
    },
    {
        "name": "Nicole Thompson",
        "email": "nicole.thompson@email.com",
        "skills": ["Finance", "Investment", "Financial Planning", "Startups"],
        "bio": "Former Goldman Sachs analyst, now startup CFO. Expert in financial modeling, fundraising, and strategic planning.",
        "experience_years": 10,
        "hourly_rate": 135.0,
        "avatar_url": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150"
    },
    {
        "name": "Kevin Lee",
        "email": "kevin.lee@email.com",
        "skills": ["Operations", "Process Optimization", "Lean", "Six Sigma"],
        "bio": "Operations expert with experience scaling companies from 10 to 1000+ employees. Specialized in process improvement and efficiency.",
        "experience_years": 12,
        "hourly_rate": 115.0,
        "avatar_url": "https://images.unsplash.com/photo-1507591064344-4c6ce005b128?w=150"
    },
    {
        "name": "Sophia Rodriguez",
        "email": "sophia.rodriguez@email.com",
        "skills": ["HR", "Talent Acquisition", "People Operations", "Culture"],
        "bio": "Head of People at fast-growing tech company. Expert in hiring, culture building, and employee engagement strategies.",
        "experience_years": 9,
        "hourly_rate": 90.0,
        "avatar_url": "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150"
    }
]

async def create_dummy_mentors():
    """Create 15 dummy mentors with profiles"""
    print("Creating 15 dummy mentors...")
    
    for i, mentor_data in enumerate(DUMMY_MENTORS):
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = pwd_context.hash("mentor123")  # Default password for all mentors
        
        user_doc = {
            "id": user_id,
            "email": mentor_data["email"],
            "name": mentor_data["name"],
            "role": "mentor",
            "is_verified": True,  # Auto-verify dummy mentors
            "is_active": True,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert user
        await db.users.insert_one(user_doc)
        
        # Create profile
        profile_doc = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "bio": mentor_data["bio"],
            "skills": mentor_data["skills"],
            "experience_years": mentor_data["experience_years"],
            "hourly_rate": mentor_data["hourly_rate"],
            "available": True,
            "avatar_url": mentor_data["avatar_url"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Insert profile
        await db.profiles.insert_one(profile_doc)
        
        print(f"✅ Created mentor {i+1}: {mentor_data['name']}")
    
    print(f"\n🎉 Successfully created {len(DUMMY_MENTORS)} dummy mentors!")
    print("All mentors have been auto-verified and are ready to use.")
    print("Default password for all mentors: 'mentor123'")

async def create_admin_user():
    """Create a default admin user"""
    print("\nCreating default admin user...")
    
    # Check if admin already exists
    existing_admin = await db.users.find_one({"email": "admin@testnet.com"})
    if existing_admin:
        print("✅ Admin user already exists")
        return
    
    user_id = str(uuid.uuid4())
    hashed_password = pwd_context.hash("admin123")
    
    admin_doc = {
        "id": user_id,
        "email": "admin@testnet.com",
        "name": "Admin User",
        "role": "admin",
        "is_verified": True,
        "is_active": True,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.users.insert_one(admin_doc)
    
    # Create empty profile for admin
    profile_doc = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "bio": "Platform Administrator",
        "skills": [],
        "experience_years": 0,
        "hourly_rate": 0.0,
        "available": False,
        "avatar_url": "",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.profiles.insert_one(profile_doc)
    
    print("✅ Created admin user: admin@testnet.com")
    print("Admin password: 'admin123'")

async def main():
    """Main function to seed the database"""
    print("🌱 Seeding Testnet database with dummy data...")
    
    try:
        await create_admin_user()
        await create_dummy_mentors()
        
        print("\n🎯 Database seeding completed successfully!")
        print("\nLogin credentials:")
        print("- Admin: admin@testnet.com / admin123")
        print("- Any mentor: [mentor-email] / mentor123")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())