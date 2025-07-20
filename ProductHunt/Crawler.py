import requests
from bs4 import BeautifulSoup
import markdownify
from urllib.parse import urljoin
from typing import List, Dict
import re
import json
import time


class ProductHuntScraper:
    def __init__(self):
        self.base_url = "https://www.producthunt.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })

    def scrape_weekly_leaderboard(self, year: int, week: int) -> List[Dict]:
        """
        爬取指定年份和周的Product Hunt排行榜
        :param year: 年份 (如2025)
        :param week: 周数 (1-52)
        :return: 产品信息列表
        """
        url = f"{self.base_url}/leaderboard/weekly/{year}/{week}/all"
        print(f"正在爬取 {year}年第{week}周排行榜: {url}")

        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 解析产品列表
            products = self._parse_product_list(soup)

            # 获取每个产品的详细信息
            for product in products:
                product_details = self.scrape_product_details(product['url'])
                if product_details:
                    product.update(product_details)
                time.sleep(1)  # 礼貌性延迟

            return products

        except Exception as e:
            print(f"爬取排行榜时出错: {str(e)}")
            return []

    def _parse_product_list(self, soup: BeautifulSoup) -> List[Dict]:
        """
        解析产品列表页
        """
        products = []

        # 查找所有产品元素
        product_sections = soup.select('section[data-test^="post-item-"]')

        for section in product_sections:
            try:
                # 提取产品名称
                name_tag = section.select_one('a[data-test^="post-name-"]')
                name = name_tag.get_text(strip=True) if name_tag else "Unknown"

                # 提取产品URL
                relative_url = name_tag['href'] if name_tag else ""
                full_url = urljoin(self.base_url, relative_url)

                # 提取产品简介
                description_tag = section.select_one('a.text-secondary')
                description = description_tag.get_text(strip=True) if description_tag else ""

                # 提取标签
                tags = []

                tag_list = section.select_one('div[data-sentry-component="TagList"]')
                if tag_list:
                    for tag in tag_list.select('a[href^="/topics/"]'):
                        tag_text = tag.get_text(strip=True)
                        if tag_text:
                            tags.append(tag_text)


                #访问url获取详细信息

                #获取分类信息
                categories = []

                #获取

                products.append({
                    "name": name,
                    "url": full_url,
                    "description": description,
                    "tags": tags,
                    "categories": categories,
                })

            except Exception as e:
                print(f"解析产品时出错: {str(e)}")
                continue

        return products

    def scrape_product_details(self, url: str) -> Dict:
        """
        爬取单个产品的详细信息
        """
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 提取主要内容
            content_div = soup.select_one('div.prose') or soup.select_one('article') or soup.body

            if not content_div:
                return {"error": "无法找到内容区域"}

            # 转换为Markdown
            markdown_content = markdownify.markdownify(
                str(content_div),
                heading_style="ATX",
                autolinks=True,
                bullets='-'
            )

            # 清理Markdown内容
            markdown_content = self._clean_markdown(markdown_content)

            # 提取额外信息
            makers = []
            makers_section = soup.select_one('div[data-test="makers-section"]')
            if makers_section:
                for maker in makers_section.select('a[href^="/@"]'):
                    makers.append({
                        "name": maker.get_text(strip=True),
                        "url": urljoin(self.base_url, maker['href'])
                    })

            return {
                "content": markdown_content,
                "content_length": len(markdown_content),
                "makers": makers
            }

        except Exception as e:
            print(f"爬取产品详情时出错 {url}: {str(e)}")
            return None

    def _clean_markdown(self, text: str) -> str:
        """
        清理Markdown文本
        """
        # 移除连续空行
        text = re.sub(r'\n{3,}', '\n\n', text)
        # 修复代码块
        text = re.sub(r'```\s*\n\s*\n', '```\n', text)
        text = re.sub(r'\n\s*\n```', '\n```', text)
        # 移除HTML注释
        text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
        # 移除特殊字符
        text = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)

        return text.strip()

    def save_to_json(self, data: List[Dict], filename: str):
        """
        保存数据到JSON文件
        """
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    scraper = ProductHuntScraper()

    # 示例：爬取2025年第29周排行榜
    year = 2025
    week = 29
    products = scraper.scrape_weekly_leaderboard(year, week)

    if products:
        print(f"成功爬取 {len(products)} 个产品")
        filename = f"producthunt_leaderboard_{year}_week{week}.json"
        scraper.save_to_json(products, filename)
        print(f"数据已保存到 {filename}")

        # 打印前3个产品信息
        for i, product in enumerate(products[:3], 1):
            print(f"\n产品 #{i}:")
            print(f"名称: {product['name']}")
            print(f"简介: {product['description']}")
            print(f"标签: {', '.join(product['tags'])}")
            print(f"分类: {', '.join(product['categories'])}")
            print(f"URL: {product['url']}")
    else:
        print("未能爬取到产品数据")