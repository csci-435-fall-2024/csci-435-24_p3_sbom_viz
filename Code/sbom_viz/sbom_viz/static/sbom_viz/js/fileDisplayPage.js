import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7/+esm";

const tempTree = {
    name: "1",
    children: [
        {name: "2", children: [
            {name: "4"},
            {name: "5"},
        ]},
        {name: "3"},
        {name: "6", children: [
            {name: "7", children: [
                {name: "8"}
            ]}
        ]}
    ]
};

/**
 * Represents the page that displays the contents of the file after it has been
 * loaded.
 */
export class FileDisplayPage {
    // Set up the page
    constructor() {
        console.log("Hello")
        this.updateTree();
    }
    updateTree() {
        /*// Figure dimensions

        const root = d3.hierarchy(tempTree);
        const dx = 20;
        const dy = 20;
        
        const tree = d3.layout.tree().nodeSize([dx, dy]);
        const diagonal = d3.svg.diagonal().projection((d) => [d.x + dx/2, d.y + dy/2]);
        */

        // Create SVG
        const svg = d3.select("body")
                      .append("svg")
                      .attr("width", 100)
                      .attr("height", 100);
        
        const rect = d3.select("svg")
          .append("rect")
          .attr("x", 0)
          .attr("y", 0)
          .attr("width", 10)
          .attr("height", 10)
          .attr("stroke", "black")
          .attr("fill", "white")
    }
}

new FileDisplayPage()