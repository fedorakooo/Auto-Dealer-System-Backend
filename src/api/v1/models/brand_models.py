from pydantic import BaseModel

from src.brand_config import (
    ContactsConfig,
    DemoConfig,
    FeaturesConfig,
    HomeConfig,
    LocaleConfig,
    SeoConfig,
    SocialLink,
    ThemeConfig,
)


class BrandResponse(BaseModel):
    """Public brand configuration; asset references are already resolved to URLs."""

    name: str
    short_name: str
    tagline: str | None
    legal_name: str
    logo_url: str | None
    favicon_url: str | None
    locale: LocaleConfig
    theme: ThemeConfig
    contacts: ContactsConfig
    social: list[SocialLink]
    seo: SeoConfig
    home: HomeConfig
    features: FeaturesConfig
    demo: DemoConfig
