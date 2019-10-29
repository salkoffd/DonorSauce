// Build graphs for summary statistics

var url = "/api/summary";
d3.json(url).then(function (response) {
    // Graph 1
    var data = [
        {
            x: response.largest_recipients_amount,
            y: response.largest_recipients,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: "#1fd5d5"
            }
        }
    ];
    var layout = {
        title: 'Top $ Recipients',
        plot_bgcolor: "#e7c183",
        paper_bgcolor: "#e7c183",
        xaxis: {
            title: "$"
        },
        yaxis: {
            autorange: 'reversed',
            automargin: true
        }
    };

    Plotly.newPlot('topRecipientsGraph', data, layout);

    // Graph 2
    var data = [
        {
            x: response.biggest_donors_amount,
            y: response.biggest_donors,
            type: 'bar',
            orientation: 'h',
            marker: {
                color: "#1fd5d5"
            }
        }
    ];
    var layout = {
        title: 'Top $ Donors',
        plot_bgcolor: "#e7c183",
        paper_bgcolor: "#e7c183",
        xaxis: {
            title: "$"
        },
        yaxis: {
            autorange: 'reversed',
            automargin: true
        }
    };

    Plotly.newPlot('topDonorGraph', data, layout);

    // Graph 3
    var trace1 = {
        x: response.democrat_info.ages,
        y: response.democrat_info.amounts,
        mode: 'markers',
        type: 'scatter',
        name: 'Democrats',
        hovertext: response.democrat_info.names,
        hoverinfo: "text",
        // text: ['A-1', 'A-2', 'A-3', 'A-4', 'A-5'],
        marker: {
            size: 8,
            color: "#000bd4",
            line: {
                width: 0
            }
        },
        opacity: 0.6
    };
    var trace2 = {
        x: response.republican_info.ages,
        y: response.republican_info.amounts,
        mode: 'markers',
        type: 'scatter',
        name: 'Republicans',
        hovertext: response.republican_info.names,
        hoverinfo: "text",
        // text: ['A-1', 'A-2', 'A-3', 'A-4', 'A-5'],
        marker: {
            size: 8,
            color: "#d60b0b",
            line: {
                width: 0
            }
        },
        opacity: 0.6
    };

    var trace3 = {
        x: response.independent_info.ages,
        y: response.independent_info.amounts,
        mode: 'markers',
        type: 'scatter',
        name: 'Independent',
        text: response.independent_info.names,
        hoverinfo: "text",
        // text: ['A-1', 'A-2', 'A-3', 'A-4', 'A-5'],
        marker: {
            size: 8,
            color: "grey",
            line: {
                width: 0
            }
        },
        opacity: 0.6
    };

    var data = [trace1, trace2, trace3];

    var layout = {
        xaxis: {
            title: "Age (Years)"
        },
        yaxis: {
            title: "$"
        },
        title: 'Age vs. Money Received',
        plot_bgcolor: "white",
        paper_bgcolor: "#e7c183",
        hovermode:'closest',
        height: 800,
        width: 800
    };

    Plotly.newPlot('ageGraph', data, layout);
});