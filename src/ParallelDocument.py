from src.util import *


class ParallelDocument:

    def __init__(self, url: str, langs: List[str], main_lang: str = "es"):
        self.url = url
        self.langs = langs
        self.main_lang = main_lang
        self.df: pd.DataFrame = pd.DataFrame()

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
            sleep(1)
        except NoSuchElementException:
            logging.warning(f"Language {lang} not found in parallel document {self.url}")

    def get_text_by_lang(self, lang: str, driver: webdriver) -> List[str]:
        parallel_text = []
        self.go_to_lang(lang, driver)
        p_list = driver.find_elements(By.XPATH, ".//*[boolean(number(substring-after(@id, 'p')))]")
        q_list = driver.find_elements(By.XPATH, ".//*[boolean(number(substring-after(@id, 'q')))]")
        if len(p_list) == 0 and len(q_list) == 0:
            logging.warning(f"Language {lang} not found in parallel document {self.url}")
            return []

        for idx, p in enumerate(p_list):
            parallel_text.append(p.text)

        for idx, q in enumerate(q_list):
            parallel_text.append(q.text)

        return parallel_text

    def get_parallel_texts(self, driver) -> pd.DataFrame:
        self.df = pd.DataFrame({lang: self.get_text_by_lang(lang, driver) for lang in self.langs})
        return self.df

    def save_dataframe(self) -> None:
        self.df.to_csv(f"{self.url}.csv")

