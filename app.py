from initialize import init
from scrape import scrape


def run():
    init("recipes")
    scrape("recipes")


if __name__ == "__main__":
    run()
