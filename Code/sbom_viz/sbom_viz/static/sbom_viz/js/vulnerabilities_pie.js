import "https://d3js.org/d3.v7.min.js";

// Temporary vulnerability distribution data (replace with endpoint later)
let data = [
    {"name":"Critical", "count":10},
    {"name":"High", "count":20},
    {"name":"Medium", "count":10},
    {"name":"Low", "count":30},
    {"name":"None", "count":90},
]

// Inspired by https://d3-graph-gallery.com/graph/pie_annotation.html
const width = 500;
const height = 500;
const margin = 50;

let radius = Math.min(width, height) / 2 - margin

const svg = d3.select("#pie-chart-container")
                .append("svg")
                    .attr("width", width)
                    .attr("height", height)
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

// Draw the slices of the pie
svg.selectAll("path")
    .data(pie(data))
    .enter()
    .append("path")
        .attr("d", arc)
        .attr("fill", d => color(d.data.name))
        .attr("stroke", "white")
    .style("stroke-width", "2px");

// Add labels to each slice
svg.selectAll("text")
    .data(pie(data))
    .enter()
    .append("text")
        .attr("transform", d => `translate(${arc.centroid(d)})`)
        .attr("dy", "0.35em")
        .attr("text-anchor", "middle")
    .text(d => d.data.name);