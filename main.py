import re
from playwright.sync_api import sync_playwright
from time import sleep


def main(category_link, seller_year, prod_counter):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()
        page.goto(category_link)

        element = page.locator('[data-testid="listing-grid"]')
        links = element.evaluate('(element) => Array.from(element.querySelectorAll("a"), a => a.href)')

        for link in links[:30]:
            print(f'Parsing link: {link}')
            
            page.goto(link)

            try:
                for i in range(1, 10):
                    page.evaluate('window.scrollTo(0, window.scrollY + 200)')
                    sleep(0.5)

                text_element = page.locator('[data-testid="page-view-text"]')
                created_element = page.locator('[data-cy="ad-posted-at"]')
                user_profile_link_element = page.locator('a[data-testid="user-profile-link"]').nth(0)
                reg_element = user_profile_link_element.get_by_text('Na OLX')

                if text_element.is_visible():
                    text_content = text_element.inner_text()
                    created_text = created_element.inner_text()
                    reg_date_text = int(reg_element.inner_text().split(" ")[-1])

                    if reg_date_text >= seller_year:

                        print(f'Views: {text_content}')
                        print(f'Created at: {created_text}')
                        print(f'Reg. date: {reg_date_text}')

                        if user_profile_link_element.is_visible():
                            user_profile_link = user_profile_link_element.get_attribute('href')
                            print(f'User profile link: {user_profile_link}')

                            page.goto(f'https://www.olx.pl{user_profile_link}')
                            sleep(0.5)
                            for i in range(1, 3):
                                page.evaluate('window.scrollTo(0, window.scrollY + 200)')
                                sleep(0.5)

                            results_counter_element = page.locator('h6[data-testid="results-counter"]')

                            results_counter_text = results_counter_element.inner_text()
                            match = re.search(r'\d+', results_counter_text)

                            if match:
                                results_counter_value = int(match.group())
                                if results_counter_value <= prod_counter:
                                    print(f'Product Counter: {results_counter_value}\n')
                                    print("DATA WAS SUCCESSFULLY WRITED")
                                    with open("result.txt", 'a+', encoding='utf-8') as f:
                                        f.write(f"Views: {text_content}\n"
                                                f"Created at: {created_text}\n"
                                                f"Reg. date: {reg_date_text}\n"
                                                f"User profile link: https://www.olx.pl{user_profile_link}\n"
                                                f"Product Counter: {results_counter_value}\n\n")
                                else:
                                    continue
                            else:
                                print('No numeric value found in the results counter element.')

                        else:
                            print('User profile link not found on the page.')
                    else:
                        print("[SKIP] Bad reg date")
                        continue
                else:
                    print("[SKIP] Can't find some elements.")
                    continue

            except Exception as e:
                print(f'[Error]: {e}. Element not found after scrolling. Moving to the next page.')

        browser.close()


if __name__ == '__main__':
    # https://www.olx.pl/moda/
    link = input("Enter category link: ")
    seller_year = int(input("Enter seller year: "))
    product_count = int(input("Enter min. product count: "))
    main(category_link=link, seller_year=seller_year, prod_counter=product_count)
