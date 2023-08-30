import os
import shutil

import pandas as pd
from typing import List


class OneSentencePerLine:

    def __init__(self,
                 working_dir: str,
                 langs: List[str],
                 main_lang: str):

        self.working_dir = working_dir
        self.langs = langs
        self.main_lang = main_lang

        if os.path.exists(self.working_dir) is False:
            raise FileNotFoundError(f"Working directory '{self.working_dir}' does not exist.")

    def create_ospl(self):

        if os.path.exists(f"{self.working_dir}/text_{self.main_lang}") is True:
            shutil.rmtree(f"{self.working_dir}/text_{self.main_lang}")

        os.mkdir(f"{self.working_dir}/text_{self.main_lang}")

        for df_file in os.listdir(f"{self.working_dir}/dataframes"):

            df = pd.read_csv(f"{self.working_dir}/dataframes/{df_file}", sep="\t", index_col=0)
            langs = [lang for lang in self.langs if lang in df.columns] if self.langs is not None else df.columns
            langs = [lang for lang in langs if lang != self.main_lang]

            for lang in langs:
                if not os.path.exists(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}"):
                    os.mkdir(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}")

                with open(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}/data.{self.main_lang}",
                          "a") as f:
                    for p in df[self.main_lang]:
                        paragraph = p.strip() if type(p) == str else p
                        f.write(str(paragraph) + "\n")

                with open(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}/data.{lang}", "a") as f:
                    for p in df[lang]:
                        paragraph = p.strip()  if type(p) == str else p
                        f.write(str(paragraph) + "\n")
