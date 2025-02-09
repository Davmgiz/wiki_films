import scrapy


class FilmsSpider(scrapy.Spider):
    name = 'films_spider'
    allowed_domains = ['ru.wikipedia.org']
    start_urls = [
        'https://ru.wikipedia.org/wiki/Категория:Фильмы_по_алфавиту'
    ]

    # Флаг для тестового режима (True - обрабатывает только первую страницу)
    TEST_MODE = False

    def parse(self, response):
        """Парсим список фильмов и переходим на каждую страницу фильма"""

        # Извлекаем ссылки на фильмы
        film_links = response.css('div.mw-category-group ul li a::attr(href)').getall()
        for link in film_links:
            if "/wiki/" in link and ":" not in link:
                full_url = response.urljoin(link)
                yield scrapy.Request(full_url, callback=self.parse_film)

        # Проверяем, есть ли ссылка на следующую страницу списка (если не в тестовом режиме)
        if not self.TEST_MODE:
            next_page = response.xpath('//a[contains(text(), "Следующая страница")]/@href').get()
            if next_page:
                yield response.follow(next_page, callback=self.parse)

    def parse_film(self, response):
        """Парсим страницу конкретного фильма."""

        def extract_text(xpath_query):
            """Функция для извлечения текста, удаляя лишние пробелы и переносы строк"""

            return ' '.join(response.xpath(xpath_query).getall()).strip() or 'Неизвестно'

        # Название
        title = response.xpath('//h1[@id="firstHeading"]//span[@class="mw-page-title-main"]/text()').get() or 'Неизвестно'
        title = title.strip()

        # Жанр
        genre = ' '.join(response.xpath('//th[contains(.,"Жанр")]/following-sibling::td//a/text()').getall()) \
            or ' '.join(response.xpath('//span[@data-wikidata-property-id="P136"]/text()').getall()) \
            or "Неизвестно"

        # Режиссёр
        director = ', '.join(response.xpath('//th[contains(text(), "Режиссёр")]/following-sibling::td//a/text()').getall()) \
            or extract_text('//th[contains(text(), "Режиссёр")]/following-sibling::td//text()')

        # Страна
        country = response.xpath('//span[@data-wikidata-property-id="P495"]/span/a/span/text()').get() \
            or response.xpath('//span[@class="country-name"]/span/a/text()').get() \
            or "Неизвестно"

        # Год
        year = ' '.join(response.xpath('//th[contains(text(),"Год")]/following-sibling::td//a/text()').getall()).strip() or \
            ' '.join(response.xpath('//th[contains(text(),"Год")]/following-sibling::td//a/span/text()').getall()).strip() or \
            ' '.join(response.xpath('//th[contains(text(),"Дата выхода") or contains(text(),"Премьера")]/following-sibling::td//text()').getall()).strip() or \
            "Неизвестно"

        # Сохраняем данные
        yield {
            'title': title,
            'genre': genre,
            'director': director,
            'country': country,
            'year': year,
        }
