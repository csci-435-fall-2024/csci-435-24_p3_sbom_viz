import "https://d3js.org/d3.v7.min.js";

// Temporary vulnerability distribution data (replace with endpoint later)
let data = [
    {name:"Critical", count:10},
    {name:"High", count:20},
    {name:"Medium", count:10},
    {name:"Low", count:30},
    {name:"None", count:90},
]

// Inspired by https://d3-graph-gallery.com/graph/pie_annotation.html
const width = 500;
const height = 500;
const margin = 50;

let radius = Math.min(width, height) / 2 - margin

let svg = d3.select("#pie-chart-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .append("g")
            .attr("transform", `translate(${width/2},${height/2})`);

// set the color scale
/*var color = d3.scaleOrdinal()
  .domain(vulnerability_counts)
  .range(d3.schemeSet2);*/

const arc = d3.arc()
            .innerRadius(0)
            .outerRadius(radius)

// Compute the position of each group on the pie:
var pie = d3.pie();

const color = d3.scaleOrdinal()
                .domain(data.map(d => d.name))
                .range(d3.schemeSet2);

svg.append("g")
.selectAll()
.data(pie(data.map(d => d.count)))
.join("path")
    .attr("fill", d => color(d))
    .attr("d", arc)
.append("title")
    .text(d => {console.log(d.data)});