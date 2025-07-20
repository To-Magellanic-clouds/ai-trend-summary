import requests
import json
import time
from datetime import datetime, timedelta


class ProductHuntAPIClient:
    def __init__(self, access_token):
        """
        初始化API客户端
        access_token: 从 https://www.producthunt.com/v2/oauth/applications 获取的开发者token
        """
        self.access_token = access_token
        self.api_url = "https://api.producthunt.com/v2/api/graphql"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def get_weekly_products(self, days_back=7):
        """获取指定天数内的产品数据"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)

        query = """
        query GetPosts($after: String, $first: Int, $postedAfter: DateTime, $postedBefore: DateTime) {
            posts(
                after: $after
                first: $first
                postedAfter: $postedAfter
                postedBefore: $postedBefore
                order: VOTES
            ) {
                edges {
                    node {
                        id
                        name
                        tagline
                        description
                        url
                        slug
                        votesCount
                        commentsCount
                        createdAt
                        featuredAt
                        thumbnail {
                            url
                        }
                        gallery {
                            images {
                                url
                            }
                        }
                        topics {
                            edges {
                                node {
                                    id
                                    name
                                    slug
                                }
                            }
                        }
                        makers {
                            edges {
                                node {
                                    id
                                    name
                                    username
                                    headline
                                    profileImage
                                }
                            }
                        }
                        user {
                            id
                            name
                            username
                            headline
                        }
                        comments(first: 10) {
                            edges {
                                node {
                                    id
                                    body
                                    createdAt
                                    user {
                                        name
                                        username
                                    }
                                }
                            }
                        }
                        reviewsRating
                        reviewsCount
                    }
                }
                pageInfo {
                    hasNextPage
                    endCursor
                }
            }
        }
        """

        all_products = []
        has_next_page = True
        cursor = None

        while has_next_page:
            variables = {
                "first": 20,
                "after": cursor,
                "postedAfter": start_date.isoformat() + "Z",
                "postedBefore": end_date.isoformat() + "Z"
            }

            payload = {
                "query": query,
                "variables": variables
            }

            try:
                response = requests.post(
                    self.api_url,
                    json=payload,
                    headers=self.headers,
                    timeout=30
                )
                response.raise_for_status()

                data = response.json()

                if 'errors' in data:
                    print(f"GraphQL错误: {data['errors']}")
                    break

                if 'data' in data and 'posts' in data['data']:
                    posts = data['data']['posts']['edges']
                    page_info = data['data']['posts']['pageInfo']

                    for post in posts:
                        product = self.parse_product(post['node'])
                        all_products.append(product)

                    has_next_page = page_info['hasNextPage']
                    cursor = page_info['endCursor']

                    print(f"已获取 {len(all_products)} 个产品...")

                else:
                    print("没有找到产品数据")
                    break

            except requests.exceptions.RequestException as e:
                print(f"请求错误: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"JSON解析错误: {e}")
                break

            # 添加延迟避免超过速率限制
            time.sleep(0.5)

        return all_products

    def parse_product(self, product_data):
        """解析产品数据"""
        # 提取分类标签
        topics = []
        if product_data.get('topics') and product_data['topics'].get('edges'):
            topics = [topic['node']['name'] for topic in product_data['topics']['edges']]

        # 提取创始人信息
        makers = []
        if product_data.get('makers') and product_data['makers'].get('edges'):
            makers = [
                {
                    'name': maker['node']['name'],
                    'username': maker['node']['username'],
                    'headline': maker['node'].get('headline', ''),
                    'profile_image': maker['node'].get('profileImage')
                }
                for maker in product_data['makers']['edges']
            ]

        # 提取评论（作为创始人评价的替代）
        comments = []
        if product_data.get('comments') and product_data['comments'].get('edges'):
            comments = [
                {
                    'body': comment['node']['body'],
                    'created_at': comment['node']['createdAt'],
                    'user': {
                        'name': comment['node']['user']['name'],
                        'username': comment['node']['user']['username']
                    }
                }
                for comment in product_data['comments']['edges']
            ]

        return {
            'id': product_data.get('id'),
            'title': product_data.get('name', ''),
            'tagline': product_data.get('tagline', ''),
            'description': product_data.get('description', ''),
            'url': product_data.get('url', ''),
            'ph_url': f"https://www.producthunt.com/posts/{product_data.get('slug', '')}",
            'slug': product_data.get('slug', ''),
            'categories': topics,
            'tags': topics,
            'votes_count': product_data.get('votesCount', 0),
            'comments_count': product_data.get('commentsCount', 0),
            'created_at': product_data.get('createdAt'),
            'featured_at': product_data.get('featuredAt'),
            'thumbnail': product_data.get('thumbnail', {}).get('url'),
            'makers': makers,
            'comments': comments,  # 可以作为"评价"的替代
            'reviews_rating': product_data.get('reviewsRating'),
            'reviews_count': product_data.get('reviewsCount', 0)
        }

    def save_to_json(self, products, filename=None):
        """保存数据到JSON文件"""
        if filename is None:
            filename = f"producthunt_weekly_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)

        print(f"数据已保存到 {filename}")

    def save_to_csv(self, products, filename=None):
        """保存数据到CSV文件"""
        import pandas as pd

        if filename is None:
            filename = f"producthunt_weekly_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

        csv_data = []
        for product in products:
            row = {
                'ID': product['id'],
                'Title': product['title'],
                'Tagline': product['tagline'],
                'Description': product['description'][:500] + '...' if len(product['description']) > 500 else product[
                    'description'],
                'URL': product['url'],
                'PH_URL': product['ph_url'],
                'Categories': ', '.join(product['categories']),
                'Tags': ', '.join(product['tags']),
                'Votes': product['votes_count'],
                'Comments': product['comments_count'],
                'Created_At': product['created_at'],
                'Featured_At': product['featured_at'],
                'Makers': ', '.join([maker['name'] for maker in product['makers']]),
                'Maker_Usernames': ', '.join([maker['username'] for maker in product['makers']]),
                'Reviews_Rating': product['reviews_rating'],
                'Reviews_Count': product['reviews_count'],
                'Top_Comments': ' | '.join(
                    [comment['body'][:100] + '...' if len(comment['body']) > 100 else comment['body']
                     for comment in product['comments'][:3]])
            }
            csv_data.append(row)

        df = pd.DataFrame(csv_data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"数据已保存到 {filename}")


# 使用示例
if __name__ == "__main__":
    # 你需要从 https://www.producthunt.com/v2/oauth/applications 获取开发者token
    ACCESS_TOKEN = "GGB1Z2kRiLHnhi-24ZqeXIvj4dCbKpMQ66ixUsZP_2U"

    if ACCESS_TOKEN == "YOUR_ACCESS_TOKEN_HERE":
        print("请先获取Product Hunt API token:")
        print("1. 访问 https://www.producthunt.com/v2/oauth/applications")
        print("2. 创建一个新的应用程序")
        print("3. 复制Developer Token")
        print("4. 替换上面的ACCESS_TOKEN变量")
        exit()

    client = ProductHuntAPIClient(ACCESS_TOKEN)

    print("开始获取Product Hunt周榜数据...")

    # 获取最近7天的产品
    products = client.get_weekly_products(days_back=7)

    print(f"\n成功获取到 {len(products)} 个产品")

    # 显示前几个产品
    for i, product in enumerate(products[:3]):
        print(f"\n产品 {i + 1}:")
        print(f"标题: {product['title']}")
        print(f"简介: {product['tagline']}")
        print(f"分类: {', '.join(product['categories'])}")
        print(f"投票数: {product['votes_count']}")
        print(f"创始人: {', '.join([maker['name'] for maker in product['makers']])}")
        print(f"产品链接: {product['url']}")
        print(f"PH链接: {product['ph_url']}")
        if product['comments']:
            print(f"热门评论: {product['comments'][0]['body'][:100]}...")

    # 保存数据
    client.save_to_json(products)

    try:
        client.save_to_csv(products)
    except ImportError:
        print("需要安装pandas来保存CSV格式: pip install pandas")
