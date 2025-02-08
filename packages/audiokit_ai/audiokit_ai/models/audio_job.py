# CONFIDENTIAL AND PROPRIETARY
# 
# Copyright (c) 2025 AudioKit.ai. All rights reserved.
# 
# This software is confidential and proprietary.
# 

# 
# This file is part of the AudioKit AI package.
# 

from pydantic import BaseModel
from datetime import datetime

class AudioJob(BaseModel):
    id: int
    task_name: str
    status: str
    created_at: datetime
    result_url: str = None 