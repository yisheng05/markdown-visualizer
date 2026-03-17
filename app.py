import streamlit as st
import markdown
from fpdf import FPDF
from io import BytesIO

def create_pdf(md_content):
    # Normalize common Unicode characters that cause issues with standard PDF fonts (helvetica)
    replacements = {
        "\u2018": "'", "\u2019": "'",  # Smart single quotes
        "\u201c": '"', "\u201d": '"',  # Smart double quotes
        "\u2013": "-", "\u2014": "-",  # En and em dashes
        "\u2026": "...",              # Ellipsis
        "\u27a2": ">", "\u2022": "*",  # Bullets
    }
    for old, new in replacements.items():
        md_content = md_content.replace(old, new)

    # Convert Markdown to HTML (avoiding 'smarty' which generates smart quotes)
    html_content = markdown.markdown(md_content, extensions=['extra'])
    
    # Create PDF object
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # Set default font
    pdf.set_font("helvetica", size=11)
    
    # Write HTML to PDF (handles basic tags)
    try:
        pdf.write_html(html_content)
    except Exception as e:
        # Fallback if HTML rendering fails (e.g. unsupported tags or characters)
        # Note: some fpdf2 errors leave the pdf object without an open page
        if pdf.page == 0:
            pdf.add_page()
            pdf.set_font("helvetica", size=11)
            
        st.warning(f"Note: Some complex formatting might not render perfectly in PDF. Error: {e}")
        # Try to write the raw markdown content as a fallback
        try:
            pdf.multi_cell(0, 10, md_content)
        except Exception as fallback_e:
            # If even multi_cell fails (e.g. more unsupported characters), 
            # we try one last time with basic ASCII encoding
            pdf.multi_cell(0, 10, md_content.encode('ascii', 'replace').decode('ascii'))
    
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
            st.markdown(file_content, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Error reading file: {e}")
    else:
        st.info("Please upload a Markdown file to get started.")

if __name__ == "__main__":
    main()
