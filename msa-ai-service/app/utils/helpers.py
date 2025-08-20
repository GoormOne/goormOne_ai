# 공통 유틸

# app/utils/helpers.py
import uuid

def gen_uuid() -> str:
    """UUID v4 문자열 반환"""
    return str(uuid.uuid4())
