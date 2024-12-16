import "https://d3js.org/d3.v7.min.js";

/**
 * Represents the page that displays the contents of the file after it has been
 * loaded.
 */
export class FileDisplayPage {
    // Set up the page
    constructor() {

    }
}

new FileDisplayPage()

let idToData = {};
let relationshipMap = {};

// Create a function to load both data sources
async function loadData() {
    const [relationshipResponse, idDataResponse] = await Promise.all([
        fetch("http://127.0.0.1:8000/relationship-map"),
        fetch("http://127.0.0.1:8000/id-data-map")
    ]);
    
    relationshipMap = await relationshipResponse.json();
    idToData = await idDataResponse.json();
}

      /*
       * Credit: 
       * Collapsible tree diagram in v7
       * by d3noob
       * (https://gist.github.com/d3noob/918a64abe4c3682cac3b4c3c852a698d)
       * An interactive version of a Reingold–Tilford tree. Click on the nodes to expand or collapse.
       * by Mike Bostock
       * (https://gist.github.com/mbostock/4339083)
       * With some changes to each to allow for:
       *    JSON file input,
       *    and Vertical orientation
       */

      /* 

      ** UNUSED **
      ** Previously used when initially developing the tree, **
      ** before the tool could use real data                 **

      var treeData =
      {
        "name": "Top Level",
        "children": [
          { 
            "name": "Level 2: A",
            "children": [
              { "name": "Son of A" },
              { "name": "Daughter of A" }
            ]
          },
          { "name": "Level 2: B" }
        ]
      };
      */

    // Set the dimensions and margins of the diagram

    const sidebarWidth = document.querySelector("#sidebar").getBoundingClientRect().width;
    const headerHeight = document.querySelector("div.header").getBoundingClientRect().height;
    const controlsHeight = document.querySelector("div.controls").getBoundingClientRect().height;

    /*
     * The #tree-svg-container is all the space to the left 
     * of the sidebar, under the header.
     * To center the #tree-svg inside of it, set its width
     * dynamically based on the window size.
     */
    document.getElementById("tree-svg-container")
      .setAttribute("style", `width:${
            window.innerWidth - sidebarWidth - 10 // <- accounting for sidebar shadow
      }px`)

    // these sizes refer to the actual "#tree-svg"
    var margin = {top: 50, right: 50, bottom: 50, left: 50},
        width = window.innerWidth - margin.left - margin.right - sidebarWidth,
        height = window.innerHeight - margin.top - margin.bottom - headerHeight - controlsHeight;

    /*
     * append the svg object to the body of the page
     * appends a 'group' element to 'svg'
     * moves the 'group' element to the top left margin
     * ** this [svg] var actually refers to the appended 'g'
     */
    var svg = d3.select("#tree-svg-container").append("svg")
      .attr("id", "tree-svg")
      .attr("width", width)
      .attr("height", height)
        .append("g")
          .attr("transform", "translate("
              + margin.left + "," + margin.top + ")");
    
    // Set up zoom behavior
    var currentTransform = d3.zoomIdentity;
    const zoom = d3.zoom()
      .scaleExtent([0.1, 3]) // Minimum and maximum zoom scale
      .on("zoom", (event) => {
        currentTransform = event.transform;
        svg.attr("transform", currentTransform); // Apply zoom and pan to the g element
      });


    // Attach zoom to the SVG
    d3.select('#tree-svg').call(zoom)
      .call(zoom.transform,
        d3.zoomIdentity.translate(
          width / 2 ,
          height / 4) // slightly higher vertically
            .scale(currentTransform.k) // scale to current zoom level
      );

    var i = 0,
        duration = 750, // in milliseconds
        nodeList,       // flattened list of all nodes, used for searching
        nodeNames,      // list of node names, used for searching
        root;
    
    /*
     * A 'node' is a single software component found in the SBOM,
     * represented by a rectangle with the following dimensions:
     */
    let node_width = 200;
    let node_height = 100;
    
    // Declares a tree layout and assign the size
    var treemap = d3.tree().nodeSize([node_width,node_height]);
    
    /*
     * Assigns parent, children, height, depth
     * Currently loads JSON data from this link,
     * The commented out line below would allow it to use the
     * Raw JSON defined above (treeData)
     */
    d3.json("http://127.0.0.1:8000/tree").then(async function(data){
        // Wait for relationship and id data to load first
        await loadData();
        
        root = d3.hierarchy(data, function(d){return d.children;});
        //root = d3.hierarchy(treeData, function(d) { return d.children; }); // <- USE DUMMY DATA INSTEAD
        root.x0 = height / 2;
        root.y0 = 0;

        // Recursively collapse after the second level
        root.children.forEach(collapse);
        
        update(root);

        // Initialize the list of node names for autocomplete
        nodeList = flattenTree(root); 
        nodeNames = nodeList.map(node => node.data.name); 
    });

    // Attach the "Focus Root" button handler
    d3.select("#focus-root-button").on("click", () => {
      focusNode(root);
    });

    /* ***** START OF SEARCHING CODE ***** */

    /*
     * Flatten the tree to get a list of all nodes
     * Ran once, after tree data is loaded from /tree/
     */
    function flattenTree(node, nodeList = []) {
      nodeList.push(node);
      if (node.children || node._children) {
        (node.children || node._children).forEach(child => flattenTree(child, nodeList));
      }
      return nodeList;
    }

    /* 
     * Handle input for autocomplete
     * When the user types something, gather all node names
     * that match this search and append a div for each. When
     * a search suggestion is clicked:
     *  1) Expand the tree to that node
     *  2) Center that node in the tree box
     *  3) Add the corresponding card to the sidebar
     * Then clear the search box
     */
    const searchInput = d3.select("#node-search");
    const suggestionBox = d3.select("#autocomplete-suggestions");

    searchInput.on("input", function () {
      const query = this.value.toLowerCase();
      suggestionBox.html(""); // clear previous suggestions

      if (query) {
        const matches = nodeNames.filter(name => name.toLowerCase().includes(query));
        matches.forEach(name => {
          suggestionBox.append("div")
            .attr("class", "suggestion")
            .text(name)
            .on("click", function () {
              const selectedNode = nodeList.find(node => node.data.name === name);
              if (selectedNode) {
                expandToNode(selectedNode);
                focusNode(selectedNode);
                addCard(selectedNode); // add clicked search result to the sidebar
              }
              suggestionBox.html(""); // clear suggestions
              searchInput.property("value", ""); // clear search input
            });
        });
      }
    });

    /*
     * Function to expand the tree to a specific node
     * Expand upwards while there is a parent
     */
    function expandToNode(node) {
      let current = node;
      while (current.parent) {
        current = current.parent;
        if (current._children) {
          current.children = current._children; // expand hidden children
          current._children = null;
        }
      }
      update(current);
    }

    /*
     * Function to focus a specific node by translating
     * so that the node is in the center of the screen.
     * Called when clicking the "Focus Root" button (with node = root)
     * or when selecting a node in the search box.
     */
    function focusNode(node) {
      const containerWidth = d3.select('#tree-svg').node().clientWidth;
      const containerHeight = d3.select('#tree-svg').node().clientHeight;

      // Calculate the container's center
      const centerX = containerWidth / 2;
      const centerY = containerHeight / 4; // put the node slightly towards the top rather than directly in the middle

      const translateX = centerX - node.x * currentTransform.k; 
      const translateY = centerY - node.y * currentTransform.k; 

      // Update the view to center the node
      d3.select('#tree-svg')
        .transition()
        .duration(duration)
        .call(
          zoom.transform,
          d3.zoomIdentity.translate(translateX, translateY).scale(currentTransform.k) // k = zoom level
        );
    }
    /* ***** END OF SEARCHING CODE ***** */

    /* 
     * -- Helper function --
     * Recursively collapse the levels under the node [d].
     * Used when initially building the tree (just above),
     * and in the collapseAllNodes() function
     */
    function collapse(d) {
      if (d.children) {
          d._children = d.children
          d._children.forEach(collapse)
          d.children = null
      }
      else if (d._children) {
        d._children.forEach(collapse);
        d.children = null;
      }
    }

    /* 
     * -- Helper function --
     * Recursively expand the levels under the node [d]
     * Called in the collapseAllNodes() function.
     * 
     * A note on D3 - 
     *    d._children is the set of hidden children of [d],
     *    d.children is the set of visible children of [d]
     */
    function expand(d){
      var children = (d.children) ? d.children : d._children;
      if (d._children) {        
          d.children = d._children;
          d._children = null;       
      }
      if(children)
        children.forEach(expand);
    }

    /*
     * Called when the circular button in the bottom left of a node
     * is pressed, if the node has ANY collapsed children,              <- Start = node that was clicked
     * or when the 'Collapse All' button in the top left is selected.   <- No start passed in, so root is default
     * 
     * Whether or not [start] has visible children,
     * go through its children and try to collapse them.
     * Correct any '+'/'-' that may need to be updated after this change.
     */
    function collapseAllNodes(start = root){
      if (start.children) 
        start.children.forEach(collapse);
      else
        start._children.forEach(collapse);
      collapse(start);
      update(start);
      setAllPlusMinusButton(); // these nodes are now collapsed, so set their buttons to '+'
    }

    /*
     * Called when the circular button in the bottom left of a node
     * is pressed, if there is AT LEAST ONE collapsed child of [start],  <- Start = node that was clicked
     * or when the 'Expand All' button in the top left is selected.      <- No start passed in, so root is default
     * 
     * Whether or not [start] has visible children,
     * go through its children and try to collapse them.
     * Correct any '+'/'-' that may need to be updated after this change.
     */
    function expandAllNodes(start = root){
      expand(start);
      update(start);
      setAllPlusMinusButton(); // these nodes are now expanded, so set their buttons to '-'
    }

    /* 
     * Called when the circular button in the bottom left of a node is clicked,
     * in order to decide which of expandAllNodes() or collapseAllNodes() should be called
     *
     * Return true if there is at least one collapsed child
     * somewhere below the node [start].
     */
    function collapsedChildExists(start){

      if (!start.children && !start._children) // edge case - this is a leaf node
        return false;

      else if (start._children) // the node has collapsed children
        return true;

      else if (start.children){ // recursively check children
        for (let child of start.children){
          if (collapsedChildExists(child))
            return true;
        }
      }
      return false;
    }

    /*
     * Find all nodes that are parents 
     * (these are the only nodes that have the plus/minus button).
     * If the node does not have visible children, then set the text 
     * in the bottom right to '+' so the user knows to expand the node's children.
     * Otherwise, set the text to '-' so the user knows they can collapse 
     * this node's children.
     * !! This function serves both the simple 'show-more' button and  !!
     * !! the larger 'show-all' button (they are in order in the code) !!
     */
    function setAllPlusMinusButton(){
      d3.selectAll('.node.parent')
        .each(function(){

          // find the '+' or '-'
          d3.select(this).select("text.show-more")
            .text(function(node){

              // all children are 'hidden', none are visible -> this node's children are contracted
              if (node._children && (!node.children))
                return '+';
              
              // node's children are expanded
              else 
                return '-';
            })

          d3.select(this).select("text.show-all")
            .text(function(node){

              // all children are 'hidden', none are visible -> this node's children are contracted
              if (collapsedChildExists(node))
                return '+';
              
              // node's children are expanded
              else 
                return '-';
            })
      });
    }

    const cardStates = {};
    async function addCard(node) {
      // Get the data for this node from the id-data map
      const nodeData = idToData[node.data.id] || {};
      // Use name if available, otherwise use id
      const displayName = nodeData.name || node.data.id;

      const sidebar = document.getElementById('sidebar');
      let card = document.getElementById(`card-${displayName}`);

      // If this card is already in the sidebar, then toggle it.
      if (card) {
          toggleCard(card, displayName);
      
      // Otherwise, Create a new card
      } else {
          card = document.createElement('div');
          card.className = 'card';
          card.id = `card-${displayName}`;

          // Create card content based on available data
          let cardContent = `<h3>${displayName}</h3>`;
          
          if (nodeData.name) {
              cardContent += `<p><strong>Name:</strong> ${nodeData.name}</p>`;
          }
          if (nodeData.id) {
              cardContent += `<p><strong>ID:</strong> ${nodeData.id}</p>`;
          }
          if (nodeData.version) {
              cardContent += `<p><strong>Version:</strong> ${nodeData.version}</p>`;
          }
          if (nodeData.licenseConcluded) {
              cardContent += `<p><strong>License:</strong> ${nodeData.licenseConcluded}</p>`;
          }
          if (nodeData.supplier) {
              cardContent += `<p><strong>Supplier:</strong> ${nodeData.supplier}</p>`;
          }
          if (nodeData.downloadLocation) {
              cardContent += `<p><strong>Download:</strong> ${nodeData.downloadLocation}</p>`;
          }
          if (nodeData.checksums) {
              cardContent += `<p><strong>SHA1:</strong> ${nodeData.checksums.SHA1 || 'N/A'}</p>`;
          }
          if (nodeData.copyrightText) {
              cardContent += `<p><strong>Copyright:</strong> ${nodeData.copyrightText}</p>`;
          }

          card.innerHTML = cardContent;
          card.onclick = function() { toggleCard(card, displayName); };
          sidebar.appendChild(card);
          cardStates[displayName] = true;
          toggleNodeHighlight(displayName);
      }
    }

    function toggleCard(card, cardName) {
      const sidebar = document.getElementById('sidebar');
      if (cardName in cardStates) {
          if (cardStates[cardName]) {
              sidebar.removeChild(card);
              cardStates[cardName] = false;
          } else {
              sidebar.appendChild(card);
              cardStates[cardName] = true;
          }
      } else {
          // First time the card is clicked
          cardStates[cardName] = true;
      }
      toggleNodeHighlight(cardName);
    }

    // Select all node labels. Filter to 
    // the title that has the same label as this card. (*Not using label because it may be truncated*)
    // Select the previous previous sibling of this label (the rect that presents as the node).
    // Change the border of this rect, if this node is present in the sidebar.
    function toggleNodeHighlight(cardName){
        d3.selectAll('g.node > title') 
          .filter(function(d) { 
            const nodeData = idToData[d.data.id] || {};
            return nodeData.name === cardName || d.data.id === cardName;
          })
          .each(function(){
            d3.select(this)            
            .node()                    
            .previousElementSibling    
            .previousElementSibling    
            .style.stroke = 
            (cardStates[cardName]) ? "blue" : "steelblue"
          });
    }

    function clearAllCards() {
        const sidebar = document.getElementById('sidebar');
        const cards = sidebar.querySelectorAll('.card');
        
        // For each card, reset its node highlight before removing it
        cards.forEach(card => {
            const cardName = card.querySelector('h3').textContent;
            cardStates[cardName] = false;  // Set state to false before toggling highlight
            toggleNodeHighlight(cardName);  // Reset the node highlight
            sidebar.removeChild(card);
        });
        
        // Reset all card states
        for (let key in cardStates) {
            cardStates[key] = false;
        }
    }

    async function update(source) {
      // Assigns the x and y position for the nodes
      var treeData = treemap(root);

      var rectHeight = 60, rectWidth = 120;

      const treeBbox = treeCoordinates(treeData, rectWidth, rectHeight);
    
      // Compute the new tree layout.
      var nodes = treeData.descendants(),
          links = treeData.descendants().slice(1);
    
      // Normalize for fixed-depth.
      nodes.forEach(function(d){ d.y = d.depth * 90});
    
      // ****************** Nodes section ***************************
    
      // Update the nodes...
      var node = svg.selectAll('g.node')
          .data(nodes, function(d) {return d.id || (d.id = ++i); });
    
      // Enter any new modes at the parent's previous position.
      // If this node has children, it has class "node parent"
      // Otherwise, it has class "node leaf".
      // If this node is a ghost node, apply a filter so that it appears red.
      var nodeEnter = node.enter().append('g')
          .attr('class', function(d){
            if (d._children || d.children) return "node parent";
            else return "node leaf";
          })
          .attr("transform", function(d) {
            return "translate(" + source.x0 + "," + source.y0 + ")";
        })
        .on('click', click)
        .style("filter", function(d){
          if (d.data.ghost)
            return 'hue-rotate(120deg)';
        });
      // Add rectangle container for each node
      nodeEnter.append('rect')
          .attr('class', 'node')
          .attr('id', 'node-container')
          .attr('width', rectWidth)
          .attr('height', rectHeight)
          .attr('x', (rectWidth/2)*-1)
          .attr('y', (rectHeight/2)*-1)
          .attr('rx', '5') // round corners
          .style("fill", function(d) {
              return d._children ? "lightsteelblue" : "#fff";
          });
    
      // Add labels for the nodes
      // Truncate label length and add "..."
      // if the label is larger than the node
      var maxLabelLength = 13;
      nodeEnter.append('text')
          .attr('id', 'node-label')
          .attr("text-anchor", "middle")
          .attr("cursor", "pointer")
          .text(function(d) { 
            const nodeData = idToData[d.data.id];
            const nodeName = nodeData?.name || d.data.id;
            if(nodeName.length > maxLabelLength){
              return nodeName.substring(0,maxLabelLength)+"...";
            }
            else{
              return nodeName; 
            }
    });

      // When the user hovers over a node, 
      // show a tooltip with the full 
      // (no ellipses) label
      nodeEnter.append("svg:title")
          .text(function(d){
            return d.data.name;
          });

        // ****************** ".show-more" button section ***************************
     
        // Append a button that will show more 
        // information about this node in the sidebar. 
        // !!! more styling is in styles.css !!!
        // ** Pass d.data.name on click to wherever necessary (sidebar)
        // x, y are arbitrary, for lining up in corner
        var buttonWidth = 16, buttonHeight = 16, 
          showmoreX = (rectWidth/2)-buttonWidth-1, 
          showmoreY = rectHeight-47;
        nodeEnter.append('rect')
            .attr('class','show-more')
            .attr("height", buttonHeight)
            .attr("width", buttonWidth)
            .attr("x", showmoreX) 
            .attr("y", showmoreY)
            .attr('rx', '5');

        // The '+' or '-' text in the bottom corner of node
        // x = (x of the rect that the text is inside of) + 1/2 the width of the rect
        // y = same but with height
        nodeEnter.append('text')
            .attr('class','show-more')
            .attr("x", showmoreX+(buttonWidth/2))
            .attr("y", showmoreY+(buttonHeight/2))
            .text('+') 
            .attr('text-anchor', 'middle');

      // Select all leaf nodes and remove their 'show-more' button
      d3.selectAll(".node.leaf").selectAll(".show-more").remove();

      // The '.show-more' class covers the '+'/'-' text and the 
      // surrounding rect. 
      // If the bounding rect is clicked, then go to the nextSibling
      // (the '+'/'-' text) and switch it. Otherwise (the text was clicked),
      // switch the text directly.
      // * stopPropagation() ensures that the click does not go through to the larger node and expand the tree.
      d3.selectAll('.show-more')
          .on('click', function(e, d){
            e.stopPropagation();

            // not able to use the expand() or collapse() functions here because they are recursive
            if (d.children) {
              d._children = d.children;
              d.children = null;
            } else {
              d.children = d._children;
              d._children = null;
            }
            update(d);
            setAllPlusMinusButton(); // update BOTH plus minus ('show-more' and 'show-all')
            //resizeCanvas(treeData, node_width, node_height);
            //repositionTree(d);
          });

      // ****************** ".show-all" button section ***************************
      // When clicking this button, toggle between recursively expanding / contracting
      // ALL children nodes of this node (not just the next level)

      // from 'show-more' above: 
          // buttonWidth, buttonHeight
          // showmoreX, showmoreY
          var showallX = showmoreX-rectWidth+buttonWidth+11,
          showallY = showmoreY+7,
          radius = buttonHeight/2;
      nodeEnter.append('circle')
          .attr('class','show-all')
          .attr("r", radius)
          .attr("cx", showallX) 
          .attr("cy", showallY)
          .attr('rx', '5');
      
      nodeEnter.append('text')
          .attr('class','show-all')
          .attr("x", showallX)
          .attr("y", showallY)
          .text('+') 
          .attr('text-anchor', 'middle');

      // Select all leaf nodes and remove their 'show-all' button
      d3.selectAll(".node.leaf").selectAll(".show-all").remove();

      // When clicked, evaluate if the node should expand or collapse
      // The changing of the symbol is handled down the line in
      // SetPlusMinusButton(node)
      d3.selectAll('.show-all')
          .on('click', function(e, d){
            e.stopPropagation();

            // check the state of this node (should we expand, or should we collapse)
            if (collapsedChildExists(d))
              expandAllNodes(d);
            else 
              collapseAllNodes(d);
          });

      // ****************** nodeUpdate section ***************************


      // UPDATE
      // Extra styling is from:
      // https://observablehq.com/@bumbeishvili/vertical-collapsible-tree
      var nodeUpdate = nodeEnter.merge(node)
        .attr("fill", "#fff")
        .attr("stroke", "steelblue")
        .attr("stroke-width", "3px;")
        .style('font', '12px');
    
      // Transition to the proper position for the node
      nodeUpdate.transition()
        .duration(duration)
        .attr("transform", function(d) { 
            return "translate(" + (d.x) + "," + d.y + ")";
         });
    
      // Update the node attributes and style
      nodeUpdate.select('rect.node')
        .attr('r', 10)
        .style("fill", function(d) {
            return d._children ? "lightsteelblue" : "#fff";
        })
        .attr('cursor', 'pointer');
    
    
      // Remove any exiting nodes
      var nodeExit = node.exit().transition()
          .duration(duration)
          .attr("transform", function(d) {
              return "translate(" + (source.x) + "," + source.y + ")";
          })
          .remove();
    
      // On exit reduce the node rectangle size to 0
      nodeExit.select('rect')
        .attr('r', 1e-6);
    
      // On exit reduce the opacity of text labels
      nodeExit.select('text')
        .style('fill-opacity', 1e-6);
    
      // ****************** links section ***************************
    
      // Update the links...
      var link = svg.selectAll('path.link')
          .data(links, function(d) { return d.id; });
    
      // Enter any new links at the parent's previous position.
      var linkEnter = link.enter().insert('path', "g")
          .attr("class", "link")
          .attr('d', function(d){
            var o = {x: source.x0, y: source.y0}
            return diagonal(o, o)
          });

      // Add tooltips for the links
      linkEnter.append('title')
          .text(function(d){
            // Get parent and child names/IDs
            const parentData = idToData[d.parent.data.id] || {};
            const childData = idToData[d.data.id] || {};
            const parentName = parentData.name || d.parent.data.id;
            const childName = childData.name || d.data.id;
            
            // Get relationships from relationshipMap using child's ID
            const relationships = relationshipMap[d.data.node_id] || ['Unknown Relationship'];
            
            // Format relationships as a bulleted list if multiple exist
            const relationshipText = relationships.length > 1
              ? 'Relationships:\n• ' + relationships.join('\n• ')
              : 'Relationship: ' + relationships[0];
            
            // Return formatted tooltip text
            return `${parentName} → ${childName}\n${relationshipText}`;
          });
    
      // UPDATE
      // Extra styling is from: 
      // https://observablehq.com/@bumbeishvili/vertical-collapsible-tree
      var linkUpdate = linkEnter.merge(link)
        .attr("fill", "none")
        .attr("stroke", "#ccc")
        .attr("stroke-width", "2px");
    
      // Transition back to the parent element position
      linkUpdate.transition()
          .duration(duration)
          .attr('d', function(d){ return diagonal(d, d.parent) });
    
      // Remove any exiting links
      var linkExit = link.exit().transition()
          .duration(duration)
          .attr('d', function(d) {
            var o = {x: source.x, y: source.y}
            return diagonal(o, o)
          })
          .remove();
    
      // Store the old positions for transition.
      nodes.forEach(function(d){
        d.x0 = d.x;
        d.y0 = d.y;
      });
    
      // Creates a curved (diagonal) path from parent to the child nodes
      // Creates a curved (diagonal) path from parent to the child nodes
      function diagonal(s, d) {
    
        const path = `M ${s.x} ${s.y}
                      C ${(s.x + d.x) / 2} ${s.y},
                        ${(s.x + d.x) / 2} ${d.y},
                        ${d.x} ${d.y}`
        return path
      }

      // Add or remove card in sidebar when 
      // corresponding node is clicked
      function click(event, d) {
        addCard(d);
      }

      // This fixes the issue of the root node  
      // having '+' button, despite being expanded
      setAllPlusMinusButton();
    }

    // Resize the canvas to fit the tree
    function resizeCanvas(treeData, nodeWidth, nodeHeight) {
      
      // Calculate old and new dimensions
      let svg = document.getElementById("tree-svg");
      let oldDimensions = svg.getBBox(); // old dimensions are the current dimensions of the SVG figure
      let newCoords = treeCoordinates(treeData, nodeWidth, nodeHeight) // new coordinates are determined from the d3 treeData
      let newDimensions = { x: newCoords.left, y: newCoords.top, width: newCoords.right - newCoords.left, height: newCoords.bottom - newCoords.top }; // calculate new dimensions from new coordinates

      // Resize width
      if (newDimensions.width >= oldDimensions.width) {           // If the tree will grow,
        resizeWidth(newDimensions);                               // immediately make room for the tree so it won't clip as it grows.
      } else {                                                    // If the tree will collapse,
        setTimeout(() => {resizeWidth(newDimensions)}, duration); // wait until the tree has finished collapsing before shrinking the canvas to avoid clipping the tree while it is still collapsing.
      }

      if (newDimensions.height >= oldDimensions.height) {         // If the tree will grow,
        resizeHeight(newDimensions);                              // immediately make room for the tree so it won't clip as it grows.
      } else {                                                    // If the tree will collapse,
        setTimeout(() => {resizeHeight(newDimensions)}, duration);// wait until the tree has finished collapsing before shrinking the canvas to avoid clipping the tree while it is still collapsing.
      }

      // Function calculating the new width of the tree, accounting for margins.
      function resizeWidth(newDimensions) {
        let svg = document.getElementById("tree-svg");
        svg.setAttribute("width", newDimensions.width + margin.left + margin.right);
      }

      // Function calculating the new height of the tree, accounting for margins.
      function resizeHeight(newDimensions) {
        let svg = document.getElementById("tree-svg");
        svg.setAttribute("height", newDimensions.height + margin.top + margin.bottom);
      }

    }

    // Determine the bounding box of coordinates surrounding the tree as an object: {left, top, right, down}
    // Recursively look through the subtrees and combine the results 
    function treeCoordinates(currentNode, nodeWidth, nodeHeight) { 
      let result = {left: currentNode.x, top: currentNode.y, right: currentNode.x + nodeWidth, bottom: currentNode.y + nodeHeight}; // Consider the current node's bounding box.
      if (currentNode.children) { // If the node has any subtrees,
        for (let child of currentNode.children) { // Then for each subtree,
          // Get the bounding box of the subtree and expand the bounding box of the current tree (with currentNode as the root) accordingly.
          let subTreeCoords = treeCoordinates(child, nodeWidth, nodeHeight);
          if (subTreeCoords.left < result.left) { result.left = subTreeCoords.left; }
          if (subTreeCoords.right > result.right) { result.right = subTreeCoords.right; }
          if (subTreeCoords.top < result.top) { result.top = subTreeCoords.top; }
          if (subTreeCoords.bottom > result.bottom) { result.bottom = subTreeCoords.bottom; }
        }
      }
      return result;
    }


// Expose clearAllCards to the global scope
window.clearAllCards = clearAllCards;
window.collapseAllNodes = collapseAllNodes;
window.expandAllNodes = expandAllNodes;
