"""
誠品書局寵物書籍爬蟲 - 互動版
提供選單介面讓用戶選擇操作
"""

import asyncio
import os
import sys
from datetime import datetime
from pet_books_scraper import EslitePetBooksScraper, CATEGORIES

try:
    from playwright.async_api import async_playwright
    import pandas as pd
except ImportError:
    print("缺少必要套件，請先執行 setup.bat 安裝")
    sys.exit(1)


def clear_screen():
    """清除螢幕"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_menu():
    """顯示主選單"""
    print("\n" + "="*60)
    print("    誠品書局寵物書籍收集工具")
    print("="*60)
    print("\n請選擇操作：")
    print("  1. 收集所有寵物書籍")
    print("  2. 載入已存在的資料")
    print("  3. 查看分類統計")
    print("  4. 依分類篩選書籍")
    print("  5. 匯出指定分類")
    print("  6. 離開")
    print()


def print_categories_menu():
    """顯示分類選單"""
    print("\n可用分類：")
    categories = list(CATEGORIES.keys()) + ["其他", "全部"]
    for i, cat in enumerate(categories, 1):
        print(f"  {i}. {cat}")
    return categories


class InteractiveBookManager:
    """互動式書籍管理器"""

    def __init__(self):
        self.scraper = EslitePetBooksScraper()
        self.books = []
        self.data_file = "pet_books_data.json"

    def load_existing_data(self):
        """載入已存在的資料"""
        import json

        # 尋找最新的 CSV 檔案
        csv_files = [f for f in os.listdir('.') if f.startswith('pet_books_') and f.endswith('.csv')]

        if not csv_files:
            print("找不到已存在的資料檔案")
            return False

        # 選擇最新的檔案
        latest_file = sorted(csv_files)[-1]
        print(f"載入檔案: {latest_file}")

        try:
            df = pd.read_csv(latest_file)
            self.books = []

            for _, row in df.iterrows():
                book = {
                    'title': row.get('書名', ''),
                    'author': row.get('作者', ''),
                    'price': row.get('價格', ''),
                    'category_str': row.get('分類', '其他'),
                    'url': row.get('連結', ''),
                    'image': row.get('圖片', '')
                }
                # 解析分類
                book['categories'] = book['category_str'].split(', ') if book['category_str'] else ['其他']
                self.books.append(book)

            print(f"成功載入 {len(self.books)} 本書籍")
            return True

        except Exception as e:
            print(f"載入失敗: {e}")
            return False

    async def collect_books(self):
        """收集書籍"""
        async with async_playwright() as p:
            print("\n正在啟動瀏覽器...")
            browser = await p.chromium.launch(headless=True)

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )

            page = await context.new_page()

            try:
                print("開始收集書籍...")
                self.books = await self.scraper.scrape_multiple_keywords(page)

                if self.books:
                    self.books = self.scraper.categorize_all_books(self.books)
                    self.scraper.print_summary(self.books)

                    # 自動儲存
                    self.scraper.export_to_excel(self.books)
                    self.scraper.export_to_csv(self.books)
                else:
                    print("未收集到任何書籍")

            finally:
                await browser.close()

    def show_statistics(self):
        """顯示統計資訊"""
        if not self.books:
            print("尚未載入任何書籍資料")
            return

        self.scraper.print_summary(self.books)

    def filter_and_show(self, category):
        """篩選並顯示特定分類的書籍"""
        if not self.books:
            print("尚未載入任何書籍資料")
            return

        if category == "全部":
            filtered = self.books
        else:
            filtered = [b for b in self.books if category in b.get('categories', [])]

        if not filtered:
            print(f"沒有找到【{category}】分類的書籍")
            return

        print(f"\n【{category}】書籍列表 (共 {len(filtered)} 本)")
        print("-"*60)

        for i, book in enumerate(filtered, 1):
            print(f"\n{i}. {book['title'][:50]}")
            if book.get('author'):
                print(f"   作者: {book['author']}")
            if book.get('price'):
                print(f"   價格: {book['price']}")
            print(f"   分類: {book.get('category_str', '其他')}")

            if i >= 20:
                remaining = len(filtered) - 20
                if remaining > 0:
                    print(f"\n... 還有 {remaining} 本書籍")
                break

    def export_category(self, category):
        """匯出指定分類的書籍"""
        if not self.books:
            print("尚未載入任何書籍資料")
            return

        if category == "全部":
            filtered = self.books
            filename = f"pet_books_全部_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        else:
            filtered = [b for b in self.books if category in b.get('categories', [])]
            filename = f"pet_books_{category}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"

        if not filtered:
            print(f"沒有【{category}】分類的書籍可匯出")
            return

        # 匯出
        export_data = []
        for book in filtered:
            export_data.append({
                "書名": book.get('title', ''),
                "作者": book.get('author', ''),
                "價格": book.get('price', ''),
                "分類": book.get('category_str', ''),
                "連結": book.get('url', ''),
            })

        df = pd.DataFrame(export_data)
        df.to_excel(filename, index=False, engine='openpyxl')
        print(f"已匯出 {len(filtered)} 本書籍到: {filename}")


async def main():
    """主程式"""
    manager = InteractiveBookManager()

    while True:
        clear_screen()
        print_menu()

        choice = input("請輸入選項 (1-6): ").strip()

        if choice == '1':
            print("\n即將開始收集書籍，這可能需要幾分鐘...")
            await manager.collect_books()
            input("\n按 Enter 繼續...")

        elif choice == '2':
            manager.load_existing_data()
            input("\n按 Enter 繼續...")

        elif choice == '3':
            manager.show_statistics()
            input("\n按 Enter 繼續...")

        elif choice == '4':
            categories = print_categories_menu()
            try:
                cat_choice = int(input("\n請選擇分類 (輸入數字): ")) - 1
                if 0 <= cat_choice < len(categories):
                    manager.filter_and_show(categories[cat_choice])
            except ValueError:
                print("無效的選擇")
            input("\n按 Enter 繼續...")

        elif choice == '5':
            categories = print_categories_menu()
            try:
                cat_choice = int(input("\n請選擇要匯出的分類 (輸入數字): ")) - 1
                if 0 <= cat_choice < len(categories):
                    manager.export_category(categories[cat_choice])
            except ValueError:
                print("無效的選擇")
            input("\n按 Enter 繼續...")

        elif choice == '6':
            print("\n感謝使用，再見！")
            break

        else:
            print("無效的選項，請重新選擇")
            input("\n按 Enter 繼續...")


if __name__ == "__main__":
    asyncio.run(main())
