import streamlit as st
from st_files_connection import FilesConnection

# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
conn = st.connection('s3', type=FilesConnection)
df = conn.read("projet3-avions/exports_mageAI/delays_20250204_140042.csv", input_format="csv", ttl=600)
st.dataframe(df)