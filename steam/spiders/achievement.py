import re
from collections.abc import AsyncIterator, Generator
from typing import Any

import scrapy
from parsel import Selector, SelectorList
from scrapy.http import Response

from steam.items import Achievement
from steam.utils.http import HttpUtils


class AchievementSpider(scrapy.Spider, HttpUtils):
    name = 'achievement'

    def __init__(self):
        HttpUtils.__init__(self)
        super().__init__()
        self.username = 'kaironn1'
        self.game_urls = set()

    async def start(self) -> AsyncIterator[Any]:
        url = f'https://steamcommunity.com/id/{self.username}/games/?tab=all'

        yield scrapy.Request(
            url=url,
            callback=self.parse_game_urls_from_all_tab,
            headers=self.headers,
            cookies=self.cookies,
        )

    def parse_game_urls_from_all_tab(self, response: Response) -> Generator[scrapy.Request, Any, None]:
        urls = self._parse_app_ids_to_achievements_urls(response=response)
        self.game_urls.update(urls)

        perfect_tab_url = f'https://steamcommunity.com/id/{self.username}/games/?tab=perfect'

        yield scrapy.Request(
            url=perfect_tab_url,
            callback=self.parse_game_urls_from_perfect_tab,
            headers=self.headers,
            cookies=self.cookies,
        )

    def parse_game_urls_from_perfect_tab(self, response: Response) -> Generator[scrapy.Request, Any, None]:
        urls = self._parse_app_ids_to_achievements_urls(response=response)
        self.game_urls.update(urls)

        for url in self.game_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse_achievements_page,
                headers=self.headers,
                cookies=self.cookies,
            )

    def parse_achievements_page(self, response: Response) -> Generator[Achievement, Any, None]:
        game = response.xpath('(//span[@class="profile_small_header_location"])[2]/text()').get()
        game = self._parse_game(game)

        language = self.cookies.get('Steam_Language')

        achivements_summary = response.xpath('//div[@id="topSummaryAchievements"]/div[1]/text()').get()
        unlocked, total = self._parse_achivements_summary(achivements_summary)

        achievement_cards = response.xpath('//div[@class="achieveTxtHolder"]')
        for card in achievement_cards:
            achievement_info = card.xpath('./div[contains(@class, "achieveTxt")]')
            title = achievement_info.xpath('./h3/text()').get()
            description = achievement_info.xpath('./h5/text()').get()

            progress_bar = achievement_info.xpath('./div[contains(@class, "achievementProgressBar")]')
            current_progress, total_progress = self._parse_progression(progress_bar=progress_bar)
                
            unlock_time = card.xpath('./div[@class="achieveUnlockTime"]/text()').get()

            achievement = Achievement()
            achievement['username'] = self.username
            achievement['game'] = game
            achievement['title'] = title
            achievement['description'] = description
            achievement['unlock_time'] = unlock_time
            achievement['unlocked'] = unlocked
            achievement['total'] = total
            achievement['current_progress'] = current_progress
            achievement['total_progress'] = total_progress
            achievement['language'] = language
            achievement['url'] = response.url

            yield achievement

    def _parse_achivements_summary(self, summary: str | None) -> tuple[int | None, int | None]:
        if not summary:
            return None, None
        
        parts = summary.strip().split(' de ')
        if len(parts) >= 2:
            unlocked = int(parts[0].strip())
            total = int(parts[1].split()[0].strip())
            return unlocked, total
        
        return None, None

    def _parse_game(self, game: str | None) -> str | None:
        if not game:
            return None
        
        game = game.strip()
        game = game.replace('Estatísticas de ', '')
        
        return game

    def _parse_app_ids_to_achievements_urls(self, response: Response) -> set[str]:
        urls = set()
        appids = set(re.findall(r'"appid\\*"?:(\d+)', response.text))
        for appid in appids:
            url = f'https://steamcommunity.com/id/{self.username}/stats/{appid}/achievements/'
            urls.add(url)
        return urls

    def _parse_progression(self, progress_bar: SelectorList[Selector]) -> tuple[float | None, float | None]:
        if not progress_bar:
            return None, None

        progression_info = progress_bar.xpath('./div[contains(@class, "progressText")]/text()').get()
        if progression_info:
            parts = progression_info.strip().split(' / ')
            current_progress = float(parts[0])
            total_progress = float(parts[1])
            return current_progress, total_progress
        
        return None, None
