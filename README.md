# SBOM Visualization and Exploration Toolkit
**A tool made with Django that visualizes and displays critical information from a Software Bill of Materials (SBOM), such as a dependency graph and a distribution of security vulnerabilities and licenses present in components of the SBOM.**

_csci-435-24_p3_sbom_viz_

## Installation
Clone the repo, and run the following lines to create a virtual environment:

```bash
python -m venv sbom_env

sbom_env\Scripts\activate
```
To activate the virtual environment on Linux, run the following instead:
```bash
source sbom_env\bin\activate
```
After creating the virtual environment, you will need to install a few dependencies. Run:
```bash
pip install -r ./code/requirements.txt
```

This will give you a virtual environment with all necessary dependencies to use the tool.
If you are getting an error trying to activate your virtual environment you might need to run this first:

```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

To run the Django project locally, navigate to the sbom_viz directory in your terminal:

```bash
cd sbom_viz
```

and then begin the local webserver by running:

```bash
python manage.py runserver
```

Now you should be able to view the site on your browser by going to your [local address](http://127.0.0.1:8000/).

## Usage
### Upload an SBOM file on the homepage.
Supporting more SBOM formats is currently WIP, but to ensure that the SBOM can correctly be parsed we suggest to using one of the SBOM examples in `Artifacts/Examples/`.
We initially tried to use the [lib4sbom](https://pypi.org/project/lib4sbom/) library to parse the SBOM, but found that this tool eliminated information that could be valuable to the user. Currently, the `sbom_viz/sbom_viz/scripts/build_tree.py` file still makes use of this library. A custom parser is a WIP.
The input is parsed and stored in a workable format in `sbom_viz/templates/data.json`.

From there, selecting the 'Upload File' button will take you to the SBOM display page (`sbom_viz/static/sbom_viz/js/FileDisplayPage.js`).

### Tree visualization
The tree visualization page displays your inputted SBOM file in the form of a tree, with a single `root` node added. Each node of the tree represents a single software component present in the SBOM file. You can interact with the tree through:
  - Clicking on a node -> display node in the sidebar
  - Clicking **+** on a node -> expand the children of this node
  - Clicking **-** on a node -> contract the children of this node
    
The **Sidebar** on the right of the screen has the following features:
  - When a node is added to the sidebar, the corresponding node is highlighted with a blue border.
  - The sidebar displays more detailed information about a specific node.
  - All open sidebar cards can be cleared with the use of the 'Clear All' button.

### Planned features
- Downloadable summary document of SBOM information (vulnerabilites and license distribution)
- Security vulnerability analysis page (distribution of severity of security vulnerabilitiies)
- License analysis page (distribution of different licenses present in software components)
