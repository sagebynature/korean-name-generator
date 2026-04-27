from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal

Gender = Literal["female", "male", "neutral"]
GenderSelection = Literal["any", "female", "male", "neutral"]
NameOrder = Literal["western", "korean"]
NamePair = tuple[str, str]


@dataclass(frozen=True, slots=True)
class KoreanName:
    """A generated Korean name in romanized and Hangul forms."""

    family_name_en: str
    family_name_ko: str
    given_name_en: str
    given_name_ko: str
    gender: Gender

    @property
    def romanized(self) -> str:
        """Return the Western-order romanized display name."""

        return f"{self.given_name_en} {self.family_name_en}"

    @property
    def hangul(self) -> str:
        """Return the Korean-order Hangul display name."""

        return f"{self.family_name_ko}{self.given_name_ko}"

    def display(self, order: NameOrder = "western") -> str:
        """Return a combined display string in Western or Korean order."""

        if order == "western":
            return f"{self.romanized} ({self.hangul})"
        if order == "korean":
            return f"{self.hangul} ({self.family_name_en} {self.given_name_en})"
        raise ValueError("order must be 'western' or 'korean'")

    def as_dict(self) -> dict[str, str]:
        """Return a JSON/CSV-friendly representation."""

        payload = asdict(self)
        payload["romanized"] = self.romanized
        payload["hangul"] = self.hangul
        return payload
