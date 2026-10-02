class PromptTemplateManager:
    def __init__(self):
        self.templates = {      
            "generate_summary": """
            Based on this extracted information:
            {extracted_info}

            Based on the given info decide if the claim is legit or not
            """
        }
    
    def get_prompt(self, template_name, **kwargs):
        template = self.templates.get(template_name)
        if not template:
            raise ValueError(f"Template {template_name} not found")
        
        return template.format(**kwargs)