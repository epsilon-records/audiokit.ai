from datetime import datetime
from typing import List, Tuple

class KeyStore:
    def add_key(self, key: bytes, activation: datetime):
        """Store new encryption key with activation timestamp"""
        pass
        
    def get_valid_keys(self) -> List[bytes]:
        """Get keys still valid for decryption"""
        return []
        
    def get_oldest_key_date(self) -> datetime:
        """Get activation date of oldest active key"""
        return datetime.utcnow()
        
    def has_active_keys(self) -> bool:
        """Check if any keys are available"""
        return False
        
    def remove_keys_older_than(self, cutoff: datetime):
        """Remove keys activated before cutoff date"""
        pass 