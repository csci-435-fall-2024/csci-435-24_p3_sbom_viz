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

To use the vulnerability analysis, extract the archives
```bash
csci-435-24_p3_sbom_viz\Code\sbom_viz\sbom_viz\security_scanning_tools\trivy_0.57.0_windows-64bit.zip
csci-435-24_p3_sbom_viz\Code\sbom_viz\sbom_viz\security_scanning_tools\bomber_0.5.1_windows_amd64.tar.gz
```
into 
```bash
security_scanning_tools\executables\trivy_0.57.0_windows-64bit\trivy.exe
security_scanning_tools\executables\bomber_0.5.1_windows_amd64\bomber.exe
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
Supporting more SBOM formats is currently WIP (currently SPDX 2.2 and SPDX 2.3 sboms in JSON are supported), but to ensure that the SBOM can correctly be parsed we suggest to using one of the SBOM examples in `Artifacts/Examples/`.
We initially tried to use the [lib4sbom](https://pypi.org/project/lib4sbom/) library to parse the SBOM, but found that this tool eliminated information that could be valuable to the user. Instead, we implemented a custom parser which builds the SBOM into a tree object that can be easily used for visualization. This process is done in `parse_files.py` and `build_tree.py`. Then in `relationship_map_builder.py`, a map is created between each node of the custom tree and the relationship to its parent.

If a file has been uploaded to the tool and able to be analyzed, its name will be displayed on the Home page.

From there, selecting the 'Upload File' button will take you to the SBOM display page (`sbom_viz/static/sbom_viz/js/FileDisplayPage.js`).

### Tree visualization
The tree visualization page (or the Diagram tab) displays your inputted SBOM file in the form of a tree, with a single `root` node added. The raw JSON of the tree can be seen by navigating to `/tree/`. Each node of the tree represents a single software component present in the SBOM file. There are many ways to interact with the nodes on the tree:
  - Clicking the circle in the bottom left -> expand or collapse __all children__ of this node, depending on if there are children to expand.
  - Clicking the square in the bottom right -> expand or collapse __only the next level of children__ under this node, depending on if there are children to expand.
  - Clicking anywhere else on the node -> add this node to the sidebar to view more information *(a node can be removed from the sidebar by clicking on the node again, or clicking on its corresponding card in the sidebar)*.
  - Hovering over the link between two nodes will show a tooltip of the relationship between the two, if a relationship is known.
  - In case you get lost in the tree, there are buttons in the top left of the screen to expand or collapse all nodes of the tree.
    
The **Sidebar** on the right of the screen has the following features:
  - When a node is added to the sidebar, the corresponding node is highlighted with a blue border.
  - The sidebar displays more detailed information about a specific node.
  - All open sidebar cards can be cleared with the use of the 'Clear All' button.
---
_A note on **Ghost Nodes**_: 
- Due to a quirk of visualizing an SBOM, we have run into difficulties making it clear when one single software component is related to two other components.
- For example, say we have software components A, B, and X. Component X is related to component A, but also related to component B, so in the tree visualization we have two separate instances of component X - one as a child of component A, and one as a child of component B.
- To make it clear that these two instances of X refer to the same actual software component, the first instance of component X that is encountered when building the tree is marked as the *real* node, while all other instances are marked as a *ghost* node. These ghost nodes are colored red to be visible and when any instance of a software component is highlighted, all other ghost instances will be highlighted as well.
---

### Vulnerability Analysis
After an SBOM has been uploaded, our analysis of the vulnerabilities present in the SBOM can be viewed on the Vulnerabilities tab. The tool finds the vulnerabilities present in the SBOM by parsing the file with [trivy](https://github.com/aquasecurity/trivy). In case trivy fails in parsing and analyzing the SBOM, we have [bomber](https://github.com/devops-kung-fu/bomber) set up as a backup. Ensure that both of these executables are extracted to the correct folder as shown above in the Installation section, otherwise the tool will not be able to find the executables and conduct the security analysis.

Security analysis happens in `security.py` and generates a JSON which can be found by navigating to `/sec-info/`. The formatted analysis page includes
- A summary of the vulnerability distribution, as the number of vulnerabilities in each CVSS severity category,
- A pie chart reflecting this distribution,
- A table of the top 10 most severe vulnerabilities found in the SBOM, along with
  - The component name,
  - The CVE_ID,
  - The score and severity category
  - A description of the vulnerability.
More information about a specific vulnerability can be found by searching for the related CVE_ID, and all vulnerabilities found in the SBOM can be found in the `Effected_Components` field at the bottom of `/sec-info/`.

### License Analysis
After an SBOM has been uploaded, our analysis of the licenses present in the SBOM can be viewed on the Licenses tab. The tool looks for any license attached to a software component in the SBOM and presents a distribution of the licenses found in the form of a pie chart, as well as in a table with the relative composition of each respective license. 

### Planned features
- More compatability for vulnerability analysis
- Making inferences based off of licenses found (what can I do with this software?)
