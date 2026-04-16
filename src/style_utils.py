"""Styling utilities and helpers for the Streamlit application."""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path


def get_plotly_config():
    """Get default Plotly configuration for interactive charts."""
    return {
        "scrollZoom": True,
        "displayModeBar": True,
        "displaylogo": False,
        "modeBarButtonsToRemove": [
            "toImage",
            "lasso2d",
            "select2d",
            "orbitRotation",
            #"tableRotation",
            "resetCameraDefault3d",
            "resetCameraLastSave3d",
        ],
    }


def setup_ui(page_title: str = "Example of interactive plots for bioinformatics data analysis"):
    """Setup main UI elements including page config and custom styling."""
    st.set_page_config(layout="wide")
    st.markdown(
        """
        <style>
        /* Keep modebar icons visible and 2x larger for Streamlit Plotly charts. */
        .stPlotlyChart .modebar {
            transform: scale(2);
            transform-origin: top right;
        }

        /* Increase Streamlit tabs size: larger font, padding and minimum dimensions. */
        div[role="tablist"] > button[role="tab"] {
            font-size: 22px !important;
            padding: 10px 18px !important;
            min-height: 48px !important;
            min-width: 140px !important;
            border-radius: 8px !important;
        }

        /* Make the selected tab slightly more prominent. */
        div[role="tablist"] > button[role="tab"][aria-selected="true"] {
            font-weight: 700 !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.08) !important;
        }

        /* Keep checkboxes vertically aligned with their labels. */
        div[data-testid="stCheckbox"] label {
            align-items: center;
            gap: 0.5rem;
        }

        div[data-testid="stCheckbox"] label p {
            margin: 0;
            line-height: 1.35;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.title(page_title)


def style_plot_text(fig, title_font_size: int = 22, label_font_size: int = 16):
    """Apply unified text styling to Plotly figures.
    
    Args:
        fig: Plotly figure object
        title_font_size: Font size for plot titles
        label_font_size: Font size for axis labels and legends
        
    Returns:
        Styled Plotly figure object
    """
    title_text = getattr(getattr(fig.layout, "title", None), "text", None)
    if title_text is None or str(title_text).strip().lower() == "undefined":
        title_text = ""

    text_color = "black"
    label_font = dict(size=label_font_size, color=text_color)
    axis_font = dict(title_font=label_font, tickfont=label_font)

    fig.update_layout(
        font=dict(color=text_color),
        title=dict(
            text=title_text,
            font=dict(size=title_font_size, color=text_color),
        ),
        annotationdefaults=dict(font=label_font),
        legend=dict(
            font=label_font,
            title=dict(font=label_font),
        ),
    )

    fig.for_each_xaxis(lambda axis: axis.update(**axis_font))
    fig.for_each_yaxis(lambda axis: axis.update(**axis_font))

    if "scene" in fig.layout and fig.layout.scene:
        fig.update_layout(
            scene=dict(
                dragmode="zoom",
                xaxis=dict(
                    title_font=label_font,
                    tickfont=label_font,
                ),
                yaxis=dict(
                    title_font=label_font,
                    tickfont=label_font,
                ),
                zaxis=dict(
                    title_font=label_font,
                    tickfont=label_font,
                ),
                aspectmode="cube",
            )
        )

    # Apply to existing annotations as well (e.g., facet subplot titles).
    if fig.layout.annotations:
        fig.update_annotations(font=label_font)

    return fig




def question(ids, text, function):
    """Render question section(s) with bordered container and numbered label.
    
    Args:
        ids: Single question id string (e.g. "1.2.3") or list of ids to render in sequence
        text: Question description/title text
        function: Callable to render content inside the bordered container
    """
    
    ids = [ids] if isinstance(ids, str) else ids
    

    st.subheader("".join([f"Q.{q_id}" for q_id in ids]))
    st.text(text)
    with st.container(border=True):
        function()


def render_feature_selector(
    feat_cols: list[str],
    help_text: str,
    checkbox_key_prefix: str,
    col_count: int = 1,
) -> list[str]:
    """Render a reusable feature checkbox grid and return selected feature names.

    This is a generalized version that accepts the feature column list rather
    than relying on any class state.
    """
    selected_features: list[str] = []

    with st.container(border=True):

        for feat in feat_cols:
            if st.checkbox(label=feat, value=True, key=f"{checkbox_key_prefix}_{feat}"):
                selected_features.append(feat)

    return selected_features


def validate_feature_selection(
    selected_features: list[str],
    min_features: int,
    plot_name: str,
) -> bool:
    """Validate selected feature count and show a generic warning when insufficient."""
    if len(selected_features) < min_features:
        feature_word = "feature" if min_features == 1 else "features"
        st.warning(
            f"Please select at least {min_features} {feature_word} to display the {plot_name}."
        )
        return False
    return True
