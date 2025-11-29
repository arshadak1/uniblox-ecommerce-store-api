"""
Admin service for managing administrative operations.
Provides statistics and reporting functionality.
"""

import logging
from tkinter import Listbox
from typing import Dict, List
from app.repositories.repository import UnibloxRepository
from app.models.schema import AdminStoreStatisticsResponse, User

logger = logging.getLogger(__name__)


class AdminService:
    """Service class for administrative operations."""

    def __init__(self, repository: UnibloxRepository):
        """
        Initialize the admin service.

        Args:
            repository: Data repository instance
        """
        self.repository = repository

    def get_statistics(self) -> AdminStoreStatisticsResponse:
        """
        Get comprehensive store statistics.

        Returns:
            Statistics response with all metrics
        """
        logger.info("Fetching store statistics")

        stats = self.repository.get_statistics()

        logger.info(
            f"Statistics retrieved - Orders: {stats.total_orders}, "
            f"Revenue: ${stats.total_purchase_amount:.2f}"
        )

        return stats

    def get_users(self) -> List[User]:
        return self.repository.get_users()
