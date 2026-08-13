"""Test the directive options the 'httpdomain' renderer accepts."""

import textwrap

import pytest

from sphinxcontrib.openapi import renderers

_SPEC = """\
openapi: 3.0.0
info:
  title: An example spec.
  version: 1.0.0
paths:
  /evidences:
    get:
      responses:
        '200':
          description: An evidence.
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
"""


_WHITESPACE_DELIMITED_OPTIONS = [
    pytest.param("http-methods-order", "head get"),
    pytest.param("response-examples-for", "200 201 2XX 404"),
    pytest.param("request-parameters-order", "query path header cookie"),
    pytest.param("example-preference", "application/json text/plain"),
    pytest.param("request-example-preference", "application/json text/plain"),
    pytest.param("response-example-preference", "application/json text/plain"),
]


@pytest.mark.parametrize(["option", "value"], _WHITESPACE_DELIMITED_OPTIONS)
def test_option_is_accepted(tmpdir, run_sphinx, option, value):
    """A whitespace delimited option is not rejected as an unknown one."""

    tmpdir.join("src", "test-spec.yml").write_text(_SPEC, encoding="utf-8")
    warnings = run_sphinx(
        "test-spec.yml",
        options={option: value},
        renderer="httpdomain",
    )

    assert "unknown option" not in warnings


@pytest.mark.parametrize(["option", "value"], _WHITESPACE_DELIMITED_OPTIONS)
def test_option_is_parsed(option, value):
    """A whitespace delimited option is parsed into a list of tokens."""

    convertor = renderers.HttpdomainRenderer.option_spec[option]
    assert convertor(value) == value.split()


@pytest.mark.parametrize(["option", "value"], _WHITESPACE_DELIMITED_OPTIONS)
def test_option_without_value_is_parsed(option, value):
    """A whitespace delimited option may be passed with no value at all."""

    convertor = renderers.HttpdomainRenderer.option_spec[option]
    assert convertor(None) == []


def test_response_examples_for_is_effective(tmpdir, run_sphinx):
    """The 'response-examples-for' option reaches the renderer."""

    tmpdir.join("src", "test-spec.yml").write_text(
        textwrap.dedent("""\
            openapi: 3.0.0
            info:
              title: An example spec.
              version: 1.0.0
            paths:
              /evidences:
                get:
                  responses:
                    '404':
                      description: An evidence is not found.
                      content:
                        text/plain:
                          example: no-such-evidence
            """),
        encoding="utf-8",
    )
    warnings = run_sphinx(
        "test-spec.yml",
        options={"response-examples-for": "404"},
        renderer="httpdomain",
    )

    assert "unknown option" not in warnings

    # By default examples are rendered for successful status codes only, so
    # this example is rendered if and only if the option took effect.
    assert "no-such-evidence" in tmpdir.join("out", "index.html").read_text(
        encoding="utf-8"
    )
