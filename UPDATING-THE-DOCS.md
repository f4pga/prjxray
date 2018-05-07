# Guide to updating the Project X-Ray docs

We welcome updates to the Project X-Ray docs. The docs are published on [Read
the Docs](http://prjxray.readthedocs.io) and the source is on
[GitHub](https://github.com/SymbiFlow/prjxray/tree/master/docs).

Updating the docs is a three-step process: Make your updates, test your updates,
send a pull request.

# 1. Make your updates

The standard Project X-Ray [contribution guidelines](CONTRIBUTING.md) apply to
doc updates too.

Follow your usual process for updating content on GitHub. See GitHub's guide to
[working with forks](https://help.github.com/articles/working-with-forks/).

# 2. Test your updates

Before sending a pull request with your doc updates, you need to check the
effects of your changes on the page you've updated and on the docs as a whole.

## Check your markup

There are a few places on the web where you can view ReStructured Text rendered
as HTML. For example:
[https://livesphinx.herokuapp.com/](https://livesphinx.herokuapp.com/) 

## Perform basic tests: make html and linkcheck

If your changes are quite simple, you can perform a few basic checks before
sending a pull request. At minimum:

-  Check that `make html` generates output without errors
-  Check that `make linkcheck` reports no warnings. 
-  When editing, `make livehtml` is helpful. 

To make these checks work, you need to install Sphinx. We recommend `pipenv`. 

Follow the steps below to install `pipenv` via `pip`, run `pipenv install` in
the `docs` directory, then run `pipenv shell` to enter an environment where
Sphinx and all the necessary plugins are installed:

Steps in detail, on Linux:

- Install pip:

    sudo apt install python-pip

- Install pipenv - see the
  [pipenv installation
  guide](http://pipenv.readthedocs.io/en/latest/install/#installing-pipenv):

    pip install pipenv
 
- Add pipenv to your path, as recommended in the
  [pipenv installation
  guide](http://pipenv.readthedocs.io/en/latest/install/#installing-pipenv):

  - On Linux, add this in your ~/.profile file:
 
      export PATH=$PATH:~/.local/bin source ~/.profile

  - Note: On OS X the path is different: `~/Library/Python/2.7/bin`

- Go to the docs directory in the Project X-Ray repo:

    cd ~/github-repos/prjxray/docs
 
- Run pipenv to install the Sphinx environment:

    pipenv install

- Activate the shell:

    pipenv shell

- Run the HTML build checker, and check for _errors_:

    make html

- Run the link checker, and check for _warnings_:

    make linkcheck

- To leave the shell, type: `exit`.

## Perform more comprehensive testing on your own staging doc site

If your changes are more comprehensive, you should do a full test of your fork
of the docs before sending a pull request to the Project X-Ray repo. You can
test your fork by viewing the docs on your own copy of the Read the Docs
build.

Follow these steps to create your own staging doc site on Read the Docs (RtD):

-  Sign up for a RtD account here:
   [https://readthedocs.org/](https://readthedocs.org/)
-  Go to your [RtD connected
   services](https://readthedocs.org/accounts/social/connections/), click
   **Connect to GitHub**, and connect RtD to your GitHub account. (If you
   decide not to do this, you'll need to import your project manually in the
   following steps.)
-  Go to [your RtD dashboard](https://readthedocs.org/dashboard/).
-  Click **Import a Project**.
-  Add your GitHub fork of the Project X-Ray project. Give your doc site a
   **name** that distinguishes it from the canonical Project X-Ray docs. For
   example, `your-username-prjxray`
-  Make your doc site **protected**. See the [RtD guide to privacy
   levels](http://docs.readthedocs.io/en/latest/privacy.html).
   Reason for protecting your doc site: If you leave your doc site public, it
   will appear in web searches. That may be confusing for readers who are
   looking for the canonical Project X-Ray docs.
-  Set RtD to build from your branch, rather than from master. This ensures
   that the content you see on your doc site reflect your latest updates:
   -  On the RtD dashboard, go to **Admin > Advanced Settings.**
   -  Add the name of your branch in **Default branch**. This is the
      branch that the "latest" build config points to. If you leave this field
      empty, RtD uses `master` or `trunk`.

-  RtD now builds your doc site, based on the contents in your Project X-Ray
   fork.
-  See the [RtD getting-started
   guide](https://docs.readthedocs.io/en/latest/getting_started.html#import-docs)
   for more info.

# 3. Send a pull request

Follow your standard GitHub process to send a pull request to the Project X-Ray
repo. See the GitHub guide to [creating a pull request from a
fork](https://help.github.com/articles/creating-a-pull-request-from-a-fork/).
