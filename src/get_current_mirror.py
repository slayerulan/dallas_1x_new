from requests_html import HTMLSession


def get_current_mirror(session):
    """
    Returns current available mirror of the 1xbet.com, 
    first try to redirects, if fails, try to use google
    """
    url = 'https://1xstavka.ru'
    try:
        return session.get('https://1xstavka.ru', timeout=10).url.split('?')[0]
    except Exception as e:
        url = 'https://www.google.ru/search?&q=1xbet.com'
        try:
            r = session.get(url, timeout=10)
        except Exception as e:
            raise ValueError("Can't find mirror")
        return f"https://{r.html.search('⇒ {} ⇒')[0]}"
