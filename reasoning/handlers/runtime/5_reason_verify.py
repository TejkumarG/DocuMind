import dspy
from typing import List


class ReasonSignature(dspy.Signature):
    """Generate a factual answer based on the given context."""

    context = dspy.InputField(desc="Retrieved context chunks")
    question = dspy.InputField(desc="User's question")
    answer = dspy.OutputField(desc="Direct, factual answer based on context")


class VerifySignature(dspy.Signature):
    """Verify and correct the answer to ensure accuracy."""

    context = dspy.InputField(desc="Retrieved context chunks")
    question = dspy.InputField(desc="User's question")
    draft_answer = dspy.InputField(desc="Initial answer to verify")
    verified_answer = dspy.OutputField(desc="Verified and corrected answer")


class ReasonVerifyRAG(dspy.Module):
    """
    Two-stage RAG pipeline:
    1. Reason: Generate draft answer from context
    2. Verify: Check and correct the answer
    """

    def __init__(self):
        super().__init__()
        self.reason = dspy.ChainOfThought(ReasonSignature)
        self.verify = dspy.ChainOfThought(VerifySignature)

    def forward(self, context: List[str], question: str):
        """
        Execute the two-stage reasoning process.

        Args:
            context: List of context strings
            question: User's question

        Returns:
            Verified answer
        """
        # Convert context list to string
        context_str = "\n\n".join(context)

        # Stage 1: Reason - Generate draft answer
        reason_result = self.reason(context=context_str, question=question)

        # Stage 2: Verify - Check and correct
        verify_result = self.verify(
            context=context_str,
            question=question,
            draft_answer=reason_result.answer
        )

        return verify_result
