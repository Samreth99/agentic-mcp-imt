import hashlib
import requests
from pathlib import Path
from typing import List, Optional, Literal
from urllib.parse import urlparse

from langchain_community.document_loaders import (
    DirectoryLoader, 
    PyMuPDFLoader
)
from langchain_core.documents import Document
from mcp_server.utils.logger import get_logger
from mcp_server.config.constants import DATA_PATH, CACHE_PATH

logger = get_logger(__name__)
SourceType = Literal["file", "directory", "url"]

class PDFLoader:
    """
    Unified PDF loader supporting files, directories, and URLs with caching.
    """
    
    def __init__(
        self, 
        cache_dir: str = CACHE_PATH,
        enable_cache: bool = True,
        verify_ssl: bool = True
    ):
        """
        Initialize PDF loader.
        
        Args:
            cache_dir: Directory for caching downloaded PDFs
            enable_cache: Whether to enable URL caching
            verify_ssl: Whether to verify SSL certificates for URL downloads
        """
        self.cache_dir = Path(cache_dir)
        self.enable_cache = enable_cache
        self.verify_ssl = verify_ssl
        
        if self.enable_cache:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"PDF cache directory: {self.cache_dir}")
    
    def load(
        self, 
        source: str, 
        source_type: Literal["auto", "file", "directory", "url"] = "auto"
    ) -> List[Document]:
        """
        Universal PDF loader that auto-detects source type.
        
        Args:
            source: File path, directory path, or URL
            source_type: Type of source ("auto" for auto-detection)
            
        Returns:
            List of loaded documents
        """
        if source_type == "auto":
            source_type = self._detect_source_type(source)
        
        logger.info(f"Loading PDF from {source_type}: {source}")
        
        if source_type == "file":
            return self.load_file(source)
        elif source_type == "directory":
            return self.load_directory(source)
        elif source_type == "url":
            return self.load_from_url(source)
        else:
            raise ValueError(f"Invalid source_type: {source_type}")
    
    def load_file(self, file_path: str) -> List[Document]:
        """
        Load a single PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of document chunks from the PDF
        """
        path = Path(file_path)
        
        if not path.exists():
            error_msg = f"File does not exist: {file_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if path.suffix.lower() != '.pdf':
            error_msg = f"File is not a PDF: {file_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Loading PDF file: {file_path}")
        
        try:
            loader = PyMuPDFLoader(str(path))
            documents = loader.load()

            # Sort pages to ensure consistent order
            documents.sort(key=lambda doc: doc.metadata.get('page', 0))
            
            logger.info(f"Successfully loaded {len(documents)} pages from {path.name}")
            return documents
            
        except Exception as e:
            logger.exception(f"Failed to load PDF file: {file_path}")
            raise
    
    def load_directory(self, directory: Optional[str] = None) -> List[Document]:
        """
        Load all PDF files from a directory.
        
        Args:
            directory: Path to directory 
            
        Returns:
            List of loaded documents
        """
        data_path = Path(directory) if directory else Path(DATA_PATH)
        
        if not data_path.exists():
            error_msg = f"Directory does not exist: {data_path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        if not data_path.is_dir():
            error_msg = f"Path is not a directory: {data_path}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        logger.info(f"Loading PDF files from {data_path}")
        
        try:
            loader = DirectoryLoader(
                str(data_path),
                glob="*.pdf",
                loader_cls=PyMuPDFLoader, # type: ignore[arg-type]
                show_progress=True
            )
            
            documents = loader.load()
            
            if not documents:
                warning_msg = f"No PDF files found in {data_path}"
                logger.warning(warning_msg)
                raise ValueError(warning_msg)
            
            # Sort documents by source and page to ensure consistent order
            documents.sort(key=lambda doc: (doc.metadata.get('source', ''), doc.metadata.get('page', 0)))
            
            logger.info(f"Successfully loaded and sorted {len(documents)} documents from {data_path}")
            return documents
            
        except Exception as e:
            logger.exception(f"Failed to load PDFs from directory: {data_path}")
            raise
    
    def load_from_url(self, url: str) -> List[Document]:
        """
        Load a PDF file from a URL with caching support.
        
        Args:
            url: HTTP/HTTPS URL to the PDF file
            
        Returns:
            List of document chunks from the PDF
        """
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ['http', 'https']:
            error_msg = f"Invalid URL scheme (must be http/https): {url}"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if self.enable_cache:
            cached_file = self._get_cached_file_path(url)
            if cached_file.exists():
                logger.info(f"Loading PDF from cache: {url}")
                return self.load_file(str(cached_file))
        
        logger.info(f"Downloading PDF from URL: {url}")
        pdf_content = self._download_pdf(url)
        
        if self.enable_cache:
            cached_file = self._save_to_cache(url, pdf_content)
            logger.info(f"PDF cached at: {cached_file}")
            return self.load_file(str(cached_file))
        else:
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                tmp_path = tmp_file.name
            
            try:
                documents = self.load_file(tmp_path)
                return documents
            finally:
                # Clean up temp file
                Path(tmp_path).unlink(missing_ok=True)
    
    def clear_cache(self) -> int:
        """
        Clear all cached PDF files.
        
        Returns:
            Number of files deleted
        """
        if not self.cache_dir.exists():
            logger.info("Cache directory does not exist")
            return 0
        
        deleted_count = 0
        for file_path in self.cache_dir.glob("*.pdf"):
            try:
                file_path.unlink()
                deleted_count += 1
            except Exception as e:
                logger.warning(f"Failed to delete cached file {file_path}: {e}")
        
        logger.info(f"Cleared {deleted_count} cached PDF files")
        return deleted_count
    
    def get_cache_info(self) -> dict:
        """
        Get information about the cache.
        
        Returns:
            Dictionary with cache statistics
        """
        if not self.cache_dir.exists():
            return {
                "enabled": self.enable_cache,
                "directory": str(self.cache_dir),
                "files": 0,
                "total_size_mb": 0
            }
        
        pdf_files = list(self.cache_dir.glob("*.pdf"))
        total_size = sum(f.stat().st_size for f in pdf_files)
        
        return {
            "enabled": self.enable_cache,
            "directory": str(self.cache_dir),
            "files": len(pdf_files),
            "total_size_mb": round(total_size / (1024 * 1024), 2)
        }
    
        
    def _detect_source_type(self, source: str) -> SourceType:
        """Auto-detect the source type."""
        if source.startswith(('http://', 'https://')):
            return "url"
        
        path = Path(source)
        if path.is_dir():
            return "directory"
        elif path.is_file() or not path.exists():
            return "file"
        else:
            raise ValueError(f"Cannot determine source type for: {source}")
        
    
    def _get_cached_file_path(self, url: str) -> Path:
        """Generate cache file path from URL."""
        url_hash = hashlib.md5(url.encode()).hexdigest()
        parsed_url = urlparse(url)
        original_name = Path(parsed_url.path).name
        
        if original_name.endswith('.pdf'):
            filename = f"{url_hash}_{original_name}"
        else:
            filename = f"{url_hash}.pdf"
        
        return self.cache_dir / filename
    
    def _download_pdf(self, url: str) -> bytes:
        """Download PDF from URL."""
        try:
            response = requests.get(
                url, 
                verify=self.verify_ssl,
                timeout=30,
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type and not url.lower().endswith('.pdf'):
                logger.warning(f"URL may not be a PDF. Content-Type: {content_type}")
            
            return response.content
            
        except requests.RequestException as e:
            logger.exception(f"Failed to download PDF from {url}")
            raise
    
    def _save_to_cache(self, url: str, content: bytes) -> Path:
        """Save downloaded PDF to cache."""
        cached_file = self._get_cached_file_path(url)
        
        try:
            cached_file.write_bytes(content)
            logger.debug(f"Saved {len(content)} bytes to cache")
            return cached_file
        except Exception as e:
            logger.exception(f"Failed to save PDF to cache: {cached_file}")
            raise