import string

from bayes import NaiveBayesClassifier
from bottle import redirect, request, route, run, template
from db import News, session
from scraputils import get_news


@route("/")  # корень
def root():
    redirect("/news")


@route("/news")  # неразмеченные новости(новости, у которых нет оценки)
def news_list():
    s = session()
    rows = s.query(News).filter(News.label == None).all()
    return template("news_template", rows=rows)


@route("/add_label/")
def add_label():
    label = request.GET.get("label")
    news_id = request.GET.get("id")

    s = session()
    news = s.query(News).get(news_id)

    if news:
        news.label = label
        s.commit()
    redirect("/news")


@route("/update")
def update_news():
    news_pack = get_news(url="https://news.ycombinator.com/newest", n_pages=1)
    s = session()

    for news in news_pack:
        existing_news = (
            s.query(News)
            .filter(
                News.title == news["title"],
                News.author == news["author"],
                News.url == news["url"],
                News.comments == news["comments"],
                News.points == news["points"],
            )
            .first()
        )

        if not existing_news:
            new_news = News(
                title=news["title"],
                author=news["author"],
                url=news["url"],
                comments=news["comments"],
                points=news["points"],
            )
            s.add(new_news)
            s.commit()

    redirect("/news")


@route("/classify")
def classify_news():
    def clean(s):
        translator = str.maketrans("", "", string.punctuation)
        return s.translate(translator)

    s = session()
    model = NaiveBayesClassifier()
    news_without_label = s.query(News).filter(News.label == None).all()
    news_with_label = s.query(News).filter(News.label != None).all()

    X = [news_l.title for news_l in news_with_label]
    X = [clean(x).lower() for x in X]
    y = [news_l.label for news_l in news_with_label]
    X_test = [news.title for news in news_without_label]
    X_test = [clean(x).lower() for x in X_test]

    model.fit(X, y)
    predictions = model.predict(X_test)

    classified_news = [
        (news, prediction) for news, prediction in zip(news_without_label, predictions) if news.label is None
    ]

    label_order = {"good": 0, "maybe": 1, "never": 2}
    classified_news = sorted(
        classified_news,
        key=lambda x: label_order[x[1]],
    )
    result_news = []
    for news in classified_news:
        result_news.append(news[0])

    return template('news_template', rows=result_news)


if __name__ == "__main__":
    run(host="localhost", port=8080)