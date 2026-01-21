#!/usr/bin/env python3
"""
誠品寵物書籍 - 新書通知腳本
定期檢查是否有新書上架，並發送 Email 通知
"""

import asyncio
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# 設定
PET_CATEGORY_URL = "https://www.eslite.com/category/3/123"
DATA_FILE = "previous_books.json"

# Email 設定 (從環境變數讀取)
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SENDER_EMAIL = os.environ.get("SENDER_EMAIL", "")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD", "")  # Gmail 應用程式密碼
RECIPIENT_EMAIL = os.environ.get("RECIPIENT_EMAIL", "")


async def get_total_pages(page) -> int:
    """取得總頁數"""
    try:
        pagination = await page.query_selector_all('.pagination button, .pagination a')
        max_page = 1
        for btn in pagination:
            text = await btn.inner_text()
            if text.isdigit():
                max_page = max(max_page, int(text))
        return max_page
    except Exception:
        return 1


async def scrape_books_from_page(page) -> list:
    """從當前頁面抓取書籍資料"""
    books = []

    await page.wait_for_selector('.product-card, [class*="product"]', timeout=15000)
    await asyncio.sleep(2)

    product_cards = await page.query_selector_all('.product-card')

    for card in product_cards:
        try:
            # 書名
            name_el = await card.query_selector('.product-name')
            name = await name_el.inner_text() if name_el else ""

            # 作者
            author_el = await card.query_selector('.product-author')
            author = await author_el.inner_text() if author_el else ""

            # 售價
            price_el = await card.query_selector('.slider-price')
            price = await price_el.inner_text() if price_el else ""
            price = price.replace('$', '').replace(',', '').strip() if price else ""

            # 連結
            link_el = await card.query_selector('a')
            link = await link_el.get_attribute('href') if link_el else ""
            if link and not link.startswith('http'):
                link = f"https://www.eslite.com{link}"

            # 圖片
            img_el = await card.query_selector('img')
            img_src = await img_el.get_attribute('src') if img_el else ""

            if name:
                books.append({
                    'name': name.strip(),
                    'author': author.strip(),
                    'price': price,
                    'link': link,
                    'image': img_src
                })
        except Exception as e:
            continue

    return books


async def scrape_all_books() -> list:
    """抓取所有書籍"""
    all_books = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        )
        page = await context.new_page()

        print(f"正在載入第一頁...")
        await page.goto(PET_CATEGORY_URL, wait_until='domcontentloaded', timeout=60000)
        await asyncio.sleep(3)

        max_pages = await get_total_pages(page)
        print(f"共 {max_pages} 頁")

        current_page = 1
        while current_page <= max_pages:
            if current_page > 1:
                url = f"{PET_CATEGORY_URL}?page={current_page}"
                print(f"正在抓取第 {current_page}/{max_pages} 頁...")
                await page.goto(url, wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(2)

            books = await scrape_books_from_page(page)
            all_books.extend(books)
            print(f"  已收集 {len(books)} 本，累計 {len(all_books)} 本")

            current_page += 1

        await browser.close()

    return all_books


def load_previous_books() -> dict:
    """載入上次的書籍資料"""
    if Path(DATA_FILE).exists():
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'books': [], 'last_check': None}


def save_current_books(books: list):
    """儲存當前書籍資料"""
    data = {
        'books': books,
        'last_check': datetime.now().isoformat()
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def find_new_books(current_books: list, previous_books: list) -> list:
    """找出新書"""
    previous_names = {book['name'] for book in previous_books}
    new_books = [book for book in current_books if book['name'] not in previous_names]
    return new_books


def send_email(new_books: list):
    """發送新書通知 Email"""
    if not all([SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL]):
        print("Email 設定不完整，跳過發送")
        print("新書清單：")
        for book in new_books:
            print(f"  - {book['name']} ({book['author']})")
        return False

    # 建立郵件
    msg = MIMEMultipart('alternative')
    msg['Subject'] = f'📚 誠品寵物書籍新書通知 - {len(new_books)} 本新書上架！'
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL

    # 純文字版本
    text_content = f"誠品寵物書籍有 {len(new_books)} 本新書上架！\n\n"
    for book in new_books:
        text_content += f"書名：{book['name']}\n"
        text_content += f"作者：{book['author']}\n"
        text_content += f"售價：${book['price']}\n"
        text_content += f"連結：{book['link']}\n\n"

    # HTML 版本
    html_content = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 20px; }}
            h1 {{ color: #667eea; }}
            .book-card {{ border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 15px 0; display: flex; gap: 15px; }}
            .book-card img {{ width: 80px; height: 120px; object-fit: cover; border-radius: 4px; }}
            .book-info h3 {{ margin: 0 0 8px 0; color: #333; }}
            .book-info p {{ margin: 4px 0; color: #666; font-size: 14px; }}
            .price {{ color: #e53935; font-weight: bold; font-size: 18px; }}
            .btn {{ display: inline-block; background: #667eea; color: white; padding: 8px 16px; border-radius: 5px; text-decoration: none; margin-top: 10px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 誠品寵物書籍新書通知</h1>
            <p>有 <strong>{len(new_books)}</strong> 本新書上架！</p>
    """

    for book in new_books:
        html_content += f"""
            <div class="book-card">
                <img src="{book['image']}" alt="{book['name']}" onerror="this.style.display='none'">
                <div class="book-info">
                    <h3>{book['name']}</h3>
                    <p>作者：{book['author']}</p>
                    <p class="price">${book['price']}</p>
                    <a href="{book['link']}" class="btn">前往購買</a>
                </div>
            </div>
        """

    html_content += """
            <p style="color: #999; font-size: 12px; margin-top: 30px;">
                此郵件由誠品寵物書籍新書通知系統自動發送
            </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))

    # 發送郵件
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print(f"✅ Email 已發送至 {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Email 發送失敗: {e}")
        return False


async def main():
    print("=" * 50)
    print("誠品寵物書籍 - 新書檢查")
    print(f"時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

    # 載入上次資料
    previous_data = load_previous_books()
    previous_books = previous_data.get('books', [])
    last_check = previous_data.get('last_check', '從未檢查')
    print(f"上次檢查: {last_check}")
    print(f"上次書籍數: {len(previous_books)}")

    # 抓取當前書籍
    print("\n正在抓取最新書籍資料...")
    current_books = await scrape_all_books()
    print(f"當前書籍數: {len(current_books)}")

    # 比對新書
    if previous_books:
        new_books = find_new_books(current_books, previous_books)
        print(f"\n🆕 發現 {len(new_books)} 本新書")

        if new_books:
            print("\n新書清單:")
            for i, book in enumerate(new_books, 1):
                print(f"  {i}. {book['name']}")
                print(f"     作者: {book['author']}")
                print(f"     售價: ${book['price']}")

            # 發送 Email
            send_email(new_books)
        else:
            print("沒有新書上架")
    else:
        print("\n首次執行，建立基準資料")

    # 儲存當前資料
    save_current_books(current_books)
    print(f"\n✅ 資料已更新，共 {len(current_books)} 本書")


if __name__ == "__main__":
    asyncio.run(main())
