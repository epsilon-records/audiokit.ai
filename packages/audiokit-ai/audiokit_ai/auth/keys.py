from datetime import datetime, timedelta
from cryptography.fernet import Fernet, MultiFernet
import logging

logger = logging.getLogger(__name__)

class KeyManager:
    def __init__(self, key_store):
        self.key_store = key_store
        self.current_key = None
        self.fernet = None
        self.rotation_interval = timedelta(days=90)
        
    def initialize_keys(self):
        """Initialize or rotate keys on startup"""
        if not self.key_store.list_keys():
            self._generate_new_key()
        else:
            self._load_current_key()
            
        self._schedule_rotation()
        
    def _generate_new_key(self):
        """Generate and activate new encryption key"""
        new_key = Fernet.generate_key()
        activation = datetime.utcnow()
        
        self.key_store.add_key(new_key, activation)
        self._update_fernet()
        logger.info("Generated new encryption key: %s", new_key.decode()[:8])
        
    def _load_current_key(self):
        """Load most recent valid key"""
        keys = self.key_store.list_valid_keys()
        if not keys:
            raise ValueError("No valid encryption keys available")
            
        self.current_key = keys[0]
        self._update_fernet()
        
    def _update_fernet(self):
        """Update Fernet instance with current+previous keys"""
        valid_keys = self.key_store.list_valid_keys()
        self.fernet = MultiFernet([Fernet(k) for k in valid_keys])
        
    def _schedule_rotation(self):
        """Check and rotate keys periodically"""
        now = datetime.utcnow()
        next_rotation = self.key_store.oldest_key_date() + self.rotation_interval
        
        if now >= next_rotation:
            logger.info("Initiating key rotation...")
            self._generate_new_key()
            self._purge_old_keys()
            
    def _purge_old_keys(self):
        """Remove keys beyond retention period"""
        cutoff = datetime.utcnow() - (self.rotation_interval * 2)
        self.key_store.purge_keys(cutoff) 