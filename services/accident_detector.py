from PIL import Image
from io import BytesIO
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.output_parsers import JsonOutputParser
import logging
import time

class AccidentDetect(BaseModel):
    Accident: str = Field(description="Output will be in YES or NO.")
    Explanation: str = Field(description="Explain of the accident in the image.")

class AccidentDetector:
    def __init__(self, api_key):
        self.parser = JsonOutputParser(pydantic_object=AccidentDetect)
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key
        )
        self.prompt_template = self._create_prompt_template()
        self.chain = self._create_chain()

    def _create_prompt_template(self):
        return PromptTemplate(
            input_variables=["image"],
            template="""You are an accident analyst tasked with examining visual data to detect accidents. Analyze the provided image and determine if an accident has occurred.

**Instructions:**
1. Return a JSON object with two fields:
   - "Accident": Set to "Yes" if an accident is detected, or "No" if no accident is detected.
   - "Explanation": Provide a concise explanation for your conclusion, referencing specific visual evidence (e.g., collisions, damage, hazardous conditions).
2. Ensure the output is valid JSON.

**Additional Notes:**
- Focus on clear indicators of accidents, such as vehicle collisions, overturned objects, debris, or unsafe behaviors.
- Ensure the explanation is precise and directly tied to the visual content.

**Image Analysis:**
{image}

**Output Format:**
{format_instructions}
""",
            partial_variables={"format_instructions": self.parser.get_format_instructions()}
        )

    def _create_chain(self):
        return (
            {"image": RunnablePassthrough()}
            | self.prompt_template
            | self.llm
            | self.parser
        )

    def process_image(self, image_path, retries=3, delay=2):
        filename = image_path.split('/')[-1]
        for attempt in range(retries):
            try:
                raw_image = Image.open(image_path).convert('RGB')
                
                # Resize image to prevent token limit errors
                max_size = (512, 512)
                raw_image.thumbnail(max_size, Image.Resampling.LANCZOS)

                img_byte_arr = BytesIO()
                # Save the image to a byte array with PNG format
                raw_image.save(img_byte_arr, format='PNG', optimize=True, quality=85)
                # Get the byte data from the byte array
                img_bytes = img_byte_arr.getvalue()

                result = self.chain.invoke({"image": {"mime_type": "image/png", "data": img_bytes}})
                status = result["Accident"]
                explanation = result["Explanation"]

                log_message = f"Image: {filename}, Accident: {status}, Explanation: {explanation}"
                logging.info(log_message)

                return {
                    "filename": filename,
                    "status": status,
                    "explanation": explanation
                }
            except Exception as e:
                logging.warning(f"Attempt {attempt+1} failed for {filename}: {str(e)}")
                if attempt < retries - 1:
                    time.sleep(delay)
                else:
                    logging.error(f"Error processing {filename}: {str(e)}")
                    return {
                        "filename": filename,
                        "status": "Error",
                        "explanation": f"Error processing image: {str(e)}"
                    }