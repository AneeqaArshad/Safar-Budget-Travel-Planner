"""
Database initialization module.
Provides the shared SQLAlchemy db instance used across all models.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
