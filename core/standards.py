from dataclasses import dataclass


@dataclass(frozen=True)
class Pass:
    label: str
    pattern: bytes | None  # None = random


@dataclass(frozen=True)
class Standard:
    id: str
    name: str
    description: str
    passes: list[Pass]
    verify: bool = False


def _random(label: str = "Random") -> Pass:
    return Pass(label=label, pattern=None)


def _fixed(byte: int, label: str | None = None) -> Pass:
    return Pass(label=label or f"0x{byte:02X}", pattern=bytes([byte]))


ZERO = Standard(
    id="zero",
    name="Zero Fill",
    description="Single pass of zeros. Fast, not forensically secure.",
    passes=[_fixed(0x00, "Zeros")],
)

RANDOM = Standard(
    id="random",
    name="Random (1-Pass)",
    description="Single pass of cryptographically random data.",
    passes=[_random()],
)

DOD_3 = Standard(
    id="dod3",
    name="DoD 5220.22-M (3-Pass)",
    description="US DoD standard. Passes: 0x00 → 0xFF → random.",
    passes=[
        _fixed(0x00, "Pass 1 – Zeros"),
        _fixed(0xFF, "Pass 2 – Ones"),
        _random("Pass 3 – Random"),
    ],
    verify=True,
)

DOD_7 = Standard(
    id="dod7",
    name="DoD 5220.22-M ECE (7-Pass)",
    description="Extended DoD standard with 7 passes.",
    passes=[
        _fixed(0x00, "Pass 1 – Zeros"),
        _fixed(0xFF, "Pass 2 – Ones"),
        _random("Pass 3 – Random"),
        _fixed(0x00, "Pass 4 – Zeros"),
        _fixed(0xFF, "Pass 5 – Ones"),
        _random("Pass 6 – Random"),
        _random("Pass 7 – Random"),
    ],
    verify=True,
)

GUTMANN = Standard(
    id="gutmann",
    name="Gutmann (35-Pass)",
    description="Peter Gutmann's algorithm. Maximum security for older HDDs.",
    passes=[
        _random("Pass 1 – Random"),
        _random("Pass 2 – Random"),
        _random("Pass 3 – Random"),
        _random("Pass 4 – Random"),
        _fixed(0x55, "Pass 5"),
        _fixed(0xAA, "Pass 6"),
        Pass("Pass 7",  bytes([0x92, 0x49, 0x24])),
        Pass("Pass 8",  bytes([0x49, 0x24, 0x92])),
        Pass("Pass 9",  bytes([0x24, 0x92, 0x49])),
        _fixed(0x00, "Pass 10"),
        _fixed(0x11, "Pass 11"),
        _fixed(0x22, "Pass 12"),
        _fixed(0x33, "Pass 13"),
        _fixed(0x44, "Pass 14"),
        _fixed(0x55, "Pass 15"),
        _fixed(0x66, "Pass 16"),
        _fixed(0x77, "Pass 17"),
        _fixed(0x88, "Pass 18"),
        _fixed(0x99, "Pass 19"),
        _fixed(0xAA, "Pass 20"),
        _fixed(0xBB, "Pass 21"),
        _fixed(0xCC, "Pass 22"),
        _fixed(0xDD, "Pass 23"),
        _fixed(0xEE, "Pass 24"),
        _fixed(0xFF, "Pass 25"),
        Pass("Pass 26", bytes([0x92, 0x49, 0x24])),
        Pass("Pass 27", bytes([0x49, 0x24, 0x92])),
        Pass("Pass 28", bytes([0x24, 0x92, 0x49])),
        Pass("Pass 29", bytes([0x6D, 0xB6, 0xDB])),
        Pass("Pass 30", bytes([0xB6, 0xDB, 0x6D])),
        Pass("Pass 31", bytes([0xDB, 0x6D, 0xB6])),
        _random("Pass 32 – Random"),
        _random("Pass 33 – Random"),
        _random("Pass 34 – Random"),
        _random("Pass 35 – Random"),
    ],
)

ALL_STANDARDS: dict[str, Standard] = {
    s.id: s for s in [ZERO, RANDOM, DOD_3, DOD_7, GUTMANN]
}


def get(standard_id: str) -> Standard:
    if standard_id not in ALL_STANDARDS:
        raise KeyError(f"Unknown standard '{standard_id}'. Available: {list(ALL_STANDARDS)}")
    return ALL_STANDARDS[standard_id]
