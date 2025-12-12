# Don't import models here to avoid circular imports
# Models should be imported directly where needed

from models.db import db

__all__ = ['db']