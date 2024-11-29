import os
import validators
import requests
from page_analyzer.repositories import Urls, Checks
from dotenv import load_dotenv
from urllib.parse import urlparse
from datetime import date
from flask import Flask
from flask import render_template
from flask import request
from flask import flash, get_flashed_messages
from flask import redirect
from flask import url_for


load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    url = {'url': ''}
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'index.html',
        messages=messages,
        url=url
    )


@app.route('/urls')
def urls_index():
    repo = Checks()
    urls = repo.get_url_with_last_check()
    return render_template(
        'urls.html',
        urls=urls,
    )


@app.route('/urls', methods=['POST'])
def index_post():
    repo = Urls()

    url = request.form.to_dict()
    is_valid = validators.url(url.get('url'))

    if not is_valid:
        flash('Некорректный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', url=url, messages=messages)

    parsed_url = urlparse(url.get('url'))
    name = f'{parsed_url.scheme}://{parsed_url.netloc}'
    created_at = date.today().isoformat()
    url = {
        'name': name,
        'created_at': created_at
    }
    url, status = repo.save(url)
    if status == 'success':
        flash('Страница успешно добавлена', 'success')
    elif status == 'exist':
        flash('Страница уже существует', 'info')

    return redirect(url_for('urls_show', id=url['id']))


@app.route('/urls/<id>')
def urls_show(id):
    urls_repo = Urls()
    checks_repo = Checks()
    url = urls_repo.find(id)
    checks = checks_repo.get_checks(id)
    messages = get_flashed_messages(with_categories=True)
    return render_template(
        'show.html',
        messages=messages,
        url=url,
        checks=checks
    )

@app.route('/urls/<id>/checks', methods=['POST'])
def url_check(id):
    urls_repo = Urls()
    checks_repo = Checks()
    url = urls_repo.find(id)

    response = requests.get(url['name'])
    try: 
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        flash('Произошла ошибка при проверке', 'danger')
        return redirect(url_for('urls_show', id=id))
    else:
        html = response.text
        code = response.status_code
        # Временная заглушка
        _ = ''

        created_at = date.today().isoformat()
        check = {
            'url_id': id,
            'code': code,
            'h1': _,
            'title': _,
            'description': _,
            'created_at': created_at
            }
        checks_repo.save(check)
        flash('Страница успешно проверена', 'success')
        return redirect(url_for('urls_show', id=id))