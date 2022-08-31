from tkinter import W
import pytest
import httpx
import datetime
import pathlib
import json
import engine

from newsletter import (
    get_publish_time,
    schedule_email_from_post,
    get_show_file,
    build_email_from_content,
    get_newsletter_issues,
)


def test_shownotes_date_creation(date, time):
    """Given a date and time, return the publish time for the email in datetime format"""
    assert get_publish_time(date, time) == datetime.datetime.combine(date, time)
    

def test_shownotes_file(date, time, tmp_path):
    """Given the date, time, and temporary_path return the filepath"""
    publish_date = datetime.datetime.combine(date, time)
    assert get_show_file('fake_directory', publish_date) == pathlib.Path('fake_directory') / pathlib.Path(publish_date.strftime("%Y-%m-%d") + ".md")


def test_shownotes_content(shownotes_text, newsletter_body, tmp_path):
    """Given the shownotes_text, return the body of the email"""
    filepath = tmp_path / pathlib.Path('test_path.md')
    filepath.write_text(shownotes_text)
    assert build_email_from_content(filepath) == newsletter_body


def test_shownotes_request_from_file(
    httpx_mock, 
    newsletter_body,
    date,
    time,
):
    publish_date = datetime.datetime.combine(date, time)
    httpx_mock.add_response()
    publish_date = datetime.datetime.combine(date, time)

    with httpx.Client() as _:
        request = schedule_email_from_post(newsletter_body, publish_date=publish_date)
        content = bytes.decode(httpx_mock.get_requests()[0]._content, 'utf-8')
        assert json.loads(content) == newsletter_body


def test_newsletter_template_exists():
    assert 'newsletter.md' in engine.engine.list_templates()


def test_malformed_newsletter_issue_raises_issue():
    bad_issue = """### Issue Name
There's no issues in here
"""
    with pytest.raises(ValueError):
        get_newsletter_issues(bad_issue, 'Issue')


def test_valid_issue_returns_issue_list(issue_text):
    assert list(get_newsletter_issues(issue_text, 'Issues')) == [1,2,3,4]
