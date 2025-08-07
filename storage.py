from sqlalchemy.orm import Session
from database import engine, get_db
from models import Base, ModelNationality

# Step 1: Create tables if not exist
Base.metadata.create_all(bind=engine)

# Step 2: List of nationalities (add more as needed)
nationalities = [
    "Afghan", "Albanian", "Algerian", "American", "Andorran", "Angolan", "Argentine",
    "Armenian", "Australian", "Austrian", "Azerbaijani", "Bangladeshi", "Belarusian",
    "Belgian", "Bolivian", "Bosnian", "Brazilian", "British", "Bulgarian", "Cambodian",
    "Cameroonian", "Canadian", "Chilean", "Chinese", "Colombian", "Croatian", "Cuban",
    "Czech", "Danish", "Dominican", "Dutch", "Ecuadorian", "Egyptian", "Emirati",
    "English", "Estonian", "Ethiopian", "Filipino", "Finnish", "French", "Georgian",
    "German", "Ghanaian", "Greek", "Guatemalan", "Hungarian", "Icelandic", "Indian",
    "Indonesian", "Iranian", "Iraqi", "Irish", "Israeli", "Italian", "Jamaican", "Japanese",
    "Jordanian", "Kazakh", "Kenyan", "Korean", "Kuwaiti", "Kyrgyz", "Latvian", "Lebanese",
    "Libyan", "Lithuanian", "Luxembourgish", "Malaysian", "Maltese", "Mexican", "Moldovan",
    "Mongolian", "Moroccan", "Nepali", "New Zealander", "Nigerian", "Norwegian", "Pakistani",
    "Palestinian", "Panamanian", "Paraguayan", "Peruvian", "Polish", "Portuguese", "Qatari",
    "Romanian", "Russian", "Rwandan", "Saudi", "Scottish", "Senegalese", "Serbian", "Singaporean",
    "Slovak", "Slovenian", "Somali", "South African", "Spanish", "Sri Lankan", "Sudanese",
    "Swedish", "Swiss", "Syrian", "Taiwanese", "Tajik", "Tanzanian", "Thai", "Tunisian",
    "Turkish", "Turkmen", "Ukrainian", "Uruguayan", "Uzbek", "Venezuelan", "Vietnamese",
    "Welsh", "Yemeni", "Zambian", "Zimbabwean"
]

# Step 3: Insert nationalities
def seed_nationalities():
    db: Session = next(get_db())
    for name in nationalities:
        exists = db.query(ModelNationality).filter_by(nationality=name).first()
        if not exists:
            db.add(ModelNationality(nationality=name))
    db.commit()
    db.close()
    print("Nationalities added successfully.")

if __name__ == "__main__":
    seed_nationalities()
