from datetime import datetime, timedelta
from cryptography.fernet import Fernet, MultiFernet
import logging

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self, key_store):
        self.key_store = key_store
        self.key_rotation_interval = timedelta(days=90)
        self._init_keys()
        
    def _init_keys(self):
        """Initialize or rotate encryption keys"""
        if not self.key_store.has_active_keys():
            self._generate_new_key()
        self._rotate_keys_if_needed()
        self._update_crypto_system()
        
    def _generate_new_key(self):
        """Generate and store new encryption key"""
        new_key = Fernet.generate_key()
        self.key_store.add_key(new_key, datetime.utcnow())
        logger.info("Generated new encryption key")
        
    def _rotate_keys_if_needed(self):
        """Check and perform key rotation"""
        oldest_key_date = self.key_store.get_oldest_key_date()
        if datetime.utcnow() - oldest_key_date > self.key_rotation_interval:
            self._generate_new_key()
            self._cleanup_old_keys()
            
    def _cleanup_old_keys(self):
        """Remove keys beyond retention period"""
        cutoff = datetime.utcnow() - (self.key_rotation_interval * 2)
        self.key_store.remove_keys_older_than(cutoff)
        
    def _update_crypto_system(self):
        """Update crypto with current valid keys"""
        valid_keys = self.key_store.get_valid_keys()
        self.crypto = MultiFernet([Fernet(k) for k in valid_keys]) 