import streamlit as st
import plotly.express as px


def render_page_header(title: str, subtitle: str = ""):
    st.title(title)

    if subtitle:
        st.caption(subtitle)


def render_section_header(title: str):
    st.markdown(f"### {title}")


def render_divider():
    st.markdown("---")


def render_kpi_card(label: str, value, delta: str = None):
    st.metric(
        label=label,
        value=value,
        delta=delta
    )


def render_kpi_row(kpis: list):
    cols = st.columns(len(kpis))

    for col, kpi in zip(cols, kpis):
        with col:
            render_kpi_card(
                label=kpi.get("label"),
                value=kpi.get("value"),
                delta=kpi.get("delta")
            )


def render_bar_chart(df, x: str, y: str, title: str):
    if df.empty:
        st.info("No data available.")
        return

    fig = px.bar(
        df,
        x=x,
        y=y,
        title=title
    )

    st.plotly_chart(fig, use_container_width=True)


def render_area_chart(df, x: str, y: str, title: str):
    if df.empty:
        st.info("No data available.")
        return

    fig = px.area(
        df,
        x=x,
        y=y,
        title=title
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def render_funnel_chart(df, x: str, y: str, title: str):
    if df.empty:
        st.info("No data available.")
        return

    fig = px.funnel(
        df,
        x=x,
        y=y,
        title=title
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


def render_gauge_chart(title: str, value: float, max_value: float = 100):
    import plotly.graph_objects as go

    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            title={"text": title},
            gauge={
                "axis": {
                    "range": [0, max_value]
                }
            }
        )
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )



def render_line_chart(df, x: str, y: str, title: str):
    if df.empty:
        st.info("No data available.")
        return

    fig = px.line(
        df,
        x=x,
        y=y,
        title=title,
        markers=True
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )



def render_pie_chart(df, names: str, values: str, title: str):
    if df.empty:
        st.info("No data available.")
        return

    fig = px.pie(
        df,
        names=names,
        values=values,
        title=title
    )

    st.plotly_chart(fig, use_container_width=True)


def render_table(df, title: str = None):
    if title:
        st.markdown(f"### {title}")

    if df.empty:
        st.info("No records available.")
        return

    st.dataframe(
        df,
        use_container_width=True
    )


def render_select_filter(label: str, options: list, default_index: int = 0):
    return st.selectbox(
        label,
        options,
        index=default_index
    )


def render_multiselect_filter(label: str, options: list):
    return st.multiselect(
        label,
        options
    )


def render_date_filter(label: str):
    return st.date_input(label)