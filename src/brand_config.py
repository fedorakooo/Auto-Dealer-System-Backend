"""Deploy-time brand (white-label) configuration: YAML file + BRAND__* env overrides."""

import hashlib
import os
import re
from pathlib import Path
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

DEFAULT_BRAND_DIR = Path("/app/brand")
BRAND_ASSETS_URL_PREFIX = "/api/v1/brand/assets/"

HEX_COLOR = r"^#[0-9a-fA-F]{6}$"
E164_PHONE = r"^\+[1-9]\d{6,14}$"
ASSET_REF = re.compile(r"^(https?://\S+|[A-Za-z0-9][A-Za-z0-9._-]*)$")

Language = Literal["ru", "en"]
# Brand texts: one string for all languages, or {ru: ..., en: ...} per UI language.
LocalizedText = str | dict[Language, str]

SocialType = Literal["website", "instagram", "facebook", "telegram", "vk", "youtube", "x", "tiktok", "whatsapp"]


def brand_dir() -> Path:
    """Directory holding brand.yaml and the assets/ folder."""
    return Path(os.environ.get("BRAND_DIR", str(DEFAULT_BRAND_DIR)))


def brand_config_file() -> Path:
    """Path of the brand YAML file."""
    return Path(os.environ.get("BRAND_CONFIG_FILE", str(brand_dir() / "brand.yaml")))


def resolve_asset(value: str | None) -> str | None:
    """Turns an asset file name into its public URL (content-hash versioned); absolute URLs pass through."""
    if not value or value.startswith(("http://", "https://")):
        return value
    path = brand_dir() / "assets" / value
    if not path.is_file():
        return f"{BRAND_ASSETS_URL_PREFIX}{value}"
    version = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    return f"{BRAND_ASSETS_URL_PREFIX}{value}?v={version}"


def _mix(hex_color: str, target: tuple[int, int, int], ratio: float) -> str:
    rgb = [int(hex_color[i : i + 2], 16) for i in (1, 3, 5)]
    mixed = [round(c + (t - c) * ratio) for c, t in zip(rgb, target, strict=True)]
    return "#" + "".join(f"{c:02x}" for c in mixed)


def _validate_asset(value: str | None) -> str | None:
    if value is not None and not ASSET_REF.match(value):
        raise ValueError("must be an http(s) URL or a plain file name inside the brand assets directory")
    return value


class _Section(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LocaleConfig(_Section):
    """Language, locale, currency and timezone of the deployment."""

    language: Language = "ru"
    locale: str = Field(default="ru-RU", pattern=r"^[a-z]{2,3}(-[A-Z][a-z]{3})?(-[A-Z]{2})?$")
    currency: str = Field(default="BYN", pattern=r"^[A-Z]{3}$")
    country: str = Field(default="BY", pattern=r"^[A-Z]{2}$")
    timezone: str = "Europe/Minsk"


class ThemeConfig(_Section):
    """Brand colors; missing shades are derived from the base colors."""

    accent: str = Field(default="#dc2626", pattern=HEX_COLOR)
    accent_strong: str | None = Field(default=None, pattern=HEX_COLOR)
    accent_subtle: str | None = Field(default=None, pattern=HEX_COLOR)
    primary: str = Field(default="#1e293b", pattern=HEX_COLOR)
    primary_hover: str | None = Field(default=None, pattern=HEX_COLOR)
    focus: str = Field(default="#2563eb", pattern=HEX_COLOR)

    @model_validator(mode="after")
    def derive_shades(self) -> Self:
        """Fills unset color shades from accent and primary."""
        self.accent_strong = self.accent_strong or _mix(self.accent, (0, 0, 0), 0.18)
        self.accent_subtle = self.accent_subtle or _mix(self.accent, (255, 255, 255), 0.93)
        self.primary_hover = self.primary_hover or _mix(self.primary, (255, 255, 255), 0.12)
        return self


class WorkingHours(_Section):
    """Working hours line: days and hours."""

    days: LocalizedText
    hours: LocalizedText


class ContactsConfig(_Section):
    """Public contacts of the brand."""

    phone: str | None = Field(default=None, pattern=E164_PHONE)
    phone_display: str | None = None
    email: EmailStr | None = None
    address: LocalizedText | None = None
    location_line: LocalizedText | None = None
    working_hours: list[WorkingHours] = Field(default_factory=list)
    service_hours_note: LocalizedText | None = None

    @model_validator(mode="after")
    def default_phone_display(self) -> Self:
        """Uses the raw phone as display text when none is given."""
        if self.phone and not self.phone_display:
            self.phone_display = self.phone
        return self


class SocialLink(_Section):
    """Link to a social network profile."""

    type: SocialType
    url: str = Field(pattern=r"^https?://\S+$")


class SeoConfig(_Section):
    """SEO metadata."""

    title: LocalizedText | None = None
    description: LocalizedText | None = None
    og_image_url: str | None = None

    @field_validator("og_image_url")
    @classmethod
    def check_asset(cls, value: str | None) -> str | None:
        """Validates the OG image reference."""
        return _validate_asset(value)


class HomeImages(_Section):
    """Images of the home page."""

    hero: str | None = None
    promo: list[str] = Field(default_factory=list, max_length=3)
    tile_stock: str | None = None
    tile_test_drive: str | None = None
    tile_dealers: str | None = None
    service_maintenance: str | None = None
    service_booking: str | None = None
    service_parts: str | None = None

    @field_validator("*")
    @classmethod
    def check_assets(cls, value: str | list[str] | None) -> str | list[str] | None:
        """Validates every image reference."""
        if isinstance(value, list):
            for item in value:
                _validate_asset(item)
            return value
        return _validate_asset(value)


class HomeConfig(_Section):
    """Home page texts and images."""

    hero_kicker: LocalizedText | None = None
    hero_title: LocalizedText | None = None
    hero_subtitle: LocalizedText | None = None
    images: HomeImages = Field(default_factory=HomeImages)


class FeaturesConfig(_Section):
    """Feature switches of the deployment."""

    test_drives: bool = True
    service_appointments: bool = True
    custom_orders: bool = True
    reviews: bool = True
    favorites: bool = True


class DemoConfig(_Section):
    """Demo-only UI options."""

    show_login_hint: bool = False


class ServerConfig(_Section):
    """Backend-only settings; never exposed by GET /brand."""

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    api_title: str | None = None


class BrandSettings(BaseSettings):
    """Brand config: init kwargs > BRAND__* env > brand.yaml > defaults."""

    name: str = Field(default="Auto Dealer", min_length=1, max_length=60)
    short_name: str | None = Field(default=None, min_length=1, max_length=4)
    tagline: LocalizedText | None = None
    legal_name: str | None = Field(default=None, max_length=120)
    logo_url: str | None = None
    favicon_url: str | None = None
    locale: LocaleConfig = Field(default_factory=LocaleConfig)
    theme: ThemeConfig = Field(default_factory=ThemeConfig)
    contacts: ContactsConfig = Field(default_factory=ContactsConfig)
    social: list[SocialLink] = Field(default_factory=list)
    seo: SeoConfig = Field(default_factory=SeoConfig)
    home: HomeConfig = Field(default_factory=HomeConfig)
    features: FeaturesConfig = Field(default_factory=FeaturesConfig)
    demo: DemoConfig = Field(default_factory=DemoConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)

    model_config = SettingsConfigDict(
        env_prefix="BRAND__",
        env_nested_delimiter="__",
        extra="forbid",
    )

    @field_validator("logo_url", "favicon_url")
    @classmethod
    def check_assets(cls, value: str | None) -> str | None:
        """Validates logo and favicon references."""
        return _validate_asset(value)

    @model_validator(mode="after")
    def fill_derived(self) -> Self:
        """Fills short name, legal name and API title from the brand name."""
        if not self.short_name:
            initials = "".join(word[0] for word in self.name.split() if word[:1].isalnum())
            self.short_name = (initials or self.name)[:2].upper()
        self.legal_name = self.legal_name or self.name
        self.server.api_title = self.server.api_title or f"{self.name} API"
        return self

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """Orders sources: init kwargs, env, then the brand YAML file."""
        yaml_source = YamlConfigSettingsSource(settings_cls, yaml_file=brand_config_file(), yaml_file_encoding="utf-8")
        return init_settings, env_settings, yaml_source

    def public_dict(self) -> dict[str, Any]:
        """Public part for GET /brand: no server settings, asset names resolved to URLs."""
        data = self.model_dump(mode="json", exclude={"server"})
        for key in ("logo_url", "favicon_url"):
            data[key] = resolve_asset(data[key])
        data["seo"]["og_image_url"] = resolve_asset(data["seo"]["og_image_url"])
        images = data["home"]["images"]
        for key, value in images.items():
            images[key] = [resolve_asset(v) for v in value] if isinstance(value, list) else resolve_asset(value)
        return data
