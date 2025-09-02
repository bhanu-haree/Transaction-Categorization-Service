MCC_CATEGORY_MAP = {
    # Shopping
    "5942": "Shopping > Online Marketplace",
    "5311": "Shopping > General Retail",
    "5732": "Shopping > Electronics",
    "5651": "Shopping > Apparel",
    "5712": "Shopping > Home & Furniture",

    # Food & Drink
    "5812": "Food & Drink > Restaurant",
    "5814": "Food & Drink > Fast Food",
    "5811": "Food & Drink > Coffee Shop",
    "5411": "Food & Drink > Grocery",

    # Transport
    "4121": "Transport > Rideshare",
    "4111": "Transport > Public Transit",
    "5541": "Transport > Fuel",

    # Subscriptions
    "4899": "Subscriptions > Digital Services",
    "5734": "Subscriptions > Software",
    "7841": "Subscriptions > Streaming",

    # Bills & Utilities
    "4900": "Bills & Utilities > Electricity",
    "4931": "Bills & Utilities > Water",
    "4814": "Bills & Utilities > Internet/Mobile",

    # Cash & ATM
    "6011": "Cash & ATM > Withdrawal",
    "6010": "Cash & ATM > Deposit",

    # Transfers
    "4829": "Transfers > External",
    "6012": "Transfers > Internal",  # can also be used for fees contextually

    # Fees & Charges
    "6013": "Fees & Charges > Bank Fee",
    "7995": "Fees & Charges > Interest",

    # Travel
    "4511": "Travel > Airline",
    "7011": "Travel > Hotel",
    "6513": "Travel > Short-term Rental",

    # Healthcare
    "5912": "Healthcare > Pharmacy",
    "8062": "Healthcare > Medical Services",
}

# Regex-based rules
REGEX_RULES = [
    # Transport
    ("uber", "Transport > Rideshare", "Regex rule: 'uber'"),
    ("lyft", "Transport > Rideshare", "Regex rule: 'lyft'"),

    # Food & Drink
    ("starbucks", "Food & Drink > Coffee Shop", "Regex rule: 'starbucks'"),
    ("mcdonald", "Food & Drink > Fast Food", "Regex rule: 'mcdonald'"),
    ("kfc", "Food & Drink > Fast Food", "Regex rule: 'kfc'"),

    # Shopping
    ("bestbuy", "Shopping > Electronics", "Regex rule: 'bestbuy'"),
    ("apple store", "Shopping > Electronics", "Regex rule: 'apple store'"),
    ("gap", "Shopping > Apparel", "Regex rule: 'gap'"),
    ("ikea", "Shopping > Home & Furniture", "Regex rule: 'ikea'"),
    ("walmart", "Shopping > General Retail", "Regex rule: 'walmart'"),
    ("target", "Shopping > General Retail", "Regex rule: 'target'"),

    # Subscriptions
    ("prime", "Subscriptions > Streaming", "Regex rule: 'prime'"),
    ("netflix", "Subscriptions > Streaming", "Regex rule: 'netflix'"),
    ("spotify", "Subscriptions > Streaming", "Regex rule: 'spotify'"),
    ("office365", "Subscriptions > Software", "Regex rule: 'office365'"),

    # Travel
    ("airbnb", "Travel > Short-term Rental", "Regex rule: 'airbnb'"),
    ("marriott", "Travel > Hotel", "Regex rule: 'marriott'"),
    ("hilton", "Travel > Hotel", "Regex rule: 'hilton'"),
    ("delta", "Travel > Airline", "Regex rule: 'delta airline'"),
    ("united", "Travel > Airline", "Regex rule: 'united airline'"),

    # Bills & Utilities
    ("verizon", "Bills & Utilities > Internet/Mobile", "Regex rule: 'verizon'"),
    ("att", "Bills & Utilities > Internet/Mobile", "Regex rule: 'att'"),
    ("comcast", "Bills & Utilities > Internet/Mobile", "Regex rule: 'comcast'"),
    ("coned", "Bills & Utilities > Electricity", "Regex rule: 'coned'"),
    ("pg&e", "Bills & Utilities > Electricity", "Regex rule: 'pg&e'"),
    ("water bill", "Bills & Utilities > Water", "Regex rule: 'water bill'"),
    ("utility", "Bills & Utilities > Electricity", "Regex rule: 'utility'"),
    ("electric bill", "Bills & Utilities > Electricity", "Regex rule: 'electric bill'"),

    # Cash & ATM
    ("atm withdrawal", "Cash & ATM > Withdrawal", "Regex rule: 'atm withdrawal'"),
    ("cash wd", "Cash & ATM > Withdrawal", "Regex rule: 'cash wd'"),
    ("atm deposit", "Cash & ATM > Deposit", "Regex rule: 'atm deposit'"),

    # Transfers
    ("internal transfer", "Transfers > Internal", "Regex rule: 'internal transfer'"),
    ("external transfer", "Transfers > External", "Regex rule: 'external transfer'"),
    ("zelle", "Transfers > External", "Regex rule: 'zelle transfer'"),
    ("venmo", "Transfers > External", "Regex rule: 'venmo transfer'"),
    ("paypal", "Transfers > External", "Regex rule: 'paypal transfer'"),

    # Fees & Charges
    ("bank fee", "Fees & Charges > Bank Fee", "Regex rule: 'bank fee'"),
    ("monthly fee", "Fees & Charges > Bank Fee", "Regex rule: 'monthly fee'"),
    ("overdraft", "Fees & Charges > Bank Fee", "Regex rule: 'overdraft fee'"),
    ("charge", "Fees & Charges > Bank Fee", "Regex rule: 'charge'"),
    ("interest charge", "Fees & Charges > Interest", "Regex rule: 'interest charge'"),
]
