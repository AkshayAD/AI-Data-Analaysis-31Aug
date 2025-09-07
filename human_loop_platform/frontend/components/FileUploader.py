"""
Multi-format File Uploader Component
Supports CSV, Excel, PDF, Images, SQL, and more
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
import hashlib
from typing import List, Dict, Any, Optional
import PyPDF2
from PIL import Image
import sqlparse
import io
import base64

class MultiFormatFileUploader:
    """Advanced file uploader with multi-format support"""
    
    ALLOWED_EXTENSIONS = {
        'structured': ['csv', 'xlsx', 'xls', 'parquet', 'json'],
        'documents': ['pdf', 'docx', 'txt', 'md'],
        'images': ['png', 'jpg', 'jpeg', 'gif', 'bmp'],
        'sql': ['sql'],
        'notebooks': ['ipynb', 'py']
    }
    
    def __init__(self):
        """Initialize file uploader"""
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = {}
        if 'file_metadata' not in st.session_state:
            st.session_state.file_metadata = {}
    
    def render(self) -> Dict[str, Any]:
        """Render file upload interface"""
        st.subheader("📁 Upload Data Files")
        
        # File uploader with multiple file support
        uploaded_files = st.file_uploader(
            "Choose files to upload",
            accept_multiple_files=True,
            type=self._get_all_extensions(),
            help="Upload CSV, Excel, PDF, Images, SQL files, and more"
        )
        
        if uploaded_files:
            return self._process_uploaded_files(uploaded_files)
        
        return self._display_uploaded_files()
    
    def _get_all_extensions(self) -> List[str]:
        """Get all allowed file extensions"""
        all_extensions = []
        for category_extensions in self.ALLOWED_EXTENSIONS.values():
            all_extensions.extend(category_extensions)
        return all_extensions
    
    def _process_uploaded_files(self, files) -> Dict[str, Any]:
        """Process and categorize uploaded files"""
        processed_files = {
            'structured': [],
            'documents': [],
            'images': [],
            'sql': [],
            'notebooks': []
        }
        
        for file in files:
            # Generate unique file ID
            file_id = self._generate_file_id(file)
            
            # Skip if already processed
            if file_id in st.session_state.uploaded_files:
                category = st.session_state.file_metadata[file_id]['category']
                processed_files[category].append({
                    'id': file_id,
                    'name': file.name,
                    'metadata': st.session_state.file_metadata[file_id]
                })
                continue
            
            # Determine file category
            file_ext = Path(file.name).suffix.lower()[1:]
            category = self._get_file_category(file_ext)
            
            if category:
                # Process file based on category
                file_data, metadata = self._process_file_by_category(file, category)
                
                # Store in session state
                st.session_state.uploaded_files[file_id] = file_data
                st.session_state.file_metadata[file_id] = {
                    'name': file.name,
                    'category': category,
                    'size': file.size,
                    'type': file_ext,
                    **metadata
                }
                
                processed_files[category].append({
                    'id': file_id,
                    'name': file.name,
                    'metadata': st.session_state.file_metadata[file_id]
                })
                
                st.success(f"✅ Uploaded: {file.name}")
        
        return processed_files
    
    def _generate_file_id(self, file) -> str:
        """Generate unique ID for uploaded file"""
        content = file.read()
        file.seek(0)  # Reset file pointer
        return hashlib.md5(content).hexdigest()[:10]
    
    def _get_file_category(self, extension: str) -> Optional[str]:
        """Determine file category based on extension"""
        for category, extensions in self.ALLOWED_EXTENSIONS.items():
            if extension in extensions:
                return category
        return None
    
    def _process_file_by_category(self, file, category: str) -> tuple:
        """Process file based on its category"""
        metadata = {}
        
        if category == 'structured':
            # Process structured data files
            if file.name.endswith('.csv'):
                df = pd.read_csv(file)
                metadata['rows'] = len(df)
                metadata['columns'] = len(df.columns)
                metadata['column_names'] = df.columns.tolist()
                file_data = df
                
            elif file.name.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file)
                metadata['rows'] = len(df)
                metadata['columns'] = len(df.columns)
                metadata['column_names'] = df.columns.tolist()
                file_data = df
                
            elif file.name.endswith('.parquet'):
                df = pd.read_parquet(file)
                metadata['rows'] = len(df)
                metadata['columns'] = len(df.columns)
                metadata['column_names'] = df.columns.tolist()
                file_data = df
                
            elif file.name.endswith('.json'):
                content = json.load(file)
                metadata['keys'] = list(content.keys()) if isinstance(content, dict) else None
                metadata['length'] = len(content)
                file_data = content
        
        elif category == 'documents':
            # Process document files
            if file.name.endswith('.pdf'):
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                metadata['pages'] = len(pdf_reader.pages)
                metadata['text_length'] = len(text)
                file_data = text
                
            elif file.name.endswith('.txt'):
                text = file.read().decode('utf-8')
                metadata['text_length'] = len(text)
                metadata['lines'] = len(text.split('\n'))
                file_data = text
        
        elif category == 'images':
            # Process image files
            image = Image.open(file)
            metadata['dimensions'] = image.size
            metadata['mode'] = image.mode
            # Convert to base64 for storage
            buffered = io.BytesIO()
            image.save(buffered, format=image.format if image.format else 'PNG')
            file_data = base64.b64encode(buffered.getvalue()).decode()
        
        elif category == 'sql':
            # Process SQL files
            sql_content = file.read().decode('utf-8')
            parsed = sqlparse.parse(sql_content)
            metadata['statements'] = len(parsed)
            metadata['formatted'] = sqlparse.format(sql_content, reindent=True)
            file_data = sql_content
        
        elif category == 'notebooks':
            # Process notebook files
            content = file.read().decode('utf-8')
            if file.name.endswith('.ipynb'):
                notebook = json.loads(content)
                metadata['cells'] = len(notebook.get('cells', []))
                metadata['kernel'] = notebook.get('metadata', {}).get('kernelspec', {}).get('name')
            else:
                metadata['lines'] = len(content.split('\n'))
            file_data = content
        
        return file_data, metadata
    
    def _display_uploaded_files(self) -> Dict[str, Any]:
        """Display currently uploaded files"""
        if st.session_state.uploaded_files:
            st.subheader("📋 Uploaded Files")
            
            # Group files by category
            files_by_category = {}
            for file_id, metadata in st.session_state.file_metadata.items():
                category = metadata['category']
                if category not in files_by_category:
                    files_by_category[category] = []
                files_by_category[category].append({
                    'id': file_id,
                    'name': metadata['name'],
                    'metadata': metadata
                })
            
            # Display files by category
            for category, files in files_by_category.items():
                with st.expander(f"{category.title()} Files ({len(files)})", expanded=True):
                    for file_info in files:
                        col1, col2, col3 = st.columns([3, 2, 1])
                        with col1:
                            st.text(f"📄 {file_info['name']}")
                        with col2:
                            # Display relevant metadata
                            meta = file_info['metadata']
                            if 'rows' in meta and 'columns' in meta:
                                st.text(f"{meta['rows']:,} rows × {meta['columns']} cols")
                            elif 'pages' in meta:
                                st.text(f"{meta['pages']} pages")
                            elif 'dimensions' in meta:
                                st.text(f"{meta['dimensions'][0]}×{meta['dimensions'][1]} px")
                            elif 'statements' in meta:
                                st.text(f"{meta['statements']} SQL statements")
                            elif 'cells' in meta:
                                st.text(f"{meta['cells']} notebook cells")
                            elif 'lines' in meta:
                                st.text(f"{meta['lines']} lines")
                            elif 'text_length' in meta:
                                st.text(f"{meta['text_length']:,} characters")
                            else:
                                # Display file size as fallback
                                size_mb = meta.get('size', 0) / (1024 * 1024)
                                st.text(f"{size_mb:.2f} MB")
                        with col3:
                            if st.button("🗑️", key=f"del_{file_info['id']}"):
                                self._remove_file(file_info['id'])
                                st.rerun()
            
            return files_by_category
        
        return {}
    
    def _remove_file(self, file_id: str):
        """Remove uploaded file"""
        if file_id in st.session_state.uploaded_files:
            del st.session_state.uploaded_files[file_id]
            del st.session_state.file_metadata[file_id]
    
    def get_file_data(self, file_id: str) -> Any:
        """Get processed file data by ID"""
        return st.session_state.uploaded_files.get(file_id)
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """Get file metadata by ID"""
        return st.session_state.file_metadata.get(file_id, {})