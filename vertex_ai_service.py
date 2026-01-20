"""
Vertex AI service for extracting coupon information from PDF content using Gemini.
"""
import logging
from typing import Dict, Optional
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Part
import vertexai
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class VertexAIService:
    """Service for interacting with Vertex AI (Gemini) API."""
    
    def __init__(self, project_id: str, location: str, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Vertex AI service.
        
        Args:
            project_id: Google Cloud project ID
            location: Google Cloud region (e.g., 'us-central1')
            model_name: Name of the Gemini model to use
        """
        self.project_id = project_id
        self.location = location
        self.model_name = model_name
        
        # Initialize Vertex AI
        vertexai.init(project=project_id, location=location)
        self.model = GenerativeModel(model_name)
        
        logger.info(f"Initialized Vertex AI with model: {model_name}")
    
    def _create_extraction_prompt(self, filename: str, metadata: Dict) -> str:
        """
        Create a prompt for extracting coupon information.
        
        Args:
            filename: Name of the PDF file
            metadata: Extracted metadata from filename/path
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are analyzing a Direct Mail PDF proof for a dealership.

File: {filename}
Metadata: {metadata}

Please extract the following information about coupon offers from this document:
1. Coupon offer description (e.g., "$500 off", "0% APR for 60 months", "Free oil changes for 1 year")
2. Expiration date (if mentioned)
3. Terms and conditions (brief summary)
4. Target vehicle models or types (if specified)
5. Any special requirements or restrictions

Format your response as a structured JSON object with the following keys:
- offers: List of offer descriptions
- expiration_date: The expiration date if found, otherwise null
- terms: Brief summary of terms and conditions
- target_vehicles: List of vehicle models or types
- restrictions: Any special requirements

If no coupon information is found, return an empty offers list.
"""
        return prompt
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def extract_coupon_info(
        self, 
        filename: str, 
        metadata: Dict,
        pdf_content: Optional[bytes] = None,
        temperature: float = 0.2,
        max_output_tokens: int = 2048
    ) -> str:
        """
        Extract coupon information from PDF using Gemini.
        
        Args:
            filename: Name of the PDF file
            metadata: Extracted metadata from filename/path
            pdf_content: Optional PDF content as bytes (for full PDF analysis)
            temperature: Temperature for model generation (0.0-1.0)
            max_output_tokens: Maximum tokens in response
            
        Returns:
            Extracted information as a string (JSON format)
        """
        try:
            prompt = self._create_extraction_prompt(filename, metadata)
            
            # If PDF content is provided, include it in the request
            if pdf_content:
                # Create a Part object for the PDF
                pdf_part = Part.from_data(
                    data=pdf_content,
                    mime_type="application/pdf"
                )
                
                response = self.model.generate_content(
                    [prompt, pdf_part],
                    generation_config={
                        'temperature': temperature,
                        'max_output_tokens': max_output_tokens,
                    }
                )
            else:
                # Text-only analysis based on metadata
                response = self.model.generate_content(
                    prompt,
                    generation_config={
                        'temperature': temperature,
                        'max_output_tokens': max_output_tokens,
                    }
                )
            
            result = response.text
            logger.debug(f"Extracted coupon info for {filename}")
            return result
            
        except Exception as error:
            logger.error(f"Error extracting coupon info for {filename}: {error}")
            raise
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def batch_extract_coupon_info(
        self, 
        file_data: list,
        temperature: float = 0.2,
        max_output_tokens: int = 2048
    ) -> list:
        """
        Extract coupon information from multiple files.
        
        Args:
            file_data: List of dictionaries with 'filename', 'metadata', and optionally 'pdf_content'
            temperature: Temperature for model generation
            max_output_tokens: Maximum tokens in response
            
        Returns:
            List of extracted information strings
        """
        results = []
        
        for idx, data in enumerate(file_data):
            try:
                logger.info(f"Processing file {idx + 1}/{len(file_data)}: {data['filename']}")
                result = self.extract_coupon_info(
                    filename=data['filename'],
                    metadata=data.get('metadata', {}),
                    pdf_content=data.get('pdf_content'),
                    temperature=temperature,
                    max_output_tokens=max_output_tokens
                )
                results.append(result)
            except Exception as error:
                logger.error(f"Failed to process {data['filename']}: {error}")
                results.append(f"Error: {str(error)}")
        
        return results
