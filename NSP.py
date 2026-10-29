import streamlit as st
from PIL import Image
import fitz
import pandas as pd
import sqlite3
import io

st.set_page_config(page_title="Land Record Digitization", layout="centered")
st.title("Land Record Digitization System")
st.write("Smart India Hackathon 2026 - SIH26018")

# Database setup
conn = sqlite3.connect("land_records.db")
conn.execute("""
CREATE TABLE IF NOT EXISTS land_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    state TEXT, district TEXT, tehsil TEXT, village TEXT,
    khata TEXT, khasra TEXT, area TEXT, classification TEXT
)
""")
conn.commit()

# Upload document
file = st.file_uploader("Upload Land Record", type=["jpg", "jpeg", "png", "pdf"])

if file:
    try:
        if file.name.lower().endswith(".pdf"):
            doc = fitz.open(stream=file.getvalue(), filetype="pdf")
            if len(doc) == 0:
                st.error("PDF has no pages.")
                st.stop()
            pix = doc[0].get_pixmap(colorspace=fitz.csRGB, alpha=False)
            image = Image.open(io.BytesIO(pix.tobytes("png")))
        else:
            image = Image.open(file).convert("RGB")

        st.image(image, caption="Uploaded Document", use_container_width=True)

        # Sample data (replace with actual OCR extraction)
        fields = {
            "State": "Rajasthan",
            "District": "Jaipur",
            "Tehsil": "Sanganer",
            "Village": "Achrawala",
            "Khata Number": "01",
            "Khasra Number": "124, 125",
            "Total Area": "0.4550 Hectares",
            "Land Classification": "Agricultural"
        }

        st.subheader("Land Record Details")
        for key, value in fields.items():
            st.write(f"**{key}:** {value}")

        st.subheader("Human Verification")
        khasra = st.text_input("Verify Khasra Number", fields["Khasra Number"])

        if st.button("Save Verified Record"):
            conn.execute("""
                INSERT INTO land_records
                (state, district, tehsil, village, khata,
                 khasra, area, classification)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                fields["State"], fields["District"], fields["Tehsil"],
                fields["Village"], fields["Khata Number"], khasra,
                fields["Total Area"], fields["Land Classification"]
            ))
            conn.commit()
            st.success("Record saved successfully!")

    except Exception as e:
        st.error(f"Could not process file: {e}")

# View saved records
st.divider()
st.subheader("Saved Land Records")

records = pd.read_sql_query("SELECT * FROM land_records", conn)
st.dataframe(records, use_container_width=True, hide_index=True)

# Export records
if not records.empty:
    st.download_button(
        "Download Records as CSV",
        records.to_csv(index=False),
        "land_records.csv",
        "text/csv"
    )

conn.close()
