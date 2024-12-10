import "https://d3js.org/d3.v7.min.js";
import { getLicenseData } from "./license_data.js";

async function setUpPieChart() {
    let data_full = await getLicenseData();

    let data = data_full.map(entry => ({"license": entry["license"], "count": entry["count"]})).filter(license => license["license"] !== "other");
    data = data.slice(0,10);
    // Inspired by https://d3-graph-gallery.com/graph/pie_annotation.html
    const width = 500;
    const height = 500;
    const margin = 50;
    
    let radius = Math.min(width, height) / 2 - margin
    
    const svg = d3.select("#license-pie-chart-container")
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
    
    // Use different colors from the vulnerabilities page,
    // because we don't have a measure of how 'severe' different
    // licenses are (which we do have for the vuln. page)
    const color = d3.scaleOrdinal(d3.schemeObservable10);

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
            .attr("fill", d => color(d.data["license"]))
            .attr("stroke", "white")
        .style("stroke-width", "2px")
        // on hover, show the name of this category and the count
        .append("title")
            .text(d => `${d.data["license"]}\n${d.data.count}`);
        
    
    // Add labels and count to each slice -
    // Only if there is space to do so
    svg.selectAll("text")
        .data(pie(data))
        .enter()
        .append("text")
            // this is the bold label of the caregory
            .attr("transform", d => `translate(${arcLabel.centroid(d)})`) // using arcLabel instead of arc moves it towards the border
            .attr("text-anchor", "middle")
            .call(text => text.filter(d => (d.endAngle - d.startAngle) > 0.25).append("tspan")
                .attr("y", "-0.4em")
                .attr("font-weight", "bold")
                .text(d => d.data["license"]))
            // and this is the smaller label for the count of this category
            .call(text => text.filter(d => (d.endAngle - d.startAngle) > 0.25).append("tspan") // only show count if it will fit
                .attr("x", 0)
                .attr("y", "0.7em")
                .attr("fill-opacity", 0.7)
                .text(d => d.data.count));
    
    
    /* Sum number of licenses to show as a percentage */
    /*var num_vulnerabilities = 0;
    for (var i = 0; i < data.length; i++){
        num_vulnerabilities += data[i].count;
    }*/
}

setUpPieChart();