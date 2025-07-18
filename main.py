import streamlit as st
import requests

# Ganti dengan URL Flask backend kamu
FLASK_BACKEND_URL = "https://fdff88e3-377b-4931-9cfc-1670909b1a1d-00-2aklbh6fa4lv3.pike.replit.dev/"

# Konfigurasi halaman
st.set_page_config(page_title="Asisten Belajar", layout="wide")
st.title("📚 Asisten Belajar")

st.markdown("""
<style>
    .big-font {
        font-size:18px !important;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-size: 16px;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Input pertanyaan atau ID
st.markdown("### ❓ Tanyakan Sesuatu atau Masukkan ID Paper")
user_input = st.text_input("", placeholder="Contoh: Apa itu AI? atau 2401.12345")

if st.button("🔍 Cari"):
    with st.spinner("Sedang memproses..."):
        if any(c.isdigit() for c in user_input):
            # Kalau berisi angka, dianggap ID paper
            response = requests.post(f"{FLASK_BACKEND_URL}/get_paper_content", json={"paper_id": user_input})
            paper_info = response.json()
            if 'error' not in paper_info:
                st.success("✅ Paper Ditemukan!")
                st.subheader(paper_info['title'])
                st.write(f"**Penulis:** {', '.join(paper_info['authors'])}")
                st.write(f"**Tanggal Publikasi:** {paper_info['published']}")
                st.markdown("---")
                st.markdown("### 📄 Ringkasan")
                st.write(paper_info['summary'])
                st.markdown(f"[📥 Download PDF]({paper_info['pdf_url']})", unsafe_allow_html=True)
            else:
                st.error(paper_info['error'])
        else:
            # Kalau pertanyaan umum
            response = requests.post(f"{FLASK_BACKEND_URL}/research_assistant", json={"query": user_input})
            result = response.json()
            st.markdown("### 🤖 Jawaban Asisten Belajar")
            st.info(result.get('response', result.get('error', 'Tidak ada jawaban.')))

# Tambahan Fitur Lanjutan (bisa disembunyikan untuk pemula)
with st.expander("🔬 Cari Topik Penelitian"):
    topic = st.text_input("Masukkan topik:")
    max_results = st.slider("Jumlah hasil:", 1, 10, 3)
    if st.button("🔎 Cari Paper"):
        with st.spinner("Mencari..."):
            response = requests.post(
                f"{FLASK_BACKEND_URL}/search_papers",
                json={"topic": topic, "max_results": max_results}
            )
            st.json(response.json())
