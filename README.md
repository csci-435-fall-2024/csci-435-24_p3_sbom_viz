# csci-435-24_p3_sbom_viz

After you clone the repo, I would recommend you run the following 2 lines:

```bash
python -m venv sbom_env

sbom_env\Scripts\activate
```
After creating the virtual environment, you will need to install a few dependencies. Call:
```bash
pip install -r ./code/requirements.txt
```

This will give you a virtual environment where dependencies can be tracked more easily.
If you are getting an error trying to activate your venv you might need to run this first:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

To run the Django project locally, navigate to the sbom_viz directory in your terminal:

```bash
cd sbom_viz
```

and then run this:

```bash
python manage.py runserver
```

After, you should be able to view the site on your browser by going to your local address (http://127.0.0.1:8000/)