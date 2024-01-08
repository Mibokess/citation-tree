import dash
from dash import html, dcc, Input, Output, State
import plotly.graph_objects as go
from citation_tree.tree import search_paper, get_paper_citations

api_key = ""
api_url = "https://api.semanticscholar.org/graph/v1"
paper_url = f"{api_url}/paper"
search_url = f"{paper_url}/search"

# Initialize Dash app
app = dash.Dash(
    __name__, external_stylesheets=["https://codepen.io/chriddyp/pen/bWLwgP.css"]
)


@app.callback(
    Output("citation-graph", "figure"),
    [Input("search-button", "n_clicks")],
    [State("input-query", "value")],
)
def update_graph(n_clicks, query):
    if n_clicks > 0 and query:
        search_response = search_paper(query, f"{paper_url}/search", api_key)
        if search_response:
            paper_id = search_response["paperId"]
            paper_citations = get_paper_citations(paper_id, paper_url, api_key)

            # Sort and group citations by year
            sorted_citations = sorted(
                paper_citations, key=lambda x: x["citingPaper"].get("year", 0)
            )
            citations_by_year = {}
            for citation in sorted_citations:
                year = citation["citingPaper"].get("year", 0)
                citations_by_year.setdefault(year, []).append(citation)

            # Prepare data for visualization
            nodes_x = []
            nodes_y = []
            node_text = []
            edges = []

            # Determine root paper year and position
            root_year = search_response.get("year", 0)
            root_x = (
                sorted(list(citations_by_year.keys()) + [root_year]).index(root_year)
                + 1
            )
            nodes_x.append(root_x)
            nodes_y.append(0)
            node_text.append(search_response["title"])

            # Iterate over each year and position citations vertically
            for year, citations in citations_by_year.items():
                year_x = (
                    sorted(list(citations_by_year.keys()) + [root_year]).index(year) + 1
                )
                for iy, citation in enumerate(citations, start=1):
                    nodes_x.append(year_x)
                    nodes_y.append(iy)
                    node_text.append(citation["citingPaper"]["title"])
                    edges.append((len(nodes_x), 1))  # Index of current citation to root

            # Create edges for the graph
            edge_x = []
            edge_y = []
            edge_marker = dict(color="rgba(0,0,0,0.5)", width=1, arrowhead=2)
            for edge in edges:
                x0, y0 = nodes_x[edge[0] - 1], nodes_y[edge[0] - 1]
                x1, y1 = nodes_x[edge[1] - 1], nodes_y[edge[1] - 1]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

            # Create the figure
            fig = go.Figure()

            # Add nodes (papers) to the figure
            fig.add_trace(
                go.Scatter(
                    x=nodes_x,
                    y=nodes_y,
                    mode="markers+text",
                    text=node_text,
                    textposition="bottom center",
                )
            )

            # Add edges (citations) as lines
            for edge in edges:
                x0, y0 = nodes_x[edge[0] - 1], nodes_y[edge[0] - 1]
                x1, y1 = nodes_x[edge[1] - 1], nodes_y[edge[1] - 1]
                fig.add_trace(
                    go.Scatter(
                        x=[x0, x1],
                        y=[y0, y1],
                        mode="lines",
                        line=dict(color="rgba(0,0,0,0.5)", width=1),
                    )
                )

            # Add annotations for arrows
            annotations = []
            for edge in edges:
                x0, y0 = nodes_x[edge[0] - 1], nodes_y[edge[0] - 1]
                x1, y1 = nodes_x[edge[1] - 1], nodes_y[edge[1] - 1]
                annotations.append(
                    dict(
                        x=x1,
                        y=y1,
                        ax=x0,
                        ay=y0,
                        xref="x",
                        yref="y",
                        axref="x",
                        ayref="y",
                        showarrow=True,
                        arrowhead=2,
                        arrowsize=1,
                        arrowwidth=1,
                        arrowcolor="rgba(0,0,0,0.5)",
                    )
                )

            fig.update_layout(annotations=annotations)
            fig.update_layout(
                xaxis_title="Publication Year",
                yaxis_title="Citations",
                showlegend=False,
                paper_bgcolor="rgba(0,0,0,0)",  # Transparent background
                plot_bgcolor="rgba(0,0,0,0)",  # Transparent background
                margin=dict(l=0, r=0, t=0, b=0),  # Reduce plot margins
                font=dict(size=12, color="RebeccaPurple"),  # Custom font styling
            )
            return fig


# Function to create the initial graph
def create_initial_graph():
    default_query = "OneFormer"
    return update_graph(1, default_query)  # Assume n_clicks=1 and query="OneFormer"


# App layout with improved styling
app.layout = html.Div(
    [
        html.Div(
            [
                dcc.Input(
                    id="input-query",
                    type="text",
                    value="OneFormer",
                    placeholder="Enter Paper Title",
                    style={
                        "width": "70%",
                        "display": "inline-block",
                        "margin-right": "10px",
                    },
                ),
                html.Button(
                    "Search",
                    id="search-button",
                    n_clicks=1,
                    style={"width": "20%", "display": "inline-block"},
                ),
            ],
            style={"margin-bottom": "20px"},
        ),
        dcc.Graph(
            id="citation-graph", figure=create_initial_graph(), style={"height": "80vh"}
        ),
    ],
    style={"padding": "20px"},
)


# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
