import "https://d3js.org/d3.v7.min.js";

var data = [
    { "license name" : 'license1', 'version':'1.0', "count" : 4 },
    { "license name" : 'license2', 'version':'1.0', "count" : 17 },
    { "license name" : 'license3', 'version':'1.0', "count" : 2 },
    { "license name" : 'license4', 'version':'1.0', "count" : 1 },
    { "license name" : 'license5', 'version':'1.0', "count" : 3 },
    { "license name" : 'license6', 'version':'1.0', "count" : 7 },
    { "license name" : 'license7', 'version':'1.0', "count" : 9 },
    { "license name" : 'license8', 'version':'1.0', "count" : 1 },
    { "license name" : 'license9', 'version':'1.0', "count" : 8 },
    { "license name" : 'license10', 'version':'1.0', "count" : 0 },
    { "license name": 'other', 'version':'n/a', "count": 10 }, // for unidentifiable or missing license types
  ]

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

// Calculate percentage composition for each license of total
let total_count = data.reduce((acc, license) => acc + license["count"], 0);
data.forEach(license => {
    license["composition"] = `${(license["count"] / total_count * 100).toFixed(1)}%`
});

// render the table
data.sort((a,b) => b.count - a.count); // sort by highest value
tabulate((data.filter(license => license["license name"] !== "other")).slice(0,10), ['license name', 'version', 'count', 'composition']); // table with all columns

// Count the number of distinct licenses
let num_licenses = data.reduce((acc, license) => ((license["license name"] !== "other") ? acc + 1 : acc), 0); // count all rows except for the "other" row, if it is present
document.getElementById("number-distinct-licenses").textContent = num_licenses;

/*
if data comes in as csv:
d3.csv("path/to/data.csv", function(data) {
  tabulate(data, ["name", "age"]);
});
*/