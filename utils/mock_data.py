"""
Static mock data for the AI Knowledge Assistant demo UI.
Swap these out for real data (DB / vector store / session backend) later.
"""

STATS = [
    {"label": "Documents", "value": 24, "color": "#22C55E"},
    {"label": "Sessions", "value": 12, "color": "#60A5FA"},
    {"label": "Queries", "value": 158, "color": "#A78BFA"},
]

DOCUMENTS = [
    {"name": "MeriTech Simga-pa.pdf", "type": "PDF", "date": "Jul 15"},
    {"name": "Sigma meritech product (2).pdf", "type": "PDF", "date": "Jul 15"},
    {"name": "Sigma-ml.pdf", "type": "PDF", "date": "Aug 02"},
    {"name": "Centra-SD.pdf", "type": "PDF", "date": "Aug 02"},
    {"name": "Centra-Experitest.pdf", "type": "PDF", "date": "Aug 02"},
]

CHAT_SESSIONS = []

# Seed conversation shown on first load
INITIAL_MESSAGES = [
    {
        "role": "user",
        "content": "What is the leave policy?",
        "time": "10:30 AM",
    },
    {
        "role": "assistant",
        "content": (
            "According to the company leave policy, employees are entitled to "
            "the following types of leave:\n\n"
            "- **Casual Leave:** 12 days per year\n"
            "- **Sick Leave:** 15 days per year\n"
            "- **Earned Leave:** 20 days per year\n"
            "- **Maternity Leave:** 26 weeks\n"
            "- **Paternity Leave:** 15 days\n\n"
            "For more details, please refer to the Leave Policy document."
        ),
        "time": "10:30 AM",
        "sources": None,
    },
    {
        "role": "user",
        "content": "How many sick leaves are allowed?",
        "time": "10:31 AM",
    },
    {
        "role": "assistant",
        "content": "Employees are entitled to **15 sick leaves per year** as per the company policy.",
        "time": "10:31 AM",
        "sources": [
            {"document": "Leave_Policy.docx", "page": "Page 5", "score": 0.92},
        ],
    },
]

# Very small canned-answer knowledge base so the demo chat feels alive
CANNED_ANSWERS = {
    "leave": INITIAL_MESSAGES[1]["content"],
    "sick": INITIAL_MESSAGES[3]["content"],
    "maternity": "Maternity leave is **26 weeks**, as outlined in the Leave Policy document.",
    "paternity": "Paternity leave is **15 days**, as outlined in the Leave Policy document.",
}

DEFAULT_ANSWER = (
    "I couldn't find an exact match in the uploaded documents for that. "
    "Try asking about leave policy, sick leave, IT security, or onboarding — "
    "or upload a new document from the sidebar."
)
