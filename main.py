import streamlit as st
import arxiv
import json
import os
import time
import google.generativeai as genai
from google.api_core import exceptions
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# Konfigurasi halaman
st.set_page_config(page_title="Asisten Belajar", layout="wide")

# CSS Styling
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

# Inisialisasi session state
if 'gemini_configured' not in st.session_state:
    st.session_state.gemini_configured = False
if 'model' not in st.session_state:
    st.session_state.model = None

# Sidebar untuk API Key
with st.sidebar:
    st.header("⚙️ Konfigurasi")
    api_key = st.text_input("Gemini API Key:", type="password", help="Masukkan Google Gemini API Key Anda")
    
    if api_key and not st.session_state.gemini_configured:
        try:
            genai.configure(api_key=api_key)
            st.session_state.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            st.session_state.gemini_configured = True
            st.success("✅ API Key berhasil dikonfigurasi!")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    st.markdown("### 📖 Tentang")
    st.info("Asisten Belajar membantu Anda mencari paper ilmiah dan menjawab pertanyaan dengan AI.")

# Main content
st.title("📚 Asisten Belajar")

# Tab navigation
tab1, tab2 = st.tabs(["💬 Chat & Cari Paper", "🔬 Cari Topik Penelitian"])

with tab1:
    st.markdown("### ❓ Tanyakan Sesuatu atau Masukkan ID Paper")
    user_input = st.text_input("", placeholder="Contoh: Apa itu AI? atau 2401.12345", key="main_input")
    
    if st.button("🔍 Cari", key="main_search"):
        if not st.session_state.gemini_configured:
            st.warning("⚠️ Silakan masukkan API Key terlebih dahulu di sidebar!")
        elif user_input:
            with st.spinner("Sedang memproses..."):
                # Cek apakah input adalah ID paper (mengandung angka dan format arxiv)
                is_paper_id = any(c.isdigit() for c in user_input) and len(user_input) < 20
                
                if is_paper_id:
                    # Cari paper berdasarkan ID
                    try:
                        client = arxiv.Client()
                        search = arxiv.Search(id_list=[user_input.strip()])
                        paper = next(client.results(search))
                        
                        st.success("✅ Paper Ditemukan!")
                        st.subheader(paper.title)
                        st.write(f"**Penulis:** {', '.join([author.name for author in paper.authors])}")
                        st.write(f"**Tanggal Publikasi:** {paper.published.date()}")
                        st.markdown("---")
                        st.markdown("### 📄 Ringkasan")
                        st.write(paper.summary)
                        st.markdown(f"[📥 Download PDF]({paper.pdf_url})")
                        st.markdown(f"[🔗 Lihat di arXiv]({paper.entry_id})")
                        
                    except StopIteration:
                        st.error("❌ Paper tidak ditemukan. Pastikan ID paper benar.")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    # Pertanyaan umum - gunakan Gemini
                    try:
                        response = st.session_state.model.generate_content(
                            f"User bertanya: {user_input}. Berikan jawaban yang informatif dan mudah dipahami.",
                            safety_settings={
                                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
                            }
                        )
                        st.markdown("### 🤖 Jawaban Asisten Belajar")
                        st.info(response.text)
                    except exceptions.TooManyRequests:
                        st.error("⚠️ Terlalu banyak request. Silakan tunggu beberapa saat.")
                        time.sleep(2)
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Silakan masukkan pertanyaan atau ID paper!")

with tab2:
    st.markdown("### 🔬 Cari Paper Berdasarkan Topik")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        topic = st.text_input("Masukkan topik penelitian:", placeholder="Contoh: machine learning, quantum computing")
    with col2:
        max_results = st.slider("Jumlah hasil:", 1, 10, 5)
    
    if st.button("🔎 Cari Paper", key="topic_search"):
        if topic:
            with st.spinner("Mencari paper..."):
                try:
                    client = arxiv.Client()
                    search = arxiv.Search(
                        query=topic,
                        max_results=max_results,
                        sort_by=arxiv.SortCriterion.Relevance
                    )
                    
                    papers = list(client.results(search))
                    
                    if papers:
                        st.success(f"✅ Ditemukan {len(papers)} paper tentang '{topic}'")
                        st.markdown("---")
                        
                        for idx, paper in enumerate(papers, 1):
                            with st.expander(f"📄 {idx}. {paper.title}"):
                                st.write(f"**ID Paper:** {paper.get_short_id()}")
                                st.write(f"**Penulis:** {', '.join([author.name for author in paper.authors])}")
                                st.write(f"**Tanggal Publikasi:** {paper.published.date()}")
                                st.write(f"**Ringkasan:** {paper.summary[:300]}...")
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.markdown(f"[📥 Download PDF]({paper.pdf_url})")
                                with col_b:
                                    st.markdown(f"[🔗 Lihat di arXiv]({paper.entry_id})")
                    else:
                        st.warning("⚠️ Tidak ada paper yang ditemukan.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        else:
            st.warning("⚠️ Silakan masukkan topik penelitian!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>Dibuat dengan ❤️ menggunakan Streamlit, Google Gemini, dan arXiv API</p>
</div>
""", unsafe_allow_html=True)
