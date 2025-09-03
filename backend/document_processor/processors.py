import os
import re
from typing import List, Dict, Tuple
from pathlib import Path
import logging

logger = logging.getLogger('document_processor')

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class DocumentProcessor:
    """文档处理器基类"""
    
    def __init__(self):
        self.supported_formats = []
    
    def can_process(self, file_path: str) -> bool:
        """检查是否可以处理该文件"""
        return any(file_path.lower().endswith(fmt) for fmt in self.supported_formats)
    
    def extract_text(self, file_path: str) -> str:
        """提取文本内容"""
        raise NotImplementedError
    
    def process_content(self, text: str) -> List[Dict[str, any]]:
        """处理文本内容，返回分块结果"""
        # 基础文本分块逻辑
        chunks = []
        
        # 按段落分割
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        for i, para in enumerate(paragraphs):
            if len(para) < 10:  # 过滤太短的段落
                continue
            
            # 判断段落类型
            chunk_type = self._classify_chunk(para)
            
            chunks.append({
                'chunk_type': chunk_type,
                'content': para,
                'order': i,
                'metadata': {
                    'length': len(para),
                    'has_question': '?' in para,
                    'has_exclamation': '!' in para,
                }
            })
        
        return chunks
    
    def _classify_chunk(self, text: str) -> str:
        """分类文本块类型"""
        text_lower = text.lower()
        
        # 对话类型检测
        if re.search(r'["""].*["""]', text) or '：' in text or ':' in text:
            return 'dialogue'
        
        # 示例类型检测
        if any(word in text_lower for word in ['例如', '比如', '示例', '例子', '比如', '例如']):
            return 'example'
        
        # 说明类型检测
        if any(word in text_lower for word in ['说明', '注意', '提示', '要求', '步骤', '方法']):
            return 'instruction'
        
        # 默认段落类型
        return 'paragraph'


class PDFProcessor(DocumentProcessor):
    """PDF文档处理器"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['.pdf']
    
    def extract_text(self, file_path: str) -> str:
        """提取PDF文本"""
        if not PYPDF2_AVAILABLE:
            raise ImportError("PyPDF2 未安装，无法处理PDF文件")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return text
        except Exception as e:
            logger.error(f"PDF文本提取失败: {e}")
            raise


class WordProcessor(DocumentProcessor):
    """Word文档处理器"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['.docx', '.doc']
    
    def extract_text(self, file_path: str) -> str:
        """提取Word文本"""
        if not DOCX_AVAILABLE:
            raise ImportError("python-docx 未安装，无法处理Word文件")
        
        try:
            doc = DocxDocument(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            logger.error(f"Word文本提取失败: {e}")
            raise


class MarkdownProcessor(DocumentProcessor):
    """Markdown文档处理器"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['.md', '.markdown']
    
    def extract_text(self, file_path: str) -> str:
        """提取Markdown文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Markdown文本提取失败: {e}")
            raise
    
    def process_content(self, text: str) -> List[Dict[str, any]]:
        """处理Markdown内容，保留结构信息"""
        chunks = []
        
        # 按行分割，保留Markdown标记
        lines = text.split('\n')
        current_chunk = ""
        chunk_type = 'paragraph'
        order = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_chunk:
                    chunks.append({
                        'chunk_type': chunk_type,
                        'content': current_chunk.strip(),
                        'order': order,
                        'metadata': {
                            'length': len(current_chunk),
                            'markdown_type': chunk_type,
                        }
                    })
                    current_chunk = ""
                    order += 1
                continue
            
            # 检测Markdown标记
            if line.startswith('#'):
                chunk_type = 'instruction'
            elif line.startswith('- ') or line.startswith('* '):
                chunk_type = 'example'
            elif line.startswith('>'):
                chunk_type = 'dialogue'
            else:
                chunk_type = 'paragraph'
            
            current_chunk += line + "\n"
        
        # 处理最后一个块
        if current_chunk:
            chunks.append({
                'chunk_type': chunk_type,
                'content': current_chunk.strip(),
                'order': order,
                'metadata': {
                    'length': len(current_chunk),
                    'markdown_type': chunk_type,
                }
            })
        
        return chunks


class TextProcessor(DocumentProcessor):
    """纯文本处理器"""
    
    def __init__(self):
        super().__init__()
        self.supported_formats = ['.txt']
    
    def extract_text(self, file_path: str) -> str:
        """提取纯文本"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"文本提取失败: {e}")
            raise


def get_processor(file_path: str) -> DocumentProcessor:
    """根据文件类型获取对应的处理器"""
    file_ext = Path(file_path).suffix.lower()
    
    processors = [
        PDFProcessor(),
        WordProcessor(),
        MarkdownProcessor(),
        TextProcessor(),
    ]
    
    for processor in processors:
        if processor.can_process(file_path):
            return processor
    
    raise ValueError(f"不支持的文件格式: {file_ext}")


def process_document(file_path: str) -> Tuple[str, List[Dict[str, any]]]:
    """处理文档，返回提取的文本和分块结果"""
    processor = get_processor(file_path)
    
    # 提取文本
    text = processor.extract_text(file_path)
    
    # 处理内容
    chunks = processor.process_content(text)
    
    return text, chunks
