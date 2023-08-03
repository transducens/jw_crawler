from src.util import *


class ParallelDocument:

    def __init__(self, url: str, langs: List[str], main_lang: str = "es"):
        self.url = url
        self.langs = langs
        self.main_lang = main_lang

    def go_to_lang(self, lang: str, driver: webdriver) -> None:
        if driver.current_url != self.url:
            driver.get(self.url)

        try:
            language_input = driver.find_element(By.XPATH, ".//input[@id='otherAvailLangsChooser']")
            language_input.clear()
            language_input.send_keys(lang)
            driver.find_element(By.XPATH, f".//li[@data-value='{lang}']")
            sleep(1)
            language_input.send_keys(Keys.ENTER)
        except NoSuchElementException:
            logging.warning(f"Language {lang} not found in parallel document {self.url}")
