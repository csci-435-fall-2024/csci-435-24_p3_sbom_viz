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

let idToData = fetch("http://127.0.0.1:8000/id-data-map").then(response => response.json())

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
    
    // Set the dimensions and margins of the diagram
    var margin = {top: 50, right: 400, bottom: 30, left: 90},
        width = 1000 - margin.left - margin.right,
        height = 1000 - margin.top - margin.bottom;
    
    // append the svg object to the body of the page
    // appends a 'group' element to 'svg'
    // moves the 'group' element to the top left margin
    var svg = d3.select("body").append("svg")
    .attr("id", "tree-svg")
    .attr("width", width + margin.right + margin.left)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate("
              + margin.left + "," + margin.top + ")");
    
    var i = 0,
        duration = 750, // in milliseconds
        root;

    let node_width = 200;
    let node_height = 100;
    
    // declares a tree layout and assigns the size
    var treemap = d3.tree().nodeSize([node_width,node_height])//size([height, width]);
    
    // Assigns parent, children, height, depth
    // Currently loads JSON data from this link,
    // The commented out line below would allow it to use the
    // Raw JSON defined in this file
    d3.json("http://127.0.0.1:8000/tree").then(function(data){
        root = d3.hierarchy(data, function(d){return d.children;});
        //root = d3.hierarchy(treeData, function(d) { return d.children; });
        root.x0 = height / 2;
        root.y0 = 0;
        
        // Collapse after the second level
        root.children.forEach(collapse);
        
        update(root);
        resizeCanvas(treemap(root), node_width, node_height);
        
        // Collapse the node and all it's children
        function collapse(d) {
            if(d.children) {
                d._children = d.children
                d._children.forEach(collapse)
                d.children = null
            }
        }
    });
    const cardStates = {};
    function addCard(cardName) {
      const sidebar = document.getElementById('sidebar');
      let card = document.getElementById(`card-${cardName}`);

      if (card) {
          toggleCard(card, cardName);
      } else {
          // Create new card
          card = document.createElement('div');
          card.className = 'card';
          card.id = `card-${cardName}`;
          card.innerHTML = `<h3>${cardName}</h3><p>This is the content for "${cardName}".</p>`;
          card.onclick = function() { toggleCard(card, cardName); };
          sidebar.appendChild(card);
          cardStates[cardName] = true;
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
    }

    function clearAllCards() {
      const sidebar = document.getElementById('sidebar');
      const cards = sidebar.querySelectorAll('.card');
      cards.forEach(card => sidebar.removeChild(card));
      
      // Reset all card states
      for (let key in cardStates) {
          cardStates[key] = false;
      }
    }

    function update(source) {
    
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
      var nodeEnter = node.enter().append('g')
          .attr('class', 'node')
          .attr("transform", function(d) {
            return "translate(" + source.x0 + "," + source.y0 + ")";
        })
        .on('click', click);

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
      nodeEnter.append('text')
          .attr('id', 'node-label')
          .attr("text-anchor", "middle")
          .text(function(d) { return d.data.name; });

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
          .attr('id', 'more-info')
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

      // The '.show-more' class covers the '+'/'-' text and the 
      // surrounding rect. 
      // If the bounding rect is clicked, then go to the nextSibling
      // (the '+'/'-' text) and switch it. Otherwise (the text was clicked),
      // switch the text directly.
      // * stopPropagation() ensures that the click does not go through to the larger node and expand the tree.
      d3.selectAll('.show-more')
          .on('click', function(e, d){
            e.stopPropagation();
            if(this.tagName == 'text'){
              d3.select(this).text(d3.select(this).text() == '+' ? '-' : '+');
            }
            else {
              d3.select(this.nextSibling).text(d3.select(this.nextSibling).text() == '+' ? '-' : '+');
            }
            if (d.children) {
              d._children = d.children;
              d.children = null;
            } else {
              d.children = d._children;
              d._children = null;
            }
            update(d);
            resizeCanvas(treeData, node_width, node_height);
            console.log(d.data.name);
          });

      // UPDATE
      // Extra styling is from:
      // https://observablehq.com/@bumbeishvili/vertical-collapsible-tree
      var nodeUpdate = nodeEnter.merge(node)
        .attr("fill", "#fff")
        .attr("stroke", "steelblue")
        .attr("stroke-width", "3px;")
        .style('font', '12px sans-serif');
    
      // Transition to the proper position for the node
      nodeUpdate.transition()
        .duration(duration)
        .attr("transform", function(d) { 
            return "translate(" + (d.x-treeBbox.left) + "," + d.y + ")";
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
              return "translate(" + (source.x-treeBbox.left) + "," + source.y + ")";
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
            var o = {x: source.x0+treeBbox.left, y: source.y0}
            return diagonal(o, o)
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
        d.x0 = d.x - treeBbox.left;
        d.y0 = d.y;
      });
    
      // Creates a curved (diagonal) path from parent to the child nodes
      // Creates a curved (diagonal) path from parent to the child nodes
      function diagonal(s, d) {
    
        const path = `M ${s.x - treeBbox.left} ${s.y}
                      C ${(s.x + d.x) / 2 - treeBbox.left} ${s.y},
                        ${(s.x + d.x) / 2 - treeBbox.left} ${d.y},
                        ${d.x - treeBbox.left} ${d.y}`
        return path
      }

      // Toggle children on click.
      function click(event, d) {
        addCard(d.data.name);
      }
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

console.log("Hello")

// Expose clearAllCards to the global scope
window.clearAllCards = clearAllCards;
