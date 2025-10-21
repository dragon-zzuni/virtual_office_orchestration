# -*- coding: utf-8 -*-
"""
날짜/시간 유틸리티 함수

날짜 파싱 및 변환 관련 공통 함수를 제공합니다.
"""
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def parse_iso_datetime(value: Optional[str]) -> Optional[datetime]:
    """ISO 형식 날짜 문자열을 datetime 객체로 변환
    
    다양한 ISO 형식을 지원하며, 타임존 정보가 없으면 UTC로 간주합니다.
    
    Args:
        value: ISO 형식 날짜 문자열 (예: "2024-01-01T12:00:00Z")
        
    Returns:
        datetime 객체 또는 None (파싱 실패 시)
        
    Examples:
        >>> parse_iso_datetime("2024-01-01T12:00:00Z")
        datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        
        >>> parse_iso_datetime("2024-01-01T12:00:00")
        datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
        
        >>> parse_iso_datetime(None)
        None
    """
    if not value:
        return None
    
    try:
        # Z를 +00:00으로 변환
        value_str = str(value).strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(value_str)
        
        # naive datetime이면 UTC로 간주
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        
        return dt
    except (ValueError, AttributeError) as e:
        logger.debug(f"날짜 파싱 실패 ({value}): {e}")
        return None


def parse_message_date(message: Dict[str, Any]) -> datetime:
    """메시지에서 날짜를 파싱하여 UTC aware datetime으로 반환
    
    메시지 딕셔너리에서 날짜 정보를 추출하고 파싱합니다.
    date, timestamp, datetime 필드를 순서대로 확인합니다.
    
    Args:
        message: 메시지 딕셔너리
        
    Returns:
        UTC aware datetime 객체 (파싱 실패 시 현재 시간)
        
    Examples:
        >>> msg = {"date": "2024-01-01T12:00:00Z", "sender": "user"}
        >>> parse_message_date(msg)
        datetime.datetime(2024, 1, 1, 12, 0, tzinfo=datetime.timezone.utc)
    """
    # 날짜 필드 추출 (우선순위: date > timestamp > datetime)
    date_str = (
        message.get("date") or 
        message.get("timestamp") or 
        message.get("datetime")
    )
    
    if not date_str:
        logger.warning(f"메시지에 날짜 정보가 없습니다: {message.get('msg_id')}")
        return datetime.now(timezone.utc)
    
    # ISO 형식 파싱
    dt = parse_iso_datetime(date_str)
    if dt:
        return dt
    
    # 파싱 실패 시 현재 시간 반환
    logger.warning(f"날짜 파싱 실패 ({date_str}), 현재 시간 사용")
    return datetime.now(timezone.utc)


def ensure_utc_aware(dt: Optional[datetime]) -> Optional[datetime]:
    """naive datetime을 UTC aware datetime으로 변환
    
    이미 timezone 정보가 있는 datetime은 그대로 반환합니다.
    
    Args:
        dt: datetime 객체 (naive 또는 aware)
        
    Returns:
        UTC aware datetime 객체 또는 None (입력이 None인 경우)
        
    Examples:
        >>> from datetime import datetime, timezone
        >>> naive_dt = datetime(2024, 1, 1, 12, 0, 0)
        >>> aware_dt = ensure_utc_aware(naive_dt)
        >>> aware_dt.tzinfo
        datetime.timezone.utc
        
        >>> already_aware = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        >>> ensure_utc_aware(already_aware) == already_aware
        True
    """
    if dt is None:
        return None
    
    if dt.tzinfo is None:
        # naive datetime을 UTC로 간주
        return dt.replace(tzinfo=timezone.utc)
    
    # 이미 aware datetime이면 그대로 반환
    return dt


def is_in_time_range(
    dt: datetime,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None
) -> bool:
    """datetime 객체가 지정된 시간 범위 내에 있는지 확인
    
    타임존이 없는 naive datetime은 UTC로 간주합니다.
    
    Args:
        dt: 확인할 datetime 객체
        start: 시작 시간 (None이면 제한 없음)
        end: 종료 시간 (None이면 제한 없음)
        
    Returns:
        시간 범위 내에 있으면 True, 그렇지 않으면 False
        
    Examples:
        >>> from datetime import datetime, timedelta, timezone
        >>> now = datetime.now(timezone.utc)
        >>> start = now - timedelta(hours=1)
        >>> end = now + timedelta(hours=1)
        >>> is_in_time_range(now, start, end)
        True
        
        >>> past = now - timedelta(hours=2)
        >>> is_in_time_range(past, start, end)
        False
    """
    # naive datetime을 UTC aware로 변환
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    if start:
        if start.tzinfo is None:
            start = start.replace(tzinfo=timezone.utc)
        if dt < start:
            return False
    
    if end:
        if end.tzinfo is None:
            end = end.replace(tzinfo=timezone.utc)
        if dt > end:
            return False
    
    return True
