import os
from datetime import date

import requests
import requests.exceptions
import validators
from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer.parser import parse_response, parse_url
from page_analyzer.repositories import Page

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
db_url = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template(
        'index.html',
        url={}
    )


@app.route('/urls')
def urls_index():
    page_repo = Page(db_url)
    urls = page_repo.get_urls()
    checks = page_repo.get_last_check()
    url_with_last_check = {}

    for url in urls:
        url_with_last_check[url['id']] = url

    for check in checks:
        if check['url_id'] in url_with_last_check:
            url_with_last_check[check['url_id']].update({
                'last_check': check['last_check'],
                'status_code': check['status_code']
            })
        else:
            url_with_last_check[check['url_id']] = {
                'last_check': check['last_check'],
                'status_code': check['status_code']
            }
    urls = list(url_with_last_check.values())
    page_repo.close()

    return render_template(
        'urls.html',
        urls=urls
    )


@app.route('/urls', methods=['POST'])
def urls_index_post():
    page_repo = Page(db_url)

    url = request.form.to_dict().get('url')
    is_valid = validators.url(url)

    if not is_valid:
        flash('Некорректный URL', 'danger')
        return render_template('index.html', url=url), 422

    name = parse_url(url)
    created_at = date.today().isoformat()

    urls = page_repo.find_url_by_name(name)
    if urls:
        flash('Страница уже существует', 'info')
        url_id = urls[0].get('id')
    else:
        url = {
            'name': name,
            'created_at': created_at
        }
        url_id = page_repo.create_url(url)
        page_repo.commit()

        flash('Страница успешно добавлена', 'success')
    page_repo.close()
    return redirect(url_for('urls_show', url_id=url_id))


@app.route('/urls/<url_id>')
def urls_show(url_id):
    page_repo = Page(db_url)
    url = page_repo.find_url(url_id)
    checks = page_repo.get_checks(url_id)
    page_repo.close()
    return render_template(
        'url.html',
        url=url,
        checks=checks
    )


@app.route('/urls/<url_id>/checks', methods=['POST'])
def url_check(url_id):
    page_repo = Page(db_url)
    url = page_repo.find_url(url_id)

    try:
        response = requests.get(url['name'])
        response.raise_for_status()
    except (
        requests.exceptions.HTTPError,
        requests.exceptions.ConnectionError
    ):
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('urls_show', url_id=url_id))
    else:
        tags = parse_response(response)
        check = {
            'url_id': url_id,
            'status_code': response.status_code,
            'h1': tags.get('h1', ''),
            'title': tags.get('title', ''),
            'description': tags.get('description', ''),
            'created_at': date.today().isoformat()
        }
        page_repo.create_check(check)
        page_repo.commit()
        page_repo.close()
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('urls_show', url_id=url_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500