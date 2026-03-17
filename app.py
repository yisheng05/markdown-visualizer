import streamlit as st
import markdown
from fpdf import FPDF
from io import BytesIO

def create_pdf(md_content):
    # Convert Markdown to HTML
    html_content = markdown.markdown(md_content, extensions=['extra', 'smarty'])
    
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
        # Fallback if HTML rendering fails (e.g. unsupported tags)
        # Note: fpdf2 write_html is quite robust for basic Markdown-to-HTML
        st.warning(f"Note: Some complex formatting might not render perfectly in PDF. Error: {e}")
        pdf.multi_cell(0, 10, md_content)
    
    # Return PDF as bytes
    return pdf.output()

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
            file_content = uploaded_file.read().decode("utf-8")
            
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
