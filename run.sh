#!/bin/bash
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.
streamlit run app.py
