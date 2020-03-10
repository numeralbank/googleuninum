from pathlib import Path
from shutil import rmtree

import attr
from git import Repo
from pylexibank import Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import progressbar


@attr.s
class CustomLanguage(Language):
    Code = attr.ib(default=None)
    Script = attr.ib(default=None)
    Locale = attr.ib(default=None)
    Ethnologue = attr.ib(default=None)
    Variety = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "googleuninum"
    language_class = CustomLanguage

    def cmd_download(self, args):
        # We need to clone into a folder in raw/ to avoid git shenanigans.
        p = self.raw_dir / "uninumrepo"

        if p:
            rmtree(p, ignore_errors=True)

        Repo.clone_from("https://github.com/google/uninum.git", p, depth=1, branch="master")
        rmtree(p / ".git", ignore_errors=True)

    def cmd_makecldf(self, args):
        languages = []
        number_files = sorted(list((self.raw_dir / "uninumrepo" / "numbers/").glob("**/*.tsv")))
        codes = self.raw_dir / "uninumrepo" / "codes.tsv"
        args.writer.add_sources()
        concepts = args.writer.add_concepts(id_factory=lambda c: c.english, lookup_factory="Name")

        for code in self.raw_dir.read_csv(codes, delimiter="\t", dicts=True):
            # We add additional Glottocodes based on languages.tsv wherever applicable:
            substitute = list(filter(lambda y: y["Code"] == code["Code"], self.languages))

            args.writer.add_language(
                ID=code["Code"],
                Name=code["Language name(s)"],
                Glottocode=substitute[0]["Glottocode"] if substitute else code["Glottocode"],
                ISO639P3code=code["ISO 639-3"],
                Script=code["Script"],
                Locale=code["Locale"],
                Ethnologue=code["Ethnologue"],
                Variety=code["Variety"],
            )
            languages.append(code["Code"])

        for number_file in progressbar(number_files):
            lcode = number_file.name.split(".tsv")[0]

            for entry in self.raw_dir.read_csv(number_file, delimiter="\t"):
                # entry[0] is the concept.
                # entry[1] is the lexeme.
                args.writer.add_lexemes(
                    Language_ID=lcode,
                    Parameter_ID=concepts[entry[0]],
                    Value=entry[1],
                    Source="Ritchie2019",
                )
