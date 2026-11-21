PhishLens project overview

PhishLens checks links and email text for signs of phishing. It shows which signs led to each score.

What it does

- Checks links without opening them.
- Checks email text for common warning signs.
- Checks a list of links at once.
- Compares four scoring models.
- Can look up public domain details if the user says they are allowed to check the domain.

Main files

- `phishlens/features.py` reads parts of a link used by the checks.
- `phishlens/dataset.py` makes sample links for training and testing.
- `phishlens/model.py` scores links and shows which parts affected the score.
- `phishlens/tools.py` runs optional domain checks.
- `phishlens/app.py` starts the web app.
- `phishlens/static/index.html` has the web page.

Data and limits

The training links are made for this project. A separate test with public links is explained in [Real data notes](docs/REAL_DATA.md). It used a balanced sample and does not show how the app will work for every user.

Normal checks do not visit links. Optional domain checks need the user approval and block local or private addresses.

Run it

```bash
docker compose up --build -d
make test
make evaluate
```

Open http://localhost:8102. See the README for more details.
