README
######

.. include:: README.include.md
   :parser: myst_parser.sphinx_

How to build the docs
=====================

#. The documentation is build by `Sphinx <https://www.sphinx-doc.org/>`_, we need to install the requirements:

   .. code:: sh

      pip install -r docs/requirements.txt

#. Generate API-Docs. You may clear `docs/apidocs` directory then re-generate them if source tree changed:

   .. code:: sh

      sphinx-apidoc -o docs/apidocs -e -H APIs src

#. Build HTML documentation:

   * Make tool:

      .. code:: sh

         make -C docs html

   * Windows:

      .. code:: bat

         docs\make html

The built-out static web site is at ``docs/_build/html``, we can serve it:

.. code:: sh

   python -m http.server -d docs/_build/html

then open http://localhost:8000/ in a web browser.

.. tip::
   Try another port if ``8000`` is already in use.
   For example, to serve on port ``8080``:

   .. code:: sh

      python -m http.server -d docs/_build/html 8080

   .. seealso:: Python ``stdlib``'s :mod:`http.server`

.. tip::
   If want to build PDF, use ``make rinoh`` instead.

   .. seealso:: https://www.sphinx-doc.org/en/master/usage/builders/index.html#sphinx.builders.latex.LaTeXBuilder
