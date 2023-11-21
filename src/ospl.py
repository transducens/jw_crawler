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
        for lang in self.langs:
            os.mkdir(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}")

        for df_file in os.listdir(f"{self.working_dir}/dataframes"):
            df = pd.read_csv(f"{self.working_dir}/dataframes/{df_file}", sep="\t", index_col=0)
            for lang in [lang for lang in df.columns if lang != self.main_lang]:

                ls_lang = list(df[lang])
                ls_lang = [str(w).replace('\n', " ") for w in ls_lang]
                ls_main_lang = list(df[self.main_lang])
                ls_main_lang = [str(w).replace('\n', " ") for w in ls_main_lang]
                assert len(ls_lang) == len(ls_main_lang), f"ERROR: Dataframe '{df_file}' contains mismatch length"
                assert "" not in ls_lang, f"ERROR: Blank entry in dataframe '{df_file}'"
                assert "" not in ls_main_lang, f"ERROR: Blank entry in dataframe '{df_file}'"

                if not os.path.exists(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}"):
                    os.mkdir(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}")

                with open(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}/data.{self.main_lang}",
                          "a") as f:
                    f.writelines(p + '\n' for p in ls_main_lang)

                with open(f"{self.working_dir}/text_{self.main_lang}/{self.main_lang}_{lang}/data.{lang}", "a") as f:
                    f.writelines(p + '\n' for p in ls_lang)
