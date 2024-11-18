import "https://d3js.org/d3.v7.min.js";
import { getVulnerabilityDistribution } from "./vulnerability_data.js";


// Temporary vulnerability distribution data (replace with endpoint later)
// ** Just added a few more to see how pie chart looks when crowded
/*
let data = [
    {"name":"Critical", "count":10},
    {"name":"Critical-High", "count":15},
    {"name":"High", "count":20},
    {"name":"High-Medium", "count":25},
    {"name":"Medium", "count":10},
    {"name":"Medium-Low", "count":15},
    {"name":"Low", "count":30},
    {"name":"Low-None", "count":35},
    {"name":"None", "count":2},
]
    */


async function setUpPieChart(){



    // Inspired by https://d3-graph-gallery.com/graph/pie_annotation.html
    const width = 500;
    const height = 500;
    const margin = 50;

    let radius = Math.min(width, height) / 2 - margin

    const svg = d3.select("#pie-chart-container")
                    .append("svg")
                        .attr("width", width)
                        .attr("height", height)
                        .attr("style", "max-width: 100%; height: auto; font: 10px sans-serif;") // change if wanted, from the same link as the colors
                    .append("g")
                        .attr("transform", `translate(${width / 2}, ${height / 2})`);

    const arc = d3.arc()
                    .innerRadius(0)
                    .outerRadius(radius);

    // Compute the position of each group on the pie:
    const pie = d3.pie()
                    .sort(null) // helps to get colors right
                    .value(d => d.count);

    // The range part makes it color kind of like severity, from:
    // https://observablehq.com/@d3/pie-chart/2
    const color = d3.scaleOrdinal()
                    .domain(data.map(d => d.name))
                    .range(d3.quantize(t => d3.interpolateSpectral(t * 0.8 + 0.1), data.length))

    const labelRadius = arc.outerRadius()() * 0.8;

    // A separate arc generator for labels 
    // Used to check if there is enough space for the label
    const arcLabel = d3.arc()
        .innerRadius(labelRadius)
        .outerRadius(labelRadius);

    // Draw the slices of the pie
    svg.selectAll("path")
        .data(pie(data))
        .enter()
        .append("path")
            .attr("d", arc)
            .attr("fill", d => color(d.data.name))
            .attr("stroke", "white")
        .style("stroke-width", "2px")
        // on hover, show the name of this category
        // TODO -> implement a more through mouseover behavior
        // like create a div that has:
        //
        // name
        // count
        // percentage of total vulnerabilities
        .append("title")
            .text(d => d.data.name); // show name on hover TODO make this more thorough
        

    // Add labels and count to each slice
    svg.selectAll("text")
        .data(pie(data))
        .enter()
        .append("text")
            // this is the bold label of the caregory
            .attr("transform", d => `translate(${arcLabel.centroid(d)})`) // using arcLabel instead of arc moves it towards the border
            .attr("text-anchor", "middle")
            .call(text => text.append("tspan")
                .attr("y", "-0.4em")
                .attr("font-weight", "bold")
                .text(d => d.data.name))
            // and this is the smaller label for the count of this category
            .call(text => text.filter(d => (d.endAngle - d.startAngle) > 0.25).append("tspan") // only show count if it will fit
                .attr("x", 0)
                .attr("y", "0.7em")
                .attr("fill-opacity", 0.7)
                .text(d => d.data.count));
} // setUpPieChart()

async function setUpSeveritySummary(){
    /* Sum number of vulnerabilities to show as a percentage */
    var num_vulnerabilities = 0;
    for (var i = 0; i < data.length; i++){
        num_vulnerabilities += data[i].count;
    }

    /* Add CVSS count text at top left of page for each category of vulnerability found*/
    const container = document.querySelector("#severity-lines")
    data.forEach(d => {
        const p = document.createElement("p");
        const span = document.createElement("span");
        const percentage = (100*(d.count / num_vulnerabilities)).toFixed(1); 
        span.textContent = `${d.name}: `;
        span.className = "bold";
        p.appendChild(span);
        p.appendChild(document.createTextNode(`${d.count} (${percentage}%)`));
        container.appendChild(p);
    });
} // setUpSeveritySummary()

let data = await getVulnerabilityDistribution();
setUpPieChart();
setUpSeveritySummary();