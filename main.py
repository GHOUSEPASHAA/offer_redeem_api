from fastapi import FastAPI
from faker import Faker
import random
import hashlib
from datetime import datetime, timedelta
import requests
import uuid
import uvicorn

app = FastAPI(title=" Offer Redemption API")

fake = Faker()

# Casino codes and property configurations strictly mapped to the source dataset
properties = {
    "BMC": "Blue Meridian Casino",
    "RLC": "Red Lantern Casino",
    "GPC": "Glass Palm Casino",
    
}

# Real-world locations extracted directly from the dataset's high-frequency distributions
reinvestment_locations = [
    "Slot - R45690 712610",
    "Slot - R65299 301809",
    "Slot - R65539 603410",
    "Slot - T69753 620209",
    "Slot - R65213 403802",
    "Slot - R65218 702603",
    "Other - TPC Agilysys Int Locn",
    "Players Club - HBC Booth"
]

# The blueprint configuration for targeted strategic offers
basic_offers_blueprint = [
    {
        "OFFER_CATEGORY": "Freeplay",
        "OFFER_CHANNEL": "ONLINE",
        "OFFER_REWARD_TYPE": "Electronic Promo Credit to Machine",
        "OFFER_REWARD_NAME": "@MW0220770",
        "OFFER_REWARD_AMOUNT": 10.0,
        "TEMPLATE_TYPE": "SINGLE_DAY",
        "TEXT_PREFIX": "$10 Free Play"
    },
    {
        "OFFER_CATEGORY": "Freeplay",
        "OFFER_CHANNEL": "express-offers",
        "OFFER_REWARD_TYPE": "Electronic Promo Credit to Machine",
        "OFFER_REWARD_NAME": "M!0AD98747",
        "OFFER_REWARD_AMOUNT": 5.0,
        "TEMPLATE_TYPE": "RANGE",
        "TEXT_PREFIX": "$5 Free Play",
        "DAYS_EXTENSION": 6
    },
    {
        "OFFER_CATEGORY": "Food Credit",
        "OFFER_CHANNEL": "express-offers",
        "OFFER_REWARD_TYPE": "Food & Beverage",
        "OFFER_REWARD_NAME": "M!0AI79539",
        "OFFER_REWARD_AMOUNT": 15.0,
        "TEMPLATE_TYPE": "RANGE",
        "TEXT_PREFIX": "$15 Food Credit",
        "DAYS_EXTENSION": 6
    },
    {
        "OFFER_CATEGORY": "Hotel",
        "OFFER_CHANNEL": "comp",
        "OFFER_REWARD_TYPE": "Room",
        "OFFER_REWARD_NAME": "B0525GENRM",
        "OFFER_REWARD_AMOUNT": 45.0,
        "TEMPLATE_TYPE": "RANGE",
        "TEXT_PREFIX": "Standard 2 Comp Nights Baseline",
        "DAYS_EXTENSION": 30
    }
]

elite_offers_blueprint = [
    {
        "OFFER_CATEGORY": "Event",
        "OFFER_CHANNEL": "drawing",
        "OFFER_REWARD_TYPE": "Unassigned or Unknown Award",
        "OFFER_REWARD_NAME": "!BCV15FPW1",
        "OFFER_REWARD_AMOUNT": 15.0,
        "TEMPLATE_TYPE": "STATIC",
        "TEXT_PREFIX": "CVB Why Not? Wed $15FP Wk1"
    },
    {
        "OFFER_CATEGORY": "Freeplay",
        "OFFER_CHANNEL": "express-offers",
        "OFFER_REWARD_TYPE": "Electronic Promo Credit to Machine",
        "OFFER_REWARD_NAME": "M!0AK77172",
        "OFFER_REWARD_AMOUNT": 50.0,
        "TEMPLATE_TYPE": "RANGE",
        "TEXT_PREFIX": "$50 Free Play",
        "DAYS_EXTENSION": 6
    },
    {
        "OFFER_CATEGORY": "Freeplay",
        "OFFER_CHANNEL": "ONLINE",
        "OFFER_REWARD_TYPE": "Electronic Promo Credit to Machine",
        "OFFER_REWARD_NAME": "@MW0263590",
        "OFFER_REWARD_AMOUNT": 100.0,
        "TEMPLATE_TYPE": "SINGLE_DAY",
        "TEXT_PREFIX": "$100 Free Play"
    },
    {
        "OFFER_CATEGORY": "Food Credit",
        "OFFER_CHANNEL": "express-offers",
        "OFFER_REWARD_TYPE": "Food & Beverage",
        "OFFER_REWARD_NAME": "M!0AL82147",
        "OFFER_REWARD_AMOUNT": 20.0,
        "TEMPLATE_TYPE": "RANGE",
        "TEXT_PREFIX": "$20 Food Credit",
        "DAYS_EXTENSION": 34
    },
    {
        "OFFER_CATEGORY": "Sweepstakes",
        "OFFER_CHANNEL": "drawing",
        "OFFER_REWARD_TYPE": "Merchandise",
        "OFFER_REWARD_NAME": "!HMSCOV",
        "OFFER_REWARD_AMOUNT": 17.2,
        "TEMPLATE_TYPE": "STATIC",
        "TEXT_PREFIX": "WCH MSC Cruise Ocean View"
    }
]


def generate_person_id(activeclubid):
    return str(
        int(
            hashlib.md5(
                ("redeem" + str(activeclubid)).encode()
            ).hexdigest(),
            16
        ) % 90000 + 10000
    )


def generate_boss_offer_redeem(activeclubid):
    person_id = generate_person_id(activeclubid)
    property_code = random.choice(list(properties.keys()))
    property_name = properties[property_code]

    # Replicate exact data quirk: 'RLC' leaves PROPERTY_CODE, PROPERTY_ACCOUNTING_CODE, 
    # and SF_PROPERTY_ID blank (None) in the raw logs, but retains its code under PROPERTY_ID.
    prop_code_val = property_code
    
    # Establish transaction timestamps
    order_timestamp = (
        datetime.now()
        - timedelta(
            days=random.randint(1, 30),
            hours=random.randint(1, 12)
        )
    )

    # Establish demographics
    club_level = random.choices(["Basic", "Elite"], weights=[0.65, 0.35], k=1)[0]

    # Mimic real business pattern probability distribution found in data profiles
    pattern_type = random.choices(
        ["EARNED_POINTS", "CASHLESS_POINTS", "CASHLESS_PROMO", "MULTIPLIER", "STRATEGIC_OFFER"],
        weights=[0.33, 0.22, 0.17, 0.05, 0.23],
        k=1
    )[0]

    # Initialize standard layout metrics
    details_text = ""
    prize_code = ""
    reinvestment_category = ""
    
    tx_amt = 0.0
    reinvest_amt = 0.0
    freeplay_issued = 0.0
    freeplay_redeemed = 0.0
    points_issued = 0.0
    points_redeemed = 0.0
    comp_issued = 0.0
    comp_redeemed = 0.0
    other_expense = 0.0
    promotional_flag = 0.0

    # Pattern Group 1: Points Accruals & Associated side-by-side Comp Issuances
    if pattern_type == "EARNED_POINTS":
        details_text = "Earned Comp or Points"
        prize_code = "COMPPTS"
        reinvestment_category = "Points - Earned Card Level"
        
        # Pull typical values matching the 25th-75th percentiles up to high-roller exceptions
        if random.random() > 0.95:
            amt = round(random.uniform(100.00, 720.00), 2)
        else:
            amt = round(random.uniform(0.05, 12.50), 2)

        tx_amt = -amt
        reinvest_amt = amt
        points_issued = amt
        # Core business rule: Comps are auto-issued alongside points, scaling approx 2.0x to 3.2x higher
        comp_issued = round(amt * random.uniform(2.0, 3.2), 2) if amt > 0.10 else 0.0

    # Pattern Group 2: Point to Freeplay Transfers (Balances clear tx and offset straight to counters)
    elif pattern_type == "CASHLESS_POINTS":
        details_text = "Cashless Withdraw Points to Restricted"
        prize_code = "CSHWDPR"
        reinvestment_category = "Points to Free Play Redeem"
        points_redeemed = float(random.choice([1.0, 5.0, 10.0, 20.0, 50.0]))

    # Pattern Group 3: Direct Promo Credit Conversions (Balances clear tx and offset straight to counters)
    elif pattern_type == "CASHLESS_PROMO":
        details_text = "Cashless Withdraw Promo Credits to Restricted"
        prize_code = "CSHWDCR"
        reinvestment_category = "Free Play - Redeem"
        freeplay_redeemed = float(random.choice([5.0, 10.0, 15.0, 20.0, 25.0, 40.0, 60.0, 100.0]))

    # Pattern Group 4: Promotion Multipliers
    elif pattern_type == "MULTIPLIER":
        details_text = "2x offer Multiplier"
        prize_code = "?WMDMULT2X"
        reinvestment_category = "Unknown"
        amt = round(random.uniform(0.10, 4.50), 2)
        tx_amt = -amt
        reinvest_amt = amt

    # Pattern Group 5: Strategic Structural Offers & Discretionary Adjustments
    elif pattern_type == "STRATEGIC_OFFER":
        # Sub-Pattern: 10% chance of hitting a Discretionary Folio Settlement (Comp Redemptions)
        if random.random() > 0.90:
            details_text = "Discretionary Hotel Folio Settlement"
            prize_code = "$1FOLIO"
            reinvestment_category = "Points - Adjustment"
            amt = round(random.uniform(100.00, 550.00), 2)
            tx_amt = -amt
            reinvest_amt = amt
            # Core business rule: Discretionary overrides clear instantly into COMP_REDEEMED metrics
            comp_redeemed = amt
        else:
            blueprint = random.choice(basic_offers_blueprint) if club_level == "Basic" else random.choice(elite_offers_blueprint)
            start_date_str = order_timestamp.strftime("%m/%d")
            
            if blueprint["TEMPLATE_TYPE"] == "SINGLE_DAY":
                details_text = f"{blueprint['TEXT_PREFIX']} ({start_date_str}-{start_date_str})"
            elif blueprint["TEMPLATE_TYPE"] == "RANGE":
                end_date = order_timestamp + timedelta(days=blueprint["DAYS_EXTENSION"])
                details_text = f"{blueprint['TEXT_PREFIX']} ({start_date_str}-{end_date.strftime('%m/%d')})"
            else:
                details_text = blueprint["TEXT_PREFIX"]
                
            prize_code = blueprint["OFFER_REWARD_NAME"]
            reward_amt = blueprint["OFFER_REWARD_AMOUNT"]
            tx_amt = -float(reward_amt)
            reinvest_amt = float(reward_amt)
            
            if blueprint["OFFER_CATEGORY"] == "Freeplay":
                reinvestment_category = "Free Play - Express Offers" if blueprint["OFFER_CHANNEL"] == "express-offers" else "Free Play - WCC.COM"
                freeplay_issued = float(reward_amt)
            else:
                reinvestment_category = "Food Credit - Express Offer" if blueprint["OFFER_CATEGORY"] == "Food Credit" else "Sweepstakes"
                other_expense = float(reward_amt)
                if blueprint["OFFER_CATEGORY"] in ["Sweepstakes", "Event"]:
                    promotional_flag = 1.0

    event_id = hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()
    event_group_id = hashlib.md5(str(activeclubid).encode()).hexdigest()
    source_person_key = hashlib.md5(("redeem" + str(activeclubid)).encode()).hexdigest()

    try:
        active_club_id_val = str(activeclubid)
    except (ValueError, TypeError):
        active_club_id_val = activeclubid

    # Strictly structured to align with your required 54-column layout sequence 
    return {
        "EVENT_TIMESTAMP": order_timestamp.isoformat() + "Z",
        "DURATION": 0,
        "EVENT_TIMESTAMP_PROPERTY": order_timestamp.isoformat() + "Z",
        "EVENT_TIMESTAMP_PROPERTY_TIMEZONE": "America/Chicago",
        "GAMING_DATE": order_timestamp.strftime("%m/%d/%Y"),
        "GAMING_DATE_TIMEZONE": "America/Chicago",
        "SOURCE_PERSON_KEY": source_person_key,
        "PERSON_ID": int(person_id),
        "ACTIVE_CLUB_ID": active_club_id_val,
        "SOURCE": "CMP",
        "ENTITY": "OFFER",
        "ACTION": "REDEEM",
        "ENTITY_ACTION": "OFFER:REDEEM",
        "DETAILS": details_text,
        "EVENT_ID": event_id,
        "EVENT_GROUP_ID": event_group_id,
        "PROPERTY_NAME": property_name,
        "PROPERTY_CODE": prop_code_val,
        "PROPERTY_ACCOUNTING_CODE": prop_code_val,
        "SF_PROPERTY_ID": prop_code_val,
        "PROPERTY_ID": property_code,
        "PROPERTY_ADDR1": fake.street_address(),
        "PROPERTY_ADDR2": fake.secondary_address(),
        "PROPERTY_CITY": fake.city(),
        "PROPERTY_STATE": fake.state(),
        "PROPERTY_COUNTRY": "USA",
        "PROPERTY_POSTAL_CODE": fake.postcode(),
        "TRANSACTION_AMOUNT": tx_amt,
        "PLAYER_VALUE": tx_amt,
        "GAME_NET_CASINO_WIN": 0.0,
        "GAME_NET_THEO_WIN": 0.0,
        "REINVESTMENT_ID": float(random.randint(14000000000, 16900000000)),
        "REINVESTMENT_AMOUNT": reinvest_amt,
        "REINVESTMENT_PROMO_AMOUNT": 0.0,
        "REINVESTMENT_PRIZE_NAME": details_text,
        "REINVESTMENT_PRIZE_CODE": prize_code,
        "REINVESTMENT_DISCRETIONARY_FLAG": 0.0,
        "REINVESTMENT_FREEPLAY_ISSUED": freeplay_issued,
        "REINVESTMENT_FREEPLAY_REDEEMED": freeplay_redeemed,
        "REINVESTMENT_POINTS_ISSUED": points_issued,
        "REINVESTMENT_POINTS_REDEEMED": points_redeemed,
        "REINVESTMENT_COMP_ISSUED": comp_issued,
        "REINVESTMENT_COMP_REDEEMED": comp_redeemed,
        "REINVESTMENT_OTHER_EXPENSE": other_expense,
        "REINVESTMENT_LOCATION": random.choice(reinvestment_locations),
        "REINVESTMENT_CATEGORY": reinvestment_category,
        "REINVESTMENT_PROMOTIONAL_FLAG": promotional_flag,
        "PROMOTION_EVENT_DETAIL": details_text,
        "METADATA": None,
        "TIMESERIES_CMP_REDEMPTION_KEY": hashlib.md5((prize_code + str(event_id)).encode()).hexdigest(),
        "LAST_SYNCED": datetime.now().isoformat() + "Z",
        "LOAD_TIMESTAMP": None,
        "DW_TASKID": random.randint(1000, 9999),
        "DW_USERID": random.randint(10000, 99999)
    }


@app.get("/v1/offer-redeem")
async def boss_offer_redeem():
    api_url = (
        "https://casino-api-ob26.onrender.com/"
        "v1/player-activity"
    )

    response = requests.get(api_url)
    player_data = response.json()

    unique_activeclubids = []
    seen = set()

    for row in player_data:
        activeclubid = row["ACTIVECLUBID"]

        if activeclubid not in seen:
            seen.add(activeclubid)
            unique_activeclubids.append(activeclubid)

        if len(unique_activeclubids) == 50:
            break

    final_records = []
    for activeclubid in unique_activeclubids:
        final_records.append(
            generate_boss_offer_redeem(activeclubid)
        )

    return final_records


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8007
    )
