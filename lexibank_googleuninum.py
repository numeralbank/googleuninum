from pathlib import Path
from shutil import rmtree

import attr
from git import Repo
from pylexibank import Language
from pylexibank.dataset import Dataset as BaseDataset
from pylexibank.util import pb


@attr.s
class UniNumLanguage(Language):
    Code = attr.ib(default=None)
    Script = attr.ib(default=None)
    Locale = attr.ib(default=None)
    Ethnologue = attr.ib(default=None)
    Variety = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = Path(__file__).parent
    id = "googleuninum"
    language_class = UniNumLanguage

    def cmd_download(self, args):
        # We need to clone into a folder in raw/ to avoid git shenanigans.
        p = self.raw_dir / "uninumrepo"

        if p:
            rmtree(p, ignore_errors=True)

        Repo.clone_from("https://github.com/google/uninum.git", p, depth=1, branch="master")
        rmtree(p / ".git", ignore_errors=True)

    def cmd_makecldf(self, args):
        languages, concepts = {}, {}
        numbers = list((self.raw_dir / "uninumrepo" / "numbers/").glob("**/*.tsv"))

        for language in self.languages:
            args.writer.add_language(
                ID=language["Code"],
                Name=language["Language name(s)"],
                Glottocode=language["Glottocode"],
                ISO639P3code=language["ISO 639-3"],
                Script=language["Script"],
                Locale=language["Locale"],
                Ethnologue=language["Ethnologue"],
                Variety=language["Variety"],
            )
            languages[language["Code"]] = language["Language name(s)"]

        for concept in self.concepts:
            args.writer.add_concept(
                ID=concept["GLOSS"],
                Name=concept["GLOSS"],
                Concepticon_ID=concept["CONCEPTICON_ID"],
                Concepticon_Gloss=concept["CONCEPTICON_GLOSS"],
            )
            concepts[concept["GLOSS"]] = concept["GLOSS"]

        for number_file in pb(numbers, desc=""):
            lcode = number_file.name.split(".tsv")[0]

            # TODO: Arabic etc?
            if lcode not in languages:
                break

            f = self.raw_dir.read_csv(number_file, delimiter="\t")
            for entry in f:
                # entry[0] is the concept.
                # entry[1] is the lexeme.
                if entry[0] not in concepts:  # TODO: Change after concept list has been added.
                    break
                args.writer.add_lexemes(
                    Language_ID=lcode, Parameter_ID=concepts[entry[0]], Value=entry[1]
                )
