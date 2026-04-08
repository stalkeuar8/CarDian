from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.schemas.lookups_schemas import ManualLookupRequestSchema
from app.models.lookups import ManualLookups, ParsedLookups
from app.repo.base_repo import BaseRepo


class ManualLookupsRepo(BaseRepo[ManualLookups]):
    model = ManualLookups


class ParsedLookupsRepo(BaseRepo[ParsedLookups]):
    model = ParsedLookups