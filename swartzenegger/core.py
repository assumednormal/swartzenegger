import requests as req
from lxml import html

home_url = "https://link.springer.com"
home_resp = req.get(home_url)
home_tree = html.fromstring(home_resp.content)
disciplines = home_tree.xpath("//ol[@class='disciplines']/li/a/@href")


def get_books(discipline):
    books = list()
    url = home_url + discipline + "&facet-content-type=\"Book\"&showAll=false"
    while True:
        resp = req.get(url)
        tree = html.fromstring(resp.content)
        next_url = tree.xpath(
            "//div[contains(@class, 'top')]/form[@class='pagination']/a[@class='next']/@href")
        books += tree.xpath(
            "//ol[@id='results-list']/li/div[@class='text']/h2/a[@class='title']/@href")
        if next_url:
            url = home_url + next_url[0]
        else:
            break
    return books


books = get_books(disciplines[0])


def get_book_pdf(book):
    resp = req.get(home_url + book)
    tree = html.fromstring(resp.content)
    pdf_url = tree.xpath(
        "//a[@title='Download this book in PDF format']/@href")
    pdf = req.get(home_url + pdf_url[0])
    with open("x.pdf", "wb") as f:
        f.write(pdf.content)
