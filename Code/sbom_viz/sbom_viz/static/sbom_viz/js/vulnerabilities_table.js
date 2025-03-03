import "https://d3js.org/d3.v7.min.js";
import { getVulnerabilityTableData } from "./vulnerability_data.js";

/*
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
*/

  /*
   * From :
   *    https://gist.github.com/jfreels/6733593
   * With styling from:
   *    https://codepen.io/blackjacques/pen/RYVpKZ
   */

async function tabulate(data, columns) {        
  var table = d3.select("#vulnTable")
	var thead = table.append('thead');
	var	tbody = table.append('tbody');

	// append the header row
	thead.append('tr')
	  .selectAll('th')
	  .data(columns).enter()
	  .append('th')
	    .text(function (d) { return d; });

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
      // If this is the 'cve_id' column, then make 
      // the cve_id a link rather than text
	    .html(function (d){
        if (d.column == "CVE ID"){
          return `<a href="https://nvd.nist.gov/vuln/detail/${d.value}" target="_blank" >${d.value}</a>`;
        }
        return d.value; 
      })
        .on("mouseover", function(){
            d3.select(this).style("background-color", "powderblue");
        })
        .on("mouseout", function(){
            d3.select(this).style("background-color", "white");
        });

  return table;
}


getVulnerabilityTableData().then(s => {
  tabulate(s, ['Component', 'CVE ID', 'Score', 'Severity', 'Title']); // table with all columns
  });


// render the table
//data.sort((a,b) => b.score - a.score); // sort by highest value
//tabulate(data, ['SBOM_ID', 'SeveritySource', 'Title', 'Displayed_CVSS']); // table with all columns

/*
if data comes in as csv:
d3.csv("path/to/data.csv", function(data) {
  tabulate(data, ["name", "age"]);
});
*/