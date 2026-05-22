# imednet-streamlit

Interactive Streamlit reporting dashboards for iMednet EDC.

## Install

```bash
pip install ./packages/plugins-streamlit
```

## Run

```bash
streamlit run "$(python -c 'import imednet_streamlit.app as app; print(app.__file__)')"
```

> This currently launches a placeholder stub. The full Streamlit app scaffold is implemented in a follow-up task.
