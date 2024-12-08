import "https://d3js.org/d3.v7.min.js";

import { getLicenseData } from './license_data.js';

  function tabulate(data, columns) {
    var table = d3.select('#license-table').append('table')
          .style("border", "2px black solid")
          .style("border-collapse", "collapse");
    var thead = table.append('thead');
    var	tbody = table.append('tbody');

    // append the header row
    thead.append('tr')
      .selectAll('th')
      .data(columns).enter()
      .append('th')
        .text(function (d) { return d; })
          .style("border", "1px black solid")
          .style("padding", "5px")
          .style("background-color", "lightgray")
          .style("font-weight", "bold")
          .style("text-transform", "uppercase");

    // create a row for each object in the data
    var rows = tbody.selectAll('tr')
      .data(data)
      .enter()
      .append('tr')
        
    // create a cell in each row for each column
    var cells = rows.selectAll('td')
      .data(function (row) {
        return columns.map(function (column) {
          return {column: column, value: row[column]};
        });
      })
      .enter()
      .append('td')
        .text(function (d) { return d.value; })
          .style("border", "1px black solid")
          .style("padding", "5px")
          .on("mouseover", function(){
              d3.select(this).style("background-color", "powderblue");
          })
          .on("mouseout", function(){
              d3.select(this).style("background-color", "white");
          });

  return table;
}


async function setUpTable(){

  const licenses = await getLicenseData();

  // Calculate percentage composition for each license of total
  let total_count = licenses.reduce((acc, license) => acc + license["count"], 0);
  licenses.forEach(license => {
      license["composition"] = `${(license["count"] / total_count * 100).toFixed(1)}%`
  });

  console.log(licenses);

  // Count the number of distinct licenses
  // count all rows except for the "other" row, if it is present
  let num_licenses = licenses.reduce((acc, license) => ((license["license"] !== "other") ? acc + 1 : acc), 0); 
  // update the number of distinct licenses
  document.getElementById("number-distinct-licenses").textContent = num_licenses;

  const columns = ["License", "Restrictiveness", "Count", "Composition"];

  function updateTable(filter = 'all') {
    const table = d3.select("#licenseTable");
    table.html('') // Clear existing table 
    const tableBody = table.append('tbody');

    // Filter data based on restrictiveness
    const filteredData = licenses.filter(d => {
      const restrictiveness = d.restrictiveness.toLowerCase() || 'unknown'; // Treat empty string as 'unknown'
      return filter === 'all' || restrictiveness === filter.toLowerCase();
    });

    var thead = table.append("thead");

    // append the header row
    thead.append('tr')
      .selectAll('th')
      .data(columns)
      .enter()
      .append('th')
        .text(function (d) { return d; })

    // Create table rows and cells with stylings
    const rows = tableBody.selectAll('tr')
      .data(filteredData)
      .enter()
      .append('tr');

    // Append cells to each row
    rows.selectAll('td')
      .data(d => [
        d.license, 
        d.restrictiveness || 'Unknown', 
        d.count,
        d.composition]) // Map data to table cells
      .enter()
      .append('td')
      .text(d => d)
      .style("border", "1px black solid")
      .style("padding", "5px")
      .on("mouseover", function() {
        d3.select(this).style("background-color", "powderblue");
      })
      .on("mouseout", function() {
        d3.select(this).style("background-color", "white");
      });

    // Style header row
    d3.selectAll('thead th')
      .style("border", "1px black solid")
      .style("padding", "5px")
      .style("background-color", "lightgray")
      .style("font-weight", "bold");

    // Style the table
    d3.select('#licenseTable')
      .style("border", "2px black solid")
      .style("border-collapse", "collapse");
  }

  // Initial table load
  updateTable();

  // Filter table based on dropdown selection
  d3.select('#restrictivenessFilter').on('change', function() {
    const filter = d3.select(this).property('value').toLowerCase();
    updateTable(filter);
  });
}

setUpTable();