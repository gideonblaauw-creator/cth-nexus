from dataclasses import dataclass, field, asdict


COUNTRY_FLAGS = {
    "Colombia": "\U0001f1e8\U0001f1f4",
    "Peru": "\U0001f1f5\U0001f1ea",
    "Guatemala": "\U0001f1ec\U0001f1f9",
    "Costa Rica": "\U0001f1e8\U0001f1f7",
    "El Salvador": "\U0001f1f8\U0001f1fb",
}

MODULES = [
    {"number": 1, "name": "El Sueño del Founder", "emoji": "\U0001f9ed", "workbook_pages": "14-24"},
    {"number": 2, "name": "Lo Comercial", "emoji": "\U0001f91d", "workbook_pages": "25-42"},
    {"number": 3, "name": "El Mercado", "emoji": "\U0001f5fa️", "workbook_pages": "43-56"},
    {"number": 4, "name": "El Valor", "emoji": "\U0001f48e", "workbook_pages": "57-72"},
    {"number": 5, "name": "Venture Economics", "emoji": "\U0001f4ca", "workbook_pages": "73-88"},
    {"number": 6, "name": "Impacto Climático", "emoji": "\U0001f33f", "workbook_pages": "89-104"},
    {"number": 7, "name": "Customer Discovery", "emoji": "\U0001f465", "workbook_pages": "105-126"},
    {"number": 8, "name": "El Pitch", "emoji": "\U0001f3a4", "workbook_pages": "127-142"},
]


@dataclass
class SessionStatus:
    module_number: int
    name: str
    status: str  # "done" | "scheduled" | "needs_mentor"
    date: str | None = None
    homework_url: str | None = None

    def to_dict(self):
        return asdict(self)


@dataclass
class Startup:
    page_id: int
    name: str
    country: str
    flag: str
    category: str
    stage: str
    description: str
    oneliner: str
    wiki_url: str
    app_id: str = ""
    founder: str = ""
    sessions: list = field(default_factory=list)
    matched_mentors: list = field(default_factory=list)
    needs_mentor: list = field(default_factory=list)

    def to_dict(self):
        d = asdict(self)
        d["sessions"] = [s if isinstance(s, dict) else s for s in self.sessions]
        return d
