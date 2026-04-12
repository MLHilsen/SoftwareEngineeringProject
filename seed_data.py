"""
Paw Path — Demo Data Seeder
Run from your project root: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import app
from models import db, User, Pet, Application, Appointment, Adoption, MedicalRecord, BlogPost, Event, Notification, Favorite, CareLog
from werkzeug.security import generate_password_hash
from datetime import datetime, date, timedelta
import random

PETS = [
    dict(name="Biscuit",   species="dog",    breed="Golden Retriever", age=3,  gender="male",   size="large",  color="Golden",      status="available", adoption_fee=150, temperament="Gentle, loves kids, great with other dogs", special_needs=None,                description="Biscuit is the friendliest dog you'll ever meet. He knows sit, stay, and shake, and he's obsessed with tennis balls. Loves long walks and cuddles equally.",             image="https://images.unsplash.com/photo-1552053831-71594a27632d?w=600&q=80"),
    dict(name="Luna",      species="cat",    breed="Domestic Shorthair",age=2, gender="female", size="small",  color="Black",       status="available", adoption_fee=75,  temperament="Independent, curious, loves window perches", special_needs=None,               description="Luna is a sleek, mysterious beauty who warms up quickly once she trusts you. She loves sunny spots, feather toys, and will absolutely judge you from across the room.", image="https://images.unsplash.com/photo-1514888286974-6c03e2ca1dba?w=600&q=80"),
    dict(name="Mango",     species="dog",    breed="Beagle",           age=1,  gender="male",   size="medium", color="Tri-colour",  status="available", adoption_fee=120, temperament="Energetic, playful, nose always to the ground", special_needs=None,            description="Mango is a classic Beagle — endlessly curious and nose-first into everything. He needs an active family and a secure yard. Returns every escape with a wagging tail.", image="https://images.unsplash.com/photo-1586297135537-94bc9ba060aa?w=600&q=80"),
    dict(name="Cleo",      species="cat",    breed="Siamese Mix",      age=4,  gender="female", size="small",  color="Cream/Brown", status="available", adoption_fee=80,  temperament="Vocal, affectionate, bonds deeply with one person", special_needs=None,        description="Cleo will talk your ear off — Siamese style. She's dramatic, devoted, and will follow you from room to room narrating her day. Perfect for someone who wants a true companion.", image="https://images.unsplash.com/photo-1573865526739-10659fec78a5?w=600&q=80"),
    dict(name="Rocky",     species="dog",    breed="Labrador Mix",     age=5,  gender="male",   size="large",  color="Chocolate",   status="available", adoption_fee=100, temperament="Calm, obedient, excellent with seniors", special_needs=None,                   description="Rocky has been through basic training and is one of the most well-mannered dogs we've had. He's calm, loyal, and would thrive in a quiet home. Loves morning walks.", image="https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=600&q=80"),
    dict(name="Pepper",    species="rabbit", breed="Holland Lop",      age=2,  gender="female", size="small",  color="Grey/White",  status="available", adoption_fee=40,  temperament="Gentle, enjoys being held, quiet", special_needs=None,                          description="Pepper is a fluffy little Holland Lop with ears that flop adorably. She loves leafy greens, hay, and flopping dramatically when she's happy. Low-maintenance and sweet.", image="https://images.unsplash.com/photo-1585110396000-c9ffd4e4b308?w=600&q=80"),
    dict(name="Duke",      species="dog",    breed="German Shepherd",  age=4,  gender="male",   size="large",  color="Black/Tan",   status="available", adoption_fee=130, temperament="Protective, intelligent, needs experienced owner", special_needs="Needs secure fencing", description="Duke is sharp, loyal, and alert. He's been socialised well but thrives with an experienced dog owner who can give him purpose and structure. Would love a job to do.", image="https://images.unsplash.com/photo-1587300003388-59208cc962cb?w=600&q=80"),
    dict(name="Noodle",    species="cat",    breed="Maine Coon Mix",   age=3,  gender="male",   size="medium", color="Tabby",       status="available", adoption_fee=90,  temperament="Laid-back, fluffy, gets along with dogs", special_needs=None,                  description="Noodle is gloriously fluffy and wonderfully chill. He drapes himself over furniture like a rug and purrs at maximum volume. Surprisingly dog-friendly for a cat.", image="https://images.unsplash.com/photo-1596854407944-bf87f6fdd49e?w=600&q=80"),
    dict(name="Hazel",     species="dog",    breed="Border Collie",    age=2,  gender="female", size="medium", color="Black/White",  status="fostered",  adoption_fee=120, temperament="Highly intelligent, needs mental stimulation", special_needs="Needs daily exercise 2hr+", description="Hazel is brilliant — almost too smart. She needs a family ready to channel her energy into agility, fetch, or herding. An idle Border Collie is a destructive one.", image="https://images.unsplash.com/photo-1503256207526-0d5523f39c98?w=600&q=80"),
    dict(name="Oliver",    species="cat",    breed="Orange Tabby",     age=6,  gender="male",   size="medium", color="Orange",      status="available", adoption_fee=60,  temperament="Lazy, food-motivated, great with kids", special_needs=None,                    description="Oliver is a big orange loaf. He spends his days eating, napping in sunbeams, and occasionally allowing belly rubs. A true professional at relaxation.", image="https://images.unsplash.com/photo-1574158622682-e40e69881006?w=600&q=80"),
    dict(name="Stella",    species="dog",    breed="Dachshund",        age=3,  gender="female", size="small",  color="Brown",       status="available", adoption_fee=110, temperament="Stubborn, loyal, loves burrowing under blankets", special_needs=None,          description="Stella has the energy of a big dog in a tiny body and an opinion about everything. She burrows under every blanket she finds and will steal your spot on the couch.", image="https://images.unsplash.com/photo-1612196808214-b8e1d6145a8c?w=600&q=80"),
    dict(name="Willow",    species="cat",    breed="Persian Mix",      age=5,  gender="female", size="small",  color="White",       status="adopted",   adoption_fee=95,  temperament="Calm, regal, low-energy", special_needs="Daily grooming needed",               description="Willow has the serene energy of a cat who knows she's beautiful. She requires daily brushing but rewards it with gentle purring and slow blinking — the ultimate cat compliment.", image="https://images.unsplash.com/photo-1571566882372-1598d88abd90?w=600&q=80"),
]

BLOG_POSTS = [
    ("5 Tips for Introducing a New Pet to Your Home",
     """Bringing a new pet home is exciting — but the first few days are crucial. Here are five things we recommend to every adopter:\n\n1. Give them a safe space. Set up a quiet room with their bed, food, water and litter/pads before they arrive. Let them explore at their own pace.\n\n2. Be patient with hiding. Cats especially may disappear under a bed for 24-48 hours. This is completely normal — don't force interaction.\n\n3. Keep routines consistent. Feed at the same times, walk at the same times. Predictability builds confidence.\n\n4. Limit visitors for the first week. As tempting as it is to show off your new family member, overwhelming them with new people slows adjustment.\n\n5. Watch for stress signals — not eating, excessive hiding, or aggression. If these persist beyond a week, give us a call. We're always here to help.\n\nRemember: every pet adjusts at their own speed. Some take a day, some take a month. Your patience will be rewarded tenfold."""),
    ("Understanding Pet Adoption Fees — Where Does the Money Go?",
     """We get this question a lot, so we wanted to be fully transparent about our adoption fees and what they cover.\n\nEvery pet that comes through Paw Path receives: a full veterinary intake exam, all age-appropriate vaccinations, microchipping, spay/neuter surgery if old enough, flea/tick/heartworm prevention, and any urgent medical treatment needed.\n\nFor a dog, this typically costs us $350-600 depending on size and condition when they arrive. Our adoption fees ($100-150) cover a portion — the rest is funded by donations and grants.\n\nFor cats, costs run $200-400. Our fees ($60-95) reflect the same partial-cost model.\n\nWe will never turn away an animal because of cost, and we will never cut corners on their care. Your adoption fee isn't just a transaction — it directly funds the next animal's intake.\n\nThank you for making this possible."""),
    ("Meet Our Foster Family of the Month: The Hendersons",
     """Foster families are the backbone of Paw Path. Without them, we simply couldn't help as many animals as we do.\n\nThis month we're spotlighting the Henderson family — Sarah, Mike, and their two kids Emma (10) and Tyler (8) — who have fostered 14 animals over the past two years.\n\n"We started fostering because Emma kept asking for a dog," Sarah laughs. "We told her we'd try fostering first. That was twelve dogs and two cats ago."\n\nThe Hendersons specialise in dogs recovering from medical procedures or who need socialisation before adoption. They've helped animals overcome everything from broken legs to severe anxiety.\n\n"Tyler is magic with nervous dogs," Mike says. "He just sits on the floor, doesn't make eye contact, and eventually they come to him. Every time."\n\nIf you're interested in fostering, reach out through our website. We provide all food, supplies, and cover all vet costs. All you provide is love and a temporary home."""),
]

EVENTS = [
    ("Adoption Day — Saturday at Piedmont Park", datetime.now() + timedelta(days=7),  "Piedmont Park, Atlanta GA", "Join us for our monthly outdoor adoption day! Meet 20+ animals, chat with our team, and maybe find your forever companion. Free entry, all ages welcome."),
    ("Dog Training Workshop",                    datetime.now() + timedelta(days=14), "Paw Path HQ",              "A 2-hour beginner obedience workshop run by certified trainer Jamie Osei. Perfect for newly adopted dogs and their owners. Spots limited to 10 — RSVP required."),
    ("Fundraiser Gala — A Night for the Animals", datetime.now() + timedelta(days=21), "The Fox Theatre, Atlanta", "Our annual fundraising gala. Live music, silent auction, and a three-course dinner. Proceeds fund our 2026 expansion to a larger facility. Tickets: $75/person."),
    ("Volunteer Orientation",                    datetime.now() + timedelta(days=5),  "Paw Path HQ",              "New to volunteering with us? Attend our next orientation to learn about roles, responsibilities, and how to get started. 90 minutes, free."),
    ("Senior Pets Spotlight Day",                datetime.now() + timedelta(days=30), "Paw Path HQ",              "We're waiving adoption fees for all pets aged 7+ for one day. Senior pets make the most loving companions — come meet them!"),
]

def seed():
    with app.app_context():
        print("\n🌱 Seeding Paw Path demo data...")
        print("=" * 50)

        # ── Admin user ───────────────────────────────────
        admin = User.query.filter_by(email='admin@pawpath.com').first()
        if not admin:
            admin = User(full_name='Admin User', email='admin@pawpath.com', phone='404-555-0100',
                         address='123 Shelter Lane, Atlanta GA', role='admin', is_active=True)
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.flush()
            print("✅ Admin user created  →  admin@pawpath.com / admin123")
        else:
            print("ℹ️  Admin already exists")

        # ── Demo users ───────────────────────────────────
        demo_users = [
            ('Sarah Mitchell',  'sarah@demo.com',  '404-555-0101', '45 Maple St, Atlanta GA'),
            ('James Rivera',    'james@demo.com',  '404-555-0102', '88 Oak Ave, Decatur GA'),
            ('Priya Nair',      'priya@demo.com',  '404-555-0103', '12 Pine Rd, Sandy Springs GA'),
        ]
        users = [admin]
        for full_name, email, phone, address in demo_users:
            u = User.query.filter_by(email=email).first()
            if not u:
                u = User(full_name=full_name, email=email, phone=phone, address=address,
                         role='user', is_active=True)
                u.set_password('demo123')
                db.session.add(u)
                print(f"✅ User created  →  {email} / demo123")
            else:
                print(f"ℹ️  User already exists: {email}")
            users.append(u)
        db.session.flush()

        # ── Pets ─────────────────────────────────────────
        pets = []
        existing_pet_names = {p.name for p in Pet.query.all()}
        new_count = 0
        for p in PETS:
            if p['name'] in existing_pet_names:
                pets.append(Pet.query.filter_by(name=p['name']).first())
                continue
            pet = Pet(**p)
            db.session.add(pet)
            db.session.flush()
            pets.append(pet)
            new_count += 1
        print(f"✅ {new_count} pets added ({len(pets)} total)")

        # ── Medical records ───────────────────────────────
        available_pets = [p for p in pets if p.status != 'adopted']
        mr_count = 0
        for pet in available_pets[:8]:
            if not MedicalRecord.query.filter_by(pet_id=pet.pet_id).first():
                records = [
                    MedicalRecord(pet_id=pet.pet_id, record_type='vaccination',
                                  record_date=date.today() - timedelta(days=random.randint(30, 120)),
                                  vet_name='Dr. Angela Reeves', diagnosis=None,
                                  treatment='Annual core vaccines administered',
                                  medications='DHPP, Rabies, Bordetella' if pet.species=='dog' else 'FVRCP, Rabies',
                                  cost=85.00, next_appt_date=date.today() + timedelta(days=365),
                                  notes='Pet in good health', created_by=admin.user_id),
                    MedicalRecord(pet_id=pet.pet_id, record_type='checkup',
                                  record_date=date.today() - timedelta(days=random.randint(10, 29)),
                                  vet_name='Dr. Marcus Webb', diagnosis='Healthy, no concerns',
                                  treatment='Routine wellness exam',
                                  medications=None, cost=60.00, notes='Weight normal, teeth good',
                                  created_by=admin.user_id),
                ]
                for r in records:
                    db.session.add(r)
                mr_count += 2
        print(f"✅ {mr_count} medical records added")

        # ── Applications ──────────────────────────────────
        app_users = users[1:]  # exclude admin
        app_pets  = [p for p in pets if p.status == 'available'][:6]
        app_count = 0
        for i, (user, pet) in enumerate(zip(app_users * 3, app_pets)):
            if not Application.query.filter_by(user_id=user.user_id, pet_id=pet.pet_id).first():
                statuses = ['pending', 'pending', 'approved', 'rejected', 'pending', 'approved']
                a = Application(
                    user_id=user.user_id, pet_id=pet.pet_id,
                    application_type='adoption' if i % 3 != 0 else 'foster',
                    status=statuses[i % len(statuses)],
                    reason=f"I've always wanted a {pet.species} and {pet.name} seems like a perfect match for my lifestyle.",
                    housing=random.choice(['house', 'apartment', 'condo']),
                    has_yard=random.choice([True, False]),
                    has_other_pets=False, household_mem=random.randint(1, 4),
                    pet_experience='Grew up with pets, owned dogs/cats for 10+ years.',
                    vet_name='Dr. Angela Reeves', vet_phone='404-555-0199',
                    reference1_name='Jordan Lee', reference1_phone='404-555-0120',
                    reference2_name='Casey Park', reference2_phone='404-555-0121',
                    reviewed_by=admin.user_id if statuses[i % len(statuses)] != 'pending' else None,
                )
                db.session.add(a)
                app_count += 1
        db.session.flush()
        print(f"✅ {app_count} applications added")

        # ── Adoptions (for approved apps) ────────────────
        adopt_count = 0
        for appl in Application.query.filter_by(status='approved').all():
            if not Adoption.query.filter_by(application_id=appl.application_id).first():
                adoption = Adoption(
                    application_id=appl.application_id,
                    user_id=appl.user_id, pet_id=appl.pet_id,
                    adoption_date=date.today() - timedelta(days=random.randint(1, 30)),
                    adoption_fee_paid=appl.pet.adoption_fee,
                    contract_signed=True, notes='Smooth process, happy family!'
                )
                db.session.add(adoption)
                adopt_count += 1
        print(f"✅ {adopt_count} adoptions recorded")

        # ── Appointments ──────────────────────────────────
        appt_data = [
            (pets[0], users[1], 'vaccination', datetime.now() + timedelta(days=3),  'Dr. Angela Reeves', 85.00,  'Annual booster due'),
            (pets[1], users[2], 'checkup',     datetime.now() + timedelta(days=5),  'Dr. Marcus Webb',   60.00,  'Routine wellness'),
            (pets[2], users[3], 'grooming',    datetime.now() + timedelta(days=8),  'Paw Path Grooming', 45.00,  'Full groom + nail trim'),
            (pets[4], users[1], 'checkup',     datetime.now() + timedelta(days=12), 'Dr. Angela Reeves', 60.00,  'Pre-adoption health check'),
            (pets[6], users[2], 'vaccination', datetime.now() + timedelta(days=2),  'Dr. Marcus Webb',   90.00,  'Rabies booster'),
            (pets[7], users[3], 'grooming',    datetime.now() + timedelta(days=15), 'Paw Path Grooming', 55.00,  'Maine coon coat treatment'),
            (pets[3], users[1], 'checkup',     datetime.now() - timedelta(days=7),  'Dr. Angela Reeves', 60.00,  'Post-foster health check'),
        ]
        appt_count = 0
        for pet, user, svc, dt, vet, cost, notes in appt_data:
            if not Appointment.query.filter_by(pet_id=pet.pet_id, appointment_date=dt).first():
                status = 'completed' if dt < datetime.now() else 'scheduled'
                appt = Appointment(pet_id=pet.pet_id, user_id=user.user_id,
                                   service_type=svc, appointment_date=dt,
                                   duration_min=30, status=status,
                                   notes=notes, cost=cost, vet_name=vet,
                                   created_by=admin.user_id)
                db.session.add(appt)
                appt_count += 1
        print(f"✅ {appt_count} appointments added")

        # ── Favorites ─────────────────────────────────────
        fav_count = 0
        fav_pairs = [(users[1], pets[0]), (users[1], pets[2]), (users[1], pets[4]),
                     (users[2], pets[1]), (users[2], pets[7]), (users[3], pets[3]),
                     (users[3], pets[5]), (users[3], pets[6])]
        for user, pet in fav_pairs:
            if not Favorite.query.filter_by(user_id=user.user_id, pet_id=pet.pet_id).first():
                db.session.add(Favorite(user_id=user.user_id, pet_id=pet.pet_id))
                fav_count += 1
        print(f"✅ {fav_count} favorites added")

        # ── Blog posts ────────────────────────────────────
        post_count = 0
        for title, content in BLOG_POSTS:
            if not BlogPost.query.filter_by(title=title).first():
                db.session.add(BlogPost(title=title, content=content,
                                        author_id=admin.user_id, published=True))
                post_count += 1
        print(f"✅ {post_count} blog posts added")

        # ── Events ────────────────────────────────────────
        event_count = 0
        for title, dt, location, desc in EVENTS:
            if not Event.query.filter_by(title=title).first():
                db.session.add(Event(title=title, event_date=dt, location=location,
                                     description=desc, created_by=admin.user_id))
                event_count += 1
        print(f"✅ {event_count} events added")

        # ── Notifications ─────────────────────────────────
        notif_count = 0
        notif_data = [
            (users[1], "Your application for Biscuit is under review 🐾",   '/dashboard'),
            (users[1], "Appointment for Mango confirmed for this Friday",    '/appointments'),
            (users[2], "Your application for Luna has been approved! 🎉",   '/dashboard'),
            (users[2], "Reminder: Rocky's checkup is in 5 days",            '/appointments'),
            (users[3], "New event: Adoption Day at Piedmont Park next week", '/events'),
            (users[3], "Cleo's grooming appointment is coming up",           '/appointments'),
        ]
        for user, msg, link in notif_data:
            if not Notification.query.filter_by(user_id=user.user_id, message=msg).first():
                db.session.add(Notification(user_id=user.user_id, message=msg,
                                            link=link, is_read=False))
                notif_count += 1
        print(f"✅ {notif_count} notifications added")

        # ── Care logs ─────────────────────────────────────
        log_count = 0
        care_data = [
            (pets[0], users[1], datetime.now() - timedelta(hours=2, minutes=30), datetime.now() - timedelta(hours=1), 'Morning walk + feeding'),
            (pets[2], users[2], datetime.now() - timedelta(hours=1, minutes=15), datetime.now() - timedelta(minutes=20), 'Playtime + socialisation'),
            (pets[4], users[3], datetime.now() - timedelta(days=1, hours=3),     datetime.now() - timedelta(days=1, hours=1), 'Afternoon exercise'),
        ]
        for pet, user, cin, cout, notes in care_data:
            if not CareLog.query.filter_by(pet_id=pet.pet_id, clocked_in=cin).first():
                db.session.add(CareLog(pet_id=pet.pet_id, user_id=user.user_id,
                                       clocked_in=cin, clocked_out=cout, notes=notes))
                log_count += 1
        print(f"✅ {log_count} care log entries added")

        db.session.commit()

        print("\n" + "=" * 50)
        print("🎉 Seeding complete!")
        print("=" * 50)
        print("\nDemo accounts:")
        print("  admin@pawpath.com  /  admin123  (Admin)")
        print("  sarah@demo.com     /  demo123   (User)")
        print("  james@demo.com     /  demo123   (User)")
        print("  priya@demo.com     /  demo123   (User)")
        print(f"\n  {len(pets)} pets  |  {app_count} applications  |  {appt_count} appointments")
        print("  blog posts, events, notifications, care logs — all seeded")
        print("\nRun: python app.py")

if __name__ == '__main__':
    seed()
