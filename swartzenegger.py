import requests as req
import sys
from collections import namedtuple
from lxml import html
from slugify import slugify

base_url = "https://link.springer.com"
discipline_url = "{0}{1}&facet-content-type=\"Book\"&showAll=false"

Discipline = namedtuple("Discipline", ["name", "url"])
Book = namedtuple("Book", ["discipline", "title", "url"])


def get_disciplines():
    resp = req.get(base_url)
    tree = html.fromstring(resp.content)
    disciplines = tree.xpath("//ol[@class='disciplines']/li/a")
    return [Discipline(name=e.text, url=discipline_url.format(base_url, e.get("href"))) for e in disciplines]


def get_books(discipline):
    books = list()
    next_url = discipline.url
    while True:
        resp = req.get(next_url)
        tree = html.fromstring(resp.content)
        for book in tree.xpath("//ol[@id='results-list']/li/div[@class='text']/h2/a[@class='title']"):
            books.append(
                Book(discipline=discipline.name, title=book.text, url=base_url + book.get("href")))
        next_url = tree.xpath(
            "//div[contains(@class, 'top')]/form[@class='pagination']/a[@class='next']/@href")
        if not next_url:
            break
        next_url = base_url + next_url[0]
    return books


def download_book(book):
    resp = req.get(book.url)
    tree = html.fromstring(resp.content)
    url = tree.xpath("//a[@title='Download this book in PDF format']/@href")
    pdf_resp = req.get(base_url + url[0])
    with open("{0}.pdf".format(slugify(book.title)), "wb") as f:
        f.write(pdf_resp.content)


def main():
    disciplines = get_disciplines()
    disciplines.append(Discipline(name="All", url=None))
    print("\nAvailable Disciplines:")
    print("\n".join("[{1:2d}] {0}".format(d.name, i)
                    for i, d in enumerate(disciplines)))
    try:
        selected_disciplines = [int(n) for n in input(
            "selections (csv): ").split(",")]
        if any(s < 0 or s >= len(disciplines) for s in selected_disciplines):
            sys.exit("invalid selection")
    except ValueError:
        sys.exit("invalid selection")

    books = list()
    if len(disciplines)-1 in selected_disciplines:
        selected_disciplines = range(len(disciplines)-1)
    for s in selected_disciplines:
        books += get_books(disciplines[s])
    books.append(Book(discipline="All Disciplines",
                      title="All Books", url=None))

    print("\nAvailable Books:")
    print("\n".join("[{2:2d}] {0}: {1}".format(b.discipline, b.title, i)
                    for i, b in enumerate(books)))
    try:
        selected_books = [int(n)
                          for n in input("selections (csv): ").split(",")]
        if any(s < 0 or s >= len(books) for s in selected_books):
            sys.exit("invalid selection")
    except ValueError:
        sys.exit("invalid selection")

    if len(books)-1 in selected_books:
        selected_books = range(len(books)-1)
    for s in selected_books:
        download_book(books[s])


if __name__ == "__main__":
    main()
