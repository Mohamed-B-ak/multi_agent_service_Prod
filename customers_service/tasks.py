from crewai import Task


def get_customer_service_task(channel, customer_message, history, customer_id):
    """
    Task definition for customer service multi-agent system.
    Ensures replies are professional, context-aware, and channel-appropriate.
    """
    return Task(
        description=(
            f"You are part of an AI-powered **Customer Service Team**.\n\n"
            f"📨 **New message received** on `{channel}`:\n"
            f"- Customer ID: {customer_id}\n"
            f"- Message: {customer_message}\n\n"
            f"🧠 **Conversation history**:\n"
            f"{history}\n\n"
            "🎯 **Your Role**:\n"
            "1. Detect intent (complaint, inquiry, request, confirmation, etc.).\n"
            "2. Understand context from history (resolve ambiguities, avoid repeating info).\n"
            "3. Generate a **concise, professional, polite reply** in the same language.\n"
            "4. Ensure the reply fits the **same channel**:\n"
            "   - WhatsApp → short, friendly tone.\n"
            "   - Email → formal, structured sentences.\n"
            "5. If information is missing or unclear → Ask a direct clarifying question.\n"
            "6. If sensitive or unsupported request → Respond safely and escalate politely.\n\n"
            "⚠️ **Rules**:\n"
            "- Never invent customer info (phone, email, order IDs).\n"
            "- Never use dummy placeholders.\n"
            "- Respect conversation history — don’t contradict previous replies.\n"
            "- Always respond in the **same language as the customer**."
        ),
        expected_output=(
            "✅ A single reply message string, ready to be sent back to the customer via the same channel.\n"
            "⚠️ No explanations, no extra commentary, no debug text — just the reply content."
        )
    )
