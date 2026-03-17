import streamlit as st
import markdown
from fpdf import FPDF, FontFace
from io import BytesIO
import os

def create_pdf(md_content):
    # Convert Markdown to HTML
    # nl2br: treats single newlines as line breaks
    # extra: handles tables, footnotes, etc.
    html_content = markdown.markdown(md_content, extensions=['extra', 'nl2br'])
    
    # Create PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Try to load a Unicode font if available on the system (Mac path used here)
    unicode_font_path = "/Library/Fonts/Arial Unicode.ttf"
    if os.path.exists(unicode_font_path):
        try:
            pdf.add_font("ArialUnicode", "", unicode_font_path)
            font_name = "ArialUnicode"
        except Exception:
            font_name = "helvetica"
    else:
        font_name = "helvetica"

    pdf.add_page()
    pdf.set_margin(20) # 20mm margins for a cleaner look
    
    # Define styles for common tags using FontFace (required by fpdf2 2.8.x)
    tag_styles = {
        "h1": FontFace(family=font_name, emphasis="B", size_pt=16),
        "h2": FontFace(family=font_name, emphasis="B", size_pt=14),
        "h3": FontFace(family=font_name, emphasis="B", size_pt=12),
        "p": FontFace(family=font_name, size_pt=11),
        "li": FontFace(family=font_name, size_pt=11),
    }

    # Set default font
    pdf.set_font(font_name, size=11)
    
    # Write HTML to PDF with improved styling
    try:
        # We wrap in a div with line-height for better spacing
        styled_html = f'<div style="line-height: 1.5; text-align: justify;">{html_content}</div>'
        pdf.write_html(styled_html, tag_styles=tag_styles)
    except Exception as e:
        # Fallback if HTML rendering fails
        if pdf.page == 0:
            pdf.add_page()
            
        st.warning(f"Note: Some complex formatting might not render perfectly in PDF. Error: {e}")
        
        # Simple normalization for fallback multi_cell
        replacements = {
            "\u2018": "'", "\u2019": "'", "\u201c": '"', "\u201d": '"',
            "\u2013": "-", "\u2014": "-", "\u2026": "...",
            "\u27a2": ">", "\u2022": "*", "●": "*"
        }
        md_fixed = md_content
        for old, new in replacements.items():
            md_fixed = md_fixed.replace(old, new)
            
        try:
            pdf.set_font("helvetica", size=11)
            pdf.multi_cell(0, 8, md_fixed)
        except Exception:
            pdf.multi_cell(0, 8, md_fixed.encode('ascii', 'replace').decode('ascii'))
    
    # Return PDF as bytes (fpdf2 returns bytearray, Streamlit prefers bytes)
    return bytes(pdf.output())

def main():
    st.set_page_config(
        page_title="Markdown Visualizer",
        page_icon="📝",
        layout="wide"
    )

    st.title("📝 Markdown Visualizer")
    st.markdown("Upload a `.md` file to see its rendered output and export to PDF.")

    # Sidebar for additional options
    st.sidebar.title("Settings")
    show_raw = st.sidebar.checkbox("Show Raw Content", value=False)
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a Markdown file", type=["md"])

    if uploaded_file is not None:
        try:
            # Read and decode the file content
            # Use getvalue() instead of read() for robustness across reruns
            file_content = uploaded_file.getvalue().decode("utf-8")
            
            # Display file name and size
            st.info(f"Viewing: **{uploaded_file.name}** ({uploaded_file.size} bytes)")
            
            # Export Options
            st.sidebar.divider()
            st.sidebar.subheader("Export Options")
            
            # Use session state to persist PDF bytes across reruns
            if "pdf_bytes" not in st.session_state:
                st.session_state.pdf_bytes = None
            if "last_prepared_file" not in st.session_state:
                st.session_state.last_prepared_file = None

            if st.sidebar.button("Prepare PDF"):
                with st.spinner("Generating PDF..."):
                    st.session_state.pdf_bytes = create_pdf(file_content)
                    st.session_state.last_prepared_file = uploaded_file.name
                st.sidebar.success("PDF Ready!")

            # Show download button if PDF is prepared and still matches current file
            if st.session_state.pdf_bytes and st.session_state.last_prepared_file == uploaded_file.name:
                st.sidebar.download_button(
                    label="⬇️ Download PDF",
                    data=st.session_state.pdf_bytes,
                    file_name=f"{uploaded_file.name.replace('.md', '')}.pdf",
                    mime="application/pdf"
                )

            if show_raw:
                st.subheader("Raw Markdown Source")
                st.code(file_content, language="markdown")
                st.divider()

            # Render the markdown content
            st.subheader("Rendered Visualization")
            rendered_html = markdown.markdown(file_content, extensions=['extra', 'nl2br'])
            st.markdown(rendered_html, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload a Markdown file to get started.")

if __name__ == "__main__":
    main()
