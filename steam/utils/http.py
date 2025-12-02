import json
from pathlib import Path
from typing import Any

class HttpUtils:
    DEFAULT_JSON_FILE = Path('curl.json')

    def __init__(self, json_file: str | Path | None = None):
        self.json_file = Path(json_file) if json_file else self.DEFAULT_JSON_FILE

    @property
    def data(self) -> dict[str, Any]:
        json_path = Path(self.json_file)
        if not json_path.exists():
            raise FileNotFoundError(f'{json_path} not found')
        
        data = json.loads(json_path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError('expected top-level JSON object (dict)')

        return data
    
    @property
    def headers(self) -> dict[str, str]:
        headers: dict[str, str] | None = self.data.get('headers')
        if not headers:
            raise ValueError('"headers" key not found on json')

        headers.pop('Referer', None)

        return headers

    @property
    def cookies(self) -> dict[str, str]:
        cookies: dict[str, str] | None = self.data.get('cookies')
        if not cookies:
            raise ValueError('"cookies" key not found on json')
        
        required_keys = ['steamLoginSecure', 'browserid', 'sessionid']
        if not all(key in cookies for key in required_keys):
            raise ValueError(f'Missing required cookies: {required_keys}')

        return cookies
