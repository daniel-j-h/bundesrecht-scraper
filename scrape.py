#!/usr/bin/env python3

import sys
import time
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.error import URLError
from xml.etree import ElementTree

kTocXmlUrl = "https://www.gesetze-im-internet.de/gii-toc.xml"
kTocDtdUrl = "https://www.gesetze-im-internet.de/dtd/1.0/gii-toc.dtd"
kNormDtdUrl = "https://www.gesetze-im-internet.de/dtd/1.0/gii-norm.dtd"


def main():
    datadir = Path("data")
    datadir.mkdir(exist_ok=True)

    tocXmlPath = datadir / "gii-toc.xml"
    tocDtdPath = datadir / "gii-toc.dtd"
    normDtdPath = datadir / "gii-norm.dtd"

    sync(tocXmlPath, kTocXmlUrl)
    sync(tocDtdPath, kTocDtdUrl)
    sync(normDtdPath, kNormDtdUrl)

    tree = ElementTree.parse(tocXmlPath)
    items = list(tree.iter("item"))

    t0 = time.time()

    for i, item in enumerate(items):
        title = item.find("title").text
        link = item.find("link").text

        url = urlparse(link)

        # http://www.gesetze-im-internet.de/ksg/xml.zip
        assert url.netloc == "www.gesetze-im-internet.de"
        assert url.path[0] == "/"

        path = Path(url.path[1:])
        assert path.name == "xml.zip"

        # ksg
        subdir = path.parent.name

        outdir = datadir / Path(subdir)
        outdir.mkdir(exist_ok=True)

        # low key rate limiting to play nice
        t1 = time.time()
        dt = max(t1 - t0, 0)

        if (dt < 0.1):
            time.sleep(0.1 - dt)

        zipdata = fetch(f"https://{url.netloc}/{subdir}/xml.zip")

        t0 = time.time()

        # TODO: we should decouple fetching from extracting and writing
        # the extracted files to disk, since the gh runner seems to have
        # a relatively slow file system; look into this to speed it up
        with ZipFile(BytesIO(zipdata)) as zipfile:
            zipfile.extractall(outdir)

        print(f"{i+1:4} {len(items):4} {subdir}", file=sys.stderr)


def fetch(url, timeout=10):
    with urlopen(url, timeout=timeout) as f:
        return f.read()


def sync(dst, url, timeout=10):
    return dst.write_bytes(fetch(url, timeout=timeout))


if __name__ == "__main__":
    main()
