import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import base64
import mimetypes
from pathlib import Path
from src import style_utils


HUE_PALETTE =["#56B4E9",  # sky blue
        "#009E73",  # bluish green
        "#F0E442",  # yellow
        "#D55E00",  # vermillion
        "#CC79A7",  # reddish purple
        "#E69F00",  # orange
        "#0072B2",  # blue
    ]



class App:
    def __init__(self):
        style_utils.setup_ui("Example user interface for bioinformatics task")
        self.iris_df = pd.read_csv("data/Iris.csv").rename(
            columns={
                "SepalLengthCm": "sepal_length",
                "SepalWidthCm": "sepal_width",
                "PetalLengthCm": "petal_length",
                "PetalWidthCm": "petal_width",
                "Species": "species",
            }
        )

        self.text_path = Path("data/text.md")
        with self.text_path.open("r", encoding="utf-8") as f:
            self.text_content = f.read()

    def render_markdown_with_local_images(self, markdown_text: str):
        """Render markdown and resolve local image links relative to the markdown file."""
        image_pattern = re.compile(r"!\[(.*?)\]\((.*?)\)")
        pending_lines: list[str] = []

        for line in markdown_text.splitlines():
            match = image_pattern.fullmatch(line.strip())
            if not match:
                pending_lines.append(line)
                continue

            if pending_lines:
                st.markdown("\n".join(pending_lines), unsafe_allow_html=True)
                pending_lines = []

            alt_text, image_ref = match.groups()
            image_path = (self.text_path.parent / image_ref).resolve()
            if image_path.exists():
                mime_type = mimetypes.guess_type(str(image_path))[0] or "image/png"
                image_b64 = base64.b64encode(image_path.read_bytes()).decode("utf-8")
                st.markdown(
                    (
                        f'<img src="data:{mime_type};base64,{image_b64}" '
                        'style="width:30%; max-width:100%;" />'
                    ),
                    unsafe_allow_html=True,
                )
                if alt_text:
                    st.caption(alt_text)
            else:
                st.warning(f"Image not found: {image_ref}")

        if pending_lines:
            st.markdown("\n".join(pending_lines), unsafe_allow_html=True)

    def add_species_kde_tab(self):
        """Render species selector on the left and contour plot on the right."""
        selector_col, plot_col = st.columns([1, 2])

        with selector_col:
            species_options = sorted(self.iris_df["species"].dropna().astype(str).unique().tolist())
            selected_species = style_utils.render_feature_selector(
                species_options,
                "Select species to include in the plot.",
                "species_feature_checkbox",
            )

        with plot_col:
            if not style_utils.validate_feature_selection(
                selected_species,
                min_features=1,
                plot_name="Iris Sepal contour plot",
            ):
                return

            filtered_iris_df = self.iris_df[self.iris_df["species"].isin(selected_species)].copy()
            fig = go.Figure()
            for idx, species in enumerate(selected_species):
                species_df = filtered_iris_df[filtered_iris_df["species"] == species]
                fig.add_trace(
                    go.Histogram2dContour(
                        x=species_df["sepal_length"],
                        y=species_df["sepal_width"],
                        name=species,
                        line=dict(
                            color=HUE_PALETTE[idx % len(HUE_PALETTE)],
                            width=3,
                        ),
                        contours=dict(coloring="none"),
                        showscale=False,
                        hoverinfo="skip",
                    )
                )

            fig.update_layout(
                title="Iris Sepal Contour by Species",
                xaxis_title="Sepal length (cm)",
                yaxis_title="Sepal width (cm)",
                xaxis=dict(
                    showline=True,
                    linewidth=2,
                    linecolor="black",
                    mirror=True,
                    showgrid=True,
                ),
                yaxis=dict(
                    showline=True,
                    linewidth=2,
                    linecolor="black",
                    mirror=True,
                    showgrid=True,
                ),
            )
            fig = style_utils.style_plot_text(fig)
            st.plotly_chart(
                fig,
                use_container_width=True,
                config=style_utils.get_plotly_config(),
            )

    def add_species_3d_scatter_tab(self):
        """Render a 3D scatter plot in the 3D tab area."""
        selector_col, plot_col = st.columns([1, 2])

        with selector_col:
            species_options = sorted(self.iris_df["species"].dropna().astype(str).unique().tolist())
            selected_species = style_utils.render_feature_selector(
                species_options,
                "Select species to include in the 3D scatter plot.",
                "scatter3d_species_feature_checkbox",
            )

        with plot_col:
            if not style_utils.validate_feature_selection(
                selected_species,
                min_features=1,
                plot_name="3D scatter plot",
            ):
                return

            filtered_iris_df = self.iris_df[self.iris_df["species"].isin(selected_species)].copy()
            fig = px.scatter_3d(
                filtered_iris_df,
                z="sepal_length",
                y="sepal_width",
                x="petal_length",
                color="species",
                symbol="species",
                symbol_sequence=["circle", "diamond", "square"],
                color_discrete_sequence=HUE_PALETTE,
                title="Iris Sepal and Petal Dimensions",
            )
            fig.update_layout(
                scene=dict(
                    xaxis_title="Sepal length (cm)",
                    yaxis_title="Sepal width (cm)",
                    zaxis_title="Petal length (cm)",
                    aspectmode="cube",
                )
                ,
                margin=dict(l=0, r=0, t=60, b=0),
            )
            fig.add_shape(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=1,
                line=dict(
                    color="black",
                    width=4,
                ),
            )
            fig = style_utils.style_plot_text(fig)
            st.plotly_chart(
                fig,
                use_container_width=True,
                config=style_utils.get_plotly_config(),
            )

    def run(self):

        tab_2d, tab_3d = st.tabs(["2D tab", "3D tab"])

        with tab_2d:
            style_utils.question("0.0", "This is an example question.", self.add_species_kde_tab)

        with tab_3d:
            style_utils.question("0.1", "This is an another example question.", self.add_species_3d_scatter_tab)

        st.header("Instructions and notes")
        self.render_markdown_with_local_images(self.text_content)

if __name__ == "__main__":
    
    app = App()
    app.run()