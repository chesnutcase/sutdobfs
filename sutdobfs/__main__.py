import argparse
import tokenize
import re
import typing
import pkgutil
import io
from sutdobfs import gatekeepers
from sutdobfs import providers


class Obfuscator:
    def obfuscate(self, source: typing.IO, output: typing.IO, provider):
        output_tokens = []
        gatekeeper = gatekeepers.SafeGatekeeper()
        offset = 0
        encoding = None
        for token in tokenize.tokenize(source.readline):
            if token.type == tokenize.ENCODING:
                encoding = token.string
            if token.type == tokenize.NAME and token.string[0].lower() == "f":
                inner_source = io.StringIO()
                self.obfuscate()
            if gatekeeper.read(token):
                meme = provider.meme(token.string)
                sub_offset = len(meme) - len(token.string)
                output_tokens.append(
                    (
                        tokenize.NAME,
                        meme,
                        (token.start[0], token.start[1] + offset),
                        (token.end[0], token.end[1] + offset + sub_offset),
                        token.line,
                    )
                )
                offset += sub_offset
            else:
                output_tokens.append(
                    (
                        token.type,
                        token.string,
                        (token.start[0], token.start[1] + offset),
                        (token.end[0], token.end[1] + offset),
                        token.line,
                    )
                )
            if token.type == tokenize.NEWLINE:
                offset = 0
        output.write(tokenize.untokenize(output_tokens).decode(encoding))


def main():
    parser = argparse.ArgumentParser(
        description="Obfuscates variables in collaboration with MIT."
    )

    parser.add_argument(
        "input_file", type=argparse.FileType("rb"), help="the Python file to obfuscate"
    )

    parser.add_argument(
        "-o",
        "--output-file",
        type=argparse.FileType("w"),
        required=False,
        help="the destination file",
    )

    parser.add_argument(
        "-r",
        "--random",
        action="store_true",
        required=False,
        help="makes the obfuscation process non deterministic",
    )

    parser.add_argument(
        "-d",
        "--dictionary-file",
        type=argparse.FileType("r"),
        required=False,
        help="custom dictionary file for retrieving replacement names in obfuscation",
    )

    args = vars(parser.parse_args())

    input_file = args.get("input_file")
    output_file = args.get("o") or open(
        re.sub(r"\.py$", ".sutd.py", input_file.name), "w"
    )
    dictionary_file = args.get("d") or io.StringIO(
        pkgutil.get_data("sutdobfs", "memes.txt").decode("utf-8")
    )

    memes = [
        line.strip()
        for line in dictionary_file.readlines()
        if str.isidentifier(line.strip())
    ]

    provider = providers.ConsistentProvider(memes)

    obfs = Obfuscator()

    obfs.obfuscate(input_file, output_file, provider)

    input_file.close()
    output_file.close()

    return 0


if __name__ == "__main__":
    code = main()
    exit(code)