import os
from crewai.tools import BaseTool
from openai import OpenAI

class MessageContentTool(BaseTool):
    name: str = "Message Content Preparation Tool"
    description: str = (
        "Prepares professional Email or WhatsApp message content based on a given goal, audience, and message details. "
        "This tool only drafts content — it does NOT send messages."
    )

    user_email: str  # ✅ for logging or context if needed

    def _run(self, channel: str, subject: str, message: str) -> str:
        """
        Prepare Email or WhatsApp message content without sending.
        Args:
            channel (str): 'email' or 'whatsapp'
            subject (str): Subject or headline for the message
            message (str): The raw or draft message content
            tone (str): Tone style, e.g., 'professional', 'friendly', 'promotional'
        """
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            prompt = f"""
            You are a professional content writer and marketing assistant.
            Your task is to prepare a {channel.upper()} message with the following:
            - Subject: {subject}
            - Message: {message}

            Formatting Rules:
            - For EMAIL: Return HTML-formatted message (paragraphs, bold text, bullet points, links if relevant).
            - For WHATSAPP: Use plain text with emojis (sparingly), line breaks, and clear call-to-actions.
            - Keep it concise, clear, and aligned with marketing best practices.
            - Do NOT include sending instructions.
            - Remove any placeholder tokens like {{name}} or {{email}}; use neutral phrasing instead.

            Output Format:
            Subject: [Improved subject line]
            Content:
            [Improved formatted message for {channel.upper()}]
            """

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            content = response.choices[0].message.content.strip()

            # ✅ Split structured parts
            if "Subject:" in content and "Content:" in content:
                parts = content.split("Content:")
                new_subject = parts[0].replace("Subject:", "").strip()
                new_body = parts[1].strip()
            else:
                new_subject = subject
                new_body = content

            # ✅ Log formatted preview
            preview = (
                f"📝 **Prepared {channel.upper()} Content Preview**\n\n"
                f"**Subject:** {new_subject}\n\n"
                f"{new_body}\n\n"
                "⚠️ This content is only prepared — it has NOT been sent."
            )
            return {
            "subject": new_subject,
            "content": new_body,
            "message": preview 
        }

        except Exception as e:
            return f"❌ Error preparing {channel} content: {e}"
        
