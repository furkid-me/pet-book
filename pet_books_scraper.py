"""
誠品書局寵物書籍爬蟲程式
自動收集寵物分類書籍並依照分類篩選
"""

import asyncio
import re
import json
from datetime import datetime
from playwright.async_api import async_playwright
import pandas as pd


# ===== 動物種類分類 =====
ANIMAL_TYPES = {
    "貓": [
        "貓", "貓咪", "喵", "喵星人", "虎斑", "波斯貓", "暹羅貓", "布偶貓",
        "英短", "美短", "橘貓", "黑貓", "白貓", "三花", "賓士貓", "摺耳貓"
    ],
    "狗": [
        "狗", "狗狗", "犬", "汪", "汪星人", "柴犬", "柯基", "貴賓", "拉布拉多",
        "黃金獵犬", "哈士奇", "法鬥", "臘腸", "柴柴", "毛孩", "幼犬", "老犬"
    ],
    "鳥類": [
        "鳥", "鳥類", "禽", "賞鳥", "野鳥", "鸚鵡", "文鳥", "雀", "鴿",
        "老鷹", "貓頭鷹", "燕", "鶴", "鵝", "鴨", "雞", "鷹", "隼"
    ],
    "魚類水族": [
        "魚", "水族", "熱帶魚", "金魚", "錦鯉", "觀賞魚", "水草", "水族箱",
        "鯊魚", "海洋", "海魚", "淡水魚", "魟魚", "鬥魚", "孔雀魚"
    ],
    "爬蟲兩棲": [
        "爬蟲", "蜥蜴", "龜", "烏龜", "蛇", "守宮", "變色龍", "鱷魚",
        "兩棲", "青蛙", "蟾蜍", "蠑螈", "山椒魚", "壁虎"
    ],
    "小動物": [
        "兔", "兔子", "倉鼠", "天竺鼠", "刺蝟", "松鼠", "蜜袋鼯", "龍貓",
        "黃金鼠", "鼠", "雪貂", "貂"
    ],
    "野生動物": [
        "野生", "動物園", "大象", "獅", "虎", "豹", "熊", "猴", "猿",
        "斑馬", "長頸鹿", "犀牛", "河馬", "自然史", "生態", "棲地", "保育"
    ],
}

# ===== 主題內容分類 =====
TOPIC_CATEGORIES = {
    "照護飼養": [
        "照護", "照顧", "飼養", "養育", "養護", "教養", "生活", "日常",
        "指南", "入門", "新手", "基礎", "必備", "養成", "習慣", "相處",
        "陪伴", "幸福", "快樂"
    ],
    "行為訓練": [
        "訓練", "行為", "教育", "調教", "矯正", "社會化", "服從", "指令",
        "問題行為", "攻擊", "吠叫", "如廁", "散步"
    ],
    "醫療健康": [
        "醫療", "疾病", "病症", "健康", "獸醫", "醫學", "治療", "診斷",
        "症狀", "預防", "保健", "營養", "飲食", "食療", "藥物", "手術",
        "急救", "護理", "復健", "老年", "高齡", "慢性", "按摩", "穴道"
    ],
    "寵物溝通": [
        "溝通", "心靈", "靈性", "對話", "傾聽", "感應", "讀心", "心語",
        "動物溝通", "寵物溝通", "心聲", "內心", "情感", "情緒", "療癒",
        "心理", "理解", "連結", "靈魂", "能量"
    ],
    "圖鑑百科": [
        "圖鑑", "百科", "大全", "全書", "手冊", "辨識", "種類", "品種",
        "分類", "特徵", "圖解", "輕圖鑑"
    ],
    "攝影藝術": [
        "攝影", "寫真", "相片", "照片", "拍攝", "紀實", "影像"
    ],
    "故事散文": [
        "故事", "散文", "日記", "札記", "回憶", "紀錄", "手記", "真實",
        "感人", "溫馨", "事件簿", "傳奇", "冒險"
    ],
    "離世告別": [
        "離世", "告別", "道別", "再見", "天堂", "彩虹橋", "逝去", "離開",
        "悼念", "懷念", "追思", "失去", "喪失", "死亡", "臨終", "安樂",
        "寵物喪禮", "骨灰", "紀念", "永別", "思念", "緬懷", "終老"
    ],
    "美容": [
        "美容", "造型", "剪毛", "洗澡", "清潔", "毛髮", "護毛", "梳理",
        "修剪", "打扮", "穿搭", "服飾", "配件", "裝扮", "美化", "保養"
    ],
    "昆蟲": [
        "昆蟲", "蟲", "蜂", "蝴蝶", "蛾", "甲蟲", "螳螂", "蜻蜓", "蟬",
        "蚊", "蠅", "蟻", "螞蟻", "蜘蛛", "蠍", "蜈蚣", "纓翅", "薊馬",
        "鍬形蟲", "獨角仙", "瓢蟲", "蟑螂", "蝗蟲", "蟋蟀", "螢火蟲"
    ],
    "海洋生物": [
        "海洋", "海底", "珊瑚", "水母", "海星", "海膽", "貝殼", "蝦",
        "蟹", "龍蝦", "章魚", "烏賊", "鯨", "海豚", "海龜", "海馬",
        "潮汐", "深海", "礁", "磷蝦", "浮游"
    ],
    "自然科普": [
        "自然", "科普", "生態", "演化", "物種", "生物學", "自然史",
        "環遊世界", "探索", "奧祕", "科學", "大自然", "地球", "棲地",
        "遷徙", "長征", "奧德賽"
    ],
    "獸醫專業": [
        "外科", "內科", "病理", "臨床", "腫瘤", "解剖", "生理", "藥理",
        "麻醉", "影像", "檢驗", "實驗", "教科書", "專業", "學術"
    ],
    "農牧養殖": [
        "養殖", "繁殖", "畜牧", "牧場", "農場", "豬", "牛", "羊", "雞",
        "鴨", "鵝", "蜂場", "漁場", "水產", "飼料", "產蛋", "肉用"
    ],
    "童書繪本": [
        "繪本", "童書", "兒童", "親子", "故事書", "圖畫書", "漫畫",
        "卡通", "套書", "偵探", "冒險", "遊俠", "小遊", "探索"
    ],
    "環境保育": [
        "保育", "保護", "瀕危", "紅皮書", "復育", "棲地", "生態系",
        "環境", "永續", "監測", "調查", "年報", "名錄", "野放"
    ],
    "藝術人文": [
        "藝術", "人文", "文化", "歷史", "神話", "傳說", "寓意", "象徵",
        "名畫", "印象派", "文學", "詩", "哲學", "美學", "創世紀"
    ],
}

# 保留舊的 CATEGORIES 供相容性（合併動物和主題）
CATEGORIES = {**{k: v for k, v in TOPIC_CATEGORIES.items()}}

# 誠品寵物書籍分類頁面
PET_CATEGORY_URL = "https://www.eslite.com/category/3/123"


class EslitePetBooksScraper:
    """誠品寵物書籍爬蟲類別"""

    def __init__(self):
        self.books = []
        self.base_url = "https://www.eslite.com"

    async def scrape_category_page(self, page, max_pages=50):
        """爬取寵物分類頁面的所有書籍（支援分頁）"""
        all_books = []
        seen_urls = set()
        current_page = 1

        print(f"正在爬取分類頁面: {PET_CATEGORY_URL}")

        while current_page <= max_pages:
            # 構建分頁 URL
            if current_page == 1:
                url = PET_CATEGORY_URL
            else:
                url = f"{PET_CATEGORY_URL}?page={current_page}"

            print(f"\n正在訪問第 {current_page} 頁: {url}")

            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
                await asyncio.sleep(5)  # 等待 JavaScript 渲染

                # 滾動頁面確保所有內容載入
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)

            except Exception as e:
                print(f"  載入頁面失敗: {e}")
                break

            # 抓取目前頁面上的書籍
            books = await page.evaluate("""
                () => {
                    const books = [];

                    // 找所有產品卡片
                    const productCards = document.querySelectorAll('a.product-item[href*="/product/"]');

                    productCards.forEach(card => {
                        try {
                            const href = card.href || '';
                            if (!href.includes('/product/')) return;

                            // 取得書名 - 使用 product-name class
                            let title = '';
                            const nameEl = card.querySelector('.product-name');
                            if (nameEl) {
                                title = nameEl.textContent.trim();
                            }
                            // 備用：從 title 屬性取得
                            if (!title) {
                                const imgWrap = card.querySelector('.product-image');
                                if (imgWrap) {
                                    title = imgWrap.getAttribute('title') || '';
                                }
                            }

                            // 取得作者 - 使用 product-author class
                            let author = '';
                            const authorEl = card.querySelector('.product-author');
                            if (authorEl) {
                                author = authorEl.textContent.trim();
                            }

                            // 取得價格 - 使用 slider-price class (折後價)
                            let price = '';
                            let originalPrice = '';
                            let discount = '';

                            const priceEl = card.querySelector('.slider-price');
                            if (priceEl) {
                                price = priceEl.textContent.trim();
                            }

                            // 取得折扣
                            const discountEl = card.querySelector('.discount');
                            if (discountEl) {
                                discount = discountEl.textContent.trim() + '折';
                            }

                            // 取得原價 (從 pre-price 屬性)
                            const priceWrap = card.querySelector('[pre-price]');
                            if (priceWrap) {
                                originalPrice = priceWrap.getAttribute('pre-price') || '';
                            }

                            // 取得圖片
                            let image = '';
                            const imgEl = card.querySelector('img');
                            if (imgEl) {
                                image = imgEl.src || imgEl.dataset.src || '';
                            }

                            if (title && title.length > 2) {
                                books.push({
                                    title: title.substring(0, 200),
                                    author: author,
                                    price: price,
                                    originalPrice: originalPrice,
                                    discount: discount,
                                    url: href,
                                    image: image
                                });
                            }
                        } catch (e) {}
                    });

                    return books;
                }
            """)

            # 去重並加入
            page_new_count = 0
            for book in books:
                if book['url'] not in seen_urls and book['title']:
                    seen_urls.add(book['url'])
                    all_books.append(book)
                    page_new_count += 1

            print(f"  第 {current_page} 頁收集: {page_new_count} 本新書，累計: {len(all_books)} 本")

            # 如果這一頁沒有新書，表示已經到最後了
            if page_new_count == 0:
                print(f"  第 {current_page} 頁沒有新書，停止爬取")
                break

            # 前往下一頁
            current_page += 1

        print(f"\n分類頁面共收集: {len(all_books)} 本書")
        return all_books

    async def _scroll_page(self, page, scroll_times=5):
        """滾動頁面以載入更多內容"""
        for i in range(scroll_times):
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(1)
            print(f"  滾動頁面 {i+1}/{scroll_times}")

    def categorize_animal_type(self, book):
        """根據書名判斷動物種類"""
        text = f"{book.get('title', '')} {book.get('author', '')}".lower()

        matched_types = []
        for animal_type, keywords in ANIMAL_TYPES.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    if animal_type not in matched_types:
                        matched_types.append(animal_type)
                    break

        return matched_types if matched_types else ["通用"]

    def categorize_topic(self, book):
        """根據書名判斷主題分類"""
        text = f"{book.get('title', '')} {book.get('author', '')}".lower()

        matched_topics = []
        for topic, keywords in TOPIC_CATEGORIES.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    if topic not in matched_topics:
                        matched_topics.append(topic)
                    break

        return matched_topics if matched_topics else ["其他"]

    def categorize_book(self, book):
        """根據書名和作者判斷書籍分類（相容舊版）"""
        return self.categorize_topic(book)

    def categorize_all_books(self, books):
        """為所有書籍進行雙層分類"""
        for book in books:
            # 動物種類
            book['animal_types'] = self.categorize_animal_type(book)
            book['animal_type_str'] = ", ".join(book['animal_types'])

            # 主題分類
            book['topics'] = self.categorize_topic(book)
            book['topic_str'] = ", ".join(book['topics'])

            # 組合分類（動物-主題）
            combined = []
            for animal in book['animal_types']:
                for topic in book['topics']:
                    combined.append(f"{animal}-{topic}")
            book['combined_category'] = ", ".join(combined)

            # 保留舊欄位供相容性
            book['categories'] = book['topics']
            book['category_str'] = book['topic_str']

        return books

    def filter_by_category(self, books, category):
        """根據分類篩選書籍"""
        return [book for book in books if category in book.get('categories', [])]

    def filter_by_animal_type(self, books, animal_type):
        """根據動物種類篩選書籍"""
        return [book for book in books if animal_type in book.get('animal_types', [])]

    def filter_by_topic(self, books, topic):
        """根據主題篩選書籍"""
        return [book for book in books if topic in book.get('topics', [])]

    def export_to_excel(self, books, filename=None):
        """匯出書籍資料到 Excel（含雙層分類）"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pet_books_{timestamp}.xlsx"

        # 準備資料
        export_data = []
        for book in books:
            export_data.append({
                "書名": book.get('title', ''),
                "作者": book.get('author', ''),
                "售價": book.get('price', ''),
                "原價": book.get('originalPrice', ''),
                "折扣": book.get('discount', ''),
                "動物種類": book.get('animal_type_str', ''),
                "主題分類": book.get('topic_str', ''),
                "組合分類": book.get('combined_category', ''),
                "連結": book.get('url', ''),
                "圖片": book.get('image', '')
            })

        df = pd.DataFrame(export_data)

        # 創建 Excel 並分工作表
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # 全部書籍
            df.to_excel(writer, sheet_name='全部書籍', index=False)

            # 依動物種類分頁
            for animal_type in list(ANIMAL_TYPES.keys()) + ["通用"]:
                animal_books = [b for b in export_data if animal_type in b['動物種類']]
                if animal_books:
                    animal_df = pd.DataFrame(animal_books)
                    # Excel 工作表名稱限制 31 字元
                    sheet_name = f"【{animal_type}】"[:31]
                    animal_df.to_excel(writer, sheet_name=sheet_name, index=False)

            # 依主題分類分頁
            for topic in list(TOPIC_CATEGORIES.keys()) + ["其他"]:
                topic_books = [b for b in export_data if topic in b['主題分類']]
                if topic_books:
                    topic_df = pd.DataFrame(topic_books)
                    sheet_name = f"主題-{topic}"[:31]
                    topic_df.to_excel(writer, sheet_name=sheet_name, index=False)

        print(f"\n已匯出到: {filename}")
        return filename

    def export_to_csv(self, books, filename=None):
        """匯出書籍資料到 CSV（含雙層分類）"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pet_books_{timestamp}.csv"

        export_data = []
        for book in books:
            export_data.append({
                "書名": book.get('title', ''),
                "作者": book.get('author', ''),
                "售價": book.get('price', ''),
                "原價": book.get('originalPrice', ''),
                "折扣": book.get('discount', ''),
                "動物種類": book.get('animal_type_str', ''),
                "主題分類": book.get('topic_str', ''),
                "組合分類": book.get('combined_category', ''),
                "連結": book.get('url', ''),
                "圖片": book.get('image', '')
            })

        df = pd.DataFrame(export_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')

        print(f"\n已匯出到: {filename}")
        return filename

    def print_summary(self, books):
        """印出統計摘要（雙層分類）"""
        print("\n" + "="*60)
        print("書籍收集統計")
        print("="*60)
        print(f"總共收集: {len(books)} 本書")

        # 動物種類統計
        print("\n【動物種類】")
        animal_counts = {}
        for book in books:
            for animal in book.get('animal_types', ['通用']):
                animal_counts[animal] = animal_counts.get(animal, 0) + 1

        for animal, count in sorted(animal_counts.items(), key=lambda x: -x[1]):
            print(f"  {animal}: {count} 本")

        # 主題分類統計
        print("\n【主題分類】")
        topic_counts = {}
        for book in books:
            for topic in book.get('topics', ['其他']):
                topic_counts[topic] = topic_counts.get(topic, 0) + 1

        for topic, count in sorted(topic_counts.items(), key=lambda x: -x[1]):
            print(f"  {topic}: {count} 本")

        print("="*60)


async def main():
    """主程式"""
    print("="*60)
    print("誠品書局寵物書籍爬蟲")
    print(f"分類頁面: {PET_CATEGORY_URL}")
    print("="*60)

    scraper = EslitePetBooksScraper()

    async with async_playwright() as p:
        # 啟動瀏覽器
        print("\n正在啟動瀏覽器...")
        browser = await p.chromium.launch(
            headless=True,  # 設為 False 可以看到瀏覽器操作
        )

        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        page = await context.new_page()

        try:
            # 從分類頁面收集書籍
            print("\n開始從分類頁面收集寵物書籍...")
            books = await scraper.scrape_category_page(page)

            if books:
                # 分類書籍
                print("\n正在分類書籍...")
                books = scraper.categorize_all_books(books)

                # 印出統計
                scraper.print_summary(books)

                # 匯出結果
                print("\n正在匯出結果...")
                scraper.export_to_excel(books)
                scraper.export_to_csv(books)

                # 顯示各動物種類的書籍範例
                print("\n\n========== 各動物種類書籍範例 ==========")
                for animal_type in list(ANIMAL_TYPES.keys()) + ["通用"]:
                    animal_books = scraper.filter_by_animal_type(books, animal_type)
                    if animal_books:
                        print(f"\n【{animal_type}】({len(animal_books)} 本)")
                        for book in animal_books[:2]:
                            print(f"  - {book['title'][:45]}")

                # 顯示各主題的書籍範例
                print("\n\n========== 各主題分類書籍範例 ==========")
                for topic in list(TOPIC_CATEGORIES.keys()) + ["其他"]:
                    topic_books = scraper.filter_by_topic(books, topic)
                    if topic_books:
                        print(f"\n【{topic}】({len(topic_books)} 本)")
                        for book in topic_books[:2]:
                            print(f"  - {book['title'][:45]}")
            else:
                print("\n無法收集到書籍資料，可能是網站結構有變化。")
                print(f"建議手動檢查 {PET_CATEGORY_URL}")

        except Exception as e:
            print(f"\n執行時發生錯誤: {e}")
            import traceback
            traceback.print_exc()

        finally:
            await browser.close()
            print("\n瀏覽器已關閉")


if __name__ == "__main__":
    asyncio.run(main())
