import "https://d3js.org/d3.v7.min.js";

var data = [
    { "component name" : 'software_component1', 'version':'1.0', "score" : 4 },
    { "component name" : 'software_component2', 'version':'1.0', "score" : 5 },
    { "component name" : 'software_component3', 'version':'1.0', "score" : 7 },
    { "component name" : 'software_component4', 'version':'1.0', "score" : 0 },
    { "component name" : 'software_component5', 'version':'1.0', "score" : 6 },
    { "component name" : 'software_component6', 'version':'1.0', "score" : 6 },
    { "component name" : 'software_component7', 'version':'1.0', "score" : 1 },
    { "component name" : 'software_component8', 'version':'1.0', "score" : 2 },
    { "component name" : 'software_component9', 'version':'1.0', "score" : 8 },
    { "component name" : 'software_component10', 'version':'1.0', "score" : 0 },
    { "component name" : 'software_component11', 'version':'1.0', "score" : 9 }
  ]

  /*
   * From :
   *    https://gist.github.com/jfreels/6733593
   * With styling from:
   *    https://codepen.io/blackjacques/pen/RYVpKZ
   */

  function tabulate(data, columns) {
	var table = d3.select('#vulner-table').append('table')
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

// render the table
data.sort((a,b) => b.score - a.score); // sort by highest value
tabulate(data.slice(0,10), ['component name', 'version', 'score']); // table with all columns

/*
if data comes in as csv:
d3.csv("path/to/data.csv", function(data) {
  tabulate(data, ["name", "age"]);
});
*/