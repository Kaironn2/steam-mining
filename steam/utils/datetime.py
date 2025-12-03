from datetime import datetime


class DatetimeUtils:
    @staticmethod
    def parse_unlock_time(unlock_str: str | None) -> datetime | None:
        """
        Converts a Steam unlock time string to a datetime object.
        Supported formats:
        - "10 Aug @ 7:52pm" (assumes current year)
        - "4 Aug, 2024 @ 1:36pm" (with year)
        """
        if not unlock_str:
            return None
        
        unlock_str = unlock_str.strip()
        
        if unlock_str.startswith("Unlocked "):
            unlock_str = unlock_str[10:]
        
        try:
            return datetime.strptime(unlock_str, "%d %b, %Y @ %I:%M%p")
        except ValueError:
            pass
        
        try:
            dt = datetime.strptime(unlock_str, "%d %b @ %I:%M%p")
            current_year = datetime.now().year
            dt = dt.replace(year=current_year)
            return dt
        except ValueError:
            return None
