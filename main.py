from flask import Flask, render_template, request
from processing import text_summarization
from processing import get_title_from_VNE
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+os.path.join(basedir, 'data.sqlite')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)

class URLS(db.Model):
    __tablename__ = 'urls'
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text)

    def __init__(self, url):
        self.url = url

    def __repr__(self):
        return f"{self.url}"

db.create_all()

raw_url = ""
final_summary = ""
header = ""

@app.route('/')
def main():
    urls = URLS.query.all()
    return render_template('index.html', urls=urls)

@app.route('/tom-tat', methods=['GET', 'POST'])
def text_summarizer():
    if request.method == 'POST':
        raw_url = request.form['url']
        header = get_title_from_VNE(raw_url)
        final_summary = text_summarization(raw_url)
        db.session.add(URLS(raw_url))
        db.session.commit()
        urls = URLS.query.all()
        return render_template('index.html', urls=urls, header=header, final_summary=final_summary)

@app.route('/xoa', methods=['GET', 'POST'])
def delete_history():
    if request.method == 'POST':
        row_exists = bool(db.session.query(URLS).first())
        urls = ""
        if row_exists:
            db.session.query(URLS).delete()
            db.session.commit()
        return render_template('index.html', urls=urls, header=header, final_summary=final_summary)

if __name__ == '__main__':
    app.run(debug=True)