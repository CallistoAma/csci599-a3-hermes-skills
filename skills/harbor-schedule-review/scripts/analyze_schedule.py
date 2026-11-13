"""Offline interval analysis. No network, subprocesses, or calendar mutation."""
from datetime import date, datetime, time, timedelta
import json
from pathlib import Path
import sys
from zoneinfo import ZoneInfo


def analyze(data):
    tz = ZoneInfo(data['timezone'])
    day = date.fromisoformat(data['date'])
    lower = datetime.combine(day, time.fromisoformat(data.get('work_start', '09:00')), tz)
    upper = datetime.combine(day, time.fromisoformat(data.get('work_end', '18:00')), tz)
    if upper <= lower:
        raise ValueError('Working hours must be an increasing same-day interval')
    minimum = data.get('minimum_gap_minutes', 30)
    if not isinstance(minimum, int) or not 1 <= minimum <= 1440:
        raise ValueError('minimum_gap_minutes must be 1–1440')
    events = data['events']
    if not isinstance(events, list) or len(events) > 1000:
        raise ValueError('Expected at most 1000 events')
    intervals = []
    seen = set()
    for event in events:
        if event.get('status') == 'cancelled' or event.get('transparency') == 'transparent':
            continue
        identifier = str(event['id'])
        if identifier in seen:
            raise ValueError('Event IDs must be unique')
        seen.add(identifier)
        def instant(value):
            if 'dateTime' in value:
                point = datetime.fromisoformat(value['dateTime'].replace('Z', '+00:00'))
                if point.tzinfo is None:
                    raise ValueError('Timed events require a UTC offset')
                return point.astimezone(tz)
            return datetime.combine(date.fromisoformat(value['date']), time.min, tz)
        start, end = instant(event['start']), instant(event['end'])
        if end <= start:
            raise ValueError('Events must end after they start')
        start, end = max(start, lower), min(end, upper)
        if start < end:
            intervals.append((start, end, identifier))
    intervals.sort()
    conflicts = []
    for i, (start, end, identifier) in enumerate(intervals):
        for other_start, other_end, other_id in intervals[i + 1:]:
            if other_start >= end:
                break
            conflicts.append({'events': [identifier, other_id],
                'start': other_start.isoformat(), 'end': min(end, other_end).isoformat(),
                'minutes': int((min(end, other_end) - other_start).total_seconds() // 60)})
    gaps = []
    cursor = lower
    for start, end, _ in intervals + [(upper, upper, '')]:
        if start - cursor >= timedelta(minutes=minimum):
            gaps.append({'start': cursor.isoformat(), 'end': start.isoformat(),
                         'minutes': int((start - cursor).total_seconds() // 60)})
        cursor = max(cursor, end)
    return {'date': day.isoformat(), 'timezone': str(tz), 'conflicts': conflicts,
            'free_intervals': gaps, 'calendar_modified': False}


if __name__ == '__main__':
    if len(sys.argv) != 2:
        raise SystemExit('Usage: analyze_schedule.py calendar.json')
    path = Path(sys.argv[1])
    if path.stat().st_size > 1_000_000:
        raise SystemExit('Input exceeds 1 MB')
    try:
        print(json.dumps(analyze(json.loads(path.read_text(encoding='utf-8'))), indent=2))
    except (ValueError, KeyError, TypeError) as exc:
        raise SystemExit('Invalid schedule: ' + str(exc))
