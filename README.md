# Journalert

This script will read a list of RSS feeds, check for articles published in the last 24 hours and send an email with links to them. I run this as a cron job to check feeds from academic journals, hence the name.

# Dependencies

* feedparser

# Usage

* Fill out `config.py`:
	- `feeds` is a tuple of RSS feed URLs, for example `("https://www.science.org/action/showFeed?type=axatoc&feed=rss&jc=science", "http://feeds.nature.com/nature/rss/current")`.
	- `no_pubdate` is the same, but reserved for feeds lacking a pubDate tag, such as [this one](http://rss.sciencedirect.com/publication/science/0959440X).

* Run `journalert.py`.
