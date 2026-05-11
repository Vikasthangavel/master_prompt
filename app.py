import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path



os.environ["OPENROUTER_API_KEY"] = ""


from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


llm = ChatOpenAI(
    model="openai/gpt-4o-mini",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    temperature=0.2
)


system_prompt = """
# SPECIAL INSTRUCTION: think silently if needed

Act as a world-class senior frontend React engineer with deep expertise in Gemini API and UI/UX design.

Your task is to generate complete React web applications based on the user's request.

Follow these rules strictly:

Runtime:
React 18+
Language: TypeScript (.tsx)
Module System: ESM

Styling:
Use Tailwind CSS ONLY.

Important:
Return code ONLY in the required XML format.

Output format:

<changes>
  <change>
    <file>file_path</file>
    <description>description</description>
    <content><![CDATA[
FULL FILE CONTENT
]]></content>
  </change>
</changes>

Rules:

1. Return ONLY the XML
2. No explanation
3. No markdown
4. Code must be production ready
5. Use modern React patterns
6. Use functional components
7. Use hooks
8. Use TypeScript

Project Structure:

index.html
index.tsx
App.tsx

components/
services/

First file must always be metadata.json:
{{
  "name": "app name",
  "description": "short description"
}}
Design rules:

• beautiful UI
• responsive
• mobile-first
• sticky primary actions
• Tailwind only
"""

# --------------------------------------
# USER PROMPT TEMPLATE
# --------------------------------------

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("human", "{user_prompt}")
    ]
)
 
# --------------------------------------
# AGENT CHAIN
# --------------------------------------

chain = prompt | llm | StrOutputParser()

# --------------------------------------
# FILE CREATION LOGIC
# --------------------------------------

def parse_and_create_files(xml_output, output_dir="generated_project"):
    """Parse XML output and create files"""
    
    try:
        # Extract XML from the response (in case there's extra text)
        xml_match = re.search(r'<changes>.*?</changes>', xml_output, re.DOTALL)
        if not xml_match:
            print("❌ No valid XML found in response")
            return False
        
        xml_content = xml_match.group(0)
        
        # Parse XML
        root = ET.fromstring(xml_content)
        
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📁 Creating project in: {output_path.absolute()}\n")
        
        # Process each file
        file_count = 0
        for change in root.findall('change'):
            file_path = change.find('file').text
            description = change.find('description').text if change.find('description') is not None else ""
            content_elem = change.find('content')
            content = content_elem.text if content_elem is not None else ""
            
            # Create full file path
            full_path = output_path / file_path
            
            # Create parent directories if needed
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_count += 1
            print(f"✅ Created: {file_path}")
            if description:
                print(f"   {description}")
        
        print(f"\n✨ Successfully created {file_count} file(s) in {output_path.absolute()}")
        return True
        
    except ET.ParseError as e:
        print(f"❌ XML parsing error: {e}")
        print("\nRaw output:")
        print(xml_output)
        return False
    except Exception as e:
        print(f"❌ Error creating files: {e}")
        return False

# --------------------------------------
# CLI INTERFACE
# --------------------------------------

def coding_agent():

    print("\n==============================")
    print("🚀 Agentic Coding AI")
    print("==============================")

    while True:

        user_prompt = input("\nDescribe the app you want: ")

        if user_prompt.lower() in ["quit","exit","q"]:
            print("Goodbye!")
            break

        print("\n⚡ Generating project...\n")

        result = chain.invoke({
            "user_prompt": user_prompt
        })

        # Parse and create files
        success = parse_and_create_files(result)
        
        if not success:
            print("\n⚠️  Failed to create project files. Here's the raw output:")
            print("-" * 50)
            print(result)
            print("-" * 50)


# --------------------------------------

if __name__ == "__main__":
    coding_agent()
